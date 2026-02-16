"""Modello Lead Ads (leads generati dalle campagne)

Ported from Ads AI (Node.js/SQLite) → Site Builder (FastAPI/PostgreSQL).
Leads come from Meta Lead Ads forms and Google Ads conversions.
Synced via n8n lead-sync webhook.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdLead(Base):
    __tablename__ = "ad_leads"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="new")  # 'new', 'contacted', 'qualified', 'converted', 'lost'
    notes = Column(Text, nullable=True)
    source = Column(String, nullable=True)  # 'meta_form', 'google_ads', 'website', 'manual'
    form_data = Column(JSON, nullable=True)  # Raw form submission data from Meta Lead Ads

    # Relazioni
    campaign = relationship("AdCampaign", back_populates="leads")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_ad_leads_campaign_id", "campaign_id"),
        Index("ix_ad_leads_status", "status"),
    )
