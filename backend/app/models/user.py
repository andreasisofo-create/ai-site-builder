"""Modello Utente"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # NULL per OAuth
    full_name = Column(String)
    avatar_url = Column(String)  # URL immagine profilo (Google)
    
    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', etc.
    oauth_id = Column(String, nullable=True, unique=True, index=True)  # ID esterno OAuth
    
    # Subscription & Generations
    is_premium = Column(Boolean, default=False)  # Ha pagato per generazioni illimitate
    generations_used = Column(Integer, default=0)  # Quante generazioni ha fatto
    generations_limit = Column(Integer, default=2)  # Limite gratuito (2)
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def has_remaining_generations(self) -> bool:
        """Controlla se l'utente ha ancora generazioni disponibili."""
        if self.is_premium or self.is_superuser:
            return True
        return self.generations_used < self.generations_limit
    
    @property
    def remaining_generations(self) -> int:
        """Ritorna il numero di generazioni rimanenti."""
        if self.is_premium or self.is_superuser:
            return -1  # Illimitate
        return max(0, self.generations_limit - self.generations_used)
