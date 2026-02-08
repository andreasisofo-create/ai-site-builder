"""
Routes per generazione AI siti web.
Include: generazione pipeline, refine via chat, status tracking, export.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.ai_service import ai_service
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.site import Site
from app.models.site_version import SiteVersion
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generate", tags=["generation"])


# ============ SCHEMAS ============

class GenerateRequest(BaseModel):
    """Richiesta generazione sito."""
    business_name: str
    business_description: str
    sections: List[str] = ["hero", "about", "services", "contact", "footer"]
    style_preferences: Optional[Dict[str, Any]] = None
    reference_analysis: Optional[str] = None
    reference_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None
    site_id: Optional[int] = None  # Se fornito, salva direttamente sul sito


class RefineRequest(BaseModel):
    """Richiesta modifica sito via chat."""
    site_id: int
    message: str
    section: Optional[str] = None


class ImageAnalysisRequest(BaseModel):
    """Richiesta analisi immagine."""
    image_url: str


# ============ HELPER: Save Version ============

def _save_version(db: Session, site: Site, html_content: str, description: str):
    """Salva una nuova versione del sito. Mantiene max 10 versioni."""
    # Trova il numero di versione più alto
    latest = (
        db.query(SiteVersion)
        .filter(SiteVersion.site_id == site.id)
        .order_by(SiteVersion.version_number.desc())
        .first()
    )
    next_version = (latest.version_number + 1) if latest else 1

    version = SiteVersion(
        site_id=site.id,
        html_content=html_content,
        version_number=next_version,
        change_description=description,
    )
    db.add(version)

    # Elimina versioni vecchie (mantieni max 10)
    versions = (
        db.query(SiteVersion)
        .filter(SiteVersion.site_id == site.id)
        .order_by(SiteVersion.version_number.desc())
        .offset(10)
        .all()
    )
    for old_version in versions:
        db.delete(old_version)

    db.flush()


# ============ GENERATION ENDPOINTS ============

@router.post("/website")
async def generate_website(
    request: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Genera un sito web completo usando AI pipeline a 3 step.
    Richiede autenticazione. Controlla il limite di generazioni gratuite.
    """
    # Controlla limite generazioni
    if not current_user.has_remaining_generations:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Hai esaurito le generazioni gratuite",
                "generations_used": current_user.generations_used,
                "generations_limit": current_user.generations_limit,
                "upgrade_required": True,
            },
        )

    # Se site_id fornito, aggiorna il progresso sul sito
    site = None
    if request.site_id:
        site = db.query(Site).filter(
            Site.id == request.site_id,
            Site.owner_id == current_user.id,
        ).first()

    def on_progress(step: int, message: str):
        """Callback per aggiornare progresso generazione sul DB."""
        if site:
            site.generation_step = step
            site.generation_message = message
            site.status = "generating"
            db.commit()

    try:
        result = await ai_service.generate_website_pipeline(
            business_name=request.business_name,
            business_description=request.business_description,
            sections=request.sections,
            style_preferences=request.style_preferences,
            reference_image_url=request.reference_image_url,
            reference_analysis=request.reference_analysis,
            logo_url=request.logo_url,
            contact_info=request.contact_info,
            on_progress=on_progress,
        )

        if not result.get("success"):
            # Reset progress on failure
            if site:
                site.generation_step = 0
                site.generation_message = ""
                site.status = "draft"
                db.commit()
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

        # Incrementa contatore generazioni (se non è premium)
        if not current_user.is_premium and not current_user.is_superuser:
            current_user.generations_used += 1

        # Se site_id fornito, salva HTML e versione
        if site and result.get("html_content"):
            site.html_content = result["html_content"]
            site.status = "ready"
            site.generation_step = 0
            site.generation_message = ""
            _save_version(db, site, result["html_content"], "Generazione iniziale AI")

        db.commit()

        logger.info(
            f"Generazione pipeline completata per user {current_user.id}: "
            f"{current_user.generations_used}/{current_user.generations_limit}"
        )

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
        if site:
            site.generation_step = 0
            site.generation_message = ""
            site.status = "draft"
            db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ============ REFINE (CHAT) ============

@router.post("/refine")
async def refine_website(
    request: RefineRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Modifica un sito esistente via chat AI.
    Carica l'HTML attuale, applica le modifiche richieste, salva nuova versione.
    """
    # Carica il sito
    site = db.query(Site).filter(
        Site.id == request.site_id,
        Site.owner_id == current_user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Il sito non ha ancora contenuto HTML")

    try:
        result = await ai_service.refine_page(
            current_html=site.html_content,
            modification_request=request.message,
            section_to_modify=request.section,
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Errore modifica"))

        # Aggiorna HTML del sito
        site.html_content = result["html_content"]
        site.status = "ready"

        # Salva versione
        description = f"Chat: {request.message[:100]}"
        _save_version(db, site, result["html_content"], description)

        db.commit()

        return {
            "success": True,
            "html_content": result["html_content"],
            "model_used": result.get("model_used"),
            "generation_time_ms": result.get("generation_time_ms"),
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Errore refine sito")
        raise HTTPException(status_code=500, detail=str(e))


# ============ STATUS (PROGRESS TRACKING) ============

@router.get("/status/{site_id}")
async def get_generation_status(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ritorna lo stato di avanzamento della generazione per un sito."""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    is_generating = site.status == "generating"
    step = site.generation_step if is_generating else 0
    total_steps = 3

    # Calcola percentuale
    if not is_generating:
        if site.status == "ready" or site.status == "published":
            percentage = 100
        else:
            percentage = 0
    else:
        percentage = int((step / total_steps) * 100)

    return {
        "site_id": site.id,
        "status": site.status,
        "is_generating": is_generating,
        "step": step,
        "total_steps": total_steps,
        "percentage": percentage,
        "message": site.generation_message or "",
    }


# ============ IMAGE ANALYSIS ============

@router.post("/analyze-image")
async def analyze_image(request: ImageAnalysisRequest):
    """Analizza un'immagine di riferimento per estrarre stile."""
    try:
        result = await ai_service.analyze_image_style(request.image_url)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

        return result

    except Exception as e:
        logger.exception("Errore analisi immagine")
        raise HTTPException(status_code=500, detail=str(e))


# ============ TEST ============

@router.post("/test")
async def test_generation(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Endpoint di test con dati fittizi."""
    test_request = GenerateRequest(
        business_name="Caff\u00e8 Roma",
        business_description="Caff\u00e8 storico nel cuore di Roma, dal 1950. Specialit\u00e0 caff\u00e8 artigianale e cornetti freschi ogni mattina.",
        sections=["hero", "about", "menu", "gallery", "contact", "footer"],
        style_preferences={"primary_color": "#8B4513", "mood": "vintage, warm, welcoming"},
    )
    return await generate_website(test_request, current_user, db)


# ============ UPGRADE / PAYMENT ============

class UpgradeResponse(BaseModel):
    success: bool
    message: str
    is_premium: bool


@router.post("/upgrade", response_model=UpgradeResponse)
async def upgrade_to_premium(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upgrade a premium (generazioni illimitate)."""
    try:
        current_user.is_premium = True
        db.commit()

        logger.info(f"User {current_user.id} upgraded to premium")

        return UpgradeResponse(
            success=True,
            message="Upgrade a premium completato! Ora hai generazioni illimitate.",
            is_premium=True,
        )
    except Exception as e:
        logger.exception("Errore upgrade")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upgrade-demo")
async def upgrade_demo_user(db: Session = Depends(get_db)):
    """Endpoint DEMO per testare l'upgrade senza pagamento."""
    user = db.query(User).order_by(User.id.desc()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Nessun utente trovato")

    user.is_premium = True
    db.commit()

    return {
        "message": f"Utente {user.email} upgradato a premium (DEMO)",
        "user_id": user.id,
        "is_premium": user.is_premium,
    }
