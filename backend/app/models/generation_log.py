"""GenerationLog model - tracks generated site compositions for diversity"""

import uuid

from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Generation context
    category = Column(Text, nullable=False)
    style_mood = Column(Text)
    color_primary = Column(Text)
    client_ref = Column(Text)
    style_dna = Column(JSONB)

    # Composition
    components_used = Column(JSONB, nullable=False)
    layout_hash = Column(Text, nullable=False, unique=True)

    # Relationship to individual component usages
    component_entries = relationship("GenerationLogComponent", back_populates="generation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GenerationLog {self.category} hash={self.layout_hash[:12]}>"
