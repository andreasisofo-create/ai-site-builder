"""Configurazione applicazione"""

import logging
import os
import secrets
from pydantic_settings import BaseSettings
from typing import List

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Impostazioni dell'applicazione"""

    # App
    APP_NAME: str = "Site Builder"
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_hex(32)
    
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
        # Dominio custom
        "https://e-quipe.app",
        "https://www.e-quipe.app",
    ]
    
    # Se impostato a true, permette richieste da qualsiasi origine (NON sicuro per produzione!)
    # Utile per debugging temporaneo
    CORS_ALLOW_ALL: bool = False
    
    # Admin
    ADMIN_EMAILS: str = ""  # Comma-separated list of admin emails for auto-premium
    ADMIN_USERNAME: str = "E-quipe!"
    ADMIN_PASSWORD: str = "E-quipe!"

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 giorni
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Vercel
    VERCEL_TOKEN: str = ""
    VERCEL_TEAM_ID: str = ""
    
    # AI Provider selection: "openrouter" | "kimi" | "glm5" | "deepseek"
    # Auto-detected from available API keys if not set explicitly.
    AI_PROVIDER: str = ""

    # Kimi / Moonshot API (legacy, backward compatible)
    KIMI_API_KEY: str = ""
    MOONSHOT_API_KEY: str = ""
    KIMI_API_URL: str = "https://api.moonshot.ai/v1"
    KIMI_MODEL: str = "kimi-k2.5"

    # OpenRouter (unified gateway — recommended)
    # Generation: Gemini 2.5 Pro — best quality/price for HTML/CSS, vision, 1M context
    OPENROUTER_MODEL: str = "google/gemini-2.5-pro"

    # Hybrid strategy: separate model for chat refine (fast + cheap)
    # Refine: Gemini 2.5 Flash — 250 tok/s, vision, 1M context, $0.30/$2.50 per 1M
    OPENROUTER_REFINE_MODEL: str = "google/gemini-2.5-flash"

    # GLM-5 direct (Z.ai / Zhipu)
    GLM5_API_KEY: str = ""
    GLM5_API_URL: str = "https://api.z.ai/api/paas/v4"
    GLM5_MODEL: str = "glm-5"

    # DeepSeek direct
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    @property
    def active_ai_provider(self) -> str:
        """Determine the AI provider. Explicit AI_PROVIDER wins, else auto-detect from keys."""
        if self.AI_PROVIDER:
            return self.AI_PROVIDER.lower()
        # Auto-detect: prefer OpenRouter > DeepSeek > GLM5 > Kimi
        if self.OPENROUTER_API_KEY:
            return "openrouter"
        if self.DEEPSEEK_API_KEY:
            return "deepseek"
        if self.GLM5_API_KEY:
            return "glm5"
        return "kimi"

    @property
    def active_api_key(self) -> str:
        """Ritorna la API key per il provider attivo."""
        provider = self.active_ai_provider
        if provider == "openrouter":
            return self.OPENROUTER_API_KEY
        if provider == "deepseek":
            return self.DEEPSEEK_API_KEY
        if provider == "glm5":
            return self.GLM5_API_KEY
        # Kimi fallback
        return self.MOONSHOT_API_KEY or self.KIMI_API_KEY

    @property
    def admin_emails_list(self) -> List[str]:
        """Parse ADMIN_EMAILS comma-separated string into a list of lowercase emails."""
        if not self.ADMIN_EMAILS:
            return []
        return [e.strip().lower() for e in self.ADMIN_EMAILS.split(",") if e.strip()]
    
    # AI Configuration
    AI_MAX_TOKENS: int = 6000
    AI_TEMPERATURE: float = 0.7
    
    # OpenRouter API key (unified gateway for multiple AI providers)
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

    # fal.ai (Flux image generation) - $0.025/img schnell, $0.04/img pro
    FAL_API_KEY: str = ""  # fal.ai API key (get from https://fal.ai/dashboard/keys)

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

# Warn if SECRET_KEY was not explicitly set (using auto-generated random key)
if os.environ.get("SECRET_KEY") is None:
    logger.warning(
        "SECRET_KEY not set in environment. Using a random key. "
        "Sessions will not persist across restarts. Set SECRET_KEY in .env for production."
    )
