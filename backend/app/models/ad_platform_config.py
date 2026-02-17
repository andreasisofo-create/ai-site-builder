"""Modello configurazione piattaforme esterne per Ads AI.

Stores API credentials and connection status for all external
integrations: Google Ads, Meta, DataForSEO, n8n, Telegram, AI models.
One config row per user (owner_id is unique).
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdPlatformConfig(Base):
    __tablename__ = "ad_platform_configs"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Google Ads
    google_developer_token = Column(String, nullable=True)
    google_client_id = Column(String, nullable=True)
    google_client_secret = Column(String, nullable=True)
    google_refresh_token = Column(String, nullable=True)
    google_mcc_id = Column(String, nullable=True)
    google_status = Column(String, default="not_configured")

    # Meta Marketing API
    meta_system_user_token = Column(String, nullable=True)
    meta_app_id = Column(String, nullable=True)
    meta_app_secret = Column(String, nullable=True)
    meta_business_id = Column(String, nullable=True)
    meta_pixel_id = Column(String, nullable=True)
    meta_status = Column(String, default="not_configured")

    # DataForSEO
    dataforseo_login = Column(String, nullable=True)
    dataforseo_password = Column(String, nullable=True)
    dataforseo_status = Column(String, default="not_configured")

    # n8n
    n8n_base_url = Column(String, nullable=True)
    n8n_api_key = Column(String, nullable=True)
    n8n_status = Column(String, default="not_configured")

    # Telegram
    telegram_bot_token = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)
    telegram_status = Column(String, default="not_configured")

    # AI Models
    claude_api_key = Column(String, nullable=True)
    openai_api_key = Column(String, nullable=True)
    ai_status = Column(String, default="not_configured")

    # Relationships
    owner = relationship("User", backref="ad_platform_config")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_ad_platform_configs_owner_id", "owner_id"),
    )
