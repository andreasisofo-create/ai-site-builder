"""Modello Cliente Ads (business client per campagne pubblicitarie)

Ported from Ads AI (Node.js/SQLite) → Site Builder (FastAPI/PostgreSQL).
Represents any business client managed by the Ads AI platform.
Enriched by the Investigator module (Module 1) which scrapes website data.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdClient(Base):
    __tablename__ = "ad_clients"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Core business info
    business_name = Column(String, nullable=False)
    business_type = Column(String, nullable=False)  # ristorazione, fitness, estetica, servizi_legali, etc.
    city = Column(String, nullable=False)
    region = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    website_url = Column(String, nullable=True)

    # Investigator-extracted profile (Module 1)
    description = Column(Text, nullable=True)
    services = Column(JSON, nullable=True)         # ["Consulenza", "Assistenza", ...]
    target_audience = Column(String, nullable=True)  # "B2B - Aziende", "B2C - Privati", etc.
    usp = Column(JSON, nullable=True)              # ["Qualita garantita", "Esperienza decennale"]
    analysis_confidence = Column(Integer, nullable=True)  # 0-100 confidence score from Investigator

    # Budget
    budget_monthly = Column(Float, default=0)

    # Relazioni
    owner = relationship("User", backref="ad_clients")
    campaigns = relationship("AdCampaign", back_populates="client", cascade="all, delete-orphan")
    strategies = relationship("AdStrategy", back_populates="client", cascade="all, delete-orphan")
    market_research = relationship("AdMarketResearch", back_populates="client", cascade="all, delete-orphan")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_ad_clients_owner_id", "owner_id"),
        Index("ix_ad_clients_business_type", "business_type"),
    )
