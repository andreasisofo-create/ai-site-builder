"""
Routes per generazione AI siti web.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generate", tags=["generation"])


class GenerateRequest(BaseModel):
    """Richiesta generazione sito."""
    business_name: str
    business_description: str
    sections: List[str] = ["hero", "about", "services", "contact", "footer"]
    style_preferences: Optional[Dict[str, Any]] = None
    reference_analysis: Optional[str] = None
    logo_url: Optional[str] = None


class GenerateResponse(BaseModel):
    """Risposta generazione sito."""
    success: bool
    html_content: Optional[str] = None
    model_used: Optional[str] = None
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    cost_usd: Optional[float] = None
    generation_time_ms: Optional[int] = None
    error: Optional[str] = None


class ImageAnalysisRequest(BaseModel):
    """Richiesta analisi immagine."""
    image_url: str


@router.post("/website", response_model=GenerateResponse)
async def generate_website(request: GenerateRequest):
    """
    Genera un sito web completo usando AI.
    
    Esempio richiesta:
    ```json
    {
        "business_name": "Ristorante Da Mario",
        "business_description": "Ristorante italiano nel centro di Roma, specialità pasta fresca",
        "sections": ["hero", "about", "menu", "contact", "footer"],
        "style_preferences": {
            "primary_color": "#dc2626",
            "mood": "elegant"
        }
    }
    ```
    """
    try:
        result = await ai_service.generate_website(
            business_name=request.business_name,
            business_description=request.business_description,
            sections=request.sections,
            style_preferences=request.style_preferences,
            reference_analysis=request.reference_analysis,
            logo_url=request.logo_url
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        return GenerateResponse(**result)
        
    except Exception as e:
        logger.exception("Errore generazione sito")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-image")
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analizza un'immagine di riferimento per estrarre stile.
    
    Esempio:
    ```json
    {
        "image_url": "https://example.com/screenshot.png"
    }
    ```
    """
    try:
        result = await ai_service.analyze_image_style(request.image_url)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        return result
        
    except Exception as e:
        logger.exception("Errore analisi immagine")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_generation():
    """
    Endpoint di test con dati fittizi.
    Utile per verificare che l'integrazione funzioni.
    """
    test_request = GenerateRequest(
        business_name="Caffè Roma",
        business_description="Caffè storico nel cuore di Roma, dal 1950. Specialità caffè artigianale e cornetti freschi ogni mattina.",
        sections=["hero", "about", "menu", "gallery", "contact", "footer"],
        style_preferences={
            "primary_color": "#8B4513",
            "mood": "vintage, warm, welcoming"
        }
    )
    
    return await generate_website(test_request)
