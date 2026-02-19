"""CategoryBlueprint model - defines section structure per category"""

import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.sql import func

from app.core.database import Base


class CategoryBlueprint(Base):
    __tablename__ = "category_blueprints"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())

    # Category identity
    category_slug = Column(Text, unique=True, nullable=False)
    category_name = Column(Text, nullable=False)

    # Section rules
    sections_required = Column(ARRAY(Text), default=list)
    sections_optional = Column(ARRAY(Text), default=list)
    sections_forbidden = Column(ARRAY(Text), default=list)

    # Style defaults
    default_variant_cluster = Column(Text)
    mood_required = Column(ARRAY(Text), default=list)
    mood_forbidden = Column(ARRAY(Text), default=list)
    style_names = Column(ARRAY(Text), default=list)

    def __repr__(self):
        return f"<CategoryBlueprint {self.category_slug}>"
