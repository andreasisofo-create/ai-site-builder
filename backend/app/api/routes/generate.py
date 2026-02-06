"""
Routes per generazione AI siti web.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.ai_service import ai_service
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
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


@router.post("/website")
async def generate_website(
    request: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Genera un sito web completo usando AI.
    Richiede autenticazione. Controlla il limite di 2 generazioni gratuite.
    
    Esempio richiesta:
    ```json
    {
        "business_name": "Ristorante Da Mario",
        "business_description": "Ristorante italiano nel centro di Roma",
        "sections": ["hero", "about", "menu", "contact", "footer"],
        "style_preferences": {"primary_color": "#dc2626", "mood": "elegant"}
    }
    ```
    """
    # Controlla limite generazioni
    if not current_user.has_remaining_generations:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Hai esaurito le generazioni gratuite",
                "generations_used": current_user.generations_used,
                "generations_limit": current_user.generations_limit,
                "upgrade_required": True
            }
        )
    
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
        
        # Incrementa contatore generazioni (se non è premium)
        if not current_user.is_premium and not current_user.is_superuser:
            current_user.generations_used += 1
            db.commit()
            logger.info(f"Generazione usata da user {current_user.id}: {current_user.generations_used}/{current_user.generations_limit}")
        
        # Aggiungi info quote alla risposta
        result["quota"] = {
            "generations_used": current_user.generations_used,
            "generations_limit": current_user.generations_limit,
            "remaining_generations": current_user.remaining_generations,
            "is_premium": current_user.is_premium,
        }
        
        return result
        
    except HTTPException:
        raise
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
async def test_generation(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
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
    
    # Riutilizza la logica principale con utente autenticato
    return await generate_website(test_request, current_user, db)


# ============ UPGRADE / PAYMENT ============

class UpgradeResponse(BaseModel):
    success: bool
    message: str
    is_premium: bool


@router.post("/upgrade", response_model=UpgradeResponse)
async def upgrade_to_premium(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade a premium (generazioni illimitate).
    
    NOTA: In produzione, questo endpoint riceverà il webhook di Stripe
    dopo il pagamento. Per ora è un endpoint di test.
    """
    try:
        current_user.is_premium = True
        db.commit()
        
        logger.info(f"User {current_user.id} upgraded to premium")
        
        return UpgradeResponse(
            success=True,
            message="Upgrade a premium completato! Ora hai generazioni illimitate.",
            is_premium=True
        )
    except Exception as e:
        logger.exception("Errore upgrade")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upgrade-demo")
async def upgrade_demo_user(
    db: Session = Depends(get_db)
):
    """
    Endpoint DEMO per testare l'upgrade senza pagamento.
    Trova l'ultimo utente creato e lo upgrade a premium.
    """
    from app.models.user import User
    
    user = db.query(User).order_by(User.id.desc()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Nessun utente trovato")
    
    user.is_premium = True
    db.commit()
    
    return {
        "message": f"Utente {user.email} upgradato a premium (DEMO)",
        "user_id": user.id,
        "is_premium": user.is_premium
    }
