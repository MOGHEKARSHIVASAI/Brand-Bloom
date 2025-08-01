import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Alternative: Google Gemini API (if you prefer)
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # AI Configuration
    AI_MODEL = os.environ.get('AI_MODEL', 'openai')  # 'openai' or 'gemini'
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '1500'))
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.7'))
    
    # Database configuration (for future use)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ai_toolkit.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False