import os
import json
from datetime import datetime
from functools import wraps
from flask import (Flask, g, render_template, request, jsonify,redirect, url_for, session, send_from_directory, flash)
import psycopg
from psycopg.rows import dict_row
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from config import Config

try:
    from whitenoise import WhiteNoise
    _HAS_WHITENOISE = True
except ImportError:
    _HAS_WHITENOISE = False

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
if _HAS_WHITENOISE:
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
app.config.from_object(Config)


class DatabaseConfigurationError(RuntimeError):
    """Raised when a database-backed page is requested without PostgreSQL config."""

# ── Ensure upload folder exists ──────────────────────────────────────────────
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'projects'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'achievements'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resume'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'images'), exist_ok=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'])


def get_avatar_static_path():
    images_dir = os.path.join(app.static_folder, 'images')
    for ext in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
        name = f'avatar.{ext}'
        if os.path.isfile(os.path.join(images_dir, name)):
            return f'images/{name}'
    return 'images/avatar.jpg'


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def get_db():
    if 'db' not in g:
        database_url = (app.config.get('DATABASE_URL') or '').strip()
        if not database_url or database_url == 'postgresql://USER:PASSWORD@localhost:5432/portfolio_db' or 'USER:PASSWORD' in database_url:
            raise DatabaseConfigurationError(
                'Set DATABASE_URL in the project .env file or environment to connect to PostgreSQL.'
            )
        g.db = psycopg.connect(database_url, row_factory=dict_row, connect_timeout=5)
    return g.db


def get_cursor():
    return get_db().cursor()


@app.errorhandler(DatabaseConfigurationError)
def handle_database_configuration_error(error):
    message = 'PostgreSQL is not configured. Add DATABASE_URL to the project .env file and restart the app.'
    if request.path.startswith('/api/'):
        return jsonify({'error': message}), 503
    return render_template('admin/database_error.html', error_message=message), 503


@app.errorhandler(psycopg.Error)
def handle_database_error(error):
    message = (
        'Could not connect to PostgreSQL. Check DATABASE_URL in .env, make sure '
        'PostgreSQL is running, the database exists, and schema.sql has been applied. '
        'Then restart the app.'
    )
    if request.path.startswith('/api/'):
        return jsonify({'error': message, 'detail': str(error)}), 503
    return render_template('admin/database_error.html', error_message=message), 503


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ════════════════════════════════════════════════════════════════════════════
#  PUBLIC PORTFOLIO ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html', avatar_path=get_avatar_static_path())


# ── API: Projects ────────────────────────────────────────────────────────────
@app.route('/api/projects')
def api_projects():
    cur = get_cursor()
    cur.execute("SELECT * FROM projects ORDER BY featured DESC, created_at DESC")
    projects = cur.fetchall()
    cur.close()
    return jsonify(projects)


# ── API: Skills ──────────────────────────────────────────────────────────────
@app.route('/api/skills')
def api_skills():
    cur = get_cursor()
    cur.execute("SELECT * FROM skills ORDER BY category, percentage DESC")
    skills = cur.fetchall()
    cur.close()
    return jsonify(skills)


# ── API: Achievements ────────────────────────────────────────────────────────
@app.route('/api/achievements')
def api_achievements():
    cur = get_cursor()
    cur.execute("SELECT * FROM achievements ORDER BY date_earned DESC, created_at DESC")
    achievements = cur.fetchall()
    for a in achievements:
        if a.get('date_earned'):
            a['date_earned'] = str(a['date_earned'])
    cur.close()
    return jsonify(achievements)


# ── API: Coding Profiles ─────────────────────────────────────────────────────
@app.route('/api/coding-profiles')
def api_coding_profiles():
    cur = get_cursor()
    cur.execute("SELECT * FROM coding_profiles WHERE is_active=1 ORDER BY display_order, created_at")
    profiles = cur.fetchall()
    cur.close()
    return jsonify(profiles)


# ── API: About Me ────────────────────────────────────────────────────────────
@app.route('/api/about')
def api_about():
    cur = get_cursor()
    cur.execute("SELECT * FROM about ORDER BY id DESC LIMIT 1")
    about = cur.fetchone()
    cur.close()
    return jsonify(about or {})


# ── API: Contact form ────────────────────────────────────────────────────────
@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json(silent=True) or {}
    name    = (data.get('name') or '').strip()
    email   = (data.get('email') or '').strip()
    subject = (data.get('subject') or '').strip()
    message = (data.get('message') or '').strip()

    if not all([name, email, message]):
        return jsonify({'success': False, 'message': 'Please fill all required fields.'}), 400

    cur = get_cursor()
    cur.execute(
        "INSERT INTO messages (name, email, subject, message) VALUES (%s, %s, %s, %s)",
        (name, email, subject, message)
    )
    get_db().commit()
    cur.close()
    return jsonify({'success': True, 'message': 'Message sent successfully!'})


# ── Resume download ──────────────────────────────────────────────────────────
@app.route('/download-resume')
def download_resume():
    resume_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'resume')
    if not os.path.isdir(resume_dir):
        return jsonify({'error': 'Resume not yet uploaded.'}), 404
    files = [f for f in os.listdir(resume_dir) if f.lower().endswith('.pdf')]
    if files:
        latest = max(files, key=lambda f: os.path.getmtime(os.path.join(resume_dir, f)))
        return send_from_directory(resume_dir, latest, as_attachment=True)
    return jsonify({'error': 'Resume not yet uploaded.'}), 404


# ════════════════════════════════════════════════════════════════════════════
#  ADMIN ROUTES
# ════════════════════════════════════════════════════════════════════════════

@app.route('/admin')
@login_required
def admin_dashboard():
    cur = get_cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM projects")
    project_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM skills")
    skill_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM achievements")
    achievement_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM coding_profiles WHERE is_active=1")
    coding_profile_count = cur.fetchone()['cnt']
    cur.execute("SELECT COUNT(*) as cnt FROM messages WHERE is_read = 0")
    unread_count = cur.fetchone()['cnt']
    cur.execute("SELECT * FROM messages ORDER BY sent_at DESC LIMIT 5")
    recent_messages = cur.fetchall()
    cur.close()
    return render_template('admin/dashboard.html',
                           project_count=project_count,
                           skill_count=skill_count,
                           achievement_count=achievement_count,
                           coding_profile_count=coding_profile_count,
                           unread_count=unread_count,
                           recent_messages=recent_messages,
                           avatar_path=get_avatar_static_path())


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if (username == app.config['ADMIN_USERNAME'] and
                password == app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials. Try again.', 'error')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


# ── Admin: Projects ──────────────────────────────────────────────────────────
@app.route('/admin/projects')
@login_required
def admin_projects():
    cur = get_cursor()
    cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
    projects = cur.fetchall()
    cur.close()
    return render_template('admin/projects.html', projects=projects)


@app.route('/admin/projects/add', methods=['POST'])
@login_required
def admin_add_project():
    title       = request.form.get('title')
    description = request.form.get('description')
    tech_stack  = request.form.get('tech_stack')
    category    = request.form.get('category', 'Web')
    github_url  = request.form.get('github_url', '')
    live_url    = request.form.get('live_url', '')
    featured    = 1 if request.form.get('featured') else 0
    image_path  = ''

    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'projects', filename)
            file.save(filepath)
            image_path = f'uploads/projects/{filename}'

    cur = get_cursor()
    cur.execute(
        """INSERT INTO projects (title, description, tech_stack, category,
           github_url, live_url, image_path, featured)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (title, description, tech_stack, category, github_url, live_url, image_path, featured)
    )
    get_db().commit()
    cur.close()
    flash('Project added successfully!', 'success')
    return redirect(url_for('admin_projects'))


@app.route('/admin/projects/edit/<int:pid>', methods=['POST'])
@login_required
def admin_edit_project(pid):
    title       = request.form.get('title')
    description = request.form.get('description')
    tech_stack  = request.form.get('tech_stack')
    category    = request.form.get('category', 'Web')
    github_url  = request.form.get('github_url', '')
    live_url    = request.form.get('live_url', '')
    featured    = 1 if request.form.get('featured') else 0

    cur = get_cursor()
    # Handle image update
    file = request.files.get('image')
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'projects', filename)
        file.save(filepath)
        image_path = f'uploads/projects/{filename}'
        cur.execute(
            """UPDATE projects SET title=%s, description=%s, tech_stack=%s,
               category=%s, github_url=%s, live_url=%s, image_path=%s, featured=%s
               WHERE id=%s""",
            (title, description, tech_stack, category, github_url, live_url,
             image_path, featured, pid)
        )
    else:
        cur.execute(
            """UPDATE projects SET title=%s, description=%s, tech_stack=%s,
               category=%s, github_url=%s, live_url=%s, featured=%s
               WHERE id=%s""",
            (title, description, tech_stack, category, github_url, live_url, featured, pid)
        )
    get_db().commit()
    cur.close()
    flash('Project updated!', 'success')
    return redirect(url_for('admin_projects'))


@app.route('/admin/projects/delete/<int:pid>', methods=['POST'])
@login_required
def admin_delete_project(pid):
    cur = get_cursor()
    cur.execute("DELETE FROM projects WHERE id=%s", (pid,))
    get_db().commit()
    cur.close()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin_projects'))


# ── Admin: Skills ────────────────────────────────────────────────────────────
@app.route('/admin/skills')
@login_required
def admin_skills():
    cur = get_cursor()
    cur.execute("SELECT * FROM skills ORDER BY category, percentage DESC")
    skills = cur.fetchall()
    cur.close()
    return render_template('admin/skills.html', skills=skills)


@app.route('/admin/skills/add', methods=['POST'])
@login_required
def admin_add_skill():
    name       = request.form.get('name')
    category   = request.form.get('category', 'Programming')
    percentage = request.form.get('percentage', 80)
    icon_class = request.form.get('icon_class', 'fas fa-code')
    cur = get_cursor()
    cur.execute(
        "INSERT INTO skills (name, category, percentage, icon_class) VALUES (%s,%s,%s,%s)",
        (name, category, percentage, icon_class)
    )
    get_db().commit()
    cur.close()
    flash('Skill added!', 'success')
    return redirect(url_for('admin_skills'))


@app.route('/admin/skills/edit/<int:sid>', methods=['POST'])
@login_required
def admin_edit_skill(sid):
    name       = request.form.get('name')
    category   = request.form.get('category')
    percentage = request.form.get('percentage')
    icon_class = request.form.get('icon_class')
    cur = get_cursor()
    cur.execute(
        "UPDATE skills SET name=%s, category=%s, percentage=%s, icon_class=%s WHERE id=%s",
        (name, category, percentage, icon_class, sid)
    )
    get_db().commit()
    cur.close()
    flash('Skill updated!', 'success')
    return redirect(url_for('admin_skills'))


@app.route('/admin/skills/delete/<int:sid>', methods=['POST'])
@login_required
def admin_delete_skill(sid):
    cur = get_cursor()
    cur.execute("DELETE FROM skills WHERE id=%s", (sid,))
    get_db().commit()
    cur.close()
    flash('Skill deleted.', 'success')
    return redirect(url_for('admin_skills'))


# ── Admin: Achievements ──────────────────────────────────────────────────────
@app.route('/admin/achievements')
@login_required
def admin_achievements():
    cur = get_cursor()
    cur.execute("SELECT * FROM achievements ORDER BY date_earned DESC")
    achievements = cur.fetchall()
    cur.close()
    return render_template('admin/achievements.html', achievements=achievements)


@app.route('/admin/achievements/add', methods=['POST'])
@login_required
def admin_add_achievement():
    title           = request.form.get('title')
    description     = request.form.get('description')
    issuer          = request.form.get('issuer')
    date_earned     = request.form.get('date_earned') or None
    certificate_url = request.form.get('certificate_url', '')
    image_path      = ''

    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'achievements', filename)
            file.save(filepath)
            image_path = f'uploads/achievements/{filename}'

    cur = get_cursor()
    cur.execute(
        """INSERT INTO achievements (title, description, issuer, image_path,
           certificate_url, date_earned) VALUES (%s,%s,%s,%s,%s,%s)""",
        (title, description, issuer, image_path, certificate_url, date_earned)
    )
    get_db().commit()
    cur.close()
    flash('Achievement added!', 'success')
    return redirect(url_for('admin_achievements'))


@app.route('/admin/achievements/edit/<int:aid>', methods=['POST'])
@login_required
def admin_edit_achievement(aid):
    title           = request.form.get('title')
    description     = request.form.get('description')
    issuer          = request.form.get('issuer')
    date_earned     = request.form.get('date_earned') or None
    certificate_url = request.form.get('certificate_url', '')

    cur = get_cursor()
    file = request.files.get('image')
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'achievements', filename)
        file.save(filepath)
        image_path = f'uploads/achievements/{filename}'
        cur.execute(
            """UPDATE achievements SET title=%s, description=%s, issuer=%s,
               image_path=%s, certificate_url=%s, date_earned=%s WHERE id=%s""",
            (title, description, issuer, image_path, certificate_url, date_earned, aid)
        )
    else:
        cur.execute(
            """UPDATE achievements SET title=%s, description=%s, issuer=%s,
               certificate_url=%s, date_earned=%s WHERE id=%s""",
            (title, description, issuer, certificate_url, date_earned, aid)
        )
    get_db().commit()
    cur.close()
    flash('Achievement updated!', 'success')
    return redirect(url_for('admin_achievements'))


@app.route('/admin/achievements/delete/<int:aid>', methods=['POST'])
@login_required
def admin_delete_achievement(aid):
    cur = get_cursor()
    cur.execute("DELETE FROM achievements WHERE id=%s", (aid,))
    get_db().commit()
    cur.close()
    flash('Achievement deleted.', 'success')
    return redirect(url_for('admin_achievements'))


# ── Admin: Messages ──────────────────────────────────────────────────────────
@app.route('/admin/messages')
@login_required
def admin_messages():
    cur = get_cursor()
    cur.execute("UPDATE messages SET is_read=1")
    get_db().commit()
    cur.execute("SELECT * FROM messages ORDER BY sent_at DESC")
    messages = cur.fetchall()
    cur.close()
    return render_template('admin/messages.html', messages=messages)


@app.route('/admin/messages/delete/<int:mid>', methods=['POST'])
@login_required
def admin_delete_message(mid):
    cur = get_cursor()
    cur.execute("DELETE FROM messages WHERE id=%s", (mid,))
    get_db().commit()
    cur.close()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin_messages'))


# ── Admin: Resume upload ─────────────────────────────────────────────────────
@app.route('/admin/resume/upload', methods=['POST'])
@login_required
def admin_upload_resume():
    if 'resume' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_dashboard'))
    file = request.files['resume']
    if file and file.filename.endswith('.pdf'):
        filename = 'Madasamy_C_Resume.pdf'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'resume', filename)
        file.save(filepath)
        flash('Resume uploaded successfully!', 'success')
    else:
        flash('Only PDF files allowed.', 'error')
    return redirect(url_for('admin_dashboard'))


# ── Admin: Avatar upload ─────────────────────────────────────────────────────
@app.route('/admin/avatar/upload', methods=['POST'])
@login_required
def admin_upload_avatar():
    if 'avatar' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_dashboard'))
    file = request.files['avatar']
    if not file or not file.filename:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_dashboard'))

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
        flash('Only image files (png, jpg, jpeg, gif, webp) are allowed.', 'error')
        return redirect(url_for('admin_dashboard'))

    images_dir = os.path.join(app.static_folder, 'images')
    os.makedirs(images_dir, exist_ok=True)
    for old_ext in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
        old_path = os.path.join(images_dir, f'avatar.{old_ext}')
        if os.path.isfile(old_path):
            os.remove(old_path)

    filename = f'avatar.{ext}'
    file.save(os.path.join(images_dir, filename))
    flash('Avatar updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


# ── Admin: Coding Profiles ───────────────────────────────────────────────────
@app.route('/admin/coding-profiles')
@login_required
def admin_coding_profiles():
    cur = get_cursor()
    cur.execute("SELECT * FROM coding_profiles ORDER BY display_order, created_at")
    profiles = cur.fetchall()
    cur.close()
    return render_template('admin/coding_profiles.html', profiles=profiles)


@app.route('/admin/coding-profiles/add', methods=['POST'])
@login_required
def admin_add_coding_profile():
    platform = request.form.get('platform')
    username = request.form.get('username')
    profile_url = request.form.get('profile_url')
    icon_class = request.form.get('icon_class')
    display_name = request.form.get('display_name')
    stats_json = request.form.get('stats_json') or '{}'
    is_active = 1 if request.form.get('is_active') else 0
    display_order = int(request.form.get('display_order') or 0)

    cur = get_cursor()
    cur.execute(
        """INSERT INTO coding_profiles (platform, username, profile_url, icon_class, display_name, stats_json, is_active, display_order)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (platform, username, profile_url, icon_class, display_name, stats_json, is_active, display_order)
    )
    get_db().commit()
    cur.close()
    flash('Coding profile added successfully!', 'success')
    return redirect(url_for('admin_coding_profiles'))


@app.route('/admin/coding-profiles/edit/<int:pid>', methods=['POST'])
@login_required
def admin_edit_coding_profile(pid):
    platform = request.form.get('platform')
    username = request.form.get('username')
    profile_url = request.form.get('profile_url')
    icon_class = request.form.get('icon_class')
    display_name = request.form.get('display_name')
    stats_json = request.form.get('stats_json') or '{}'
    is_active = 1 if request.form.get('is_active') else 0
    display_order = int(request.form.get('display_order') or 0)

    cur = get_cursor()
    cur.execute(
        """UPDATE coding_profiles SET platform=%s, username=%s, profile_url=%s, icon_class=%s, display_name=%s, stats_json=%s, is_active=%s, display_order=%s WHERE id=%s""",
        (platform, username, profile_url, icon_class, display_name, stats_json, is_active, display_order, pid)
    )
    get_db().commit()
    cur.close()
    flash('Coding profile updated!', 'success')
    return redirect(url_for('admin_coding_profiles'))


@app.route('/admin/coding-profiles/delete/<int:pid>', methods=['POST'])
@login_required
def admin_delete_coding_profile(pid):
    cur = get_cursor()
    cur.execute("DELETE FROM coding_profiles WHERE id=%s", (pid,))
    get_db().commit()
    cur.close()
    flash('Coding profile deleted.', 'success')
    return redirect(url_for('admin_coding_profiles'))


# ── Admin: About Me ──────────────────────────────────────────────────────────
@app.route('/admin/about', methods=['GET', 'POST'])
@login_required
def admin_about():
    cur = get_cursor()
    if request.method == 'POST':
        title = request.form.get('title')
        intro_text = request.form.get('intro_text')
        journey_text = request.form.get('journey_text')
        status_text = request.form.get('status_text')
        location = request.form.get('location')
        role = request.form.get('role')
        experience = request.form.get('experience')

        cur.execute("SELECT id FROM about ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            cur.execute(
                """UPDATE about SET title=%s, intro_text=%s, journey_text=%s, status_text=%s, location=%s, role=%s, experience=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s""",
                (title, intro_text, journey_text, status_text, location, role, experience, row['id'])
            )
        else:
            cur.execute(
                """INSERT INTO about (title, intro_text, journey_text, status_text, location, role, experience) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (title, intro_text, journey_text, status_text, location, role, experience)
            )
        get_db().commit()
        flash('About section updated!', 'success')
        return redirect(url_for('admin_about'))

    cur.execute("SELECT * FROM about ORDER BY id DESC LIMIT 1")
    about = cur.fetchone()
    cur.close()
    return render_template('admin/about.html', about=about or {})


# ── Serve uploads ────────────────────────────────────────────────────────────
@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=False, port=5000)
