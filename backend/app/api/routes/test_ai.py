"""
Routes per testare la connessione con Kimi AI
"""

from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/test", tags=["test"])


@router.get("/kimi-status")
async def test_kimi_connection():
    """
    Testa la connessione a Kimi API.
    Verifica che la API key sia configurata e valida.
    """
    try:
        # Verifica che la API key sia impostata
        if not settings.KIMI_API_KEY:
            logger.error("KIMI_API_KEY non impostata!")
            return {
                "status": "error",
                "message": "KIMI_API_KEY non configurata",
                "configured": False
            }
        
        # Testa una semplice chiamata
        logger.info("Test connessione Kimi...")
        result = await ai_service.generate_website(
            business_name="Test Bar",
            business_description="Un bar di test per verificare la connessione",
            sections=["hero"],
            style_preferences={"primary_color": "#3b82f6"}
        )
        
        if result.get("success"):
            return {
                "status": "ok",
                "message": "Connessione Kimi funzionante",
                "configured": True,
                "model": result.get("model_used"),
                "tokens_input": result.get("tokens_input"),
                "tokens_output": result.get("tokens_output"),
                "cost_usd": result.get("cost_usd"),
                "html_preview": result.get("html_content", "")[:200] + "..." if result.get("html_content") else None
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", "Errore sconosciuto"),
                "configured": True,
                "details": result.get("details")
            }
            
    except Exception as e:
        logger.exception("Errore test Kimi")
        return {
            "status": "error",
            "message": str(e),
            "configured": bool(settings.KIMI_API_KEY)
        }


@router.get("/env")
async def test_env():
    """
    Testa che le variabili ambiente siano caricate.
    ATTENZIONE: Non mostrare in produzione!
    """
    return {
        "kimi_api_key_configured": bool(settings.KIMI_API_KEY),
        "kimi_api_key_preview": settings.KIMI_API_KEY[:10] + "..." if settings.KIMI_API_KEY else None,
        "kimi_api_url": settings.KIMI_API_URL,
        "debug": settings.DEBUG,
        "database_url_configured": bool(settings.DATABASE_URL),
        "cors_allow_all": settings.CORS_ALLOW_ALL
    }


@router.post("/generate-simple")
async def test_simple_generation():
    """
    Genera un sito di test molto semplice.
    Utile per verificare che tutto funzioni.
    """
    try:
        result = await ai_service.generate_website(
            business_name="Pizzeria Test",
            business_description="Una pizzeria tradizionale napoletana",
            sections=["hero", "about"],
            style_preferences={
                "primary_color": "#ef4444",
                "mood": "traditional, warm"
            }
        )
        
        return result
        
    except Exception as e:
        logger.exception("Errore generazione test")
        raise HTTPException(status_code=500, detail=str(e))
