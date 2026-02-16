"""Modello Log Ottimizzazione Ads (optimization changes log)

Ported from Ads AI (Node.js/SQLite) → Site Builder (FastAPI/PostgreSQL).
Created by the Broker module (Module 4) when optimizing campaigns.
Tracks bid adjustments, keyword pauses, budget changes, and negative keyword additions.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdOptimizationLog(Base):
    __tablename__ = "ad_optimization_logs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id", ondelete="CASCADE"), nullable=False)

    changes = Column(JSON, nullable=False)  # [{type, action, value, reason}]
    status = Column(String, default="applied")  # 'applied', 'pending', 'rejected'

    # Relazioni
    campaign = relationship("AdCampaign", back_populates="optimization_logs")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_ad_optimization_logs_campaign_id", "campaign_id"),
    )
