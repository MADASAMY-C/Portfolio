# AI-Animated Portfolio — Madasamy C

## Overview

A full-stack, recruiter-focused portfolio website with stunning AI-inspired animations, Flask backend, and MySQL database. The design targets product-based company recruiters, showcasing DSA, ML/AI, and software skills in a compelling, modern UI.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3 (custom animations), Vanilla JS |
| Backend | Python (Flask) |
| Database | MySQL |
| Animation | CSS keyframes, Particles.js, GSAP, Three.js (neural net background) |

---

## Proposed File Structure

```
Portfolio/
├── app.py                   # Flask app entry point
├── config.py                # DB + secret config
├── requirements.txt
├── static/
│   ├── css/
│   │   ├── style.css        # Global styles & animations
│   │   ├── admin.css        # Admin panel styles
│   ├── js/
│   │   ├── main.js          # Animations, particles, GSAP
│   │   ├── admin.js         # Admin CRUD logic
│   │   ├── particles.js     # Particles background
│   ├── images/              # Uploaded images/certificates
│   ├── resume/              # Resume PDF upload
├── templates/
│   ├── index.html           # Main portfolio (all sections SPA)
│   ├── admin/
│   │   ├── login.html       # Admin login
│   │   ├── dashboard.html   # Admin dashboard
│   │   ├── projects.html    # Manage projects
│   │   ├── skills.html      # Manage skills
│   │   ├── achievements.html# Manage certificates
│   │   └── messages.html    # View contact messages
├── uploads/                 # File upload directory
```

---

## Database Schema (MySQL)

### Tables

- **projects** — id, title, description, tech_stack, github_url, live_url, image_path, created_at
- **skills** — id, name, category, percentage, icon_class
- **achievements** — id, title, description, image_path, date_earned, certificate_url
- **messages** — id, name, email, subject, message, sent_at, is_read
- **admin** — id, username, password_hash

---

## Sections & Features

### 🏠 Home
- Full-screen hero with animated neural network / particle background (Three.js)
- Typing animation: "I'm Madasamy C — Data Analyst | Software Engineer | AI/ML Engineer"
- **LeetCode DSA stats widget** (animated counters showing problems solved)
- **"Let's Connect" button** → opens LinkedIn profile in new tab
- Floating animated code snippets as decoration

### 👤 About
- Left: animated profile avatar + floating badges (MCA, AI/ML, etc.)
- Right: bio text with stagger-in animation
- Highlights: MCA student, passionate about AI/ML, Data Analytics, Software Dev
- **Download Resume** button → serves PDF from server

### 🚀 Projects
- Filterable project cards (All | AI/ML | Web | Data)
- Cards with: image, title, tech stack badges, GitHub + Live Demo links
- Hover: 3D card flip with project details
- Data loaded from MySQL via Flask API

### 🛠 Skills
- Animated radial/circular progress bars per skill
- Grouped by: Programming | AI/ML | Data | Tools
- Data from MySQL

### 🏆 Achievements
- Certificate gallery with lightbox viewer
- Timeline layout with entrance animations
- Data from MySQL

### 📬 Contact
- Glassmorphism form: Name, Email, Subject, Message
- Submit → Flask API → saves to MySQL
- Info cards: Email, GitHub, LinkedIn
- Success/error toast notifications

### 🔐 Admin Panel (`/admin`)
- Password-protected login
- Dashboard with counts overview
- Full CRUD for: Projects, Skills, Achievements
- View/delete contact messages
- Upload resume PDF
- Upload project images & certificate images

---

## API Routes (Flask)

| Method | Route | Description |
|---|---|---|
| GET | `/` | Serve main portfolio |
| GET | `/api/projects` | Get all projects |
| GET | `/api/skills` | Get all skills |
| GET | `/api/achievements` | Get all achievements |
| POST | `/api/contact` | Submit contact form |
| GET | `/admin` | Admin dashboard |
| POST | `/admin/login` | Admin login |
| POST | `/admin/logout` | Admin logout |
| GET/POST | `/admin/projects` | CRUD projects |
| GET/POST | `/admin/skills` | CRUD skills |
| GET/POST | `/admin/achievements` | CRUD achievements |
| GET | `/admin/messages` | View messages |
| POST | `/download-resume` | Serve resume PDF |

---

## Animation Strategy

- **Neural network background** — Three.js animated dots + connecting lines (AI theme)
- **Typing effect** — Typewriter.js or custom JS
- **Scroll animations** — Intersection Observer API + CSS transitions
- **Skill bars** — CSS animation triggered on scroll
- **Particle system** — Particles.js in hero section
- **3D card hover** — CSS perspective + rotateX/Y
- **Counter animation** — Animated number increment for DSA stats
- **Glassmorphism UI** — Frosted glass cards throughout

---

## Verification Plan

### Automated
- Run `python app.py` and verify all routes respond
- Test contact form submission saves to DB
- Test admin CRUD operations

### Manual
- Open portfolio in browser, verify all animations play
- Verify "Let's Connect" → LinkedIn opens
- Verify "Download Resume" works
- Verify admin login/logout
- Test on mobile (responsive design)
