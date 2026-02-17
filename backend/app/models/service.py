"""Modelli per Catalogo Servizi, Abbonamenti Utente e Storico Pagamenti"""

from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ServiceCatalog(Base):
    """Catalogo servizi e pacchetti disponibili per l'acquisto.

    Categorie:
    - pack: pacchetti completi (Presenza, Clienti, Crescita, Premium)
    - site: servizi sito web (Homepage AI, Custom Site, Extra Page)
    - ads: gestione campagne pubblicitarie (Meta, Google, Full)
    - content: contenuti AI (Base, Pro)
    - hosting: hosting e manutenzione
    - domain: domini
    """
    __tablename__ = "service_catalog"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    category = Column(String, nullable=False)  # pack, site, ads, content, hosting, domain
    setup_price_cents = Column(Integer, default=0)      # Una tantum in centesimi EUR
    monthly_price_cents = Column(Integer, default=0)     # Mensile in centesimi EUR
    yearly_price_cents = Column(Integer, nullable=True)  # Annuale (opzionale)
    description = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    features_json = Column(Text, nullable=True)           # JSON array di feature strings
    features_en_json = Column(Text, nullable=True)
    included_services_json = Column(Text, nullable=True)  # Per pack: JSON array di slug servizi inclusi
    is_active = Column(Boolean, default=True)
    is_highlighted = Column(Boolean, default=False)       # Badge "CONSIGLIATO"
    display_order = Column(Integer, default=0)

    # Limiti associati al servizio (per pack che danno limiti di generazione)
    generations_limit = Column(Integer, nullable=True)
    refines_limit = Column(Integer, nullable=True)
    pages_limit = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserSubscription(Base):
    """Abbonamento/acquisto di un servizio da parte di un utente."""
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_slug = Column(String, nullable=False)  # Riferimento a ServiceCatalog.slug

    # Stato abbonamento
    status = Column(String, default="pending_setup")  # pending_setup, active, paused, cancelled, expired

    # Pagamento setup
    setup_paid = Column(Boolean, default=False)
    setup_order_id = Column(String, nullable=True)  # Revolut order ID per setup

    # Abbonamento mensile
    monthly_amount_cents = Column(Integer, default=0)
    revolut_customer_id = Column(String, nullable=True)  # Per addebiti ricorrenti

    # Periodo corrente
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)

    # Admin
    notes = Column(Text, nullable=True)
    activated_by = Column(String, nullable=True)  # "revolut", "admin", "manual"

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Relazioni
    user = relationship("User", backref="subscriptions")

    __table_args__ = (
        Index("ix_user_subscriptions_user_id", "user_id"),
        Index("ix_user_subscriptions_status", "status"),
        Index("ix_user_subscriptions_next_billing", "next_billing_date"),
    )


class PaymentHistory(Base):
    """Storico di tutti i pagamenti effettuati."""
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=True)

    # Revolut
    revolut_order_id = Column(String, nullable=True)

    # Dettagli pagamento
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="EUR")
    payment_type = Column(String, nullable=False)  # setup, monthly, yearly, one_time, refund
    status = Column(String, default="pending")      # completed, failed, pending, refunded
    description = Column(String, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relazioni
    user = relationship("User", backref="payments")
    subscription = relationship("UserSubscription", backref="payments")

    __table_args__ = (
        Index("ix_payment_history_user_id", "user_id"),
        Index("ix_payment_history_subscription_id", "subscription_id"),
    )
