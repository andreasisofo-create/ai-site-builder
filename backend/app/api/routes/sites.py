"""Routes per gestione siti"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.site import Site

router = APIRouter()


@router.get("/")
async def list_sites(db: Session = Depends(get_db)):
    """Lista tutti i siti"""
    sites = db.query(Site).all()
    return sites


@router.post("/")
async def create_site(name: str, slug: str, db: Session = Depends(get_db)):
    """Crea un nuovo sito"""
    # Verifica slug unico
    existing = db.query(Site).filter(Site.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug già in uso")
    
    site = Site(name=name, slug=slug)
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/{site_id}")
async def get_site(site_id: int, db: Session = Depends(get_db)):
    """Ottiene un sito specifico"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    return site


@router.put("/{site_id}")
async def update_site(site_id: int, name: str = None, config: dict = None, db: Session = Depends(get_db)):
    """Aggiorna un sito"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    if name:
        site.name = name
    if config:
        site.config = config
    
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}")
async def delete_site(site_id: int, db: Session = Depends(get_db)):
    """Elimina un sito"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    db.delete(site)
    db.commit()
    return {"message": "Sito eliminato"}
