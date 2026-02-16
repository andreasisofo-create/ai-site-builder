"""Modello Utente"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime, timezone

from app.core.database import Base

# ============ PIANI E LIMITI ============
# Pagamenti una tantum, NON abbonamenti mensili.
#
# Starter (gratis):  1 generazione, 3 modifiche chat, NO pubblicazione, solo preview
# Base (€200):       3 generazioni, 20 modifiche, pubblicazione sottodominio, 2 pagine (extra €70/pag)
# Premium (€500):    5 generazioni, 30 modifiche, dominio incluso, pagine illimitate

PLAN_CONFIG = {
    "free": {
        "price": 0,
        "generations_limit": 1,
        "refines_limit": 3,
        "pages_limit": 1,        # Solo homepage (preview)
        "can_publish": False,
        "domain_included": False,
        "ads_campaigns_limit": 0,
        "label": "Starter",
    },
    "base": {
        "price": 200,
        "generations_limit": 3,
        "refines_limit": 20,
        "pages_limit": 2,        # Homepage + 1 extra (ulteriori €70/pag)
        "can_publish": True,
        "domain_included": False,  # Acquistabile a parte dallo shop
        "ads_campaigns_limit": 3,
        "label": "Creazione Sito",
    },
    "premium": {
        "price": 500,
        "generations_limit": 5,
        "refines_limit": 30,
        "pages_limit": 9999,     # Illimitate
        "can_publish": True,
        "domain_included": True,  # Dominio incluso nel prezzo
        "ads_campaigns_limit": 20,
        "label": "Premium",
    },
}

EXTRA_PAGE_PRICE = 70  # €70 per ogni pagina aggiuntiva (solo piano base)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # NULL per OAuth
    full_name = Column(String)
    avatar_url = Column(String)  # URL immagine profilo (Google)

    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', etc.
    oauth_id = Column(String, nullable=True, unique=True, index=True)

    # Piano e limiti (pagamento una tantum)
    plan = Column(String, default="free")  # free, base, premium
    is_premium = Column(Boolean, default=False)  # Legacy/override admin

    # Contatori generazioni sito (rigenerazioni)
    generations_used = Column(Integer, default=0)
    generations_limit = Column(Integer, default=1)

    # Contatori modifiche chat AI
    refines_used = Column(Integer, default=0)
    refines_limit = Column(Integer, default=3)

    # Contatori pagine extra
    pages_used = Column(Integer, default=0)
    pages_limit = Column(Integer, default=1)

    # Revolut
    revolut_customer_id = Column(String, nullable=True, unique=True, index=True)

    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_token_created_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset
    password_reset_token = Column(String, nullable=True)
    password_reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def plan_config(self) -> dict:
        """Ritorna la configurazione del piano corrente."""
        return PLAN_CONFIG.get(self.plan or "free", PLAN_CONFIG["free"])

    @property
    def can_publish(self) -> bool:
        """Controlla se l'utente puo pubblicare siti."""
        if self.is_premium or self.is_superuser:
            return True
        return self.plan_config["can_publish"]

    @property
    def has_remaining_generations(self) -> bool:
        """Controlla se l'utente ha ancora rigenerazioni disponibili."""
        if self.is_premium or self.is_superuser:
            return True
        return self.generations_used < self.generations_limit

    @property
    def remaining_generations(self) -> int:
        """Ritorna il numero di rigenerazioni rimanenti."""
        if self.is_premium or self.is_superuser:
            return -1  # Illimitate
        return max(0, self.generations_limit - self.generations_used)

    @property
    def has_remaining_refines(self) -> bool:
        """Controlla se l'utente ha ancora modifiche chat AI."""
        if self.is_premium or self.is_superuser:
            return True
        return self.refines_used < self.refines_limit

    @property
    def remaining_refines(self) -> int:
        """Ritorna il numero di modifiche chat AI rimanenti."""
        if self.is_premium or self.is_superuser:
            return -1
        return max(0, self.refines_limit - self.refines_used)

    @property
    def has_remaining_pages(self) -> bool:
        """Controlla se l'utente puo aggiungere altre pagine."""
        if self.is_premium or self.is_superuser:
            return True
        return self.pages_used < self.pages_limit

    @property
    def remaining_pages(self) -> int:
        """Ritorna il numero di pagine extra rimanenti."""
        if self.is_premium or self.is_superuser:
            return -1
        return max(0, self.pages_limit - self.pages_used)

    @property
    def is_verification_token_valid(self) -> bool:
        """Controlla se il token di verifica email e' ancora valido (24h)."""
        if not self.email_verification_token or not self.email_verification_token_created_at:
            return False
        from datetime import timedelta
        expiry = self.email_verification_token_created_at + timedelta(hours=24)
        return datetime.now(timezone.utc) < expiry

    @property
    def is_reset_token_valid(self) -> bool:
        """Controlla se il token di reset password e' ancora valido (1h)."""
        if not self.password_reset_token or not self.password_reset_token_expires:
            return False
        return datetime.now(timezone.utc) < self.password_reset_token_expires

    def activate_plan(self, plan_name: str):
        """Attiva un piano dopo il pagamento. Imposta tutti i limiti.
        NON salva nel DB - il caller deve fare commit."""
        config = PLAN_CONFIG.get(plan_name)
        if not config:
            raise ValueError(f"Piano '{plan_name}' non valido")
        self.plan = plan_name
        self.generations_limit = config["generations_limit"]
        self.refines_limit = config["refines_limit"]
        self.pages_limit = config["pages_limit"]
        # Reset contatori alla attivazione del piano
        self.generations_used = 0
        self.refines_used = 0
        self.pages_used = 0
