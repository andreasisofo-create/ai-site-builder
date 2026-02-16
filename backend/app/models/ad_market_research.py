"""Modello Ricerca di Mercato Ads (market research data)

Ported from Ads AI (Node.js/SQLite) → Site Builder (FastAPI/PostgreSQL).
Created by the Analyst module (Module 2).
Stores keyword research, competitor analysis, benchmarks, and trend data.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdMarketResearch(Base):
    __tablename__ = "ad_market_research"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("ad_clients.id", ondelete="CASCADE"), nullable=False)

    # Research data from Analyst module
    keywords_data = Column(JSON, nullable=True)      # {keywords: [...], negativeKeywords: [...], summary: {...}}
    competitors_data = Column(JSON, nullable=True)    # {competitors: [...], marketShare: {...}}
    benchmarks = Column(JSON, nullable=True)          # {avgCpc, avgCpm, avgCtr, avgCpl, recommendedBudget}
    trends = Column(JSON, nullable=True)              # {currentTrend, seasonality, recommendation}

    # Relazioni
    client = relationship("AdClient", back_populates="market_research")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_ad_market_research_client_id", "client_id"),
    )
