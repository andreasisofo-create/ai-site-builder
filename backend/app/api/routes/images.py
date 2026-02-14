"""
Routes per generazione immagini AI.
Usa Flux via fal.ai per generare immagini contestuali
per le sezioni del sito.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.rate_limiter import limiter
from app.models.user import User
from app.models.site import Site

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ SCHEMAS ============

class GenerateImagesRequest(BaseModel):
    """Richiesta generazione immagini per una sezione."""
    business_name: str
    business_description: str
    section_type: str
    style_mood: str
    color_palette: Optional[Dict[str, str]] = None
    count: Optional[int] = None
    quality: Optional[str] = "fast"  # "fast" (schnell $0.025) or "quality" (pro $0.04)


class RegenerateImagesRequest(BaseModel):
    """Richiesta rigenerazione immagini da editor."""
    site_id: int
    section_type: str
    quality: Optional[str] = "fast"


class ImagesResponse(BaseModel):
    images: List[str]
    section_type: str
    count: int


# ============ ENDPOINTS ============

@router.post("/generate", response_model=ImagesResponse)
@limiter.limit("5/minute")
async def generate_images(
    request: Request,
    data: GenerateImagesRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Genera immagini AI per una sezione specifica.
    Rate limit: 5 richieste/minuto per IP.
    Richiede autenticazione.
    """
    from app.services.image_generator import (
        generate_section_images,
        SECTION_IMAGE_COUNTS,
    )

    # Validazione section_type
    valid_sections = [
        "hero", "about", "gallery", "services", "features",
        "team", "testimonials", "portfolio", "contact", "cta",
        "blog", "event",
    ]
    if data.section_type not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo sezione non valido: '{data.section_type}'. "
                   f"Sezioni supportate: {', '.join(valid_sections)}",
        )

    # Validazione quality
    if data.quality not in ("fast", "quality"):
        raise HTTPException(
            status_code=400,
            detail="Qualita' non valida. Usa 'fast' o 'quality'.",
        )

    count = data.count or SECTION_IMAGE_COUNTS.get(data.section_type, 1)

    try:
        urls = await generate_section_images(
            business_name=data.business_name,
            business_description=data.business_description,
            section_type=data.section_type,
            style_mood=data.style_mood,
            color_palette=data.color_palette,
            count=count,
            quality=data.quality,
        )

        return ImagesResponse(
            images=urls,
            section_type=data.section_type,
            count=len(urls),
        )

    except Exception as e:
        logger.exception(f"Errore generazione immagini per sezione '{data.section_type}'")
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la generazione delle immagini: {str(e)}",
        )


@router.post("/regenerate", response_model=ImagesResponse)
@limiter.limit("5/minute")
async def regenerate_images(
    request: Request,
    data: RegenerateImagesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Rigenera immagini per una sezione di un sito esistente.
    Recupera le info del business dal DB e genera nuove immagini.
    Rate limit: 5 richieste/minuto per IP.
    Richiede autenticazione + proprieta del sito.
    """
    from app.services.image_generator import (
        generate_section_images,
        SECTION_IMAGE_COUNTS,
    )

    # Verifica proprieta del sito
    site = db.query(Site).filter(
        Site.id == data.site_id,
        Site.owner_id == current_user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    # Estrai info business dalla config del sito
    config = site.config or {}
    business_name = config.get("business_name") or site.name
    business_description = config.get("business_description") or site.description or ""
    style_mood = config.get("style_mood") or config.get("style_preferences", {}).get("mood", "modern")

    color_palette = None
    theme = config.get("theme", {})
    if theme and theme.get("primary_color"):
        color_palette = {
            "primary_color": theme.get("primary_color", ""),
            "secondary_color": theme.get("secondary_color", ""),
        }

    # Validazione section_type
    valid_sections = [
        "hero", "about", "gallery", "services", "features",
        "team", "testimonials", "portfolio", "contact", "cta",
        "blog", "event",
    ]
    if data.section_type not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo sezione non valido: '{data.section_type}'. "
                   f"Sezioni supportate: {', '.join(valid_sections)}",
        )

    # Validazione quality
    if data.quality not in ("fast", "quality"):
        raise HTTPException(
            status_code=400,
            detail="Qualita' non valida. Usa 'fast' o 'quality'.",
        )

    count = SECTION_IMAGE_COUNTS.get(data.section_type, 1)

    try:
        urls = await generate_section_images(
            business_name=business_name,
            business_description=business_description,
            section_type=data.section_type,
            style_mood=style_mood,
            color_palette=color_palette,
            count=count,
            quality=data.quality,
        )

        return ImagesResponse(
            images=urls,
            section_type=data.section_type,
            count=len(urls),
        )

    except Exception as e:
        logger.exception(f"Errore rigenerazione immagini per sito {data.site_id}, sezione '{data.section_type}'")
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la rigenerazione delle immagini: {str(e)}",
        )
