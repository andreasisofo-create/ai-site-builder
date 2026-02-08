"""Modello Versione Sito - salva snapshot HTML ad ogni generazione/refine"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SiteVersion(Base):
    __tablename__ = "site_versions"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    html_content = Column(Text, nullable=False)
    version_number = Column(Integer, nullable=False)
    change_description = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni
    site = relationship("Site", backref="versions")
