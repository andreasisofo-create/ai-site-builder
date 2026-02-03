"""Routes per gestione componenti"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.component import Component, ComponentType

router = APIRouter()


@router.get("/site/{site_id}")
async def list_components(site_id: int, db: Session = Depends(get_db)):
    """Lista componenti di un sito"""
    components = db.query(Component).filter(Component.site_id == site_id).order_by(Component.order).all()
    return components


@router.post("/")
async def create_component(
    site_id: int,
    name: str,
    type: ComponentType,
    content: dict = None,
    styles: dict = None,
    db: Session = Depends(get_db)
):
    """Crea un nuovo componente"""
    component = Component(
        site_id=site_id,
        name=name,
        type=type,
        content=content or {},
        styles=styles or {},
    )
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


@router.put("/{component_id}")
async def update_component(
    component_id: int,
    content: dict = None,
    styles: dict = None,
    html: str = None,
    css: str = None,
    is_visible: bool = None,
    db: Session = Depends(get_db)
):
    """Aggiorna un componente"""
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Componente non trovato")
    
    if content is not None:
        component.content = content
    if styles is not None:
        component.styles = styles
    if html is not None:
        component.html = html
    if css is not None:
        component.css = css
    if is_visible is not None:
        component.is_visible = is_visible
    
    db.commit()
    db.refresh(component)
    return component


@router.delete("/{component_id}")
async def delete_component(component_id: int, db: Session = Depends(get_db)):
    """Elimina un componente"""
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Componente non trovato")
    
    db.delete(component)
    db.commit()
    return {"message": "Componente eliminato"}
