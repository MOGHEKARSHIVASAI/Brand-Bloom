import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # AI API Keys (add your keys here)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Database configuration (for future use)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ai_toolkit.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False