"""Modello Sito Web"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class SiteStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    PUBLISHED = "published"


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    
    # Configurazione sito
    template = Column(String, default="default")
    config = Column(JSON, default=dict)
    custom_css = Column(Text)
    custom_js = Column(Text)
    
    # Stato
    status = Column(String, default=SiteStatus.DRAFT.value)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True))
    
    # Preview
    thumbnail = Column(String)
    html_content = Column(Text)  # HTML generato dall'AI
    
    # Deploy
    vercel_project_id = Column(String)
    domain = Column(String)
    
    # Relazioni
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", backref="sites")
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
