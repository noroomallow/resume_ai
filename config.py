import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key-change-in-production-32-chars')
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max file upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')