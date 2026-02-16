"""Modello Wizard Progress Ads (campaign wizard state)

Ported from Ads AI (Node.js/SQLite) → Site Builder (FastAPI/PostgreSQL).
Tracks progress through the 6-step Campaign Wizard in 3 modes (Guided/Assisted/Manual).
Steps: objective → budget → audience → content → ad_copy → review.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdWizardProgress(Base):
    __tablename__ = "ad_wizard_progress"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("ad_clients.id", ondelete="CASCADE"), nullable=False)

    mode = Column(String, nullable=False)          # 'guided', 'assisted', 'manual'
    current_step = Column(String, nullable=False)  # 'objective', 'budget', 'audience', 'content', 'ad_copy', 'review'
    step_data = Column(JSON, nullable=True)        # Accumulated wizard form data
    campaign_data = Column(JSON, nullable=True)    # Final campaign config (on completion)
    status = Column(String, default="in_progress") # 'in_progress', 'completed', 'abandoned'

    # Relazioni
    client = relationship("AdClient", backref="wizard_progress")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_ad_wizard_progress_client_id", "client_id"),
        Index("ix_ad_wizard_progress_status", "status"),
    )
