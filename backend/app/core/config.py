"""Configurazione applicazione"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Impostazioni dell'applicazione"""
    
    # App
    APP_NAME: str = "Site Builder"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database (SQLite per Render - funziona subito)
    DATABASE_URL: str = "sqlite:///./sitebuilder.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://site-generator-v2.vercel.app"]
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Vercel
    VERCEL_TOKEN: str = ""
    VERCEL_TEAM_ID: str = ""
    
    # Kimi API (AI Generation) - Diretta
    KIMI_API_KEY: str = ""
    KIMI_API_URL: str = "https://api.moonshot.cn/v1"
    KIMI_MODEL: str = "kimi-k2.5"
    
    # AI Configuration
    AI_MAX_TOKENS: int = 6000
    AI_TEMPERATURE: float = 0.7
    
    # Fallback OpenRouter (opzionale)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1"
    
    # Email (opzionale)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
