"""
Routes per generazione AI siti web.
Include: generazione pipeline, refine via chat, status tracking, export.
La generazione gira in background (asyncio.create_task) per evitare
il timeout di 30s del proxy Render free tier.
"""

import asyncio
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.swarm_generator import swarm
from app.services.databinding_generator import databinding_generator
from app.services.ai_service import ai_service  # fallback
from app.core.database import get_db, SessionLocal
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.models.site import Site
from app.models.site_version import SiteVersion
from app.models.global_counter import GlobalCounter
from app.services.sanitizer import sanitize_output
from datetime import date
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generate", tags=["generation"])

# Import limiter dal modulo dedicato (evita import circolare con main.py)
from app.core.rate_limiter import limiter


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
    photo_urls: Optional[List[str]] = None  # List of base64 data URLs from user uploads


class RefineRequest(BaseModel):
    """Richiesta modifica sito via chat."""
    site_id: int
    message: str
    section: Optional[str] = None


class ImageAnalysisRequest(BaseModel):
    """Richiesta analisi immagine."""
    image_url: str


# ============ HELPER: Spending Cap ============

MAX_DAILY_GENERATIONS = 200  # ~$7/giorno massimo di spesa AI

def _check_and_increment_spending_cap(db: Session):
    """Verifica e incrementa il contatore globale giornaliero.
    Incrementa PRIMA della generazione per prevenire race condition.
    Ritorna True se ok, False se cap raggiunto."""
    today = date.today()
    counter = db.query(GlobalCounter).filter(GlobalCounter.date == today).first()

    if not counter:
        counter = GlobalCounter(date=today, daily_generations=0)
        db.add(counter)
        db.flush()

    if counter.daily_generations >= MAX_DAILY_GENERATIONS:
        return False

    counter.daily_generations += 1
    db.flush()
    return True


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

        def on_progress(step: int, message: str, preview_data: dict = None):
            if site:
                site.generation_step = step
                site.generation_message = message
                site.status = "generating"
                if preview_data:
                    site.config = {"_generation_preview": preview_data}
                db.commit()

        # Seleziona pipeline in base alla configurazione
        pipeline = settings.GENERATION_PIPELINE
        logger.info(f"[BG] Inizio generazione per user {user_id}, site {site_id}, pipeline={pipeline}")

        if pipeline == "n8n" and settings.N8N_WEBHOOK_URL:
            await _trigger_n8n_generation(request, site_id)
            return  # n8n chiamera' il callback quando finisce
        elif pipeline == "databinding":
            generator = databinding_generator
        else:
            generator = swarm  # fallback legacy

        result = await generator.generate(
            business_name=request.business_name,
            business_description=request.business_description,
            sections=request.sections,
            style_preferences=request.style_preferences,
            reference_image_url=request.reference_image_url,
            reference_analysis=request.reference_analysis,
            logo_url=request.logo_url,
            contact_info=request.contact_info,
            on_progress=on_progress,
            photo_urls=request.photo_urls,
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

        # Salva HTML, versione e site_data
        if site and result.get("html_content"):
            site.html_content = result["html_content"]
            site.status = "ready"
            site.generation_step = 0
            site.generation_message = ""
            if result.get("site_data"):
                site.config = json.dumps(result["site_data"]) if isinstance(result["site_data"], dict) else result["site_data"]
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
@limiter.limit("3/hour")
async def generate_website(
    request: Request,
    data: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Avvia generazione sito in background e ritorna subito.
    Il frontend fa polling su GET /api/generate/status/{site_id}.
    Rate limit: 3 generazioni per ora per IP.
    """
    # Controlla email verificata (obbligatorio per generare, skip per premium/superuser)
    if not getattr(current_user, 'email_verified', False) and not current_user.is_superuser and not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Verifica la tua email prima di generare un sito",
                "email_verification_required": True,
            },
        )

    # Controlla limite generazioni utente
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

    # Controlla spending cap globale (max 200 generazioni/giorno)
    if not _check_and_increment_spending_cap(db):
        logger.warning(f"Spending cap raggiunto! User {current_user.id} bloccato.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Il sistema ha raggiunto il limite giornaliero di generazioni. Riprova domani.",
        )

    # Imposta sito in stato "generating" subito
    site = None
    if data.site_id:
        site = db.query(Site).filter(
            Site.id == data.site_id,
            Site.owner_id == current_user.id,
        ).first()
        if site:
            site.status = "generating"
            site.generation_step = 0
            site.generation_message = "Avvio generazione..."
            db.commit()

    # Lancia generazione in background
    asyncio.create_task(
        _run_generation_background(data, current_user.id, data.site_id)
    )

    return {
        "success": True,
        "message": "Generazione avviata in background",
        "site_id": data.site_id,
        "status": "generating",
        "poll_url": f"/api/generate/status/{data.site_id}" if data.site_id else None,
    }


# ============ REFINE (CHAT) ============

@router.post("/refine")
@limiter.limit("10/hour")
async def refine_website(
    request: Request,
    data: RefineRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Modifica un sito esistente via chat AI.
    Carica l'HTML attuale, applica le modifiche richieste, salva nuova versione.
    Rate limit: 10 refinement per ora per IP.
    """
    # Controlla limite modifiche chat AI
    if not current_user.has_remaining_refines:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Hai esaurito le modifiche chat AI disponibili",
                "refines_used": current_user.refines_used,
                "refines_limit": current_user.refines_limit,
                "upgrade_required": True,
            },
        )

    # Carica il sito
    site = db.query(Site).filter(
        Site.id == data.site_id,
        Site.owner_id == current_user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Il sito non ha ancora contenuto HTML")

    try:
        result = await swarm.refine(
            current_html=site.html_content,
            modification_request=data.message,
            section_to_modify=data.section,
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Errore modifica"))

        # Aggiorna HTML del sito
        site.html_content = result["html_content"]
        site.status = "ready"

        # Incrementa contatore modifiche chat AI
        if not current_user.is_premium and not current_user.is_superuser:
            current_user.refines_used += 1

        # Salva versione
        description = f"Chat: {data.message[:100]}"
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
    total_steps = 4 if settings.GENERATION_PIPELINE == "databinding" else 3

    # Calcola percentuale
    if not is_generating:
        if site.status == "ready" or site.status == "published":
            percentage = 100
        else:
            percentage = 0
    else:
        percentage = int((step / total_steps) * 100)

    # Extract preview data if generating
    preview_data = None
    if is_generating and isinstance(site.config, dict):
        preview_data = site.config.get("_generation_preview")

    return {
        "site_id": site.id,
        "status": site.status,
        "is_generating": is_generating,
        "step": step,
        "total_steps": total_steps,
        "percentage": percentage,
        "message": site.generation_message or "",
        "preview_data": preview_data,
    }


# ============ IMAGE ANALYSIS ============

@router.post("/analyze-image")
@limiter.limit("10/hour")
async def analyze_image(request: Request, data: ImageAnalysisRequest):
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
            image_url=data.image_url,
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
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Endpoint di test con dati fittizi."""
    test_data = GenerateRequest(
        business_name="Caff\u00e8 Roma",
        business_description="Caff\u00e8 storico nel cuore di Roma, dal 1950. Specialit\u00e0 caff\u00e8 artigianale e cornetti freschi ogni mattina.",
        sections=["hero", "about", "menu", "gallery", "contact", "footer"],
        style_preferences={"primary_color": "#8B4513", "mood": "vintage, warm, welcoming"},
    )
    return await generate_website(request, test_data, current_user, db)


# ============ UPGRADE / PAYMENT ============

class UpgradeRequest(BaseModel):
    plan: str  # "base" o "premium"


@router.post("/upgrade")
async def upgrade_plan(
    data: UpgradeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Attiva un piano dopo il pagamento. Accetta 'base' o 'premium'."""
    from app.models.user import PLAN_CONFIG
    if data.plan not in PLAN_CONFIG or data.plan == "free":
        raise HTTPException(
            status_code=400,
            detail=f"Piano '{data.plan}' non valido. Scegli 'base' o 'premium'.",
        )

    try:
        current_user.activate_plan(data.plan)
        db.commit()

        config = PLAN_CONFIG[data.plan]
        logger.info(f"User {current_user.id} upgraded to plan '{data.plan}'")

        return {
            "success": True,
            "message": f"Piano {config['label']} attivato!",
            "plan": data.plan,
            "plan_label": config["label"],
            "generations_limit": config["generations_limit"],
            "refines_limit": config["refines_limit"],
            "pages_limit": config["pages_limit"],
            "can_publish": config["can_publish"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Errore upgrade")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upgrade-demo")
async def upgrade_demo_user(plan: str = "premium", db: Session = Depends(get_db)):
    """Endpoint DEMO per testare l'upgrade senza pagamento."""
    user = db.query(User).order_by(User.id.desc()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Nessun utente trovato")

    try:
        user.activate_plan(plan)
    except ValueError:
        user.is_premium = True
    db.commit()

    return {
        "message": f"Utente {user.email} upgradato a piano '{user.plan}' (DEMO)",
        "user_id": user.id,
        "plan": user.plan,
        "generations_limit": user.generations_limit,
        "refines_limit": user.refines_limit,
        "pages_limit": user.pages_limit,
    }


# ============ N8N INTEGRATION ============

class N8nProgressRequest(BaseModel):
    site_id: int
    step: int
    message: str
    secret: str
    preview_data: Optional[Dict[str, Any]] = None


class N8nCallbackRequest(BaseModel):
    site_id: int
    html_content: Optional[str] = None
    site_data: Optional[Dict[str, Any]] = None
    generation_time_ms: Optional[int] = None
    secret: str


def _verify_n8n_secret(secret: str):
    """Verifica shared secret per callback n8n."""
    if not settings.N8N_CALLBACK_SECRET:
        raise HTTPException(status_code=503, detail="n8n integration not configured")
    if secret != settings.N8N_CALLBACK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid callback secret")


@router.post("/n8n-progress")
async def n8n_progress_update(
    data: N8nProgressRequest,
    db: Session = Depends(get_db),
):
    """Riceve aggiornamenti progress da n8n durante la generazione."""
    _verify_n8n_secret(data.secret)

    site = db.query(Site).filter(Site.id == data.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    site.generation_step = data.step
    site.generation_message = data.message
    if data.preview_data:
        site.config = {"_generation_preview": data.preview_data}
    db.commit()

    return {"success": True}


@router.post("/n8n-callback")
async def n8n_generation_callback(
    data: N8nCallbackRequest,
    db: Session = Depends(get_db),
):
    """Riceve risultato da n8n. Se site_data presente senza html, assembla automaticamente."""
    _verify_n8n_secret(data.secret)

    site = db.query(Site).filter(Site.id == data.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Auto-assembly: se solo site_data, assembla HTML con TemplateAssembler
    if not data.html_content and data.site_data:
        from app.services.template_assembler import assembler
        try:
            html_content = assembler.assemble(data.site_data)
            html_content = sanitize_output(html_content)
        except Exception as e:
            logger.error(f"[n8n] Assembly failed for site {data.site_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Assembly failed: {str(e)}")
    elif data.html_content:
        html_content = sanitize_output(data.html_content)
    else:
        raise HTTPException(status_code=400, detail="Either html_content or site_data required")

    site.html_content = html_content
    site.status = "ready"
    site.generation_step = 0
    site.generation_message = ""

    if data.site_data:
        site.config = json.dumps(data.site_data) if isinstance(data.site_data, dict) else data.site_data

    _save_version(db, site, html_content, "Generazione via n8n")

    # Incrementa contatore generazioni per il proprietario
    user = db.query(User).filter(User.id == site.owner_id).first()
    if user and not user.is_premium and not user.is_superuser:
        user.generations_used += 1

    db.commit()

    logger.info(f"[n8n] Callback ricevuto per site {data.site_id}, {len(html_content)} chars")
    return {"success": True, "site_id": data.site_id}


async def _trigger_n8n_generation(request: GenerateRequest, site_id: int):
    """Invia richiesta generazione al webhook n8n."""
    import httpx

    payload = {
        "site_id": site_id,
        "business_name": request.business_name,
        "business_description": request.business_description,
        "sections": request.sections,
        "style_preferences": request.style_preferences,
        "reference_image_url": request.reference_image_url,
        "logo_url": request.logo_url,
        "contact_info": request.contact_info,
        "callback_url": f"{settings.RENDER_EXTERNAL_URL}/api/generate/n8n-callback",
        "progress_url": f"{settings.RENDER_EXTERNAL_URL}/api/generate/n8n-progress",
        "secret": settings.N8N_CALLBACK_SECRET,
        "moonshot_api_key": settings.active_api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(settings.N8N_WEBHOOK_URL, json=payload)
            logger.info(f"[n8n] Webhook triggered for site {site_id}, status={resp.status_code}")
    except Exception as e:
        logger.error(f"[n8n] Failed to trigger webhook: {e}")
