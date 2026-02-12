"""
Chat endpoint - AI chatbot powered by Kimi K2.5 for the landing page.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import logging

from app.services.kimi_client import KimiClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Simple in-memory rate limit
_rate_limits: dict = {}
RATE_LIMIT_MAX = 20
RATE_LIMIT_WINDOW = 3600

SYSTEM_PROMPT = """Sei l'assistente virtuale di E-quipe, una piattaforma AI italiana che crea siti web professionali e gestisce campagne pubblicitarie.

SERVIZI E-QUIPE:

1. CREAZIONE SITI WEB AI:
   - 19 template professionali in 8 categorie: Ristorante (3 stili), SaaS (3), Portfolio (3), E-commerce (2), Business (3), Blog (2), Eventi (2), Custom (1)
   - L'AI genera il sito completo in ~60 secondi
   - Animazioni GSAP professionali (29 effetti)
   - Editor chat AI per modifiche in tempo reale
   - Pubblicazione con 1 click su {slug}.e-quipe.app

2. GESTIONE ADS:
   - Campagne Meta Ads (Facebook/Instagram) e Google Ads
   - Gestite dagli esperti di E-quipe (team umano, NON un'AI)
   - Setup completo, monitoraggio e ottimizzazione continua
   - Report mensili dettagliati

PIANI E PREZZI (pagamento unico, NO abbonamento):
- Starter: GRATIS - 1 generazione, 3 modifiche chat, solo anteprima
- Sito Web: EUR 200 - 3 generazioni, 20 modifiche, pubblicazione sottodominio
- Premium: EUR 500 - 5 generazioni, modifiche illimitate, dominio personalizzato
- Sito + Ads: EUR 700 - tutto Premium + gestione campagne Ads

CONTATTO: andrea.sisofo@e-quipe.it

REGOLE:
- Rispondi SEMPRE in italiano
- Sii conciso (max 3-4 frasi per risposta)
- Sii amichevole e professionale
- Guida gli utenti verso la creazione del sito o il contatto
- Se la domanda non riguarda E-quipe, rispondi brevemente e riporta il focus sui servizi
- NON inventare funzionalita che non esistono
- NON menzionare mai "Gaia" - le ads sono gestite dagli esperti di E-quipe"""


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    reply: str
    error: Optional[str] = None


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    if ip not in _rate_limits:
        _rate_limits[ip] = []
    _rate_limits[ip] = [t for t in _rate_limits[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limits[ip]) >= RATE_LIMIT_MAX:
        return False
    _rate_limits[ip].append(now)
    return True


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        return ChatResponse(
            reply="Hai raggiunto il limite di messaggi. Riprova tra qualche minuto.",
            error="rate_limit",
        )

    try:
        kimi = KimiClient()
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if req.history:
            for msg in req.history[-10:]:
                messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": req.message})

        result = await kimi.call(
            messages=messages, max_tokens=500, thinking=False, timeout=30.0
        )

        if result.get("success"):
            return ChatResponse(reply=result["content"])
        else:
            logger.error(f"Kimi chat error: {result.get('error')}")
            return ChatResponse(reply="", error="ai_error")

    except Exception as e:
        logger.exception("Chat endpoint error")
        return ChatResponse(reply="", error=str(e))
