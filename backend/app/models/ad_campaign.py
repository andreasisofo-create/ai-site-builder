"""Modello Campagna Ads (Google/Meta campaigns)

Ported from Ads AI (Node.js/SQLite) → Site Builder (FastAPI/PostgreSQL).
Created by the Broker module (Module 4) and optionally via Campaign Wizard.
Stores the full campaign configuration including targeting, ad groups, and ad copy.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("ad_clients.id", ondelete="CASCADE"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("ad_strategies.id", ondelete="SET NULL"), nullable=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True)

    # Campaign identity
    platform = Column(String, nullable=False)  # 'google', 'meta', 'both'
    name = Column(String, nullable=False)
    external_id = Column(String, nullable=True)  # Google/Meta API campaign ID
    status = Column(String, default="pending")   # 'pending', 'active', 'paused', 'ended'
    objective = Column(String, nullable=True)     # 'AWARENESS', 'TRAFFIC', 'LEADS', 'MESSAGES', 'SALES'

    # Budget
    budget_daily = Column(Float, default=0)
    budget_total = Column(Float, default=0)
    spent = Column(Float, default=0)

    # Campaign configuration (JSON blobs from Broker module)
    targeting = Column(JSON, nullable=True)    # locations, age, interests, radius, etc.
    ad_groups = Column(JSON, nullable=True)    # Google ad groups or Meta adsets
    ads = Column(JSON, nullable=True)          # Headlines, descriptions, creative
    settings = Column(JSON, nullable=True)     # bidStrategy, deliveryMethod, placements, etc.

    # Relazioni
    client = relationship("AdClient", back_populates="campaigns")
    strategy = relationship("AdStrategy", back_populates="campaigns")
    site = relationship("Site", backref="ad_campaigns")
    leads = relationship("AdLead", back_populates="campaign", cascade="all, delete-orphan")
    metrics = relationship("AdMetric", back_populates="campaign", cascade="all, delete-orphan")
    optimization_logs = relationship("AdOptimizationLog", back_populates="campaign", cascade="all, delete-orphan")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_ad_campaigns_client_id", "client_id"),
        Index("ix_ad_campaigns_site_id", "site_id"),
        Index("ix_ad_campaigns_status", "status"),
        Index("ix_ad_campaigns_platform", "platform"),
    )
