"""Modello Metriche Ads (performance giornaliere delle campagne)

Ported from Ads AI (Node.js/SQLite) → Site Builder (FastAPI/PostgreSQL).
Metrics are synced daily via n8n campaign-monitor webhook.
Unique constraint on (campaign_id, date) enables upsert behavior.
"""

from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdMetric(Base):
    __tablename__ = "ad_metrics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id", ondelete="CASCADE"), nullable=False)

    date = Column(Date, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0)          # Click-through rate (%)
    cpc = Column(Float, default=0)          # Cost per click
    conversions = Column(Integer, default=0)
    cost = Column(Float, default=0)         # Total spend for the day
    cpa = Column(Float, nullable=True)      # Cost per acquisition
    roas = Column(Float, nullable=True)     # Return on ad spend (ecommerce)

    # Relazioni
    campaign = relationship("AdCampaign", back_populates="metrics")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("campaign_id", "date", name="uq_ad_metrics_campaign_date"),
        Index("ix_ad_metrics_campaign_id", "campaign_id"),
        Index("ix_ad_metrics_date", "date"),
    )
