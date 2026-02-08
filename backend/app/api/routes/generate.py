"""
Routes per generazione AI siti web.
Include: generazione pipeline, refine via chat, status tracking, export.
La generazione gira in background (asyncio.create_task) per evitare
il timeout di 30s del proxy Render free tier.
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.swarm_generator import swarm
from app.services.ai_service import ai_service  # fallback
from app.core.database import get_db, SessionLocal
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


# ============ BACKGROUND GENERATION TASK ============

async def _run_generation_background(
    request: GenerateRequest,
    user_id: int,
    site_id: int | None,
):
    """
    Esegue la generazione in background con una sessione DB propria.
    Necessario per evitare il timeout di 30s del proxy Render free tier.
    """
    db = SessionLocal()
    try:
        site = None
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"[BG] User {user_id} non trovato")
            return

        if site_id:
            site = db.query(Site).filter(Site.id == site_id, Site.owner_id == user_id).first()

        def on_progress(step: int, message: str):
            if site:
                site.generation_step = step
                site.generation_message = message
                site.status = "generating"
                db.commit()

        logger.info(f"[BG] Inizio generazione per user {user_id}, site {site_id}")

        result = await swarm.generate(
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
            logger.error(f"[BG] Generazione fallita: {result.get('error')}")
            if site:
                site.generation_step = 0
                site.generation_message = result.get("error", "Errore generazione")
                site.status = "draft"
                db.commit()
            return

        # Incrementa contatore generazioni
        if not user.is_premium and not user.is_superuser:
            user.generations_used += 1

        # Salva HTML e versione
        if site and result.get("html_content"):
            site.html_content = result["html_content"]
            site.status = "ready"
            site.generation_step = 0
            site.generation_message = ""
            _save_version(db, site, result["html_content"], "Generazione iniziale AI")

        db.commit()
        logger.info(
            f"[BG] Generazione completata per user {user_id}: "
            f"{result.get('generation_time_ms')}ms, ${result.get('cost_usd')}"
        )

    except Exception as e:
        logger.exception(f"[BG] Errore generazione background")
        if site_id:
            try:
                site = db.query(Site).filter(Site.id == site_id).first()
                if site:
                    site.generation_step = 0
                    site.generation_message = str(e)[:200]
                    site.status = "draft"
                    db.commit()
            except Exception:
                pass
    finally:
        db.close()


# ============ GENERATION ENDPOINTS ============

@router.post("/website")
async def generate_website(
    request: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Avvia generazione sito in background e ritorna subito.
    Il frontend fa polling su GET /api/generate/status/{site_id}.
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

    # Imposta sito in stato "generating" subito
    site = None
    if request.site_id:
        site = db.query(Site).filter(
            Site.id == request.site_id,
            Site.owner_id == current_user.id,
        ).first()
        if site:
            site.status = "generating"
            site.generation_step = 0
            site.generation_message = "Avvio generazione..."
            db.commit()

    # Lancia generazione in background
    asyncio.create_task(
        _run_generation_background(request, current_user.id, request.site_id)
    )

    return {
        "success": True,
        "message": "Generazione avviata in background",
        "site_id": request.site_id,
        "status": "generating",
        "poll_url": f"/api/generate/status/{request.site_id}" if request.site_id else None,
    }


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
        result = await swarm.refine(
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
    from app.services.kimi_client import kimi

    prompt = """Analyze this website screenshot and describe:
1. Color palette (primary, secondary, accent colors in hex format)
2. Typography style (modern, classic, bold, minimal, elegant)
3. Layout structure (clean, busy, grid-based, fluid, centered)
4. Overall mood/atmosphere (professional, playful, elegant, corporate, cozy)
5. Key design elements that stand out

Be specific and concise. Format as a structured list."""

    try:
        result = await kimi.call_with_image(
            prompt=prompt,
            image_url=request.image_url,
            max_tokens=1500,
            thinking=True,
            timeout=90.0,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

        return {
            "success": True,
            "analysis": result["content"],
            "tokens_used": result.get("tokens_input", 0) + result.get("tokens_output", 0),
            "cost_usd": kimi.calculate_cost(
                result.get("tokens_input", 0),
                result.get("tokens_output", 0),
            ),
        }

    except HTTPException:
        raise
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
