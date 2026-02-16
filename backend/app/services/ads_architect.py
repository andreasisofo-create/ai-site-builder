"""
Modulo Architect - Creazione strategia pubblicitaria.
Ported from Node.js: backend/modules/architect.js
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

from app.services.ads_knowledge import ads_knowledge

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Creazione strategia
# ---------------------------------------------------------------------------

async def create_strategy(
    client_profile: Dict[str, Any],
    market_data: Dict[str, Any],
    budget_monthly: int = 500,
) -> Dict[str, Any]:
    """Crea una strategia pubblicitaria completa."""
    logger.info("[Architect] Creazione strategia per: %s", client_profile.get("businessName"))

    platform_selection = select_platform(client_profile, market_data)
    funnel = _define_funnel(client_profile.get("businessType", ""))
    budget_allocation = _calculate_budget_allocation(
        budget_monthly, platform_selection, market_data.get("benchmarks")
    )
    ad_copy = generate_ad_copy(client_profile, platform_selection)
    kpi_targets = _define_kpi_targets(client_profile.get("businessType", ""), market_data.get("benchmarks"))
    confidence = _calculate_strategy_confidence(client_profile, market_data)

    strategy = {
        "clientId": client_profile.get("id"),
        "platformSelection": platform_selection,
        "funnel": funnel,
        "budgetAllocation": budget_allocation,
        "adCopy": ad_copy,
        "kpiTargets": kpi_targets,
        "confidence": confidence,
        "requiresApproval": confidence < 80,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    logger.info("[Architect] Strategia creata - Confidence: %s%%", confidence)
    return strategy


# ---------------------------------------------------------------------------
# Selezione piattaforma
# ---------------------------------------------------------------------------

_PLATFORM_LOGIC: Dict[str, Dict[str, str]] = {
    "ristorazione": {"primary": "both", "reasoning": "Google per ricerca attiva, Meta per awareness"},
    "servizi_legali": {"primary": "google", "reasoning": "Ricerca ad alta intenzione su Google"},
    "sanita": {"primary": "google", "reasoning": "Pazienti cercano attivamente servizi"},
    "fitness": {"primary": "meta", "reasoning": "Meta ideale per contenuti visivi e motivazionali"},
    "estetica": {"primary": "meta", "reasoning": "Visual-heavy, ideal per Instagram/Facebook"},
    "ecommerce": {"primary": "both", "reasoning": "Google Shopping + Meta Retargeting"},
    "immobiliare": {"primary": "both", "reasoning": "Ricerca attiva + visual properties"},
    "edile": {"primary": "google", "reasoning": "Servizi B2B/B2C ricercati attivamente"},
    "tech": {"primary": "both", "reasoning": "Google per B2B, Meta per B2C"},
    "marketing": {"primary": "meta", "reasoning": "Proof of concept sui nostri canali"},
}


def select_platform(
    client_profile: Dict[str, Any], market_data: Dict[str, Any]
) -> Dict[str, Any]:
    business_type = client_profile.get("businessType", "")
    selection = _PLATFORM_LOGIC.get(business_type, {"primary": "both", "reasoning": "Approccio bilanciato"})

    primary = selection["primary"]
    if primary == "both":
        secondary = None
    elif primary == "google":
        secondary = "meta"
    else:
        secondary = "google"

    return {
        "primary": primary,
        "secondary": secondary,
        "reasoning": selection["reasoning"],
        "estimatedReach": {
            "google": "alta" if primary in ("google", "both") else "media",
            "meta": "alta" if primary in ("meta", "both") else "media",
        },
    }


# ---------------------------------------------------------------------------
# Funnel
# ---------------------------------------------------------------------------

_FUNNELS: Dict[str, Dict[str, Any]] = {
    "ristorazione": {
        "type": "direct_response",
        "steps": [
            {"step": 1, "name": "Awareness", "channel": "meta", "objective": "Visualizza il ristorante", "budgetPercent": 30},
            {"step": 2, "name": "Consideration", "channel": "google", "objective": "Cerca ristorante", "budgetPercent": 50},
            {"step": 3, "name": "Conversion", "channel": "both", "objective": "Prenota tavolo", "budgetPercent": 20},
        ],
    },
    "servizi_legali": {
        "type": "lead_gen",
        "steps": [
            {"step": 1, "name": "Research", "channel": "google", "objective": "Cerca avvocato", "budgetPercent": 70},
            {"step": 2, "name": "Lead Capture", "channel": "both", "objective": "Richiedi consulenza", "budgetPercent": 30},
        ],
    },
    "fitness": {
        "type": "direct_response",
        "steps": [
            {"step": 1, "name": "Awareness", "channel": "meta", "objective": "Vedi trasformazioni", "budgetPercent": 40},
            {"step": 2, "name": "Trial", "channel": "both", "objective": "Prova gratuita", "budgetPercent": 40},
            {"step": 3, "name": "Membership", "channel": "meta", "objective": "Iscrizione", "budgetPercent": 20},
        ],
    },
    "ecommerce": {
        "type": "direct_response",
        "steps": [
            {"step": 1, "name": "Prospecting", "channel": "meta", "objective": "Scopri prodotti", "budgetPercent": 40},
            {"step": 2, "name": "Shopping", "channel": "google", "objective": "Cerca prodotto", "budgetPercent": 40},
            {"step": 3, "name": "Retargeting", "channel": "both", "objective": "Completa acquisto", "budgetPercent": 20},
        ],
    },
}

_DEFAULT_FUNNEL: Dict[str, Any] = {
    "type": "lead_gen",
    "steps": [
        {"step": 1, "name": "Awareness", "channel": "meta", "objective": "Conosci il brand", "budgetPercent": 30},
        {"step": 2, "name": "Consideration", "channel": "google", "objective": "Valuta servizio", "budgetPercent": 40},
        {"step": 3, "name": "Conversion", "channel": "both", "objective": "Richiedi info", "budgetPercent": 30},
    ],
}


def _define_funnel(business_type: str) -> Dict[str, Any]:
    return _FUNNELS.get(business_type, _DEFAULT_FUNNEL)


# ---------------------------------------------------------------------------
# Budget allocation
# ---------------------------------------------------------------------------

def _calculate_budget_allocation(
    budget_monthly: int,
    platform_selection: Dict[str, Any],
    benchmarks: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    daily_budget = round(budget_monthly / 30)

    if benchmarks and benchmarks.get("recommendedBudget"):
        rb = benchmarks["recommendedBudget"]
        split = {
            "google": rb.get("googleSplit", 50),
            "meta": rb.get("metaSplit", 50),
        }
    else:
        primary = platform_selection.get("primary", "both")
        if primary == "both":
            split = {"google": 60, "meta": 40}
        elif primary == "google":
            split = {"google": 80, "meta": 20}
        else:
            split = {"google": 20, "meta": 80}

    return {
        "totalMonthly": budget_monthly,
        "daily": daily_budget,
        "perPlatform": {
            "google": {
                "monthly": round(budget_monthly * split["google"] / 100),
                "daily": round(daily_budget * split["google"] / 100),
            },
            "meta": {
                "monthly": round(budget_monthly * split["meta"] / 100),
                "daily": round(daily_budget * split["meta"] / 100),
            },
        },
        "split": split,
        "recommended": {
            "minimumDaily": 10,
            "learningPhaseDays": 14,
            "optimizationStart": 7,
        },
    }


# ---------------------------------------------------------------------------
# Ad copy generation
# ---------------------------------------------------------------------------

def generate_ad_copy(
    client_profile: Dict[str, Any], platform_selection: Dict[str, Any]
) -> Dict[str, Any]:
    business_name = client_profile.get("businessName", "")
    business_type = client_profile.get("businessType", "")
    services: List[str] = client_profile.get("services", [])
    usp: List[str] = client_profile.get("usp", ["Qualita garantita"])
    city: str = client_profile.get("city", "")

    kb_ad_copy = ads_knowledge.get_ad_copy(business_type)

    if kb_ad_copy:
        def personalize(text: Optional[str]) -> str:
            if not text:
                return ""
            import re
            text = re.sub(r"\[Citt[aà]\]", city, text, flags=re.IGNORECASE)
            text = re.sub(r"\[Servizio\]", services[0] if services else "Servizi", text, flags=re.IGNORECASE)
            text = re.sub(r"\[Nome\]", business_name, text, flags=re.IGNORECASE)
            return text

        google_headlines = [personalize(h) for h in kb_ad_copy.get("google_headlines", [])]
        google_descriptions = [personalize(d) for d in kb_ad_copy.get("google_descriptions", [])]
        meta_hooks = [personalize(h) for h in kb_ad_copy.get("meta_hooks", [])]
        meta_bodies = [personalize(b) for b in kb_ad_copy.get("meta_bodies", [])]
        ctas = kb_ad_copy.get("ctas", ["Scopri di piu", "Contattaci", "Richiedi Info"])

        variant_names = ["emotional", "offer", "social_proof"]
        meta_ads = [
            {
                "variant": variant_names[i] if i < len(variant_names) else "generic",
                "hook": hook,
                "body": meta_bodies[i % len(meta_bodies)] if meta_bodies else f"{business_name} offre servizi professionali a {city}.",
                "cta": ctas[i % len(ctas)],
            }
            for i, hook in enumerate(meta_hooks[:3])
        ]

        return {
            "google": {
                "headlines": google_headlines,
                "descriptions": google_descriptions,
                "path1": services[0].lower().replace(" ", "-") if services else "servizi",
                "path2": city.lower().replace(" ", "-") if city else "local",
            },
            "meta": meta_ads,
            "keywords": {
                "main": [f"{s} {city}" for s in services],
                "extensions": ["migliore", "professionale", "qualita", "prezzi", "recensioni"],
            },
            "source": "knowledge_base",
        }

    # Fallback generico
    google_headlines = [
        f"{business_name} - {city}",
        services[0] if services else "Servizi Professionali",
        usp[0] if usp else "Qualita Garantita",
        "Scopri di piu",
        "Contattaci Ora",
        f"{city} - {services[0]}" if services and city else "Servizi",
        "Prezzi Competitivi",
        "Esperienza decennale",
        "Consulenza Gratuita",
        "Prenota Online",
    ][:15]

    svc_text = ", ".join(services) if services else "servizi"
    svc_short = " e ".join(services[:2]) if services else "servizi"

    google_descriptions = [
        f"{business_name} offre {svc_text} a {city}. {usp[0]}. Contattaci per un preventivo gratuito.",
        f"Servizi professionali a {city}. {usp[1] if len(usp) > 1 else usp[0]}. Chiama ora o richiedi info online.",
        f"Scopri perche siamo i migliori a {city}. {svc_short}. Prima consulenza gratuita.",
    ][:4]

    meta_ads = [
        {
            "variant": "emotional",
            "hook": f"Cerchi {services[0] if services else 'servizi professionali'} a {city}?",
            "body": f"{business_name} e la scelta giusta. {usp[0]}. {svc_short}. Scopri come possiamo aiutarti.",
            "cta": "Scopri di piu",
        },
        {
            "variant": "offer",
            "hook": f"Offerta speciale {business_name}",
            "body": f"{usp[0]}. Servizi di {services[0] if services else 'qualita'} a {city}. Contattaci ora per un preventivo gratuito.",
            "cta": "Richiedi Info",
        },
        {
            "variant": "social_proof",
            "hook": f"Scopri perche ci scelgono a {city}",
            "body": f"{business_name}: {usp[0]}. {svc_short}. Unisciti ai nostri clienti soddisfatti.",
            "cta": "Contattaci",
        },
    ]

    return {
        "google": {
            "headlines": google_headlines,
            "descriptions": google_descriptions,
            "path1": services[0].lower().replace(" ", "-") if services else "servizi",
            "path2": city.lower().replace(" ", "-") if city else "local",
        },
        "meta": meta_ads,
        "keywords": {
            "main": [f"{s} {city}" for s in services],
            "extensions": ["migliore", "professionale", "qualita", "prezzi", "recensioni"],
        },
        "source": "generic",
    }


# ---------------------------------------------------------------------------
# KPI targets
# ---------------------------------------------------------------------------

_KPI_TARGETS: Dict[str, Dict[str, Any]] = {
    "ristorazione": {"ctr": 4.0, "cpc": {"min": 0.4, "max": 1.2}, "cpl": {"min": 3, "max": 8}, "conversionRate": 3.0, "learningPhaseDays": 7},
    "servizi_legali": {"ctr": 2.5, "cpc": {"min": 2.0, "max": 5.0}, "cpl": {"min": 20, "max": 60}, "conversionRate": 5.0, "learningPhaseDays": 14},
    "sanita": {"ctr": 3.0, "cpc": {"min": 1.5, "max": 4.0}, "cpl": {"min": 12, "max": 35}, "conversionRate": 4.0, "learningPhaseDays": 10},
    "fitness": {"ctr": 3.5, "cpc": {"min": 0.6, "max": 1.8}, "cpl": {"min": 5, "max": 15}, "conversionRate": 4.5, "learningPhaseDays": 7},
    "ecommerce": {"ctr": 2.5, "cpc": {"min": 0.5, "max": 1.5}, "cpl": {"min": 8, "max": 20}, "conversionRate": 2.0, "roas": 3.0, "learningPhaseDays": 14},
    "immobiliare": {"ctr": 3.0, "cpc": {"min": 1.0, "max": 3.0}, "cpl": {"min": 10, "max": 30}, "conversionRate": 3.5, "learningPhaseDays": 14},
}


def _define_kpi_targets(business_type: str, benchmarks: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return _KPI_TARGETS.get(business_type, {
        "ctr": 3.0, "cpc": {"min": 0.8, "max": 2.0},
        "cpl": {"min": 8, "max": 20}, "conversionRate": 3.0,
        "learningPhaseDays": 14,
    })


# ---------------------------------------------------------------------------
# Confidence score
# ---------------------------------------------------------------------------

def _calculate_strategy_confidence(
    client_profile: Dict[str, Any], market_data: Dict[str, Any]
) -> int:
    score = 70

    if (
        client_profile.get("businessType") != "servizi"
        and client_profile.get("city") != "Non specificata"
    ):
        score += 10

    keywords = market_data.get("keywords")
    if keywords and len(keywords) > 5:
        score += 10

    if market_data.get("benchmarks"):
        score += 10

    return min(score, 95)
