import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'madasamy_portfolio_secret_2024')

    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

    # Admin credentials
    ADMIN_USERNAME = 'madasamy'
    ADMIN_PASSWORD = 'admin123'   # ← change after first login

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'webp'}
