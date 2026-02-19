"""GenerationLogComponent model - junction table linking generations to components"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GenerationLogComponent(Base):
    __tablename__ = "generation_log_components"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    generation_id = Column(PG_UUID(as_uuid=True), ForeignKey("generation_logs.id", ondelete="CASCADE"), nullable=False)
    component_id = Column(PG_UUID(as_uuid=True), ForeignKey("components_v2.id"), nullable=True)
    section_type = Column(Text)
    category = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    generation = relationship("GenerationLog", back_populates="component_entries")
    # ComponentV2 relationship only available when pgvector is installed
    try:
        from app.models.component_v2 import ComponentV2 as _CV2  # noqa: F401
        component = relationship("ComponentV2")
    except ImportError:
        pass

    __table_args__ = (
        Index("ix_gen_log_comp_component_id", "component_id"),
        Index("ix_gen_log_comp_section_category", "section_type", "category"),
    )

    def __repr__(self):
        return f"<GenerationLogComponent gen={self.generation_id} comp={self.component_id}>"
