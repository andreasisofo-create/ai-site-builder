"""Rate Limiter globale per l'applicazione.

Modulo separato per evitare import circolari tra main.py e i router.
Uso: from app.core.rate_limiter import limiter
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
