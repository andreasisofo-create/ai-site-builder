"""
Modulo Investigator - Analisi sito web cliente.
Ported from Node.js: backend/modules/investigator.js
"""

import re
import httpx
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Analisi sito web
# ---------------------------------------------------------------------------

async def analyze_website(url: str) -> Dict[str, Any]:
    """Analizza un sito web estraendo informazioni chiave per la profilazione business."""
    logger.info("[Investigator] Analizzando sito: %s", url)

    normalized_url = url if url.startswith("http") else f"https://{url}"

    html = await _scrape_website(normalized_url)
    profile = _extract_business_profile(html, normalized_url)
    profile["confidence"] = _calculate_confidence(profile)

    logger.info("[Investigator] Analisi completata - Confidence: %s%%", profile["confidence"])
    return profile


async def _scrape_website(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.error("[Investigator] Errore scraping: %s", e)
        return _generate_mock_html(url)


def _extract_business_profile(html: str, url: str) -> Dict[str, Any]:
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
        "email": _extract_email(html),
        "websiteUrl": url,
        "description": _extract_meta_description(html),
        "analyzedAt": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Estrattori specifici
# ---------------------------------------------------------------------------

def _extract_title(html: str) -> Optional[str]:
    m = re.search(r"<title[^>]*>([^<]*)</title>", html, re.IGNORECASE)
    return m.group(1).strip() if m else None


def _extract_meta_description(html: str) -> Optional[str]:
    patterns = [
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
        r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']',
    ]
    for p in patterns:
        m = re.search(p, html, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _extract_from_domain(url: str) -> str:
    try:
        hostname = urlparse(url).hostname or ""
        domain = hostname.replace("www.", "")
        name = domain.split(".")[0]
        return name[0].upper() + name[1:] if name else "Business"
    except Exception:
        return "Business"


_BUSINESS_TYPES = [
    (["ristorante", "pizzeria", "trattoria", "osteria", "food", "menu", "cucina"], "ristorazione"),
    (["hotel", "albergo", "bed", "breakfast", "b&b", "vacanza", "camera"], "ospitalita"),
    (["negozio", "shop", "ecommerce", "e-commerce", "vendita", "prodotti", "store"], "ecommerce"),
    (["avvocato", "studio legale", "legge", "diritto", "consulenza legale"], "servizi_legali"),
    (["commercialista", "contabile", "fiscale", "tributario", "dottore"], "servizi_professionali"),
    (["dentista", "odontoiatra", "studio dentistico", "odontoiatria"], "sanita"),
    (["palestra", "fitness", "gym", "allenamento", "personal trainer"], "fitness"),
    (["parrucchiere", "estetista", "beauty", "capelli", "unghie"], "estetica"),
    (["immobiliare", "agenzia", "casa", "appartamento", "affitto"], "immobiliare"),
    (["costruzioni", "edile", "ristrutturazione", "impresa", "edilizia"], "edile"),
    (["fotografo", "fotografia", "photo", "video", "riprese"], "creativo"),
    (["software", "app", "web", "digital", "tecnologia", "startup"], "tech"),
    (["marketing", "agenzia marketing", "pubblicita", "comunicazione"], "marketing"),
    (["corso", "formazione", "scuola", "insegnamento", "training"], "formazione"),
]


def _detect_business_type(html: str) -> str:
    lower_html = html.lower()
    for keywords, btype in _BUSINESS_TYPES:
        if any(k in lower_html for k in keywords):
            return btype
    return "servizi"


def _extract_services(html: str) -> List[str]:
    services: List[str] = []
    patterns = [
        r"(?:servizi|services|offerta|cosa facciamo)[\s\S]*?<li[^>]*>([^<]+)",
        r"<h[23][^>]*>([^<]*(?:consulenza|servizio|supporto|assistenza|progetto)[^<]*)</h[23]>",
    ]
    for p in patterns:
        for m in re.finditer(p, html, re.IGNORECASE):
            s = m.group(1).strip()
            if 3 < len(s) < 100 and s not in services:
                services.append(s)
            if len(services) >= 5:
                break

    if not services:
        common = ["consulenza", "assistenza", "supporto", "progettazione",
                   "installazione", "manutenzione", "formazione"]
        lower_html = html.lower()
        for s in common:
            if s in lower_html and len(services) < 3:
                services.append(s[0].upper() + s[1:])

    return services or ["Servizi personalizzati"]


def _extract_target_audience(html: str) -> str:
    lower = html.lower()
    if any(k in lower for k in ("azienda", "business", "corporate")):
        return "B2B - Aziende"
    if any(k in lower for k in ("privato", "famiglia", "individuo")):
        return "B2C - Privati"
    if any(k in lower for k in ("professionista", "libero professionista")):
        return "Professionisti"
    return "Generico"


def _extract_usp(html: str) -> List[str]:
    usp: List[str] = []
    patterns = [
        r"<h[123][^>]*>([^<]*(?:miglior|esperto|qualita|esperienza|specializzato|unico|innovativo)[^<]*)</h[123]>",
        r"(?:perche scegliere|why choose|i nostri punti di forza)[\s\S]*?<li[^>]*>([^<]+)",
    ]
    for p in patterns:
        for m in re.finditer(p, html, re.IGNORECASE):
            text = m.group(1).strip()
            if 5 < len(text) < 150:
                usp.append(text)
            if len(usp) >= 3:
                break
    return usp or ["Qualita garantita", "Esperienza nel settore"]


_ITALIAN_CITIES = [
    "Milano", "Roma", "Torino", "Genova", "Bologna", "Firenze", "Napoli",
    "Verona", "Padova", "Venezia", "Brescia", "Monza", "Como", "Varese",
]


def _extract_city(html: str) -> str:
    for city in _ITALIAN_CITIES:
        if city in html:
            return city
    m = re.search(r",\s*\d{5}\s*([A-Za-z\s]+)[<,\s]", html)
    if m:
        return m.group(1).strip()
    return "Non specificata"


_CITY_REGION_MAP: Dict[str, str] = {
    "Milano": "Lombardia", "Monza": "Lombardia", "Brescia": "Lombardia",
    "Como": "Lombardia", "Varese": "Lombardia", "Bergamo": "Lombardia",
    "Roma": "Lazio",
    "Torino": "Piemonte", "Novara": "Piemonte", "Alessandria": "Piemonte",
    "Genova": "Liguria", "Savona": "Liguria", "Imperia": "Liguria",
    "Bologna": "Emilia-Romagna", "Modena": "Emilia-Romagna", "Parma": "Emilia-Romagna",
    "Firenze": "Toscana", "Pisa": "Toscana", "Siena": "Toscana",
    "Napoli": "Campania", "Salerno": "Campania",
    "Venezia": "Veneto", "Verona": "Veneto", "Padova": "Veneto", "Vicenza": "Veneto",
}


def _extract_region(html: str) -> str:
    city = _extract_city(html)
    return _CITY_REGION_MAP.get(city, "")


def _extract_address(html: str) -> str:
    m = re.search(
        r"(via|viale|corso|piazza|riviera|strada)\s+[\w\s]+\d+[\s,]*\d{5}\s*[\w\s]+",
        html, re.IGNORECASE,
    )
    return m.group(0).strip() if m else ""


def _extract_phone(html: str) -> str:
    m = re.search(r"(\+39\s*\d{8,}|\d{3}[\s.\-]*\d{3}[\s.\-]*\d{4})", html)
    return m.group(0) if m else ""


def _extract_email(html: str) -> str:
    m = re.search(r"[\w.\-]+@[\w.\-]+\.\w+", html)
    return m.group(0) if m else ""


def _calculate_confidence(profile: Dict[str, Any]) -> int:
    score = 50
    if profile.get("businessName") and profile["businessName"] != "Business":
        score += 15
    if profile.get("businessType") != "servizi":
        score += 15
    if profile.get("services"):
        score += 10
    if profile.get("city") != "Non specificata":
        score += 10
    return min(score, 95)


def _generate_mock_html(url: str) -> str:
    return f"""
    <html>
      <head><title>Business da {url}</title></head>
      <body>
        <h1>Servizi professionali</h1>
        <p>Offriamo consulenza e assistenza di qualita.</p>
      </body>
    </html>
    """
