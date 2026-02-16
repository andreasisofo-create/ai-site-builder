"""Modello AI Activity Log (Supervision Panel + pending decisions tracker)

New model for the Ads AI Supervision Panel.
Tracks all AI-generated decisions that require human approval or review.
Powers the Traffic Light System (system health monitoring).
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AdAiActivity(Base):
    __tablename__ = "ad_ai_activities"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("ad_clients.id", ondelete="CASCADE"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id", ondelete="SET NULL"), nullable=True)

    # Activity details
    module = Column(String, nullable=False)      # 'investigator', 'analyst', 'architect', 'broker'
    action_type = Column(String, nullable=False)  # 'strategy_created', 'campaign_published', 'optimization_applied', etc.
    description = Column(Text, nullable=True)
    severity = Column(String, default="info")    # Traffic Light: 'info', 'warning', 'critical'

    # Decision tracking (Supervision Panel)
    requires_approval = Column(String, default="no")  # 'no', 'pending', 'approved', 'rejected'
    decision_data = Column(JSON, nullable=True)        # The data being decided on
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String, nullable=True)

    # Relazioni
    client = relationship("AdClient", backref="ai_activities")
    campaign = relationship("AdCampaign", backref="ai_activities")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_ad_ai_activities_client_id", "client_id"),
        Index("ix_ad_ai_activities_module", "module"),
        Index("ix_ad_ai_activities_requires_approval", "requires_approval"),
        Index("ix_ad_ai_activities_severity", "severity"),
    )
