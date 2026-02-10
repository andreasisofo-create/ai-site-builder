"""Routes per gestione siti"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from pydantic import BaseModel, field_serializer

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.site import Site, SiteStatus
from app.models.site_version import SiteVersion
from app.models.user import User

router = APIRouter()


# ============ SCHEMAS ============

class SiteCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    template: Optional[str] = "default"


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    status: Optional[str] = None
    html_content: Optional[str] = None
    thumbnail: Optional[str] = None
    is_published: Optional[bool] = None


class SiteResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    status: str
    is_published: bool
    thumbnail: Optional[str]
    created_at: Any
    updated_at: Optional[Any] = None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, val: Any) -> Optional[str]:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val.isoformat()
        return str(val)

    class Config:
        from_attributes = True


class SiteDetailResponse(SiteResponse):
    """Response con html_content incluso (per editor/singolo sito)."""
    html_content: Optional[str] = None


# ============ ROUTES ============

@router.get("/", response_model=List[SiteResponse])
async def list_sites(
    status: Optional[str] = Query(None, description="Filtra per stato"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lista siti dell'utente corrente"""
    query = db.query(Site).filter(Site.owner_id == current_user.id)
    
    if status:
        query = query.filter(Site.status == status)
    
    sites = query.order_by(Site.updated_at.desc()).all()
    return sites


@router.post("/", response_model=SiteResponse)
async def create_site(
    data: SiteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crea un nuovo sito"""
    # Verifica slug unico
    existing = db.query(Site).filter(Site.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug già in uso")
    
    site = Site(
        name=data.name,
        slug=data.slug,
        description=data.description,
        template=data.template,
        owner_id=current_user.id,
        status=SiteStatus.DRAFT.value
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/{site_id}", response_model=SiteDetailResponse)
async def get_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ottiene un sito specifico (solo se proprietario)"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    return site


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    data: SiteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Aggiorna un sito"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    # Aggiorna i campi forniti
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)
    
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}")
async def delete_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Elimina un sito"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    db.query(SiteVersion).filter(SiteVersion.site_id == site_id).delete()
    db.delete(site)
    db.commit()
    return {"message": "Sito eliminato"}


@router.post("/{site_id}/generate")
async def update_site_html(
    site_id: int,
    html_content: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Aggiorna l'HTML generato di un sito"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    site.html_content = html_content
    site.status = SiteStatus.READY.value
    db.commit()
    db.refresh(site)
    return {"message": "HTML aggiornato", "site": site}


@router.get("/{site_id}/preview")
async def preview_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ottiene l'HTML preview di un sito"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Sito non ancora generato")

    return {
        "html": site.html_content,
        "name": site.name,
        "status": site.status
    }


@router.get("/{site_id}/export")
async def export_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Scarica il file HTML completo del sito."""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Sito non ancora generato")

    # Aggiungi meta commento
    html = site.html_content
    meta_comment = f"<!-- Generated by E-quipe AI Site Builder | {site.name} -->\n"
    if not html.startswith("<!--"):
        html = meta_comment + html

    filename = f"{site.slug}.html"

    return Response(
        content=html,
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
