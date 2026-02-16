"""
Modulo Analyst - Ricerca di mercato, keyword, competitor e benchmark.
Ported from Node.js: backend/modules/analyst.js
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

from app.services.ads_knowledge import ads_knowledge

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Ricerca keyword
# ---------------------------------------------------------------------------

def research_keywords(
    business_type: str, city: str, services: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Ricerca keyword rilevanti per il business."""
    logger.info("[Analyst] Ricerca keyword per: %s a %s", business_type, city)
    services = services or []

    base_keywords = _generate_base_keywords(business_type, city)
    service_keywords = [f"{s} {city}".lower() for s in services]

    all_keywords = base_keywords + service_keywords
    enriched = [_enrich_keyword_data(kw, business_type) for kw in all_keywords]
    enriched.sort(key=lambda k: k["monthlyVolume"], reverse=True)

    logger.info("[Analyst] Trovate %d keyword", len(enriched))

    return {
        "keywords": enriched,
        "negativeKeywords": _generate_negative_keywords(business_type),
        "summary": _generate_keyword_summary(enriched),
    }


_KEYWORD_TEMPLATES: Dict[str, List[str]] = {
    "ristorazione": [
        "ristorante {city}", "pizzeria {city}", "mangiare {city}",
        "pranzo {city}", "cena {city}", "ristorante zona centro {city}",
        "miglior ristorante {city}", "dove mangiare {city}",
    ],
    "ospitalita": [
        "hotel {city}", "albergo {city}", "dove dormire {city}",
        "bed and breakfast {city}", "camera {city}",
    ],
    "ecommerce": [
        "negozio online {city}", "acquisti online {city}",
        "shop {city}", "vendita online",
    ],
    "servizi_legali": [
        "avvocato {city}", "studio legale {city}", "consulenza legale {city}",
        "avvocato civilista {city}", "avvocato penalista {city}",
    ],
    "servizi_professionali": [
        "commercialista {city}", "consulenza fiscale {city}",
        "dottore commercialista {city}", "gestione contabilita {city}",
    ],
    "sanita": [
        "dentista {city}", "studio dentistico {city}",
        "odontoiatra {city}", "implantologia {city}",
    ],
    "fitness": [
        "palestra {city}", "fitness {city}", "personal trainer {city}",
        "allenamento {city}", "gym {city}",
    ],
    "estetica": [
        "parrucchiere {city}", "estetista {city}", "beauty {city}",
        "capelli {city}", "unghie {city}",
    ],
    "immobiliare": [
        "agenzia immobiliare {city}", "casa in vendita {city}",
        "appartamento affitto {city}", "agenzia immobiliare zona",
    ],
    "edile": [
        "impresa edile {city}", "ristrutturazione {city}",
        "costruzioni {city}", "edilizia {city}",
    ],
    "creativo": [
        "fotografo {city}", "fotografia {city}",
        "video {city}", "servizi fotografici {city}",
    ],
    "tech": [
        "software {city}", "sviluppo app {city}",
        "web agency {city}", "digital {city}",
    ],
    "marketing": [
        "agenzia marketing {city}", "pubblicita {city}",
        "comunicazione {city}", "digital marketing {city}",
    ],
    "formazione": [
        "corsi {city}", "formazione {city}",
        "scuola {city}", "training {city}",
    ],
    "servizi": [
        "{city} servizi", "professionista {city}", "consulenza {city}",
    ],
}


def _generate_base_keywords(business_type: str, city: str) -> List[str]:
    templates = _KEYWORD_TEMPLATES.get(business_type, _KEYWORD_TEMPLATES["servizi"])
    return [t.format(city=city) for t in templates]


def _enrich_keyword_data(keyword: str, business_type: str) -> Dict[str, Any]:
    h = sum(ord(c) for c in keyword)

    intent = "commercial"
    if "come" in keyword or "cosa" in keyword:
        intent = "informational"
    elif "acquista" in keyword or "compra" in keyword:
        intent = "transactional"
    elif "brand" in keyword:
        intent = "navigational"

    cpc_base_map: Dict[str, float] = {
        "ristorazione": 0.8, "ospitalita": 1.2, "ecommerce": 0.6,
        "servizi_legali": 3.5, "servizi_professionali": 2.8, "sanita": 2.5,
        "fitness": 1.5, "estetica": 1.0, "immobiliare": 2.0,
        "edile": 2.2, "creativo": 1.3, "tech": 2.0,
        "marketing": 1.8, "formazione": 1.2, "servizi": 1.5,
    }

    base_cpc = cpc_base_map.get(business_type, 1.0)
    cpc_variation = (h % 100) / 100

    competition_idx = h % 3
    competition = ["high", "medium", "low"][competition_idx]
    trend = ["rising", "stable", "declining"][competition_idx]

    return {
        "keyword": keyword,
        "matchType": "exact",
        "intent": intent,
        "monthlyVolume": 100 + (h % 1900),
        "cpcAvg": round(base_cpc + cpc_variation, 2),
        "cpcRange": {
            "min": round(base_cpc * 0.7, 2),
            "max": round(base_cpc * 1.3, 2),
        },
        "competition": competition,
        "trend": trend,
        "recommended": h % 2 == 0,
        "group": business_type,
    }


def _generate_negative_keywords(business_type: str) -> List[Dict[str, str]]:
    kb_keywords = ads_knowledge.get_negative_keywords(business_type)
    if kb_keywords:
        return [
            {"keyword": kw, "reason": "Filtra traffico non qualificato", "source": "knowledge_base"}
            for kw in kb_keywords
        ]

    common = [
        "gratis", "free", "senza pagare", "fai da te", "diy",
        "lavoro", "offerte lavoro", "stage", "tirocinio",
        "usato", "vintage", "second hand", "ebay",
        "ricetta", "come fare", "tutorial", "youtube",
        "libro", "pdf", "download", "torrent",
    ]

    sector_negatives: Dict[str, List[str]] = {
        "ristorazione": ["domicilio gratis", "deliveroo", "just eat", "glovo"],
        "sanita": ["fai da te", "rimedi naturali", "omeopatia"],
        "immobiliare": ["affitto breve", "airbnb", "subito"],
        "servizi_legali": ["gratis", "pro bono", "patrocinio gratuito"],
        "servizi_professionali": ["gratis", "fai da te", "software free"],
    }

    all_neg = common + sector_negatives.get(business_type, [])
    return [{"keyword": kw, "reason": "Filtra traffico non qualificato"} for kw in all_neg]


def _generate_keyword_summary(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_volume = sum(k["monthlyVolume"] for k in keywords)
    avg_cpc = sum(k["cpcAvg"] for k in keywords) / len(keywords) if keywords else 0

    return {
        "totalKeywords": len(keywords),
        "totalMonthlyVolume": total_volume,
        "averageCpc": round(avg_cpc, 2),
        "recommendedCount": sum(1 for k in keywords if k["recommended"]),
        "highCompetition": sum(1 for k in keywords if k["competition"] == "high"),
        "risingTrends": sum(1 for k in keywords if k["trend"] == "rising"),
    }


# ---------------------------------------------------------------------------
# Analisi competitor
# ---------------------------------------------------------------------------

def analyze_competitors(keywords: List[str]) -> Dict[str, Any]:
    """Analizza i competitor per le keyword target (simulato)."""
    logger.info("[Analyst] Analisi competitor per %d keyword", len(keywords))

    competitors = [
        {
            "name": "Competitor A",
            "url": "https://competitor-a.it",
            "estimatedMonthlySpend": 2500,
            "topKeywords": keywords[:3],
            "adCopyExamples": ["Miglior servizio a Milano", "Qualita garantita dal 2010"],
            "strengths": ["Brand forte", "Budget elevato"],
            "weaknesses": ["Creativita datata", "Landing page lenta"],
        },
        {
            "name": "Competitor B",
            "url": "https://competitor-b.it",
            "estimatedMonthlySpend": 1200,
            "topKeywords": keywords[1:4],
            "adCopyExamples": ["Prezzi competitivi", "Offerta speciale"],
            "strengths": ["Prezzi bassi"],
            "weaknesses": ["Qualita scarsa", "Recensioni negative"],
        },
    ]

    return {
        "competitors": competitors,
        "marketShare": {
            "leader": competitors[0]["name"],
            "estimatedTotalSpend": sum(c["estimatedMonthlySpend"] for c in competitors),
        },
    }


# ---------------------------------------------------------------------------
# Benchmark settore
# ---------------------------------------------------------------------------

def get_benchmarks(sector: str) -> Dict[str, Any]:
    """Ottiene benchmark per il settore, usa knowledge base se disponibile."""
    kb_benchmark = ads_knowledge.get_benchmark(sector)

    if kb_benchmark and kb_benchmark.get("google"):
        return {
            "avgCpc": kb_benchmark["google"]["cpc"],
            "avgCpm": kb_benchmark["google"]["cpm"],
            "avgCtr": {"min": 2.0, "max": 4.5},
            "avgCpl": kb_benchmark.get("cpl"),
            "recommendedBudget": {
                "min": kb_benchmark.get("recommendedBudget", 300),
                "googleSplit": kb_benchmark.get("platformSplit", {}).get("google", 50),
                "metaSplit": kb_benchmark.get("platformSplit", {}).get("meta", 50),
            },
        }

    fallback: Dict[str, Dict[str, Any]] = {
        "ristorazione": {
            "avgCpc": {"min": 0.4, "max": 1.2}, "avgCpm": {"min": 3, "max": 8},
            "avgCtr": {"min": 2.5, "max": 5.0}, "avgCpl": {"min": 3, "max": 8},
            "recommendedBudget": {"min": 300, "googleSplit": 60, "metaSplit": 40},
        },
        "servizi_legali": {
            "avgCpc": {"min": 1.5, "max": 4.0}, "avgCpm": {"min": 8, "max": 18},
            "avgCtr": {"min": 1.5, "max": 3.5}, "avgCpl": {"min": 15, "max": 50},
            "recommendedBudget": {"min": 400, "googleSplit": 70, "metaSplit": 30},
        },
        "fitness": {
            "avgCpc": {"min": 0.6, "max": 1.8}, "avgCpm": {"min": 4, "max": 10},
            "avgCtr": {"min": 2.0, "max": 4.5}, "avgCpl": {"min": 5, "max": 15},
            "recommendedBudget": {"min": 300, "googleSplit": 40, "metaSplit": 60},
        },
    }

    return fallback.get(sector, {
        "avgCpc": {"min": 0.8, "max": 2.0}, "avgCpm": {"min": 4, "max": 10},
        "avgCtr": {"min": 2.0, "max": 4.0}, "avgCpl": {"min": 8, "max": 20},
        "recommendedBudget": {"min": 300, "googleSplit": 60, "metaSplit": 40},
    })


# ---------------------------------------------------------------------------
# Trend di mercato
# ---------------------------------------------------------------------------

def analyze_trends(business_type: str, city: str) -> Dict[str, Any]:
    month = datetime.now(timezone.utc).month - 1  # 0-indexed like JS

    seasonality: Dict[str, Dict[str, List[int]]] = {
        "ristorazione": {"peak": [5, 6, 7, 8, 11, 12], "low": [1, 2]},
        "ospitalita": {"peak": [5, 6, 7, 8], "low": [1, 2, 11, 12]},
        "fitness": {"peak": [0, 1, 8, 9], "low": [6, 7, 11, 12]},
        "immobiliare": {"peak": [2, 3, 4, 8, 9], "low": [7, 11, 12]},
        "estetica": {"peak": [4, 5, 11, 12], "low": [1, 7, 8]},
    }

    sector_seasonality = seasonality.get(business_type, {"peak": [], "low": []})

    if month in sector_seasonality["peak"]:
        trend = "rising"
    elif month in sector_seasonality["low"]:
        trend = "declining"
    else:
        trend = "stable"

    recommendations = {
        "rising": "Aumenta budget per cogliere la stagionalita positiva",
        "declining": "Riduci budget o focalizzati su keyword di conversione",
        "stable": "Mantieni budget costante",
    }

    return {
        "currentTrend": trend,
        "seasonality": sector_seasonality,
        "recommendation": recommendations[trend],
    }
