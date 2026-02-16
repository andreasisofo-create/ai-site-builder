"""
Campaign Wizard - 3 modalita: Guidata | Assistita | Manuale
Ported from Node.js: backend/wizard/campaignWizard.js
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Modalita
# ---------------------------------------------------------------------------

class WizardMode:
    GUIDED = "guided"
    ASSISTED = "assisted"
    MANUAL = "manual"


WIZARD_STEPS: List[Dict[str, str]] = [
    {"id": "objective", "name": "Obiettivo", "description": "Scegli cosa vuoi ottenere"},
    {"id": "budget", "name": "Budget", "description": "Quanto vuoi investire"},
    {"id": "audience", "name": "Pubblico", "description": "Chi vuoi raggiungere"},
    {"id": "content", "name": "Contenuto", "description": "Cosa promuovere"},
    {"id": "ad_copy", "name": "Testo Annuncio", "description": "Scrivi il messaggio"},
    {"id": "review", "name": "Riepilogo", "description": "Controlla e conferma"},
]

# ---------------------------------------------------------------------------
# Step 1: Obiettivi
# ---------------------------------------------------------------------------

OBJECTIVES: List[Dict[str, Any]] = [
    {
        "id": "awareness",
        "name": "Piu Follower",
        "description": "Fatti conoscere da nuove persone",
        "metaObjective": "AWARENESS",
        "bestFor": ["ristorazione", "fitness", "estetica", "retail"],
        "explanation": "La campagna mostrera i tuoi contenuti a persone che potrebbero essere interessate ma non ti seguono ancora.",
    },
    {
        "id": "traffic",
        "name": "Piu Visite al Sito",
        "description": "Porta persone sul tuo sito web",
        "metaObjective": "TRAFFIC",
        "bestFor": ["ecommerce", "servizi", "tech"],
        "explanation": "Meta trovera persone che tendono a cliccare sui link e visitare siti web.",
    },
    {
        "id": "leads",
        "name": "Piu Contatti",
        "description": "Raccogli email e telefoni",
        "metaObjective": "LEADS",
        "bestFor": ["servizi_legali", "sanita", "immobiliare", "servizi_professionali"],
        "explanation": "Perfetto per servizi B2B o consulenze. Le persone lasciano i loro dati in un modulo.",
    },
    {
        "id": "messages",
        "name": "Piu Messaggi",
        "description": "Fatti scrivere su WhatsApp/IG",
        "metaObjective": "MESSAGES",
        "bestFor": ["ristorazione", "estetica", "fitness", "edile"],
        "explanation": "Ideale per prenotazioni, preventivi, domande immediate. Il cliente ti contatta direttamente.",
    },
    {
        "id": "conversions",
        "name": "Piu Vendite",
        "description": "Vendi prodotti online",
        "metaObjective": "SALES",
        "bestFor": ["ecommerce", "retail"],
        "explanation": "Richiede Meta Pixel installato. Ottimizza per acquisti reali.",
    },
]

OBJECTIVES_BY_ID: Dict[str, Dict[str, Any]] = {o["id"]: o for o in OBJECTIVES}


def get_objective_help(objective_id: str, mode: str) -> Optional[Dict[str, Any]]:
    objective = OBJECTIVES_BY_ID.get(objective_id)
    if not objective:
        return None

    if mode == WizardMode.GUIDED:
        return {
            "why": objective["explanation"],
            "when": f"Questo obiettivo e perfetto per il tuo settore ({', '.join(objective['bestFor'])}).",
            "tip": "Scegli sempre l'obiettivo piu vicino alla tua meta finale. Se vuoi prenotazioni, scegli 'Messaggi' non 'Follower'.",
        }

    if mode == WizardMode.ASSISTED:
        return {
            "why": objective["explanation"],
            "bestFor": objective["bestFor"],
        }

    return None


# ---------------------------------------------------------------------------
# Step 2: Budget
# ---------------------------------------------------------------------------

BUDGET_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "starter",
        "name": "Starter",
        "daily": 5,
        "monthly": 150,
        "duration": 30,
        "description": "Per iniziare e testare",
        "expectedReach": "500-1.500 persone/mese",
        "expectedResults": "5-15 contatti/mese",
    },
    {
        "id": "standard",
        "name": "Standard",
        "daily": 10,
        "monthly": 300,
        "duration": 30,
        "description": "Il piu scelto dai clienti",
        "expectedReach": "1.500-4.000 persone/mese",
        "expectedResults": "15-40 contatti/mese",
    },
    {
        "id": "pro",
        "name": "Pro",
        "daily": 20,
        "monthly": 600,
        "duration": 30,
        "description": "Per risultati consistenti",
        "expectedReach": "4.000-10.000 persone/mese",
        "expectedResults": "40-100 contatti/mese",
    },
    {
        "id": "custom",
        "name": "Personalizzato",
        "daily": None,
        "monthly": None,
        "duration": None,
        "description": "Decidi tu importo e durata",
    },
]


def calculate_budget_recommendation(
    business_type: str, city: str, objective: str
) -> Dict[str, Any]:
    base_budgets: Dict[str, int] = {
        "ristorazione": 8,
        "fitness": 10,
        "estetica": 8,
        "servizi_legali": 15,
        "sanita": 12,
        "ecommerce": 12,
        "immobiliare": 15,
    }

    daily = base_budgets.get(business_type, 10)

    return {
        "recommendedDaily": daily,
        "recommendedMonthly": daily * 30,
        "minimumDaily": 5,
        "explanation": f"Per {business_type} a {city} con obiettivo {objective}, consigliamo {daily} EUR/giorno per avere risultati significativi.",
        "warning": "Budget sotto 8 EUR/giorno puo dare risultati limitati." if daily < 8 else None,
    }


# ---------------------------------------------------------------------------
# Step 3: Pubblico target
# ---------------------------------------------------------------------------

def generate_audience_suggestions(
    client_profile: Dict[str, Any], mode: str
) -> Dict[str, Any]:
    business_type = client_profile.get("businessType", "")
    city = client_profile.get("city", "")

    audience_templates: Dict[str, Dict[str, Any]] = {
        "ristorazione": {
            "ageMin": 25, "ageMax": 55,
            "interests": ["Cibo", "Ristoranti", "Cucina italiana", "Uscire"],
            "behaviors": ["Frequentatori ristoranti"],
            "radius": 10,
        },
        "fitness": {
            "ageMin": 20, "ageMax": 45,
            "interests": ["Fitness", "Palestra", "Allenamento", "Benessere"],
            "behaviors": ["Appassionati fitness"],
            "radius": 5,
        },
        "estetica": {
            "ageMin": 25, "ageMax": 55,
            "interests": ["Bellezza", "Cura personale", "Moda", "Lifestyle"],
            "behaviors": ["Acquisto prodotti bellezza"],
            "radius": 8,
        },
        "servizi_legali": {
            "ageMin": 30, "ageMax": 65,
            "interests": ["Business", "Imprenditoria", "Gestione aziendale"],
            "behaviors": ["Piccoli imprenditori"],
            "radius": 25,
        },
    }

    template = audience_templates.get(business_type, {
        "ageMin": 25, "ageMax": 55,
        "interests": ["Lifestyle", "Shopping"],
        "radius": 15,
    })

    if mode == WizardMode.GUIDED:
        interests_preview = " e ".join(template.get("interests", [])[:2])
        return {
            **template,
            "explanation": (
                f"Per {business_type}, il pubblico ideale e {template['ageMin']}-{template['ageMax']} anni, "
                f"interessato a {interests_preview}, nel raggio di {template['radius']}km da {city}."
            ),
            "why": "Meta trovera automaticamente le persone piu propense a interagire.",
            "tip": "Non restringere troppo! Lascia fare all'algoritmo.",
        }

    return template


# ---------------------------------------------------------------------------
# Step 5: Generazione testo annuncio
# ---------------------------------------------------------------------------

def generate_ad_copy_suggestions(
    client_profile: Dict[str, Any],
    objective: str,
    content_description: str,
    mode: str,
) -> Dict[str, Any]:
    business_name = client_profile.get("businessName", "")
    city = client_profile.get("city", "")
    usp = client_profile.get("usp", ["Qualita garantita"])

    templates: Dict[str, List[Dict[str, str]]] = {
        "messages": [
            {
                "headline": f"{business_name} - Scrivici ora!",
                "primaryText": f"Ciao! Siamo {business_name} a {city}. {usp[0]}. Scrivici per info, prenotazioni o preventivi. Ti rispondiamo in pochi minuti!",
                "cta": "Messaggio",
            },
            {
                "headline": f"Info e prenotazioni {business_name}",
                "primaryText": f"Hai domande sui nostri servizi? Siamo qui per aiutarti! {usp[0]}. Mandaci un messaggio e scopri come possiamo esserti utili.",
                "cta": "Messaggio",
            },
            {
                "headline": f"{business_name} ti aspetta!",
                "primaryText": f"{usp[0]}. Siamo a {city} e saremo felici di conoscerti. Scrivici per qualsiasi informazione!",
                "cta": "Messaggio",
            },
        ],
        "leads": [
            {
                "headline": "Richiedi info gratuita",
                "primaryText": f"{business_name} a {city} - {usp[0]}. Lascia i tuoi dati e ti contattiamo entro 24h con un preventivo personalizzato.",
                "cta": "Scopri di piu",
            },
        ],
        "awareness": [
            {
                "headline": f"Scopri {business_name}",
                "primaryText": f"{usp[0]}. Seguici per scoprire le novita e le offerte speciali! {business_name} a {city}.",
                "cta": "Segui",
            },
        ],
    }

    suggestions = templates.get(objective, templates["messages"])

    if mode == WizardMode.GUIDED:
        return {
            "variations": suggestions,
            "explanation": {
                "hook": "La prima frase deve fermare lo scrolling. Parla del beneficio per il cliente.",
                "body": "Spiega chiaramente cosa offri e perche sei diverso.",
                "cta": "Il Call to Action deve essere chiaro e urgente.",
                "rule": "Testo max 125 caratteri per la prima riga (prima di '...altro')",
            },
        }

    return {"variations": suggestions}


# ---------------------------------------------------------------------------
# Step 6: Riepilogo
# ---------------------------------------------------------------------------

def generate_campaign_summary(wizard_data: Dict[str, Any]) -> Dict[str, Any]:
    client_profile = wizard_data.get("clientProfile", {})
    objective_id = wizard_data.get("objective", "")
    budget = wizard_data.get("budget", {})
    audience = wizard_data.get("audience", {})
    content = wizard_data.get("content")
    ad_copy = wizard_data.get("adCopy", {})
    mode = wizard_data.get("mode", WizardMode.GUIDED)

    objective = OBJECTIVES_BY_ID.get(objective_id, {})
    today = datetime.now(timezone.utc).strftime("%d/%m/%Y")

    return {
        "campaignName": f"{client_profile.get('businessName', '')} - {objective.get('name', '')} - {today}",
        "objective": objective,
        "budget": {
            "daily": budget.get("daily"),
            "total": budget.get("monthly"),
            "duration": budget.get("duration"),
        },
        "audience": {
            "location": f"{audience.get('radius', 15)}km da {client_profile.get('city', '')}",
            "age": f"{audience.get('ageMin', 25)}-{audience.get('ageMax', 55)} anni",
            "interests": audience.get("interests", [])[:3],
        },
        "content": content,
        "adCopy": ad_copy.get("selected"),
        "platform": "meta",
        "placements": ["feed", "stories", "reels"],
        "mode": mode,
        "checks": [
            {"passed": (budget.get("daily") or 0) >= 5, "message": "Budget sufficiente"},
            {"passed": (audience.get("radius") or 0) <= 50, "message": "Targeting geografico appropriato"},
            {
                "passed": len((ad_copy.get("selected", {}).get("primaryText", "") or "")) > 50,
                "message": "Testo annuncio adeguato",
            },
        ],
    }
