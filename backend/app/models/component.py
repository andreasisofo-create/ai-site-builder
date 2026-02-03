"""Modello Componente UI"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ComponentType(str, enum.Enum):
    HERO = "hero"
    NAVBAR = "navbar"
    FOOTER = "footer"
    FEATURES = "features"
    PRICING = "pricing"
    TESTIMONIALS = "testimonials"
    CTA = "cta"
    FAQ = "faq"
    CONTACT = "contact"
    GALLERY = "gallery"
    TEXT = "text"
    IMAGE = "image"
    BUTTON = "button"
    CUSTOM = "custom"


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(ComponentType), nullable=False)
    
    # Contenuto
    content = Column(JSON, default=dict)  # Testi, immagini, link
    styles = Column(JSON, default=dict)   # Colori, spaziature, font
    
    # Codice (per componenti custom)
    html = Column(Text)
    css = Column(Text)
    js = Column(Text)
    
    # Posizionamento
    order = Column(Integer, default=0)
    section_id = Column(String)  # ID sezione nel sito
    
    # Stato
    is_visible = Column(Boolean, default=True)
    
    # Relazioni
    site_id = Column(Integer, ForeignKey("sites.id"))
    site = relationship("Site", backref="components")
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
