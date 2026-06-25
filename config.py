import os
from dotenv import load_dotenv

# Load .env in development if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'devops-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///devops_board.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookie / session hardening defaults
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('1', 'true', 'yes')

    # Flask-WTF (CSRF) can be enabled by setting this to True in production
    WTF_CSRF_ENABLED = True
