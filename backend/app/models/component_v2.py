"""ComponentV2 model - 5-cluster variant system with pgvector embeddings"""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ComponentV2(Base):
    __tablename__ = "components_v2"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Identity
    name = Column(Text, nullable=False, unique=True)
    section_type = Column(Text, nullable=False)
    variant_cluster = Column(Text, nullable=False)

    # Category compatibility
    compatible_categories = Column(ARRAY(Text), default=list)
    incompatible_categories = Column(ARRAY(Text), default=list)
    is_special = Column(Boolean, default=False, server_default="false")

    # Style metadata
    mood_tags = Column(ARRAY(Text), default=list)
    density = Column(Text)  # "minimal" | "balanced" | "dense"
    typography_style = Column(Text)  # "serif" | "sans" | "display" | "mixed"
    has_video = Column(Boolean, default=False, server_default="false")
    has_slider = Column(Boolean, default=False, server_default="false")
    animation_level = Column(Text, default="moderate", server_default="moderate")

    # Content
    html_code = Column(Text, nullable=False)
    css_variables = Column(JSONB, default=dict)
    placeholders = Column(ARRAY(Text), default=list)
    gsap_effects = Column(ARRAY(Text), default=list)

    # Usage tracking / cooldown
    usage_count = Column(Integer, default=0, server_default="0")
    last_used_at = Column(DateTime(timezone=True))
    cooldown_until = Column(DateTime(timezone=True))

    # Vector embedding (768-dim for text-embedding-004)
    embedding = Column(Vector(768))

    # Metadata
    preview_url = Column(Text)
    reference_source = Column(Text)
    notes = Column(Text)

    __table_args__ = (
        Index("ix_components_v2_section_type", "section_type"),
        Index("ix_components_v2_compatible_categories", "compatible_categories", postgresql_using="gin"),
        Index("ix_components_v2_cooldown_until", "cooldown_until"),
        Index(
            "ix_components_v2_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    def __repr__(self):
        return f"<ComponentV2 {self.name} [{self.section_type}/{self.variant_cluster}]>"
