"""Model for tracking which GSAP effects were used per site generation."""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class EffectUsage(Base):
    __tablename__ = "effect_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    template_style = Column(String, nullable=True)
    effects_json = Column(JSON, nullable=False)  # {"h1": ["text-split"], "h2": ["blur-in"], ...}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
