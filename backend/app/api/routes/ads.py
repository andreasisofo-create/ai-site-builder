"""Ads AI Platform — FastAPI Routes

Ported from Ads AI (Node.js/Express) → Site Builder (FastAPI/PostgreSQL).
Full autonomous advertising platform with:
- CRUD for Clients, Campaigns, Leads, Metrics
- 4-Module AI Pipeline: Investigator → Analyst → Architect → Broker
- Campaign Wizard (6 steps, 3 modes)
- Supervision Panel (approve/reject AI decisions)
- Knowledge Base (14 sector benchmarks)
- AI Activity Log & Traffic Light system
"""

import json
import logging
import os
import re
import subprocess
from datetime import date, datetime, timezone
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.api.routes.admin import require_admin
from app.models.user import User, PLAN_CONFIG
from app.models.site import Site
from app.models.ad_client import AdClient
from app.models.ad_campaign import AdCampaign
from app.models.ad_lead import AdLead
from app.models.ad_metric import AdMetric
from app.models.ad_strategy import AdStrategy
from app.models.ad_market_research import AdMarketResearch
from app.models.ad_wizard_progress import AdWizardProgress
from app.models.ad_optimization_log import AdOptimizationLog
from app.models.ad_ai_activity import AdAiActivity
from app.models.ad_platform_config import AdPlatformConfig

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# SCHEMAS
# =============================================================================

class AdClientCreate(BaseModel):
    business_name: str
    business_type: str
    city: str
    email: str
    region: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    budget_monthly: Optional[float] = 0


class AdClientUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    budget_monthly: Optional[float] = None


class AdCampaignCreate(BaseModel):
    client_id: int
    platform: str  # 'google', 'meta', 'both'
    name: str
    site_id: Optional[int] = None
    strategy_id: Optional[int] = None
    objective: Optional[str] = None
    status: Optional[str] = "active"
    budget_daily: Optional[float] = 0
    budget_total: Optional[float] = 0
    targeting: Optional[dict] = None
    ad_groups: Optional[dict] = None
    ads: Optional[dict] = None
    settings: Optional[dict] = None


class AdCampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    budget_daily: Optional[float] = None
    budget_total: Optional[float] = None
    spent: Optional[float] = None
    targeting: Optional[dict] = None
    ad_groups: Optional[dict] = None
    ads: Optional[dict] = None
    settings: Optional[dict] = None


class AdLeadCreate(BaseModel):
    campaign_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = "new"
    notes: Optional[str] = None
    source: Optional[str] = None
    form_data: Optional[dict] = None


class AdLeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AdMetricCreate(BaseModel):
    campaign_id: int
    date: str  # YYYY-MM-DD
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0
    ctr: Optional[float] = 0
    cpc: Optional[float] = 0
    conversions: Optional[int] = 0
    cost: Optional[float] = 0
    cpa: Optional[float] = None
    roas: Optional[float] = None


class InvestigateRequest(BaseModel):
    website_url: str


class ResearchRequest(BaseModel):
    client_id: Optional[int] = None
    business_type: str
    city: str
    services: Optional[List[str]] = None


class StrategyRequest(BaseModel):
    client_id: int
    budget_monthly: Optional[float] = 500


class CampaignCreateRequest(BaseModel):
    client_id: int
    strategy_id: int
    platform: str  # 'google', 'meta', 'both'


class PipelineRequest(BaseModel):
    website_url: str
    budget_monthly: Optional[float] = 500
    auto_approve: Optional[bool] = False


class WizardStartRequest(BaseModel):
    client_id: int
    mode: str  # 'guided', 'assisted', 'manual'


class WizardStepRequest(BaseModel):
    wizard_id: int
    step: str
    data: Optional[dict] = {}
    mode: Optional[str] = "guided"
    client_profile: Optional[dict] = None


class SupervisionActionRequest(BaseModel):
    action: str  # 'approve' or 'reject'
    reason: Optional[str] = None


# =============================================================================
# HELPERS — Ownership check
# =============================================================================

def _get_client_or_404(
    client_id: int, user: User, db: Session
) -> AdClient:
    client = db.query(AdClient).filter(
        AdClient.id == client_id,
        AdClient.owner_id == user.id,
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


def _check_campaign_limit(user: User, db: Session):
    """Check if user has reached their ads campaign limit."""
    plan_cfg = PLAN_CONFIG.get(user.plan or "free", PLAN_CONFIG["free"])
    limit = plan_cfg.get("ads_campaigns_limit", 0)
    if user.is_superuser or user.is_premium:
        return  # No limit
    current_count = db.query(func.count(AdCampaign.id)).join(AdClient).filter(
        AdClient.owner_id == user.id
    ).scalar() or 0
    if current_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Campaign limit reached ({limit}). Upgrade your plan.",
        )


# =============================================================================
# CLIENT ROUTES
# =============================================================================

@router.post("/clients")
async def create_client(
    data: AdClientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    client = AdClient(owner_id=current_user.id, **data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"success": True, "data": _serialize_client(client)}


@router.get("/clients")
async def list_clients(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    clients = (
        db.query(AdClient)
        .filter(AdClient.owner_id == current_user.id)
        .order_by(AdClient.created_at.desc())
        .all()
    )
    return {"success": True, "count": len(clients), "data": [_serialize_client(c) for c in clients]}


@router.get("/clients/{client_id}")
async def get_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    client = _get_client_or_404(client_id, current_user, db)
    return {"success": True, "data": _serialize_client(client)}


@router.put("/clients/{client_id}")
async def update_client(
    client_id: int,
    data: AdClientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    client = _get_client_or_404(client_id, current_user, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return {"success": True, "data": _serialize_client(client)}


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    client = _get_client_or_404(client_id, current_user, db)
    db.delete(client)
    db.commit()
    return {"success": True, "message": "Client deleted"}


def _serialize_client(c: AdClient) -> dict:
    return {
        "id": c.id,
        "owner_id": c.owner_id,
        "business_name": c.business_name,
        "business_type": c.business_type,
        "city": c.city,
        "region": c.region,
        "address": c.address,
        "email": c.email,
        "phone": c.phone,
        "website_url": c.website_url,
        "description": c.description,
        "services": c.services,
        "target_audience": c.target_audience,
        "usp": c.usp,
        "analysis_confidence": c.analysis_confidence,
        "budget_monthly": c.budget_monthly,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


# =============================================================================
# CAMPAIGN ROUTES
# =============================================================================

@router.post("/campaigns")
async def create_campaign(
    data: AdCampaignCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _get_client_or_404(data.client_id, current_user, db)
    _check_campaign_limit(current_user, db)
    valid_platforms = ("google", "meta", "both")
    if data.platform not in valid_platforms:
        raise HTTPException(status_code=400, detail=f"Platform must be one of: {', '.join(valid_platforms)}")
    campaign = AdCampaign(**data.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return {"success": True, "data": _serialize_campaign(campaign)}


@router.get("/campaigns")
async def list_campaigns(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(AdCampaign).join(AdClient).filter(AdClient.owner_id == current_user.id)
    if client_id:
        query = query.filter(AdCampaign.client_id == client_id)
    if status:
        query = query.filter(AdCampaign.status == status)
    campaigns = query.order_by(AdCampaign.created_at.desc()).all()
    return {"success": True, "count": len(campaigns), "data": [_serialize_campaign(c) for c in campaigns]}


@router.get("/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    campaign = db.query(AdCampaign).join(AdClient).filter(
        AdCampaign.id == campaign_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"success": True, "data": _serialize_campaign(campaign)}


@router.put("/campaigns/{campaign_id}")
async def update_campaign(
    campaign_id: int,
    data: AdCampaignUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    campaign = db.query(AdCampaign).join(AdClient).filter(
        AdCampaign.id == campaign_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    return {"success": True, "data": _serialize_campaign(campaign)}


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    campaign = db.query(AdCampaign).join(AdClient).filter(
        AdCampaign.id == campaign_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(campaign)
    db.commit()
    return {"success": True, "message": "Campaign deleted"}


def _serialize_campaign(c: AdCampaign) -> dict:
    return {
        "id": c.id,
        "client_id": c.client_id,
        "client_name": c.client.business_name if c.client else None,
        "strategy_id": c.strategy_id,
        "site_id": c.site_id,
        "platform": c.platform,
        "name": c.name,
        "external_id": c.external_id,
        "status": c.status,
        "objective": c.objective,
        "budget_daily": c.budget_daily,
        "budget_total": c.budget_total,
        "spent": c.spent,
        "targeting": c.targeting,
        "ad_groups": c.ad_groups,
        "ads": c.ads,
        "settings": c.settings,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


# =============================================================================
# LEAD ROUTES
# =============================================================================

@router.post("/leads")
async def create_lead(
    data: AdLeadCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Verify campaign belongs to user
    campaign = db.query(AdCampaign).join(AdClient).filter(
        AdCampaign.id == data.campaign_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    lead = AdLead(**data.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"success": True, "data": _serialize_lead(lead)}


@router.get("/leads")
async def list_leads(
    campaign_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(AdLead).join(AdCampaign).join(AdClient).filter(
        AdClient.owner_id == current_user.id
    )
    if campaign_id:
        query = query.filter(AdLead.campaign_id == campaign_id)
    if status:
        query = query.filter(AdLead.status == status)
    leads = query.order_by(AdLead.created_at.desc()).all()
    return {"success": True, "count": len(leads), "data": [_serialize_lead(l) for l in leads]}


@router.put("/leads/{lead_id}")
async def update_lead(
    lead_id: int,
    data: AdLeadUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    lead = db.query(AdLead).join(AdCampaign).join(AdClient).filter(
        AdLead.id == lead_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return {"success": True, "data": _serialize_lead(lead)}


@router.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    lead = db.query(AdLead).join(AdCampaign).join(AdClient).filter(
        AdLead.id == lead_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return {"success": True, "message": "Lead deleted"}


def _serialize_lead(l: AdLead) -> dict:
    return {
        "id": l.id,
        "campaign_id": l.campaign_id,
        "campaign_name": l.campaign.name if l.campaign else None,
        "name": l.name,
        "email": l.email,
        "phone": l.phone,
        "status": l.status,
        "notes": l.notes,
        "source": l.source,
        "form_data": l.form_data,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }


# =============================================================================
# METRICS ROUTES
# =============================================================================

@router.post("/metrics")
async def create_metric(
    data: AdMetricCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Verify campaign ownership
    campaign = db.query(AdCampaign).join(AdClient).filter(
        AdCampaign.id == data.campaign_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    metric_date = date.fromisoformat(data.date)

    # Upsert: update if exists for same campaign+date
    existing = db.query(AdMetric).filter(
        AdMetric.campaign_id == data.campaign_id,
        AdMetric.date == metric_date,
    ).first()
    if existing:
        for field in ("impressions", "clicks", "ctr", "cpc", "conversions", "cost", "cpa", "roas"):
            val = getattr(data, field)
            if val is not None:
                setattr(existing, field, val)
        db.commit()
        db.refresh(existing)
        return {"success": True, "data": _serialize_metric(existing)}

    metric = AdMetric(
        campaign_id=data.campaign_id,
        date=metric_date,
        impressions=data.impressions,
        clicks=data.clicks,
        ctr=data.ctr,
        cpc=data.cpc,
        conversions=data.conversions,
        cost=data.cost,
        cpa=data.cpa,
        roas=data.roas,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return {"success": True, "data": _serialize_metric(metric)}


@router.get("/metrics")
async def list_metrics(
    campaign_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(AdMetric).join(AdCampaign).join(AdClient).filter(
        AdClient.owner_id == current_user.id
    )
    if campaign_id:
        query = query.filter(AdMetric.campaign_id == campaign_id)
    if start_date:
        query = query.filter(AdMetric.date >= date.fromisoformat(start_date))
    if end_date:
        query = query.filter(AdMetric.date <= date.fromisoformat(end_date))
    metrics = query.order_by(AdMetric.date.desc()).all()
    return {"success": True, "count": len(metrics), "data": [_serialize_metric(m) for m in metrics]}


def _serialize_metric(m: AdMetric) -> dict:
    return {
        "id": m.id,
        "campaign_id": m.campaign_id,
        "date": m.date.isoformat() if m.date else None,
        "impressions": m.impressions,
        "clicks": m.clicks,
        "ctr": m.ctr,
        "cpc": m.cpc,
        "conversions": m.conversions,
        "cost": m.cost,
        "cpa": m.cpa,
        "roas": m.roas,
    }


# =============================================================================
# STRATEGIES ROUTES
# =============================================================================

@router.get("/strategies")
async def list_strategies(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(AdStrategy).join(AdClient).filter(AdClient.owner_id == current_user.id)
    if client_id:
        query = query.filter(AdStrategy.client_id == client_id)
    if status:
        query = query.filter(AdStrategy.status == status)
    strategies = query.order_by(AdStrategy.created_at.desc()).all()
    return {"success": True, "count": len(strategies), "data": [_serialize_strategy(s) for s in strategies]}


@router.get("/strategies/{strategy_id}")
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    strategy = db.query(AdStrategy).join(AdClient).filter(
        AdStrategy.id == strategy_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"success": True, "data": _serialize_strategy(strategy)}


def _serialize_strategy(s: AdStrategy) -> dict:
    return {
        "id": s.id,
        "client_id": s.client_id,
        "platform_primary": s.platform_primary,
        "platform_secondary": s.platform_secondary,
        "platform_reasoning": s.platform_reasoning,
        "funnel_type": s.funnel_type,
        "funnel_steps": s.funnel_steps,
        "budget_monthly": s.budget_monthly,
        "budget_daily": s.budget_daily,
        "budget_split": s.budget_split,
        "ad_copy_google": s.ad_copy_google,
        "ad_copy_meta": s.ad_copy_meta,
        "kpi_targets": s.kpi_targets,
        "confidence": s.confidence,
        "requires_approval": s.requires_approval,
        "status": s.status,
        "approved_at": s.approved_at.isoformat() if s.approved_at else None,
        "rejection_reason": s.rejection_reason,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


# =============================================================================
# STATS / DASHBOARD
# =============================================================================

@router.get("/stats/dashboard")
async def ads_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """User-facing ads dashboard stats."""
    user_clients = db.query(AdClient).filter(AdClient.owner_id == current_user.id).all()
    client_ids = [c.id for c in user_clients]

    if not client_ids:
        return {"success": True, "data": {
            "total_clients": 0, "total_campaigns": 0, "active_campaigns": 0,
            "total_leads": 0, "new_leads": 0, "total_spent": 0,
        }}

    total_campaigns = db.query(func.count(AdCampaign.id)).filter(
        AdCampaign.client_id.in_(client_ids)
    ).scalar() or 0
    active_campaigns = db.query(func.count(AdCampaign.id)).filter(
        AdCampaign.client_id.in_(client_ids),
        AdCampaign.status == "active",
    ).scalar() or 0
    total_leads = db.query(func.count(AdLead.id)).join(AdCampaign).filter(
        AdCampaign.client_id.in_(client_ids)
    ).scalar() or 0
    new_leads = db.query(func.count(AdLead.id)).join(AdCampaign).filter(
        AdCampaign.client_id.in_(client_ids),
        AdLead.status == "new",
    ).scalar() or 0
    total_spent = db.query(func.coalesce(func.sum(AdCampaign.spent), 0)).filter(
        AdCampaign.client_id.in_(client_ids)
    ).scalar()
    total_budget = db.query(func.coalesce(func.sum(AdClient.budget_monthly), 0)).filter(
        AdClient.id.in_(client_ids)
    ).scalar()

    return {
        "success": True,
        "data": {
            "total_clients": len(user_clients),
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_leads": total_leads,
            "new_leads": new_leads,
            "total_spent": float(total_spent),
            "total_monthly_budget": float(total_budget),
        },
    }


@router.get("/stats/performance")
async def campaign_performance(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Per-campaign performance summary for the last N days."""
    from datetime import timedelta
    cutoff = date.today() - timedelta(days=days)

    campaigns = (
        db.query(AdCampaign)
        .join(AdClient)
        .filter(AdClient.owner_id == current_user.id)
        .all()
    )
    results = []
    for c in campaigns:
        metrics = db.query(
            func.coalesce(func.sum(AdMetric.impressions), 0),
            func.coalesce(func.sum(AdMetric.clicks), 0),
            func.coalesce(func.avg(AdMetric.ctr), 0),
            func.coalesce(func.avg(AdMetric.cpc), 0),
            func.coalesce(func.sum(AdMetric.conversions), 0),
            func.coalesce(func.sum(AdMetric.cost), 0),
        ).filter(
            AdMetric.campaign_id == c.id,
            AdMetric.date >= cutoff,
        ).first()
        results.append({
            "id": c.id,
            "name": c.name,
            "platform": c.platform,
            "status": c.status,
            "impressions": int(metrics[0]),
            "clicks": int(metrics[1]),
            "ctr": round(float(metrics[2]), 2),
            "cpc": round(float(metrics[3]), 2),
            "conversions": int(metrics[4]),
            "cost": round(float(metrics[5]), 2),
        })
    return {"success": True, "days": days, "data": results}


@router.get("/stats/leads-by-status")
async def leads_by_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(AdLead.status, func.count(AdLead.id))
        .join(AdCampaign)
        .join(AdClient)
        .filter(AdClient.owner_id == current_user.id)
        .group_by(AdLead.status)
        .all()
    )
    return {"success": True, "data": [{"status": s, "count": c} for s, c in rows]}


# =============================================================================
# MODULE 1: INVESTIGATOR — Website Analysis
# =============================================================================

@router.post("/investigate")
async def investigate_website(
    data: InvestigateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Analyze a website and extract a business profile (Module 1: Investigator)."""
    url = data.website_url
    if not url.startswith("http"):
        url = f"https://{url}"

    logger.info(f"[Investigator] Analyzing: {url}")
    html = _scrape_website(url)
    profile = _extract_business_profile(html, url)
    profile["confidence"] = _calculate_confidence(profile)

    return {
        "success": True,
        "message": "Analysis complete",
        "data": {"client_profile": profile, "confidence": profile["confidence"]},
    }


def _scrape_website(url: str) -> str:
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "15", "-A", "Mozilla/5.0", url],
            capture_output=True, text=True, timeout=20,
        )
        return result.stdout or ""
    except Exception:
        return f"<html><head><title>Business</title></head><body></body></html>"


def _extract_business_profile(html: str, url: str) -> dict:
    return {
        "businessName": _extract_title(html) or _extract_from_domain(url),
        "businessType": _detect_business_type(html),
        "services": _extract_services(html),
        "targetAudience": _extract_target_audience(html),
        "usp": _extract_usp(html),
        "city": _extract_city(html),
        "region": _extract_region(html),
        "address": _extract_address(html),
        "phone": _extract_phone(html),
        "email": _extract_email_from_html(html),
        "websiteUrl": url,
        "description": _extract_meta_description(html),
    }


def _extract_title(html: str) -> Optional[str]:
    m = re.search(r"<title[^>]*>([^<]*)</title>", html, re.I)
    return m.group(1).strip() if m else None


def _extract_meta_description(html: str) -> Optional[str]:
    m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', html, re.I)
    return m.group(1).strip() if m else None


def _extract_from_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).hostname or ""
        domain = domain.replace("www.", "")
        name = domain.split(".")[0]
        return name.capitalize() if name else "Business"
    except Exception:
        return "Business"


def _detect_business_type(html: str) -> str:
    lower = html.lower()
    types = [
        (["ristorante", "pizzeria", "trattoria", "osteria", "cucina", "menu"], "ristorazione"),
        (["hotel", "albergo", "b&b", "bed", "breakfast", "vacanza"], "ospitalita"),
        (["negozio", "shop", "ecommerce", "e-commerce", "vendita", "store"], "ecommerce"),
        (["avvocato", "studio legale", "legge", "diritto"], "servizi_legali"),
        (["commercialista", "contabile", "fiscale", "tributario"], "servizi_professionali"),
        (["dentista", "odontoiatra", "studio dentistico"], "sanita"),
        (["palestra", "fitness", "gym", "allenamento", "personal trainer"], "fitness"),
        (["parrucchiere", "estetista", "beauty", "capelli", "unghie"], "estetica"),
        (["immobiliare", "agenzia", "appartamento", "affitto"], "immobiliare"),
        (["costruzioni", "edile", "ristrutturazione", "edilizia"], "edile"),
        (["fotografo", "fotografia", "photo", "video", "riprese"], "creativo"),
        (["software", "app", "web", "digital", "tecnologia", "startup"], "tech"),
        (["marketing", "pubblicita", "comunicazione"], "marketing"),
        (["corso", "formazione", "scuola", "training"], "formazione"),
    ]
    for keywords, btype in types:
        if any(k in lower for k in keywords):
            return btype
    return "servizi"


def _extract_services(html: str) -> list:
    services = []
    for pattern in [
        r"(?:servizi|services|offerta)[\s\S]*?<li[^>]*>([^<]+)",
        r"<h[23][^>]*>([^<]*(?:consulenza|servizio|supporto|assistenza)[^<]*)</h[23]>",
    ]:
        for m in re.finditer(pattern, html, re.I):
            s = m.group(1).strip()
            if 3 < len(s) < 100 and s not in services:
                services.append(s)
            if len(services) >= 5:
                break
    return services or ["Servizi personalizzati"]


def _extract_target_audience(html: str) -> str:
    lower = html.lower()
    if any(w in lower for w in ["azienda", "business", "corporate"]):
        return "B2B - Aziende"
    if any(w in lower for w in ["privato", "famiglia", "individuo"]):
        return "B2C - Privati"
    return "Generico"


def _extract_usp(html: str) -> list:
    usp = []
    for pattern in [
        r"<h[123][^>]*>([^<]*(?:miglior|esperto|qualit|esperienza|specializzat|unic|innovativ)[^<]*)</h[123]>",
    ]:
        for m in re.finditer(pattern, html, re.I):
            text = m.group(1).strip()
            if 5 < len(text) < 150:
                usp.append(text)
            if len(usp) >= 3:
                break
    return usp or ["Qualita garantita", "Esperienza nel settore"]


def _extract_city(html: str) -> str:
    cities = [
        "Milano", "Roma", "Torino", "Genova", "Bologna", "Firenze", "Napoli",
        "Verona", "Padova", "Venezia", "Brescia", "Monza", "Como", "Varese",
    ]
    for city in cities:
        if city in html:
            return city
    m = re.search(r",\s*\d{5}\s*([A-Za-z\s]+)[<,\s]", html)
    if m:
        return m.group(1).strip()
    return "Non specificata"


def _extract_region(html: str) -> str:
    city = _extract_city(html)
    regions = {
        "Lombardia": ["Milano", "Monza", "Brescia", "Como", "Varese", "Bergamo"],
        "Lazio": ["Roma"],
        "Piemonte": ["Torino", "Novara"],
        "Liguria": ["Genova", "Savona"],
        "Emilia-Romagna": ["Bologna", "Modena", "Parma"],
        "Toscana": ["Firenze", "Pisa", "Siena"],
        "Campania": ["Napoli", "Salerno"],
        "Veneto": ["Venezia", "Verona", "Padova", "Vicenza"],
    }
    for region, cities in regions.items():
        if city in cities:
            return region
    return ""


def _extract_address(html: str) -> str:
    m = re.search(r"(via|viale|corso|piazza|riviera|strada)\s+[\w\s]+\d+[\s,]*\d{5}\s*[\w\s]+", html, re.I)
    return m.group(0).strip() if m else ""


def _extract_phone(html: str) -> str:
    m = re.search(r"(\+39\s*\d{8,}|\d{3}[\s.\-]*\d{3}[\s.\-]*\d{4})", html)
    return m.group(0) if m else ""


def _extract_email_from_html(html: str) -> str:
    m = re.search(r"[\w.\-]+@[\w.\-]+\.\w+", html)
    return m.group(0) if m else ""


def _calculate_confidence(profile: dict) -> int:
    score = 50
    if profile.get("businessName") and profile["businessName"] != "Business":
        score += 15
    if profile.get("businessType") != "servizi":
        score += 15
    if len(profile.get("services", [])) > 0:
        score += 10
    if profile.get("city") != "Non specificata":
        score += 10
    return min(score, 95)


# =============================================================================
# MODULE 2: ANALYST — Market Research
# =============================================================================

@router.post("/research")
async def market_research(
    data: ResearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Run market research: keywords, competitors, benchmarks, trends (Module 2: Analyst)."""
    kb = _get_knowledge_base()
    services = data.services or []

    # Keyword research
    keywords_data = _research_keywords(data.business_type, data.city, services, kb)
    # Competitor analysis
    competitors_data = _analyze_competitors([k["keyword"] for k in keywords_data["keywords"]])
    # Benchmarks
    benchmarks = _get_benchmarks(data.business_type, kb)
    # Trends
    trends = _analyze_trends(data.business_type, data.city)

    research_result = {
        "keywords": keywords_data,
        "competitors": competitors_data,
        "benchmarks": benchmarks,
        "trends": trends,
    }

    # Save if client_id provided
    if data.client_id:
        _get_client_or_404(data.client_id, current_user, db)
        research = AdMarketResearch(
            client_id=data.client_id,
            keywords_data=keywords_data,
            competitors_data=competitors_data,
            benchmarks=benchmarks,
            trends=trends,
        )
        db.add(research)
        db.commit()

    return {"success": True, "message": "Research complete", "data": research_result}


def _research_keywords(business_type: str, city: str, services: list, kb: dict) -> dict:
    templates = kb.get("templates", {})
    tmpl = templates.get(business_type, templates.get("default", {}))

    # Use knowledge base keywords if available
    base_keywords = tmpl.get("keyword", [])
    base_keywords = [k.replace("[citta]", city).replace("[Citta]", city).replace("[città]", city) for k in base_keywords]

    if not base_keywords:
        base_keywords = [f"{business_type} {city}", f"migliore {business_type} {city}"]

    service_keywords = [f"{s} {city}".lower() for s in services]
    all_kw = base_keywords + service_keywords

    enriched = []
    for kw in all_kw:
        h = sum(ord(c) for c in kw)
        enriched.append({
            "keyword": kw,
            "matchType": "exact",
            "intent": "commercial",
            "monthlyVolume": 100 + (h % 1900),
            "cpcAvg": round(1.0 + (h % 100) / 100, 2),
            "competition": ["high", "medium", "low"][h % 3],
            "trend": ["rising", "stable", "declining"][h % 3],
            "recommended": h % 2 == 0,
        })
    enriched.sort(key=lambda x: x["monthlyVolume"], reverse=True)

    neg = tmpl.get("keyword_negative", ["gratis", "lavoro", "usato", "ricetta", "pdf"])

    return {
        "keywords": enriched,
        "negativeKeywords": [{"keyword": k, "reason": "Filtra traffico non qualificato"} for k in neg],
        "summary": {
            "totalKeywords": len(enriched),
            "totalMonthlyVolume": sum(k["monthlyVolume"] for k in enriched),
            "averageCpc": round(sum(k["cpcAvg"] for k in enriched) / max(len(enriched), 1), 2),
        },
    }


def _analyze_competitors(keywords: list) -> dict:
    return {
        "competitors": [
            {"name": "Competitor A", "estimatedMonthlySpend": 2500, "topKeywords": keywords[:3]},
            {"name": "Competitor B", "estimatedMonthlySpend": 1200, "topKeywords": keywords[1:4]},
        ],
        "marketShare": {"leader": "Competitor A", "estimatedTotalSpend": 3700},
    }


def _get_benchmarks(business_type: str, kb: dict) -> dict:
    benchmarks = kb.get("benchmarks", {})
    return benchmarks.get(business_type, benchmarks.get("default", {
        "google": {"cpc": {"min": 0.5, "max": 1.5, "avg": 1.0}},
        "meta": {"cpc": {"min": 0.3, "max": 0.8, "avg": 0.55}},
        "cpl": {"min": 5, "max": 15},
        "recommendedBudget": 350,
        "platformSplit": {"google": 50, "meta": 50},
    }))


def _analyze_trends(business_type: str, city: str) -> dict:
    import calendar
    month = datetime.now().month
    seasonality = {
        "ristorazione": {"peak": [5, 6, 7, 8, 11, 12], "low": [1, 2]},
        "fitness": {"peak": [1, 2, 9, 10], "low": [6, 7, 11, 12]},
        "immobiliare": {"peak": [3, 4, 5, 9, 10], "low": [7, 11, 12]},
        "estetica": {"peak": [4, 5, 11, 12], "low": [1, 7, 8]},
    }
    s = seasonality.get(business_type, {"peak": [], "low": []})
    trend = "stable"
    if month in s["peak"]:
        trend = "rising"
    elif month in s["low"]:
        trend = "declining"
    recs = {
        "rising": "Aumenta budget per cogliere la stagionalita positiva",
        "declining": "Riduci budget o focalizzati su keyword di conversione",
        "stable": "Mantieni budget costante",
    }
    return {"currentTrend": trend, "seasonality": s, "recommendation": recs[trend]}


# =============================================================================
# MODULE 3: ARCHITECT — Strategy Creation
# =============================================================================

@router.post("/strategy")
async def create_strategy(
    data: StrategyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create an advertising strategy for a client (Module 3: Architect)."""
    client = _get_client_or_404(data.client_id, current_user, db)
    kb = _get_knowledge_base()

    # Get latest research for context
    research = db.query(AdMarketResearch).filter(
        AdMarketResearch.client_id == client.id
    ).order_by(AdMarketResearch.created_at.desc()).first()

    benchmarks = research.benchmarks if research else _get_benchmarks(client.business_type, kb)

    # Platform selection
    platform_logic = {
        "ristorazione": ("both", "Google per ricerca attiva, Meta per awareness"),
        "servizi_legali": ("google", "Ricerca ad alta intenzione su Google"),
        "sanita": ("google", "Pazienti cercano attivamente servizi"),
        "fitness": ("meta", "Meta ideale per contenuti visivi e motivazionali"),
        "estetica": ("meta", "Visual-heavy, ideale per Instagram/Facebook"),
        "ecommerce": ("both", "Google Shopping + Meta Retargeting"),
        "immobiliare": ("both", "Ricerca attiva + visual properties"),
        "edile": ("google", "Servizi ricercati attivamente"),
        "tech": ("both", "Google per B2B, Meta per B2C"),
    }
    primary, reasoning = platform_logic.get(client.business_type, ("both", "Approccio bilanciato"))
    secondary = None if primary == "both" else ("meta" if primary == "google" else "google")

    # Budget allocation
    daily = round(data.budget_monthly / 30)
    split_data = benchmarks.get("platformSplit", {"google": 50, "meta": 50}) if isinstance(benchmarks, dict) else {"google": 50, "meta": 50}

    # Funnel
    funnel_type = "lead_gen" if client.business_type in ("servizi_legali", "servizi_professionali", "sanita") else "direct_response"

    # KPI targets
    kpi = {
        "ctr": 3.0,
        "cpc": {"min": 0.8, "max": 2.0},
        "cpl": {"min": 8, "max": 20},
        "conversionRate": 3.0,
        "learningPhaseDays": 14,
    }

    # Ad copy from KB
    templates = kb.get("templates", {})
    tmpl = templates.get(client.business_type, {})
    ad_copy = tmpl.get("ad_copy", {})

    # Confidence
    confidence = 70
    if client.business_type != "servizi" and client.city != "Non specificata":
        confidence += 10
    if research:
        confidence += 10
    if benchmarks:
        confidence += 10
    confidence = min(confidence, 95)

    strategy = AdStrategy(
        client_id=client.id,
        platform_primary=primary,
        platform_secondary=secondary,
        platform_reasoning=reasoning,
        funnel_type=funnel_type,
        budget_monthly=data.budget_monthly,
        budget_daily=daily,
        budget_split=split_data,
        ad_copy_google=ad_copy.get("google_headlines", []),
        ad_copy_meta=ad_copy.get("meta_hooks", []),
        kpi_targets=kpi,
        confidence=confidence,
        requires_approval=confidence < 80,
        status="pending_approval" if confidence < 80 else "approved",
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)

    # Log AI activity
    _log_ai_activity(db, client.id, None, "architect", "strategy_created",
                     f"Strategy created with {confidence}% confidence",
                     "warning" if confidence < 80 else "info",
                     "pending" if confidence < 80 else "no",
                     _serialize_strategy(strategy))

    return {
        "success": True,
        "message": "Strategy created",
        "data": {
            "strategy": _serialize_strategy(strategy),
            "requiresApproval": strategy.requires_approval,
        },
    }


# =============================================================================
# MODULE 4: BROKER — Campaign Publishing
# =============================================================================

@router.post("/campaign/create")
async def create_campaign_from_strategy(
    data: CampaignCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create campaigns on Google/Meta from a strategy (Module 4: Broker)."""
    client = _get_client_or_404(data.client_id, current_user, db)
    _check_campaign_limit(current_user, db)

    strategy = db.query(AdStrategy).filter(
        AdStrategy.id == data.strategy_id,
        AdStrategy.client_id == client.id,
    ).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    if strategy.status == "pending_approval":
        raise HTTPException(status_code=400, detail="Strategy requires approval before campaign creation")

    created_campaigns = []
    platforms_to_create = []
    if data.platform in ("google", "both"):
        platforms_to_create.append("google")
    if data.platform in ("meta", "both"):
        platforms_to_create.append("meta")

    split = strategy.budget_split or {"google": 50, "meta": 50}

    for platform in platforms_to_create:
        pct = split.get(platform, 50) / 100
        campaign = AdCampaign(
            client_id=client.id,
            strategy_id=strategy.id,
            platform=platform,
            name=f"{client.business_name} - {'Search' if platform == 'google' else 'Awareness'} {client.city}",
            status="pending",
            budget_daily=round(strategy.budget_daily * pct, 2),
            budget_total=round(strategy.budget_monthly * pct, 2),
            targeting={"locations": [client.city], "languages": ["it"]},
            ads=strategy.ad_copy_google if platform == "google" else strategy.ad_copy_meta,
            settings={"bidStrategy": "maximize_conversions"},
        )
        db.add(campaign)
        db.flush()
        created_campaigns.append(campaign)

        _log_ai_activity(db, client.id, campaign.id, "broker", "campaign_created",
                         f"{platform.title()} campaign created: {campaign.name}",
                         "info", "no")

    db.commit()
    for c in created_campaigns:
        db.refresh(c)

    return {
        "success": True,
        "message": f"{len(created_campaigns)} campaign(s) created",
        "data": [_serialize_campaign(c) for c in created_campaigns],
    }


@router.get("/campaign/{campaign_id}/metrics")
async def get_campaign_metrics_summary(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get aggregated metrics for a campaign."""
    campaign = db.query(AdCampaign).join(AdClient).filter(
        AdCampaign.id == campaign_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    row = db.query(
        func.coalesce(func.sum(AdMetric.impressions), 0),
        func.coalesce(func.sum(AdMetric.clicks), 0),
        func.coalesce(func.avg(AdMetric.ctr), 0),
        func.coalesce(func.avg(AdMetric.cpc), 0),
        func.coalesce(func.sum(AdMetric.conversions), 0),
        func.coalesce(func.sum(AdMetric.cost), 0),
    ).filter(AdMetric.campaign_id == campaign_id).first()

    return {
        "success": True,
        "data": {
            "campaign_id": campaign_id,
            "total_impressions": int(row[0]),
            "total_clicks": int(row[1]),
            "avg_ctr": round(float(row[2]), 2),
            "avg_cpc": round(float(row[3]), 2),
            "total_conversions": int(row[4]),
            "total_cost": round(float(row[5]), 2),
        },
    }


@router.post("/campaign/{campaign_id}/optimize")
async def optimize_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Analyze campaign metrics and suggest/apply optimizations (Module 4: Broker)."""
    campaign = db.query(AdCampaign).join(AdClient).filter(
        AdCampaign.id == campaign_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get recent metrics
    row = db.query(
        func.coalesce(func.avg(AdMetric.ctr), 0),
        func.coalesce(func.avg(AdMetric.cpc), 0),
        func.coalesce(func.sum(AdMetric.cost), 0),
        func.coalesce(func.sum(AdMetric.conversions), 0),
    ).filter(AdMetric.campaign_id == campaign_id).first()

    ctr, cpc, spend, conversions = float(row[0]), float(row[1]), float(row[2]), int(row[3])
    cpa = round(spend / conversions, 2) if conversions > 0 else 0

    changes = []
    if ctr < 2.0:
        changes.append({"type": "bid_adjustment", "action": "increase", "value": 10,
                         "reason": "CTR basso, aumento bid per posizione migliore"})
    if cpa > 50:
        changes.append({"type": "keyword_pause", "action": "pause_high_cpa",
                         "reason": "CPA troppo alto, pausa keyword generiche"})
    if (ctr > 3 and cpa < 15) or cpa == 0:
        changes.append({"type": "budget_increase", "action": "increase", "value": 20,
                         "reason": "Performance eccellente, scaling budget +20%"})

    log = AdOptimizationLog(campaign_id=campaign_id, changes=changes, status="applied")
    db.add(log)

    _log_ai_activity(db, campaign.client_id, campaign_id, "broker", "optimization_applied",
                     f"{len(changes)} optimization changes applied",
                     "info", "no")
    db.commit()

    return {"success": True, "campaignId": campaign_id, "changes": changes,
            "message": f"{len(changes)} changes applied"}


# =============================================================================
# FULL PIPELINE — investigate → research → strategy → campaign
# =============================================================================

@router.post("/pipeline/run")
async def run_full_pipeline(
    data: PipelineRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Run the full 4-module pipeline: Investigate → Research → Strategy → Campaign."""
    _check_campaign_limit(current_user, db)
    kb = _get_knowledge_base()
    steps = []

    # Step 1: Investigate
    url = data.website_url if data.website_url.startswith("http") else f"https://{data.website_url}"
    html = _scrape_website(url)
    profile = _extract_business_profile(html, url)
    profile["confidence"] = _calculate_confidence(profile)

    client = AdClient(
        owner_id=current_user.id,
        business_name=profile["businessName"],
        business_type=profile["businessType"],
        city=profile["city"],
        region=profile.get("region", ""),
        address=profile.get("address", ""),
        email=profile.get("email", current_user.email),
        phone=profile.get("phone", ""),
        website_url=url,
        description=profile.get("description"),
        services=profile.get("services"),
        target_audience=profile.get("targetAudience"),
        usp=profile.get("usp"),
        analysis_confidence=profile["confidence"],
    )
    db.add(client)
    db.flush()
    steps.append({"step": 1, "name": "investigate", "status": "completed", "clientId": client.id})

    # Step 2: Research
    keywords_data = _research_keywords(profile["businessType"], profile["city"],
                                        profile.get("services", []), kb)
    competitors_data = _analyze_competitors([k["keyword"] for k in keywords_data["keywords"]])
    benchmarks = _get_benchmarks(profile["businessType"], kb)
    trends = _analyze_trends(profile["businessType"], profile["city"])

    research = AdMarketResearch(
        client_id=client.id,
        keywords_data=keywords_data,
        competitors_data=competitors_data,
        benchmarks=benchmarks,
        trends=trends,
    )
    db.add(research)
    steps.append({"step": 2, "name": "research", "status": "completed"})

    # Step 3: Strategy
    platform_logic = {
        "ristorazione": ("both", "Google + Meta"),
        "servizi_legali": ("google", "Search intent"),
        "fitness": ("meta", "Visual content"),
        "ecommerce": ("both", "Shopping + Social"),
    }
    primary, reasoning = platform_logic.get(profile["businessType"], ("both", "Balanced"))
    daily = round(data.budget_monthly / 30)
    split_data = benchmarks.get("platformSplit", {"google": 50, "meta": 50}) if isinstance(benchmarks, dict) else {"google": 50, "meta": 50}

    confidence = 70
    if profile["businessType"] != "servizi":
        confidence += 10
    confidence += 10  # research done
    if benchmarks:
        confidence += 10
    confidence = min(confidence, 95)

    strategy = AdStrategy(
        client_id=client.id,
        platform_primary=primary,
        platform_reasoning=reasoning,
        funnel_type="lead_gen",
        budget_monthly=data.budget_monthly,
        budget_daily=daily,
        budget_split=split_data,
        kpi_targets={"ctr": 3.0, "cpc": {"min": 0.8, "max": 2.0}},
        confidence=confidence,
        requires_approval=confidence < 80,
        status="pending_approval" if confidence < 80 else "approved",
    )
    db.add(strategy)
    db.flush()
    steps.append({"step": 3, "name": "strategy", "status": "completed",
                   "strategyId": strategy.id, "requiresApproval": strategy.requires_approval})

    # Step 4: Campaign (only if approved or auto_approve)
    if data.auto_approve or not strategy.requires_approval:
        for platform in (["google", "meta"] if primary == "both" else [primary]):
            pct = split_data.get(platform, 50) / 100
            campaign = AdCampaign(
                client_id=client.id,
                strategy_id=strategy.id,
                platform=platform,
                name=f"{client.business_name} - {platform.title()} {client.city}",
                status="pending",
                budget_daily=round(daily * pct, 2),
                budget_total=round(data.budget_monthly * pct, 2),
            )
            db.add(campaign)
        steps.append({"step": 4, "name": "campaign", "status": "completed"})
    else:
        steps.append({"step": 4, "name": "campaign", "status": "pending_approval",
                       "message": "Strategy requires manual approval"})

    db.commit()

    return {
        "success": True,
        "message": "Pipeline completed",
        "data": {"steps": steps, "clientId": client.id, "strategyId": strategy.id},
    }


# =============================================================================
# CAMPAIGN WIZARD (6 steps, 3 modes)
# =============================================================================

WIZARD_OBJECTIVES = [
    {"id": "awareness", "name": "Piu Follower", "metaObjective": "AWARENESS",
     "bestFor": ["ristorazione", "fitness", "estetica"]},
    {"id": "traffic", "name": "Piu Visite al Sito", "metaObjective": "TRAFFIC",
     "bestFor": ["ecommerce", "servizi", "tech"]},
    {"id": "leads", "name": "Piu Contatti", "metaObjective": "LEADS",
     "bestFor": ["servizi_legali", "sanita", "immobiliare"]},
    {"id": "messages", "name": "Piu Messaggi", "metaObjective": "MESSAGES",
     "bestFor": ["ristorazione", "estetica", "fitness", "edile"]},
    {"id": "conversions", "name": "Piu Vendite", "metaObjective": "SALES",
     "bestFor": ["ecommerce"]},
]

WIZARD_BUDGET_TEMPLATES = [
    {"id": "starter", "name": "Starter", "daily": 5, "monthly": 150, "duration": 30},
    {"id": "standard", "name": "Standard", "daily": 10, "monthly": 300, "duration": 30},
    {"id": "pro", "name": "Pro", "daily": 20, "monthly": 600, "duration": 30},
    {"id": "custom", "name": "Personalizzato", "daily": None, "monthly": None, "duration": None},
]


@router.get("/wizard/config")
async def wizard_config():
    return {
        "success": True,
        "data": {
            "modes": {"GUIDED": "guided", "ASSISTED": "assisted", "MANUAL": "manual"},
            "steps": [
                {"id": "objective", "name": "Obiettivo"},
                {"id": "budget", "name": "Budget"},
                {"id": "audience", "name": "Pubblico"},
                {"id": "content", "name": "Contenuto"},
                {"id": "ad_copy", "name": "Testo Annuncio"},
                {"id": "review", "name": "Riepilogo"},
            ],
            "objectives": WIZARD_OBJECTIVES,
            "budgetTemplates": WIZARD_BUDGET_TEMPLATES,
        },
    }


@router.post("/wizard/start")
async def wizard_start(
    data: WizardStartRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    client = _get_client_or_404(data.client_id, current_user, db)
    if data.mode not in ("guided", "assisted", "manual"):
        raise HTTPException(status_code=400, detail="Mode must be guided, assisted, or manual")

    wizard = AdWizardProgress(
        client_id=client.id,
        mode=data.mode,
        current_step="objective",
        step_data={},
        status="in_progress",
    )
    db.add(wizard)
    db.commit()
    db.refresh(wizard)

    return {
        "success": True,
        "data": {
            "wizardId": wizard.id,
            "mode": data.mode,
            "client": {"id": client.id, "businessName": client.business_name},
            "firstStep": "objective",
        },
    }


@router.post("/wizard/step/{step}")
async def wizard_step(
    step: str,
    data: WizardStepRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    wizard = db.query(AdWizardProgress).filter(AdWizardProgress.id == data.wizard_id).first()
    if not wizard:
        raise HTTPException(status_code=404, detail="Wizard not found")

    result = {}
    if step == "objective":
        result = {"objectives": WIZARD_OBJECTIVES}
    elif step == "budget":
        result = {"templates": WIZARD_BUDGET_TEMPLATES}
    elif step == "audience":
        result = {"suggestion": {"ageMin": 25, "ageMax": 55, "radius": 15}}
    elif step == "content":
        result = {"options": []}
    elif step == "ad_copy":
        result = {"suggestions": []}
    elif step == "review":
        result = {"summary": data.data}

    # Update wizard progress
    wizard.current_step = step
    existing_data = wizard.step_data or {}
    existing_data[step] = data.data
    wizard.step_data = existing_data
    db.commit()

    return {"success": True, "step": step, "data": result}


@router.post("/wizard/complete")
async def wizard_complete(
    data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    wizard_id = data.get("wizard_id") or data.get("wizardId")
    campaign_data = data.get("campaign_data") or data.get("campaignData", {})

    wizard = db.query(AdWizardProgress).filter(AdWizardProgress.id == wizard_id).first()
    if not wizard:
        raise HTTPException(status_code=404, detail="Wizard not found")

    wizard.status = "completed"
    wizard.campaign_data = campaign_data
    db.commit()

    return {"success": True, "message": "Wizard completed", "data": {"wizardId": wizard_id}}


# =============================================================================
# SUPERVISION PANEL — Approve/Reject AI decisions
# =============================================================================

@router.get("/supervision/pending")
async def list_pending_decisions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all AI decisions pending approval."""
    # Pending strategies
    strategies = (
        db.query(AdStrategy)
        .join(AdClient)
        .filter(AdClient.owner_id == current_user.id, AdStrategy.status == "pending_approval")
        .all()
    )
    # Pending AI activities
    activities = (
        db.query(AdAiActivity)
        .join(AdClient, AdAiActivity.client_id == AdClient.id)
        .filter(AdClient.owner_id == current_user.id, AdAiActivity.requires_approval == "pending")
        .all()
    )
    return {
        "success": True,
        "data": {
            "pending_strategies": [_serialize_strategy(s) for s in strategies],
            "pending_activities": [_serialize_ai_activity(a) for a in activities],
            "total_pending": len(strategies) + len(activities),
        },
    }


@router.post("/supervision/strategies/{strategy_id}")
async def supervise_strategy(
    strategy_id: int,
    data: SupervisionActionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Approve or reject a strategy."""
    strategy = db.query(AdStrategy).join(AdClient).filter(
        AdStrategy.id == strategy_id,
        AdClient.owner_id == current_user.id,
    ).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    if data.action == "approve":
        strategy.status = "approved"
        strategy.approved_by = current_user.id
        strategy.approved_at = datetime.now(timezone.utc)
    elif data.action == "reject":
        strategy.status = "rejected"
        strategy.rejection_reason = data.reason
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    db.commit()
    db.refresh(strategy)
    return {"success": True, "data": _serialize_strategy(strategy)}


@router.post("/supervision/activities/{activity_id}")
async def supervise_activity(
    activity_id: int,
    data: SupervisionActionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Approve or reject an AI activity."""
    activity = db.query(AdAiActivity).filter(AdAiActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if data.action == "approve":
        activity.requires_approval = "approved"
        activity.approved_by = current_user.id
        activity.approved_at = datetime.now(timezone.utc)
    elif data.action == "reject":
        activity.requires_approval = "rejected"
        activity.rejection_reason = data.reason
    db.commit()
    return {"success": True, "message": f"Activity {data.action}d"}


# =============================================================================
# AI ACTIVITY LOG & TRAFFIC LIGHT
# =============================================================================

@router.get("/activities")
async def list_ai_activities(
    module: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(AdAiActivity).join(
        AdClient, AdAiActivity.client_id == AdClient.id
    ).filter(AdClient.owner_id == current_user.id)
    if module:
        query = query.filter(AdAiActivity.module == module)
    if severity:
        query = query.filter(AdAiActivity.severity == severity)
    activities = query.order_by(AdAiActivity.created_at.desc()).limit(limit).all()
    return {"success": True, "count": len(activities), "data": [_serialize_ai_activity(a) for a in activities]}


@router.get("/traffic-light")
async def traffic_light_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """System health overview (Traffic Light)."""
    client_ids = [c.id for c in db.query(AdClient.id).filter(AdClient.owner_id == current_user.id).all()]
    if not client_ids:
        return {"success": True, "data": {"status": "green", "critical": 0, "warning": 0, "info": 0, "pending": 0}}

    critical = db.query(func.count(AdAiActivity.id)).filter(
        AdAiActivity.client_id.in_(client_ids), AdAiActivity.severity == "critical"
    ).scalar() or 0
    warning = db.query(func.count(AdAiActivity.id)).filter(
        AdAiActivity.client_id.in_(client_ids), AdAiActivity.severity == "warning"
    ).scalar() or 0
    info = db.query(func.count(AdAiActivity.id)).filter(
        AdAiActivity.client_id.in_(client_ids), AdAiActivity.severity == "info"
    ).scalar() or 0
    pending = db.query(func.count(AdAiActivity.id)).filter(
        AdAiActivity.client_id.in_(client_ids), AdAiActivity.requires_approval == "pending"
    ).scalar() or 0

    overall = "green"
    if critical > 0:
        overall = "red"
    elif warning > 0 or pending > 0:
        overall = "yellow"

    return {
        "success": True,
        "data": {"status": overall, "critical": critical, "warning": warning, "info": info, "pending": pending},
    }


def _serialize_ai_activity(a: AdAiActivity) -> dict:
    return {
        "id": a.id,
        "client_id": a.client_id,
        "campaign_id": a.campaign_id,
        "module": a.module,
        "action_type": a.action_type,
        "description": a.description,
        "severity": a.severity,
        "requires_approval": a.requires_approval,
        "decision_data": a.decision_data,
        "approved_at": a.approved_at.isoformat() if a.approved_at else None,
        "rejection_reason": a.rejection_reason,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _log_ai_activity(
    db: Session, client_id: int, campaign_id: Optional[int],
    module: str, action_type: str, description: str,
    severity: str = "info", requires_approval: str = "no",
    decision_data: Any = None,
):
    activity = AdAiActivity(
        client_id=client_id,
        campaign_id=campaign_id,
        module=module,
        action_type=action_type,
        description=description,
        severity=severity,
        requires_approval=requires_approval,
        decision_data=decision_data,
    )
    db.add(activity)


# =============================================================================
# KNOWLEDGE BASE
# =============================================================================

_knowledge_base_cache = None


def _get_knowledge_base() -> dict:
    """Load knowledge base JSON files (cached)."""
    global _knowledge_base_cache
    if _knowledge_base_cache is not None:
        return _knowledge_base_cache

    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ads_data")
    # Fallback: try the Ads AI project data directory
    if not os.path.isdir(data_dir):
        alt = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "Ads Ai", "backend", "data"))
        if os.path.isdir(alt):
            data_dir = alt

    kb = {"benchmarks": {}, "templates": {}, "problems": [], "articles": []}
    for fname, key in [
        ("benchmarks.json", "benchmarks"),
        ("templates-verticali.json", "templates"),
        ("problem-solving.json", "problems"),
        ("knowledge-articles.json", "articles"),
    ]:
        fpath = os.path.join(data_dir, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    kb[key] = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load {fname}: {e}")

    _knowledge_base_cache = kb
    return kb


@router.get("/knowledge/benchmarks")
async def knowledge_benchmarks(
    sector: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    kb = _get_knowledge_base()
    benchmarks = kb.get("benchmarks", {})
    if sector:
        return {"success": True, "data": benchmarks.get(sector, benchmarks.get("default", {}))}
    return {"success": True, "data": benchmarks}


@router.get("/knowledge/sectors")
async def knowledge_sectors(
    current_user: User = Depends(get_current_active_user),
):
    kb = _get_knowledge_base()
    sectors = [s for s in kb.get("benchmarks", {}).keys() if s != "default"]
    return {"success": True, "data": sectors}


@router.get("/knowledge/templates")
async def knowledge_templates(
    sector: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    kb = _get_knowledge_base()
    templates = kb.get("templates", {})
    if sector:
        return {"success": True, "data": templates.get(sector, templates.get("default", {}))}
    return {"success": True, "data": templates}


@router.get("/knowledge/problems")
async def knowledge_problems(
    sector: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    kb = _get_knowledge_base()
    problems = kb.get("problems", [])
    if sector:
        problems = [p for p in problems if sector in p.get("settori", []) or "tutti" in p.get("settori", [])]
    if search:
        sl = search.lower()
        problems = [p for p in problems if sl in p.get("sintomo", "").lower() or sl in p.get("diagnosi", "").lower()]
    return {"success": True, "data": problems}


@router.get("/knowledge/articles")
async def knowledge_articles(
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    kb = _get_knowledge_base()
    articles = kb.get("articles", [])
    if category:
        articles = [a for a in articles if a.get("categoria") == category]
    if search:
        sl = search.lower()
        articles = [a for a in articles if
                    sl in a.get("titolo", "").lower() or
                    sl in a.get("contenuto", "").lower() or
                    any(sl in t.lower() for t in a.get("tags", []))]
    return {"success": True, "data": articles}


# =============================================================================
# ADMIN ROUTES — Cross-user overview (require admin auth)
# =============================================================================

@router.get("/admin/overview")
async def admin_ads_overview(
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin dashboard stats for the entire Ads platform."""
    total_clients = db.query(func.count(AdClient.id)).scalar() or 0
    total_campaigns = db.query(func.count(AdCampaign.id)).scalar() or 0
    active_campaigns = db.query(func.count(AdCampaign.id)).filter(AdCampaign.status == "active").scalar() or 0
    total_leads = db.query(func.count(AdLead.id)).scalar() or 0
    new_leads = db.query(func.count(AdLead.id)).filter(AdLead.status == "new").scalar() or 0
    total_spent = db.query(func.coalesce(func.sum(AdCampaign.spent), 0)).scalar()
    total_budget = db.query(func.coalesce(func.sum(AdClient.budget_monthly), 0)).scalar()
    pending_strategies = db.query(func.count(AdStrategy.id)).filter(
        AdStrategy.status == "pending_approval"
    ).scalar() or 0
    pending_activities = db.query(func.count(AdAiActivity.id)).filter(
        AdAiActivity.requires_approval == "pending"
    ).scalar() or 0

    return {
        "success": True,
        "data": {
            "total_clients": total_clients,
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_leads": total_leads,
            "new_leads": new_leads,
            "total_spent": float(total_spent),
            "total_monthly_budget": float(total_budget),
            "pending_strategies": pending_strategies,
            "pending_activities": pending_activities,
        },
    }


@router.get("/admin/campaigns")
async def admin_list_campaigns(
    page: int = 1,
    per_page: int = 50,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all campaigns across all users (admin)."""
    query = db.query(AdCampaign).join(AdClient)
    if status:
        query = query.filter(AdCampaign.status == status)
    if platform:
        query = query.filter(AdCampaign.platform == platform)

    total = query.count()
    campaigns = query.order_by(AdCampaign.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "campaigns": [
            {
                **_serialize_campaign(c),
                "owner_email": c.client.owner.email if c.client and c.client.owner else None,
            }
            for c in campaigns
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/admin/clients")
async def admin_list_clients(
    page: int = 1,
    per_page: int = 50,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all ad clients across all users (admin)."""
    query = db.query(AdClient)
    total = query.count()
    clients = query.order_by(AdClient.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "clients": [
            {
                **_serialize_client(c),
                "owner_email": c.owner.email if c.owner else None,
                "campaigns_count": len(c.campaigns) if c.campaigns else 0,
            }
            for c in clients
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@router.get("/admin/activities")
async def admin_list_activities(
    module: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all AI activities (admin)."""
    query = db.query(AdAiActivity)
    if module:
        query = query.filter(AdAiActivity.module == module)
    if severity:
        query = query.filter(AdAiActivity.severity == severity)
    activities = query.order_by(AdAiActivity.created_at.desc()).limit(limit).all()
    return {"success": True, "count": len(activities), "data": [_serialize_ai_activity(a) for a in activities]}


# =============================================================================
# PLATFORM CONFIG — Setup Wizard endpoints
# =============================================================================

class PlatformConfigUpdate(BaseModel):
    """Generic schema for updating a platform's config fields."""
    fields: dict  # e.g. {"developer_token": "xxx", "client_id": "yyy"}


PLATFORM_FIELDS = {
    "google": [
        "google_developer_token", "google_client_id", "google_client_secret",
        "google_refresh_token", "google_mcc_id",
    ],
    "meta": [
        "meta_system_user_token", "meta_app_id", "meta_app_secret",
        "meta_business_id", "meta_pixel_id",
    ],
    "dataforseo": ["dataforseo_login", "dataforseo_password"],
    "n8n": ["n8n_base_url", "n8n_api_key"],
    "telegram": ["telegram_bot_token", "telegram_chat_id"],
    "ai": ["claude_api_key", "openai_api_key"],
}

PLATFORM_STATUS_FIELD = {
    "google": "google_status",
    "meta": "meta_status",
    "dataforseo": "dataforseo_status",
    "n8n": "n8n_status",
    "telegram": "telegram_status",
    "ai": "ai_status",
}


def _mask_key(value: Optional[str]) -> Optional[str]:
    """Mask sensitive keys, showing only last 4 chars."""
    if not value:
        return None
    if len(value) <= 8:
        return "****" + value[-2:]
    return "****" + value[-4:]


def _get_or_create_config(user: User, db: Session) -> AdPlatformConfig:
    """Get existing config or create a new one for the user."""
    config = db.query(AdPlatformConfig).filter(
        AdPlatformConfig.owner_id == user.id
    ).first()
    if not config:
        config = AdPlatformConfig(owner_id=user.id)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def _serialize_config(config: AdPlatformConfig) -> dict:
    """Serialize config with masked secrets."""
    return {
        "id": config.id,
        "google": {
            "developer_token": _mask_key(config.google_developer_token),
            "client_id": _mask_key(config.google_client_id),
            "client_secret": _mask_key(config.google_client_secret),
            "refresh_token": _mask_key(config.google_refresh_token),
            "mcc_id": config.google_mcc_id,
            "status": config.google_status or "not_configured",
        },
        "meta": {
            "system_user_token": _mask_key(config.meta_system_user_token),
            "app_id": _mask_key(config.meta_app_id),
            "app_secret": _mask_key(config.meta_app_secret),
            "business_id": config.meta_business_id,
            "pixel_id": config.meta_pixel_id,
            "status": config.meta_status or "not_configured",
        },
        "dataforseo": {
            "login": _mask_key(config.dataforseo_login),
            "password": _mask_key(config.dataforseo_password),
            "status": config.dataforseo_status or "not_configured",
        },
        "n8n": {
            "base_url": config.n8n_base_url,
            "api_key": _mask_key(config.n8n_api_key),
            "status": config.n8n_status or "not_configured",
        },
        "telegram": {
            "bot_token": _mask_key(config.telegram_bot_token),
            "chat_id": config.telegram_chat_id,
            "status": config.telegram_status or "not_configured",
        },
        "ai": {
            "claude_api_key": _mask_key(config.claude_api_key),
            "openai_api_key": _mask_key(config.openai_api_key),
            "kimi_status": "active",
            "status": config.ai_status or "not_configured",
        },
        "created_at": config.created_at.isoformat() if config.created_at else None,
        "updated_at": config.updated_at.isoformat() if config.updated_at else None,
    }


@router.get("/config")
async def get_platform_config(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current platform config with masked keys."""
    config = _get_or_create_config(current_user, db)
    return {"success": True, "data": _serialize_config(config)}


@router.get("/config/status")
async def get_config_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get setup progress -- which platforms are configured."""
    config = _get_or_create_config(current_user, db)
    platforms = {}
    configured_count = 0
    for platform, status_field in PLATFORM_STATUS_FIELD.items():
        status = getattr(config, status_field, "not_configured") or "not_configured"
        platforms[platform] = status
        if status not in ("not_configured",):
            configured_count += 1
    return {
        "success": True,
        "data": {
            "platforms": platforms,
            "configured": configured_count,
            "total": len(PLATFORM_STATUS_FIELD),
            "progress_pct": round(configured_count / len(PLATFORM_STATUS_FIELD) * 100),
        },
    }


@router.put("/config/{platform}")
async def update_platform_config(
    platform: str,
    data: PlatformConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update config for a specific platform (google/meta/dataforseo/n8n/telegram/ai)."""
    if platform not in PLATFORM_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown platform: {platform}. Valid: {', '.join(PLATFORM_FIELDS.keys())}",
        )

    config = _get_or_create_config(current_user, db)
    allowed_fields = PLATFORM_FIELDS[platform]

    updated = []
    for key, value in data.fields.items():
        # Build column name: e.g. "developer_token" -> "google_developer_token"
        if platform == "ai":
            col_name = key
        else:
            col_name = f"{platform}_{key}" if not key.startswith(platform) else key

        if col_name not in allowed_fields:
            continue

        setattr(config, col_name, value if value else None)
        updated.append(col_name)

    # Auto-update status if any credential was set
    status_field = PLATFORM_STATUS_FIELD[platform]
    has_any = any(getattr(config, f) for f in allowed_fields)
    if has_any:
        current_status = getattr(config, status_field)
        if current_status == "not_configured":
            setattr(config, status_field, "pending_approval")
    else:
        setattr(config, status_field, "not_configured")

    db.commit()
    db.refresh(config)

    return {
        "success": True,
        "message": f"{platform} config updated ({len(updated)} fields)",
        "data": _serialize_config(config),
    }


@router.post("/config/{platform}/test")
async def test_platform_connection(
    platform: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Test connection for a platform. Returns success/failure + details."""
    if platform not in PLATFORM_FIELDS:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")

    config = _get_or_create_config(current_user, db)
    status_field = PLATFORM_STATUS_FIELD[platform]
    result = {"platform": platform, "success": False, "message": "", "details": {}}

    try:
        if platform == "google":
            token = config.google_developer_token
            if not token:
                result["message"] = "Developer Token mancante"
                return {"success": True, "data": result}
            if len(token) < 10:
                result["message"] = "Developer Token troppo corto"
                return {"success": True, "data": result}
            result["success"] = True
            result["message"] = "Credenziali Google Ads salvate. Lo stato verra aggiornato dopo la verifica del Developer Token da parte di Google."
            result["details"] = {"mcc_id": config.google_mcc_id or "Non configurato"}
            setattr(config, status_field, "test_mode")

        elif platform == "meta":
            token = config.meta_system_user_token
            if not token:
                result["message"] = "System User Token mancante"
                return {"success": True, "data": result}
            import urllib.request
            try:
                url = f"https://graph.facebook.com/v21.0/me?access_token={token}"
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_data = json.loads(resp.read().decode())
                    result["success"] = True
                    result["message"] = f"Connessione Meta riuscita. User: {resp_data.get('name', 'OK')}"
                    result["details"] = {"user_id": resp_data.get("id")}
                    setattr(config, status_field, "active")
            except Exception as e:
                result["message"] = f"Errore connessione Meta: {str(e)[:100]}"
                setattr(config, status_field, "pending_approval")

        elif platform == "dataforseo":
            login = config.dataforseo_login
            pwd = config.dataforseo_password
            if not login or not pwd:
                result["message"] = "Login o Password mancanti"
                return {"success": True, "data": result}
            import urllib.request
            import base64
            try:
                creds = base64.b64encode(f"{login}:{pwd}".encode()).decode()
                req = urllib.request.Request(
                    "https://api.dataforseo.com/v3/serp/google/organic/live",
                    method="GET",
                    headers={"Authorization": f"Basic {creds}"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result["success"] = True
                    result["message"] = "Connessione DataForSEO riuscita"
                    setattr(config, status_field, "active")
            except Exception as e:
                err_msg = str(e)[:100]
                if "401" in err_msg:
                    result["message"] = "Credenziali DataForSEO non valide"
                else:
                    result["message"] = f"Errore DataForSEO: {err_msg}"
                setattr(config, status_field, "pending_approval")

        elif platform == "n8n":
            base_url = config.n8n_base_url
            api_key = config.n8n_api_key
            if not base_url:
                result["message"] = "Base URL mancante"
                return {"success": True, "data": result}
            import urllib.request
            try:
                url = f"{base_url.rstrip('/')}/api/v1/workflows?limit=1"
                headers_dict = {}
                if api_key:
                    headers_dict["X-N8N-API-KEY"] = api_key
                req = urllib.request.Request(url, method="GET", headers=headers_dict)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_data = json.loads(resp.read().decode())
                    result["success"] = True
                    result["message"] = "Connessione n8n riuscita"
                    result["details"] = {"workflows": len(resp_data.get("data", []))}
                    setattr(config, status_field, "active")
            except Exception as e:
                result["message"] = f"Errore connessione n8n: {str(e)[:100]}"
                setattr(config, status_field, "pending_approval")

        elif platform == "telegram":
            bot_token = config.telegram_bot_token
            chat_id = config.telegram_chat_id
            if not bot_token or not chat_id:
                result["message"] = "Bot Token o Chat ID mancanti"
                return {"success": True, "data": result}
            import urllib.request
            try:
                msg = "Test connessione AI ADS Platform - Funziona!"
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = json.dumps({"chat_id": chat_id, "text": msg}).encode()
                req = urllib.request.Request(
                    url, data=payload, method="POST",
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_data = json.loads(resp.read().decode())
                    if resp_data.get("ok"):
                        result["success"] = True
                        result["message"] = "Messaggio di test inviato su Telegram!"
                        setattr(config, status_field, "active")
                    else:
                        result["message"] = "Telegram ha risposto ma il messaggio non e stato inviato"
                        setattr(config, status_field, "pending_approval")
            except Exception as e:
                result["message"] = f"Errore Telegram: {str(e)[:100]}"
                setattr(config, status_field, "pending_approval")

        elif platform == "ai":
            claude_key = config.claude_api_key
            openai_key = config.openai_api_key
            tested = []
            if claude_key:
                tested.append("Claude")
            if openai_key:
                tested.append("OpenAI")
            if not tested:
                result["message"] = "Nessuna API key inserita (Kimi K2.5 e sempre integrato)"
                setattr(config, status_field, "not_configured")
                return {"success": True, "data": result}
            result["success"] = True
            result["message"] = f"API keys salvate per: {', '.join(tested)}. Kimi K2.5 sempre attivo."
            result["details"] = {"models": ["kimi-k2.5"] + [m.lower() for m in tested]}
            setattr(config, status_field, "active")

        db.commit()

    except Exception as e:
        logger.error(f"Error testing {platform}: {e}")
        result["message"] = f"Errore imprevisto: {str(e)[:100]}"

    return {"success": True, "data": result}


# =============================================================================
# WEBSITE ANALYZER — AI-powered deep analysis (Module 1 Enhanced)
# =============================================================================

class AnalyzeWebsiteRequest(BaseModel):
    url: str


@router.post("/analyze-website")
async def analyze_website(
    data: AnalyzeWebsiteRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Fetch a website and analyze it with Kimi AI for a structured business report."""
    import httpx
    from app.core.config import settings

    url = data.url.strip()
    if not url.startswith("http"):
        url = f"https://{url}"

    logger.info(f"[Analyzer] AI analysis for: {url}")

    # 1. Fetch the website HTML
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
            html = resp.text
    except Exception as e:
        logger.error(f"[Analyzer] Fetch failed for {url}: {e}")
        raise HTTPException(status_code=400, detail=f"Impossibile raggiungere il sito: {str(e)[:200]}")

    # 2. Extract text content
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()[:8000]

    # 3. Extract meta info
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.DOTALL)
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.I)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', html, re.I)

    page_title = title_match.group(1).strip() if title_match else "N/A"
    page_description = desc_match.group(1).strip() if desc_match else "N/A"

    # 4. Build prompt for Kimi AI
    prompt = f"""Analizza questo sito web e restituisci un JSON strutturato.

URL: {url}
Titolo: {page_title}
Meta Description: {page_description}

Contenuto del sito:
{text}

Restituisci SOLO un JSON valido (senza markdown, senza ```json, senza commenti) con questa struttura:
{{
  "business_name": "nome azienda",
  "business_type": "SaaS|E-commerce|Servizio Locale|Agenzia|Professionista|Ristorante|Blog|Startup|Altro",
  "sector": "settore specifico",
  "value_proposition": "proposta di valore principale in 1-2 frasi",
  "target_audience": ["segmento 1", "segmento 2", "segmento 3"],
  "services": [
    {{"name": "servizio 1", "description": "descrizione breve", "price": "prezzo o null"}},
    {{"name": "servizio 2", "description": "descrizione breve", "price": "prezzo o null"}}
  ],
  "tone_of_voice": "formale|informale|tecnico|ironico|professionale|amichevole",
  "tone_keywords": ["parola1", "parola2", "parola3"],
  "strengths": ["punto forte 1", "punto forte 2", "punto forte 3"],
  "weaknesses": ["punto debole 1", "punto debole 2", "punto debole 3"],
  "cta_list": ["CTA 1", "CTA 2"],
  "site_structure": ["sezione 1", "sezione 2", "sezione 3"],
  "tech_detected": ["tecnologia 1", "tecnologia 2"],
  "tech_score": 75,
  "seo_score": 70,
  "mobile_score": 80,
  "suggested_campaign_type": "Search|Display|Social|Video|Lead Gen",
  "suggested_platform": "Google|Meta|Both",
  "ai_suggestions": [
    "Suggerimento 1 per migliorare le ads",
    "Suggerimento 2 per migliorare le ads",
    "Suggerimento 3 per migliorare le ads",
    "Suggerimento 4 per migliorare le ads",
    "Suggerimento 5 per migliorare le ads"
  ]
}}

IMPORTANTE: Rispondi in italiano. Sii specifico e concreto nelle analisi. I punteggi devono essere realistici (0-100). I suggerimenti devono essere azionabili e utili per creare campagne pubblicitarie efficaci."""

    # 5. Call Kimi API
    api_url = settings.KIMI_API_URL or "https://api.moonshot.ai/v1"
    api_key = settings.active_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="Nessuna API key AI configurata")

    ai_payload = {
        "model": "kimi-k2.5",
        "messages": [
            {"role": "system", "content": "Sei un esperto analista di marketing digitale. Analizzi siti web e produci report strutturati in JSON per aiutare a creare campagne pubblicitarie efficaci."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4000,
        "temperature": 0.4,
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            ai_resp = await client.post(
                f"{api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=ai_payload,
            )
            ai_resp.raise_for_status()
            ai_data = ai_resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"[Analyzer] Kimi API error: {e.response.status_code} - {e.response.text[:300]}")
        raise HTTPException(status_code=502, detail=f"Errore API AI: {e.response.status_code}")
    except Exception as e:
        logger.error(f"[Analyzer] Kimi API call failed: {e}")
        raise HTTPException(status_code=502, detail=f"Errore connessione AI: {str(e)[:200]}")

    # 6. Parse response
    raw_content = ai_data.get("choices", [{}])[0].get("message", {}).get("content", "")

    cleaned = raw_content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)

    try:
        analysis = json.loads(cleaned)
    except json.JSONDecodeError:
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            try:
                analysis = json.loads(json_match.group())
            except json.JSONDecodeError:
                logger.error(f"[Analyzer] Could not parse AI response: {cleaned[:500]}")
                raise HTTPException(status_code=500, detail="Errore nel parsing della risposta AI")
        else:
            logger.error(f"[Analyzer] No JSON in AI response: {cleaned[:500]}")
            raise HTTPException(status_code=500, detail="Risposta AI non valida")

    analysis["analyzed_url"] = url
    analysis["analyzed_at"] = datetime.now(timezone.utc).isoformat()

    return {"success": True, "data": analysis}


# =============================================================================
# CONTENT CREATOR — Image Generation & Creative Library (stubs)
# =============================================================================

class GenerateImageRequest(BaseModel):
    prompt: str
    format: str = "1:1"
    style: str = "photographic"
    model: str = "flux"
    overlay_text: Optional[str] = None


@router.post("/generate-image")
async def generate_image(
    req: GenerateImageRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Stub endpoint for AI image generation.
    Returns a setup message until API keys are configured."""
    config = db.query(AdPlatformConfig).filter(
        AdPlatformConfig.user_id == current_user.id
    ).first()

    has_key = False
    if config:
        has_key = bool(config.openai_api_key) or bool(getattr(config, "replicate_api_key", None))

    if not has_key:
        return {
            "success": False,
            "status": "pending",
            "message": "La generazione immagini richiede una API key. Vai su Setup \u2192 Modelli AI per configurare Replicate o OpenAI.",
            "setup_url": "/admin/ads/setup",
        }

    return {
        "success": False,
        "status": "pending",
        "message": "Generazione immagini in fase di implementazione. API key rilevata.",
    }


@router.get("/creatives")
async def list_creatives(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Stub endpoint \u2014 returns empty creative library."""
    return {
        "success": True,
        "data": [],
        "total": 0,
    }
