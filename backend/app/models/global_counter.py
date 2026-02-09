"""Modello contatore globale per spending cap anti-abuse."""

from sqlalchemy import Column, Integer, Date
from sqlalchemy.sql import func

from app.core.database import Base


class GlobalCounter(Base):
    __tablename__ = "global_counters"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, server_default=func.current_date())
    daily_generations = Column(Integer, default=0, nullable=False)
