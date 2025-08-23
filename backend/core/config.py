"""
Application configuration management.

Handles environment variables, database settings, and external service
configurations for the AI Personal Tutor system.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    APP_NAME: str = "AI-Powered Personal Tutor"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:8080"
    
    # Database settings
    DATABASE_URL: str = "postgresql://klassy:MioNuG8fcHpCU6tVBoJW0rhdFSjLT6as@dpg-d29o447diees73d0ltl0-a.singapore-postgres.render.com/daviddb_c0ni"
    DATABASE_ECHO: bool = False
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # AI/ML Service settings
    AI_PROVIDER: str = "gemini"  # "openai", "gemini", or "huggingface"
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Google Gemini settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Hugging Face settings
    HUGGINGFACE_API_TOKEN: Optional[str] = None
    HUGGINGFACE_MODEL: str = "microsoft/DialoGPT-medium"
    
    # Common AI settings
    MAX_TOKENS: int = 150
    TEMPERATURE: float = 0.7
    
    # Learning algorithm settings
    INITIAL_DIFFICULTY_LEVEL: float = 0.5
    DIFFICULTY_ADJUSTMENT_RATE: float = 0.1
    MIN_DIFFICULTY: float = 0.1
    MAX_DIFFICULTY: float = 1.0
    
    # Student engagement settings
    SESSION_TIMEOUT_MINUTES: int = 30
    PROGRESS_TRACKING_ENABLED: bool = True
    ANALYTICS_ENABLED: bool = True
    
    # Content delivery settings
    CONTENT_CACHE_TTL: int = 3600  # 1 hour
    MAX_CONTENT_LENGTH: int = 1000
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    
    # Background task settings (Celery)
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Recommendation system settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    
    # Progress tracking ML model settings
    PROGRESS_MODEL_PATH: str = "./models/progress_model.pkl"
    
    # Hugging Face model settings
    HF_DATASETS_OFFLINE: str = "0"
    TRANSFORMERS_OFFLINE: str = "0" 
    HF_HOME: str = "./models/huggingface_cache"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
