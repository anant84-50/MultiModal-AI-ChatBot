import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Multimodal AI Chatbot MVP"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database URL - default to PostgreSQL, with auto-fallback to SQLite if PostgreSQL is unreachable
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/multimodal_chat"
    SQLITE_FALLBACK_URL: str = f"sqlite:///{BASE_DIR}/multimodal_chat.db"
    
    # AI Provider Keys
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-3.1-flash-lite"
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    
    # File Storage
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    GENERATED_DIR: Path = BASE_DIR / "generated"
    MAX_FILE_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: set = {
        ".png", ".jpg", ".jpeg", ".webp", ".gif",
        ".pdf", ".docx", ".txt", ".md",
        ".mp3", ".wav", ".m4a", ".ogg"
    }

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Ensure storage directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
