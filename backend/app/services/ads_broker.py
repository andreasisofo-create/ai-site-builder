"""
Modulo Broker - Gestione campagne e ottimizzazione.
Ported from Node.js: backend/modules/broker.js
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

from app.services.n8n_ads_service import n8n_ads_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Creazione campagne
# ---------------------------------------------------------------------------

async def create_google_campaign(
    strategy: Dict[str, Any], client_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """Crea una campagna su Google Ads."""
    logger.info("[Broker] Creazione campagna Google per: %s", client_profile.get("businessName"))

    try:
        campaign_id = f"google_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

        campaign = {
            "id": campaign_id,
            "externalId": None,
            "name": f"{client_profile.get('businessName', '')} - Search {client_profile.get('city', '')}",
            "status": "pending",
            "platform": "google",
            "budget": {
                "daily": strategy["budgetAllocation"]["perPlatform"]["google"]["daily"],
                "total": strategy["budgetAllocation"]["perPlatform"]["google"]["monthly"],
                "spent": 0,
            },
            "targeting": {
                "locations": [client_profile.get("city", "")],
                "languages": ["it"],
                "networks": ["search", "display"],
            },
            "adGroups": [
                {
                    "name": "Keyword Principali",
                    "bid": strategy["kpiTargets"]["cpc"]["max"],
                    "keywords": strategy["adCopy"]["keywords"]["main"][:10],
                },
                {
                    "name": "Brand",
                    "bid": strategy["kpiTargets"]["cpc"]["min"],
                    "keywords": [client_profile.get("businessName", "")],
                },
            ],
            "ads": {
                "headlines": strategy["adCopy"]["google"]["headlines"][:15],
                "descriptions": strategy["adCopy"]["google"]["descriptions"][:4],
                "paths": [
                    strategy["adCopy"]["google"]["path1"],
                    strategy["adCopy"]["google"]["path2"],
                ],
            },
            "settings": {
                "bidStrategy": "maximize_conversions",
                "deliveryMethod": "standard",
                "adRotation": "optimize",
            },
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }

        # Trigger n8n per pubblicazione
        try:
            await n8n_ads_service.create_campaign({
                "campaignId": campaign_id,
                "platform": "google",
                "strategy": strategy,
                "adCopy": strategy["adCopy"],
                "clientProfile": {
                    "id": client_profile.get("id"),
                    "businessName": client_profile.get("businessName"),
                    "city": client_profile.get("city"),
                },
            })
            logger.info("[Broker] Campagna inviata a n8n")
        except Exception as e:
            logger.warning("[Broker] Errore invio a n8n: %s", e)

        return {
            "success": True,
            "campaignId": campaign_id,
            "campaign": campaign,
            "platform": "google",
            "status": "pending",
            "message": "Campagna Google creata e in attesa di approvazione",
        }
    except Exception as e:
        logger.error("[Broker] Errore creazione Google: %s", e)
        return {"success": False, "error": str(e), "message": "Errore nella creazione campagna Google"}


async def create_meta_campaign(
    strategy: Dict[str, Any], client_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """Crea una campagna su Meta Ads."""
    logger.info("[Broker] Creazione campagna Meta per: %s", client_profile.get("businessName"))

    try:
        campaign_id = f"meta_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

        campaign = {
            "id": campaign_id,
            "externalId": None,
            "name": f"{client_profile.get('businessName', '')} - Awareness {client_profile.get('city', '')}",
            "status": "pending",
            "platform": "meta",
            "budget": {
                "daily": strategy["budgetAllocation"]["perPlatform"]["meta"]["daily"],
                "total": strategy["budgetAllocation"]["perPlatform"]["meta"]["monthly"],
                "spent": 0,
            },
            "objective": "AWARENESS",
            "targeting": {
                "locations": [client_profile.get("city", "")],
                "ageMin": 25,
                "ageMax": 65,
                "interests": _get_interests_for_business(client_profile.get("businessType", "")),
            },
            "adsets": [
                {
                    "name": "Awareness Local",
                    "budget": strategy["budgetAllocation"]["perPlatform"]["meta"]["daily"] * 0.6,
                    "targeting": {
                        "radius": 10,
                        "locations": [client_profile.get("city", "")],
                    },
                },
                {
                    "name": "Lookalike",
                    "budget": strategy["budgetAllocation"]["perPlatform"]["meta"]["daily"] * 0.4,
                    "targeting": {"lookalike": "1%"},
                },
            ],
            "ads": strategy["adCopy"].get("meta", []),
            "placements": ["feed", "stories", "reels"],
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }

        # Trigger n8n per pubblicazione
        try:
            await n8n_ads_service.create_campaign({
                "campaignId": campaign_id,
                "platform": "meta",
                "strategy": strategy,
                "adCopy": strategy["adCopy"],
                "clientProfile": {
                    "id": client_profile.get("id"),
                    "businessName": client_profile.get("businessName"),
                    "city": client_profile.get("city"),
                },
            })
            logger.info("[Broker] Campagna inviata a n8n")
        except Exception as e:
            logger.warning("[Broker] Errore invio a n8n: %s", e)

        return {
            "success": True,
            "campaignId": campaign_id,
            "campaign": campaign,
            "platform": "meta",
            "status": "pending",
            "message": "Campagna Meta creata e in attesa di approvazione",
        }
    except Exception as e:
        logger.error("[Broker] Errore creazione Meta: %s", e)
        return {"success": False, "error": str(e), "message": "Errore nella creazione campagna Meta"}


_INTERESTS_MAP: Dict[str, List[str]] = {
    "ristorazione": ["cibo", "ristoranti", "uscire", "gourmet"],
    "fitness": ["fitness", "palestra", "allenamento", "salute"],
    "estetica": ["bellezza", "cura personale", "moda", "lifestyle"],
    "immobiliare": ["casa", "arredamento", "ristrutturazione"],
    "servizi_legali": ["business", "imprenditoria", "professionisti"],
    "sanita": ["salute", "benessere", "cura personale"],
    "ecommerce": ["shopping", "moda", "online shopping"],
    "tech": ["tecnologia", "innovazione", "startup"],
    "marketing": ["business", "marketing", "imprenditoria"],
}


def _get_interests_for_business(business_type: str) -> List[str]:
    return _INTERESTS_MAP.get(business_type, ["business", "lifestyle"])


# ---------------------------------------------------------------------------
# Monitoraggio
# ---------------------------------------------------------------------------

async def monitor_campaign(
    campaign_id: str, campaign: Dict[str, Any]
) -> Dict[str, Any]:
    """Monitora le performance di una campagna."""
    metrics = _fetch_campaign_metrics(campaign)
    analysis = _analyze_performance(metrics, campaign)

    return {
        "campaignId": campaign_id,
        "metrics": metrics,
        "analysis": analysis,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _fetch_campaign_metrics(campaign: Dict[str, Any]) -> Dict[str, Any]:
    """Genera metriche simulate realistiche."""
    day_of_month = datetime.now(timezone.utc).day
    budget_daily = campaign.get("budget", {}).get("daily", 10)
    budget_spent = budget_daily * day_of_month * (0.8 + random.random() * 0.4)

    impressions = int(budget_spent * 100)
    clicks = int(impressions * (0.02 + random.random() * 0.03))
    conversions = int(clicks * (0.03 + random.random() * 0.05))

    return {
        "impressions": impressions,
        "clicks": clicks,
        "ctr": round((clicks / impressions) * 100, 2) if impressions else 0,
        "cpc": round(budget_spent / clicks, 2) if clicks else 0,
        "spend": round(budget_spent, 2),
        "conversions": conversions,
        "cpa": round(budget_spent / conversions, 2) if conversions > 0 else 0,
        "roas": round(2 + random.random() * 2, 2) if campaign.get("platform") == "meta" else None,
    }


def _analyze_performance(
    metrics: Dict[str, Any], campaign: Dict[str, Any]
) -> Dict[str, Any]:
    analysis: Dict[str, Any] = {
        "status": "good",
        "score": 70,
        "issues": [],
        "recommendations": [],
    }

    if metrics["ctr"] < 1.5:
        analysis["status"] = "warning"
        analysis["issues"].append("CTR basso (< 1.5%)")
        analysis["recommendations"].append("Rivedi ad copy, testa nuovi titoli")
        analysis["score"] -= 15
    elif metrics["ctr"] > 4:
        analysis["score"] += 10

    target_cpa = 20
    kpi = campaign.get("kpiTargets", {})
    if isinstance(kpi, dict) and isinstance(kpi.get("cpl"), dict):
        target_cpa = kpi["cpl"].get("max", 20)

    if metrics["cpa"] > target_cpa * 1.5:
        analysis["status"] = "critical"
        analysis["issues"].append(f"CPA critico (EUR {metrics['cpa']} vs target EUR {target_cpa})")
        analysis["recommendations"].append("Pausa campagna e rivedi targeting")
        analysis["score"] -= 25

    total = campaign.get("budget", {}).get("total", 1)
    progress = (metrics["spend"] / total) * 100 if total else 0
    if progress > 90:
        analysis["recommendations"].append("Budget quasi esaurito, considera aumento")

    if analysis["score"] < 50:
        analysis["status"] = "critical"
    elif analysis["score"] < 70:
        analysis["status"] = "warning"

    return analysis


# ---------------------------------------------------------------------------
# Ottimizzazione
# ---------------------------------------------------------------------------

async def optimize_campaign(
    campaign_id: str, metrics: Dict[str, Any], campaign: Dict[str, Any]
) -> Dict[str, Any]:
    """Ottimizza una campagna in base alle metriche."""
    logger.info("[Broker] Ottimizzazione campagna: %s", campaign_id)

    changes: List[Dict[str, Any]] = []

    if metrics.get("ctr", 0) < 2.0:
        changes.append({
            "type": "bid_adjustment",
            "action": "increase",
            "value": 10,
            "reason": "CTR basso, aumento bid per posizione migliore",
        })

    if metrics.get("cpa", 0) > 50:
        changes.append({
            "type": "keyword_pause",
            "action": "pause_high_cpa",
            "keywords": ["generic"],
            "reason": "CPA troppo alto, pausa keyword generiche",
        })

    roas = metrics.get("roas")
    if (roas and roas > 3) or (metrics.get("ctr", 0) > 3 and metrics.get("cpa", 0) < 15):
        changes.append({
            "type": "budget_increase",
            "action": "increase",
            "value": 20,
            "reason": "Performance eccellente, scaling budget +20%",
        })

    changes.append({
        "type": "negative_keywords",
        "action": "add",
        "keywords": ["gratis", "lavoro", "offerte"],
        "reason": "Filtra traffico non qualificato",
    })

    logger.info("[Broker] Ottimizzazione completata: %d cambiamenti", len(changes))

    return {
        "success": True,
        "campaignId": campaign_id,
        "changes": changes,
        "message": f"Ottimizzazione completata: {len(changes)} cambiamenti applicati",
    }
