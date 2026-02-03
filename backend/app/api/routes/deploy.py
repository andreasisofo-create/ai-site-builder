"""Routes per deploy su Vercel"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
import json

from app.core.database import get_db
from app.core.config import settings
from app.models.site import Site

router = APIRouter()

VERCEL_API = "https://api.vercel.com"


@router.post("/preview/{site_id}")
async def deploy_preview(site_id: int, db: Session = Depends(get_db)):
    """Crea un deploy di preview su Vercel"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    headers = {"Authorization": f"Bearer {settings.VERCEL_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        # Qui andrebbe la logica per generare i file e deployarli
        # Per ora restituiamo un mock
        pass
    
    return {"message": "Deploy preview creato", "url": f"https://{site.slug}-preview.vercel.app"}


@router.post("/production/{site_id}")
async def deploy_production(site_id: int, db: Session = Depends(get_db)):
    """Deploy in produzione su Vercel"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    return {"message": "Deploy produzione creato", "url": f"https://{site.slug}.vercel.app"}


@router.get("/status/{site_id}")
async def deploy_status(site_id: int, db: Session = Depends(get_db)):
    """Stato del deploy"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    return {
        "site_id": site_id,
        "is_published": site.is_published,
        "domain": site.domain,
        "vercel_project_id": site.vercel_project_id,
    }
