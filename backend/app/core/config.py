"""Configurazione applicazione"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Impostazioni dell'applicazione"""
    
    # App
    APP_NAME: str = "Site Builder"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database (PostgreSQL - Supabase in produzione, locale via Docker)
    DATABASE_URL: str = "postgresql://sitebuilder:sitebuilder123@localhost:5432/sitebuilder"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS - Accetta richieste da questi domini
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        # Domini Vercel (frontend produzione)
        "https://site-generator-v2.vercel.app",
        "https://www.site-generator-v2.vercel.app",
    ]
    
    # Se impostato a true, permette richieste da qualsiasi origine (NON sicuro per produzione!)
    # Utile per debugging temporaneo
    CORS_ALLOW_ALL: bool = True  # ATTENZIONE: Cambia a False dopo aver verificato tutto funzioni
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 giorni
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Vercel
    VERCEL_TOKEN: str = ""
    VERCEL_TEAM_ID: str = ""
    
    # Kimi / Moonshot API (AI Generation) - Diretta
    # Accetta sia KIMI_API_KEY che MOONSHOT_API_KEY come env var
    KIMI_API_KEY: str = ""
    MOONSHOT_API_KEY: str = ""
    KIMI_API_URL: str = "https://api.moonshot.cn/v1"
    KIMI_MODEL: str = "kimi-k2.5"

    @property
    def active_api_key(self) -> str:
        """Ritorna la prima API key disponibile (MOONSHOT > KIMI)."""
        return self.MOONSHOT_API_KEY or self.KIMI_API_KEY
    
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

    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    
    # Render
    RENDER_EXTERNAL_URL: str = ""  # Populated automatically by Render
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
