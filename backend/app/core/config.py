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
    KIMI_API_URL: str = "https://api.moonshot.ai/v1"
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

    # Resend (email transazionali)
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "Site Builder <noreply@sitebuilder.it>"

    # Email verification
    EMAIL_VERIFICATION_REQUIRED: bool = False  # Se True, richiede verifica email alla registrazione
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    
    # Revolut Merchant API (pagamenti una tantum)
    REVOLUT_API_KEY: str = ""           # API key da Revolut Business > API Settings
    REVOLUT_WEBHOOK_SECRET: str = ""    # Signing secret per verificare webhook
    REVOLUT_SANDBOX: bool = True        # True = sandbox, False = produzione

    # Generation Pipeline
    GENERATION_PIPELINE: str = "databinding"  # "databinding" | "swarm" | "n8n"
    N8N_WEBHOOK_URL: str = ""  # n8n webhook URL for external generation
    N8N_CALLBACK_SECRET: str = ""  # Shared secret for n8n callback auth

    # VPS Deploy (Hostinger)
    VPS_DEPLOY_URL: str = ""            # e.g., "http://72.62.42.113:8090"
    VPS_DEPLOY_SECRET: str = ""         # Shared secret for VPS receiver auth
    DEPLOY_TARGET: str = "vps"          # "vps" or "vercel"
    SITE_BASE_DOMAIN: str = "e-quipe.app"

    # Render
    RENDER_EXTERNAL_URL: str = ""  # Populated automatically by Render
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
