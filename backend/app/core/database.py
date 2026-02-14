"""Database configuration"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Supporta sia PostgreSQL che SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL - use SSL if not already specified in URL
    connect_args = {}
    if "sslmode" not in settings.DATABASE_URL:
        connect_args["sslmode"] = "require"
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=300,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency per ottenere la sessione DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
