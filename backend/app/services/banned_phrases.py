"""
Canonical list of banned generic phrases (Italian).

Imported by pre_delivery_check.py, quality_reviewer.py, and quality_control.py
to ensure consistent phrase detection across all quality pipelines.
"""

# Sorted, deduplicated list — case-insensitive matching in all consumers
BANNED_PHRASES = [
    "a 360 gradi",
    "azienda leader nel settore",
    "benvenuta",
    "benvenuti",
    "benvenuti nel nostro sito",
    "benvenuti sul nostro sito",
    "benvenuto",
    "chiavi in mano",
    "contattaci per maggiori informazioni",
    "cosa offriamo",
    "da anni nel settore",
    "dolor sit amet",
    "eccellenza e innovazione",
    "i nostri servizi",
    "il nostro obiettivo",
    "il nostro team",
    "il nostro team di esperti",
    "la nostra azienda",
    "la nostra mission",
    "leader del settore",
    "leader nel settore",
    "lorem ipsum",
    "non esitare a contattarci",
    "offriamo servizi",
    "per saperne di più",
    "qualita e professionalita",
    "qualità e professionalità",
    "scopri di più",
    "siamo un team",
    "siamo un team di professionisti",
    "siamo un'azienda",
    "siamo un'azienda leader",
    "siamo un azienda leader",
    "soluzioni personalizzate",
    "soluzioni su misura",
]
