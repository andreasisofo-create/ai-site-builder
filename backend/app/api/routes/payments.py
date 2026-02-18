"""Revolut Merchant API - pagamenti una tantum e abbonamenti servizi

Flow legacy (backward-compatible):
1. POST /create-checkout: crea ordine Revolut, ritorna checkout_url
2. Utente paga sulla hosted checkout page di Revolut
3. Revolut invia webhook ORDER_COMPLETED con order_id
4. Webhook handler recupera l'ordine via API per ottenere metadata (user_id, plan)
5. Chiama user.activate_plan() per attivare il piano

Flow nuovo (catalogo servizi):
1. GET /catalog: mostra tutti i servizi disponibili
2. POST /checkout-service: crea ordine per un servizio specifico
3. Webhook: attiva abbonamento e registra in PaymentHistory
4. GET /my-subscriptions: lista abbonamenti utente
5. GET /history: storico pagamenti utente
6. POST /cancel-subscription/{id}: cancella abbonamento
7. POST /process-recurring: cron job per addebiti mensili ricorrenti

Docs: https://developer.revolut.com/docs/merchant/merchant-api
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sqlfunc
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, PLAN_CONFIG
from app.models.service import ServiceCatalog, UserSubscription, PaymentHistory

logger = logging.getLogger(__name__)

router = APIRouter()

# Prezzi in centesimi EUR (minor currency units) - LEGACY
PLAN_PRICES = {
    "base": 20000,      # EUR 200.00
    "premium": 50000,   # EUR 500.00
}

PLAN_LABELS = {
    "base": "Creazione Sito",
    "premium": "Premium",
}


def _revolut_base_url() -> str:
    """URL base Revolut Merchant API (sandbox o produzione)."""
    if settings.REVOLUT_SANDBOX:
        return "https://sandbox-merchant.revolut.com/api/1.0"
    return "https://merchant.revolut.com/api/1.0"


def _revolut_headers() -> dict:
    """Headers per chiamate Revolut Merchant API."""
    return {
        "Authorization": f"Bearer {settings.REVOLUT_API_KEY}",
        "Content-Type": "application/json",
    }


def _frontend_base_url() -> str:
    """URL base del frontend per redirect dopo pagamento."""
    return settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"


# ============ SCHEMAS ============

class CheckoutRequest(BaseModel):
    plan: str  # "base" o "premium"


class CheckoutResponse(BaseModel):
    checkout_url: str
    order_id: str


class PaymentStatusResponse(BaseModel):
    plan: str
    plan_label: str
    has_paid: bool
    revolut_customer_id: Optional[str] = None


class ServiceCheckoutRequest(BaseModel):
    service_slug: str


class ServiceCheckoutResponse(BaseModel):
    checkout_url: Optional[str] = None
    order_id: Optional[str] = None
    activated: bool = False
    subscription_id: int


class CancelSubscriptionResponse(BaseModel):
    id: int
    status: str
    cancelled_at: Optional[str] = None


class PaymentHistoryItem(BaseModel):
    id: int
    amount_cents: int
    currency: str
    payment_type: str
    status: str
    description: Optional[str] = None
    created_at: Optional[str] = None


class SubscriptionItem(BaseModel):
    id: int
    service_slug: str
    service_name: Optional[str] = None
    service_category: Optional[str] = None
    status: str
    monthly_amount_cents: int
    setup_paid: bool
    next_billing_date: Optional[str] = None
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    created_at: Optional[str] = None


# ============ WEBHOOK SIGNATURE VERIFICATION ============

def _verify_revolut_signature(payload: bytes, sig_header: str, timestamp_header: str) -> bool:
    """Verifica la firma HMAC-SHA256 del webhook Revolut.

    Revolut-Signature header format: v1=<hex_digest> (puo' contenere piu' firme separate da virgola)
    payload_to_sign = "v1.{timestamp}.{raw_payload}"

    Docs: https://developer.revolut.com/docs/guides/accept-payments/tutorials/work-with-webhooks/verify-the-payload-signature
    """
    if not settings.REVOLUT_WEBHOOK_SECRET:
        return True  # Se non configurato, accetta (per sviluppo locale)

    if not sig_header or not timestamp_header:
        return False

    # Costruisci payload da firmare
    payload_to_sign = f"v1.{timestamp_header}.{payload.decode('utf-8')}"

    # Calcola firma attesa
    expected_sig = hmac.new(
        settings.REVOLUT_WEBHOOK_SECRET.encode("utf-8"),
        payload_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    expected_full = f"v1={expected_sig}"

    # Revolut puo' inviare piu' firme separate da virgola (rotazione secret)
    signatures = [s.strip() for s in sig_header.split(",")]
    return any(hmac.compare_digest(expected_full, sig) for sig in signatures)


# ============ REVOLUT API HELPERS ============

async def _revolut_get_order(order_id: str) -> Optional[dict]:
    """Recupera un ordine da Revolut per ottenere metadata e stato."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{_revolut_base_url()}/orders/{order_id}",
                headers=_revolut_headers(),
            )
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Revolut get order {order_id}: {resp.status_code} - {resp.text}")
    except httpx.RequestError as e:
        logger.error(f"Revolut get order errore connessione: {e}")
    return None


async def _revolut_create_order(payload: dict) -> dict:
    """Crea un ordine Revolut e ritorna il JSON di risposta.

    Raises HTTPException on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{_revolut_base_url()}/orders",
                headers=_revolut_headers(),
                json=payload,
            )

        if resp.status_code not in (200, 201):
            error_detail = resp.text[:200] if resp.text else "No response body"
            logger.error(f"Revolut create order error: {resp.status_code} - {resp.text}")
            raise HTTPException(
                status_code=502,
                detail=f"Errore creazione ordine: Revolut ha risposto {resp.status_code} - {error_detail}"
            )

        return resp.json()

    except httpx.RequestError as e:
        logger.error(f"Errore connessione Revolut: {e}")
        raise HTTPException(status_code=502, detail="Errore comunicazione con il sistema di pagamento")


async def _revolut_pay_order(order_id: str, payment_method_id: str) -> Optional[dict]:
    """Pay for an order using a saved payment method (for recurring charges).

    Docs: https://developer.revolut.com/docs/merchant/pay-for-an-order
    """
    try:
        payload = {
            "saved_payment_method": {
                "type": "card",
                "id": payment_method_id,
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{_revolut_base_url()}/orders/{order_id}/payments",
                headers=_revolut_headers(),
                json=payload,
            )
        if resp.status_code in (200, 201):
            return resp.json()
        logger.error(f"Revolut pay order {order_id}: {resp.status_code} - {resp.text}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Revolut pay order errore connessione: {e}")
        return None


async def _revolut_get_customer_payment_methods(customer_id: str) -> list:
    """Retrieve saved payment methods for a customer.

    Docs: https://developer.revolut.com/docs/merchant/retrieve-all-payment-methods
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{_revolut_base_url()}/customers/{customer_id}/payment-methods",
                headers=_revolut_headers(),
            )
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Revolut get payment methods for {customer_id}: {resp.status_code} - {resp.text}")
    except httpx.RequestError as e:
        logger.error(f"Revolut get payment methods errore: {e}")
    return []


# ============ ADMIN AUTH FOR RECURRING ============

def _verify_recurring_auth(authorization: str) -> bool:
    """Verifica autenticazione per endpoint process-recurring.

    Accetta admin JWT o secret key via header.
    """
    if not authorization:
        return False

    # Try admin JWT
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            from app.api.routes.admin import verify_admin_token
            payload = verify_admin_token(token)
            if payload:
                return True
        except Exception:
            pass

    # Try secret key (for cron jobs)
    if authorization == f"Secret {settings.SECRET_KEY}":
        return True

    return False


# ============ ENDPOINTS ============

# ---- 1. CATALOG (PUBLIC) ----

@router.get("/catalog")
async def get_service_catalog(db: Session = Depends(get_db)):
    """Ritorna il catalogo servizi attivi, raggruppati per categoria.

    Endpoint pubblico, non richiede autenticazione.
    """
    services = (
        db.query(ServiceCatalog)
        .filter(ServiceCatalog.is_active == True)
        .order_by(ServiceCatalog.display_order.asc())
        .all()
    )

    # Raggruppa per categoria
    catalog = {}
    for svc in services:
        cat = svc.category or "other"
        if cat not in catalog:
            catalog[cat] = []

        # Parse features JSON
        features = []
        if svc.features_json:
            try:
                features = json.loads(svc.features_json)
            except (json.JSONDecodeError, TypeError):
                features = []

        features_en = []
        if svc.features_en_json:
            try:
                features_en = json.loads(svc.features_en_json)
            except (json.JSONDecodeError, TypeError):
                features_en = []

        catalog[cat].append({
            "slug": svc.slug,
            "name": svc.name,
            "name_en": svc.name_en,
            "category": svc.category,
            "setup_price_cents": svc.setup_price_cents or 0,
            "monthly_price_cents": svc.monthly_price_cents or 0,
            "yearly_price_cents": svc.yearly_price_cents,
            "description": svc.description,
            "description_en": svc.description_en,
            "features": features,
            "features_en": features_en,
            "is_highlighted": svc.is_highlighted or False,
            "display_order": svc.display_order or 0,
        })

    return {"catalog": catalog, "total": len(services)}


# ---- 2. CHECKOUT SERVICE (AUTH) ----

@router.post("/checkout-service", response_model=ServiceCheckoutResponse)
async def checkout_service(
    body: ServiceCheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Crea un ordine Revolut per un servizio del catalogo.

    - Se il servizio ha setup_price > 0: crea ordine Revolut, ritorna checkout_url
    - Se il servizio ha solo costo mensile (setup = 0): attiva subito l'abbonamento
    """
    if not settings.REVOLUT_API_KEY:
        raise HTTPException(status_code=503, detail="Pagamenti non configurati")

    # Cerca il servizio nel catalogo
    service = (
        db.query(ServiceCatalog)
        .filter(ServiceCatalog.slug == body.service_slug, ServiceCatalog.is_active == True)
        .first()
    )
    if not service:
        raise HTTPException(status_code=404, detail=f"Servizio '{body.service_slug}' non trovato o non attivo")

    # Crea subscription con stato pending
    now = datetime.now(timezone.utc)
    subscription = UserSubscription(
        user_id=current_user.id,
        service_slug=service.slug,
        status="pending_setup",
        monthly_amount_cents=service.monthly_price_cents or 0,
        revolut_customer_id=current_user.revolut_customer_id,
    )
    db.add(subscription)
    db.flush()  # per ottenere l'ID

    setup_amount = service.setup_price_cents or 0

    if setup_amount > 0:
        # Crea ordine Revolut per il pagamento setup
        frontend_base = _frontend_base_url()

        order_payload = {
            "amount": setup_amount,
            "currency": "EUR",
            "description": f"Site Builder - {service.name} (Setup)",
            "merchant_order_ext_ref": f"svc_{current_user.id}_{service.slug}_{subscription.id}",
            "customer_email": current_user.email,
            "metadata": {
                "user_id": str(current_user.id),
                "service_slug": service.slug,
                "subscription_id": str(subscription.id),
                "flow": "service_checkout",
            },
            "redirect_url": f"{frontend_base}/dashboard?payment=success&service={service.slug}",
        }

        # If the service has monthly fees, save the payment method for future recurring charges
        if service.monthly_price_cents and service.monthly_price_cents > 0:
            order_payload["save_payment_method_for"] = "merchant"
            # Update description to include monthly info
            monthly_eur = service.monthly_price_cents / 100
            order_payload["description"] = (
                f"Site Builder - {service.name} (Setup + abbonamento \u20ac{monthly_eur:.0f}/mese)"
            )

        order = await _revolut_create_order(order_payload)
        order_id = order.get("id", "")
        checkout_url = order.get("checkout_url", "")

        if not checkout_url:
            logger.error(f"Revolut order senza checkout_url: {order}")
            db.rollback()
            raise HTTPException(status_code=502, detail="Errore: checkout URL non ricevuto")

        # Salva order_id nella subscription
        subscription.setup_order_id = order_id
        db.commit()

        logger.info(
            f"Service checkout creato: user={current_user.id}, service={service.slug}, "
            f"subscription={subscription.id}, order={order_id}"
        )

        return ServiceCheckoutResponse(
            checkout_url=checkout_url,
            order_id=order_id,
            activated=False,
            subscription_id=subscription.id,
        )

    else:
        # Nessun setup fee - attiva subito (servizio solo mensile)
        subscription.status = "active"
        subscription.setup_paid = True  # Nessun setup richiesto
        subscription.activated_by = "auto"
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=30)
        subscription.next_billing_date = now + timedelta(days=30)
        db.commit()

        # Aggiorna limiti utente se il servizio li prevede
        _apply_service_limits(current_user, service, db)

        logger.info(
            f"Service attivato senza setup: user={current_user.id}, service={service.slug}, "
            f"subscription={subscription.id}"
        )

        return ServiceCheckoutResponse(
            checkout_url=None,
            order_id=None,
            activated=True,
            subscription_id=subscription.id,
        )


# ---- 3. MY SUBSCRIPTIONS (AUTH) ----

@router.get("/my-subscriptions")
async def get_my_subscriptions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ritorna tutti gli abbonamenti dell'utente corrente con info servizio."""
    subscriptions = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == current_user.id)
        .order_by(UserSubscription.created_at.desc())
        .all()
    )

    result = []
    for sub in subscriptions:
        # Join manuale con ServiceCatalog per ottenere nome e categoria
        service = db.query(ServiceCatalog).filter(ServiceCatalog.slug == sub.service_slug).first()

        service_name = service.name if service else sub.service_slug
        service_category = service.category if service else None

        # Parse features dal servizio
        features = []
        if service and service.features_json:
            try:
                features = json.loads(service.features_json)
            except (json.JSONDecodeError, TypeError):
                features = []

        result.append({
            "id": sub.id,
            "service_slug": sub.service_slug,
            "service_name": service_name,
            "service_category": service_category,
            "features": features,
            "status": sub.status,
            "monthly_amount_cents": sub.monthly_amount_cents or 0,
            "setup_paid": sub.setup_paid or False,
            "next_billing_date": sub.next_billing_date.isoformat() if sub.next_billing_date else None,
            "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "created_at": sub.created_at.isoformat() if sub.created_at else None,
        })

    return {"subscriptions": result, "total": len(result)}


# ---- 4. PAYMENT HISTORY (AUTH) ----

@router.get("/history")
async def get_payment_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ritorna lo storico pagamenti paginato dell'utente corrente."""
    # Clamp limit
    limit = min(limit, 100)
    offset = max(offset, 0)

    query = (
        db.query(PaymentHistory)
        .filter(PaymentHistory.user_id == current_user.id)
        .order_by(PaymentHistory.created_at.desc())
    )

    total = query.count()
    payments = query.offset(offset).limit(limit).all()

    result = []
    for p in payments:
        result.append({
            "id": p.id,
            "amount_cents": p.amount_cents,
            "currency": p.currency or "EUR",
            "payment_type": p.payment_type,
            "status": p.status,
            "description": p.description,
            "revolut_order_id": p.revolut_order_id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return {
        "payments": result,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# ---- 5. CANCEL SUBSCRIPTION (AUTH) ----

@router.post("/cancel-subscription/{subscription_id}")
async def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Cancella un abbonamento dell'utente corrente."""
    subscription = (
        db.query(UserSubscription)
        .filter(
            UserSubscription.id == subscription_id,
            UserSubscription.user_id == current_user.id,
        )
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Abbonamento non trovato")

    if subscription.status == "cancelled":
        raise HTTPException(status_code=400, detail="Abbonamento gia' cancellato")

    now = datetime.now(timezone.utc)
    subscription.status = "cancelled"
    subscription.cancelled_at = now
    db.commit()

    logger.info(
        f"Subscription cancellata: id={subscription.id}, user={current_user.id}, "
        f"service={subscription.service_slug}"
    )

    return {
        "id": subscription.id,
        "status": subscription.status,
        "cancelled_at": subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
        "message": "Abbonamento cancellato con successo",
    }


# ---- 6. WEBHOOK (NO AUTH - called by Revolut) ----

@router.post("/webhook")
async def revolut_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook Revolut - riceve eventi di pagamento completato.
    NOTA: Questo endpoint NON richiede autenticazione JWT (Revolut lo chiama direttamente).

    Gestisce sia il flow legacy (user_id + plan) che il nuovo flow (service_slug + subscription_id).

    Payload esempio: {"event": "ORDER_COMPLETED", "order_id": "abc-123", "merchant_order_ext_ref": "..."}
    Il webhook contiene solo order_id, quindi dobbiamo recuperare l'ordine via API per i metadata.

    Docs: https://developer.revolut.com/docs/guides/accept-payments/tutorials/work-with-webhooks/using-webhooks
    """
    payload = await request.body()
    sig_header = request.headers.get("Revolut-Signature", "")
    timestamp_header = request.headers.get("Revolut-Request-Timestamp", "")

    # Verifica firma webhook HMAC-SHA256
    if not _verify_revolut_signature(payload, sig_header, timestamp_header):
        logger.warning("Webhook Revolut: firma non valida")
        raise HTTPException(status_code=400, detail="Firma non valida")

    # Parse evento
    try:
        event = json.loads(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="Payload invalido")

    event_type = event.get("event", "")
    order_id = event.get("order_id", "")

    logger.info(f"Webhook Revolut ricevuto: type={event_type}, order_id={order_id}")

    # Gestisci solo ordine completato
    if event_type == "ORDER_COMPLETED":
        await _handle_order_completed(order_id, db)
    elif event_type in ("ORDER_PAYMENT_FAILED", "ORDER_PAYMENT_DECLINED"):
        logger.warning(f"Pagamento Revolut fallito: order_id={order_id}")
        # Registra il fallimento se troviamo una subscription associata
        await _handle_payment_failed(order_id, db)

    # Rispondi 200 (Revolut accetta 2xx)
    return {"received": True}


async def _handle_order_completed(order_id: str, db: Session):
    """Processa un pagamento completato.

    Gestisce due flussi:
    1. Nuovo: metadata contiene service_slug + subscription_id -> attiva subscription
    2. Legacy: metadata contiene user_id + plan -> attiva piano utente
    """
    if not order_id:
        logger.error("Webhook ORDER_COMPLETED senza order_id")
        return

    # Recupera ordine completo da Revolut per ottenere metadata
    order = await _revolut_get_order(order_id)
    if not order:
        logger.error(f"Impossibile recuperare ordine Revolut: {order_id}")
        return

    # Verifica stato ordine
    state = order.get("state", "")
    if state.upper() != "COMPLETED":
        logger.warning(f"Ordine Revolut non completato: order_id={order_id}, state={state}")
        return

    metadata = order.get("metadata", {})
    flow = metadata.get("flow", "")

    # ---- NUOVO FLOW: service checkout ----
    if flow == "service_checkout" or metadata.get("subscription_id"):
        await _handle_service_order_completed(order_id, order, metadata, db)
        return

    # ---- LEGACY FLOW: plan checkout ----
    await _handle_legacy_order_completed(order_id, order, metadata, db)


async def _handle_service_order_completed(
    order_id: str, order: dict, metadata: dict, db: Session
):
    """Gestisce completamento ordine per il nuovo flusso servizi."""
    user_id = metadata.get("user_id")
    service_slug = metadata.get("service_slug")
    subscription_id = metadata.get("subscription_id")

    if not user_id or not service_slug or not subscription_id:
        logger.error(
            f"Service order incompleto: order_id={order_id}, "
            f"user_id={user_id}, service_slug={service_slug}, subscription_id={subscription_id}"
        )
        return

    # Trova la subscription
    subscription = (
        db.query(UserSubscription)
        .filter(UserSubscription.id == int(subscription_id))
        .first()
    )

    if not subscription:
        logger.error(f"Subscription non trovata: id={subscription_id}, order_id={order_id}")
        return

    # Idempotenza: se gia' attivata, skip
    if subscription.status == "active" and subscription.setup_paid:
        logger.info(f"Subscription gia' attiva, skip: id={subscription_id}")
        return

    # Trova il servizio per ottenere monthly_price e limiti
    service = db.query(ServiceCatalog).filter(ServiceCatalog.slug == service_slug).first()

    now = datetime.now(timezone.utc)

    try:
        # Attiva subscription
        subscription.status = "active"
        subscription.setup_paid = True
        subscription.activated_by = "revolut"
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=30)

        # Imposta amount mensile dal catalogo se presente
        if service and service.monthly_price_cents:
            subscription.monthly_amount_cents = service.monthly_price_cents
            subscription.next_billing_date = now + timedelta(days=30)
        else:
            # Servizio solo setup, nessun rinnovo
            subscription.monthly_amount_cents = 0
            subscription.next_billing_date = None

        # Salva customer_id Revolut se disponibile
        customer_id = order.get("customer_id")
        if customer_id:
            subscription.revolut_customer_id = customer_id

        # Recupera e salva payment_method_id per addebiti ricorrenti futuri
        if customer_id and service and service.monthly_price_cents and service.monthly_price_cents > 0:
            payment_methods = await _revolut_get_customer_payment_methods(customer_id)
            if payment_methods:
                # Prendi il primo metodo di pagamento salvato
                pm = payment_methods[0] if isinstance(payment_methods, list) else None
                if pm and isinstance(pm, dict):
                    pm_id = pm.get("id")
                    if pm_id:
                        subscription.revolut_payment_method_id = pm_id
                        logger.info(f"Payment method salvato: sub={subscription_id}, pm={pm_id}")

        # Registra pagamento in PaymentHistory
        amount = order.get("amount", service.setup_price_cents if service else 0)
        payment_record = PaymentHistory(
            user_id=int(user_id),
            subscription_id=subscription.id,
            revolut_order_id=order_id,
            amount_cents=amount,
            currency=order.get("currency", "EUR"),
            payment_type="setup",
            status="completed",
            description=f"Setup - {service.name if service else service_slug}",
        )
        db.add(payment_record)

        # Aggiorna limiti utente se il servizio li prevede
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            # Salva customer_id Revolut sull'utente se non presente
            if customer_id and not user.revolut_customer_id:
                user.revolut_customer_id = customer_id

            if service:
                _apply_service_limits(user, service, db, commit=False)

        db.commit()

        logger.info(
            f"Service subscription attivata: subscription_id={subscription_id}, "
            f"user={user_id}, service={service_slug}, order={order_id}"
        )

    except Exception as e:
        logger.error(f"Errore attivazione service subscription: {e}")
        db.rollback()


async def _handle_legacy_order_completed(
    order_id: str, order: dict, metadata: dict, db: Session
):
    """Gestisce completamento ordine per il flusso legacy (piani base/premium)."""
    user_id = metadata.get("user_id")
    plan_name = metadata.get("plan")

    # Fallback: prova a estrarre da merchant_order_ext_ref (formato: user_{id}_plan_{name})
    if not user_id or not plan_name:
        ext_ref = order.get("merchant_order_ext_ref", "")
        if ext_ref.startswith("user_") and "_plan_" in ext_ref:
            parts = ext_ref.split("_plan_")
            user_id = parts[0].replace("user_", "")
            plan_name = parts[1]

    if not user_id or not plan_name:
        logger.error(f"Ordine Revolut completato senza user_id/plan: order_id={order_id}, metadata={metadata}")
        return

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        logger.error(f"Utente non trovato per ordine Revolut: user_id={user_id}")
        return

    # Controlla se il piano e' gia' stato attivato (idempotenza, webhook puo' arrivare 2 volte)
    if user.plan == plan_name:
        logger.info(f"Piano gia' attivo, skip: user={user_id}, plan={plan_name}")
        return

    # Attiva il piano
    try:
        user.activate_plan(plan_name)
        # Salva customer_id se disponibile
        customer_id = order.get("customer_id")
        if customer_id and not user.revolut_customer_id:
            user.revolut_customer_id = customer_id

        # Registra pagamento in PaymentHistory
        amount = order.get("amount", PLAN_PRICES.get(plan_name, 0))
        payment_record = PaymentHistory(
            user_id=int(user_id),
            revolut_order_id=order_id,
            amount_cents=amount,
            currency=order.get("currency", "EUR"),
            payment_type="one_time",
            status="completed",
            description=f"Piano {PLAN_LABELS.get(plan_name, plan_name)}",
        )
        db.add(payment_record)

        db.commit()
        logger.info(f"Piano attivato via Revolut: user={user_id}, plan={plan_name}, email={user.email}")
    except ValueError as e:
        logger.error(f"Errore attivazione piano: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Errore DB durante attivazione piano: {e}")
        db.rollback()


async def _handle_payment_failed(order_id: str, db: Session):
    """Registra un fallimento di pagamento se troviamo una subscription associata."""
    if not order_id:
        return

    order = await _revolut_get_order(order_id)
    if not order:
        return

    metadata = order.get("metadata", {})
    user_id = metadata.get("user_id")
    subscription_id = metadata.get("subscription_id")

    if not user_id:
        return

    try:
        amount = order.get("amount", 0)
        payment_record = PaymentHistory(
            user_id=int(user_id),
            subscription_id=int(subscription_id) if subscription_id else None,
            revolut_order_id=order_id,
            amount_cents=amount,
            currency=order.get("currency", "EUR"),
            payment_type="setup" if metadata.get("flow") == "service_checkout" else "one_time",
            status="failed",
            description=f"Pagamento fallito - {metadata.get('service_slug', metadata.get('plan', 'unknown'))}",
        )
        db.add(payment_record)
        db.commit()
        logger.warning(f"Pagamento fallito registrato: order_id={order_id}, user={user_id}")
    except Exception as e:
        logger.error(f"Errore registrazione pagamento fallito: {e}")
        db.rollback()


# ---- 7. PROCESS RECURRING (ADMIN/SECRET) ----

@router.post("/process-recurring")
async def process_recurring_payments(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Processa pagamenti ricorrenti mensili per tutte le subscription attive scadute.

    Questo endpoint e' pensato per essere chiamato da un cron job giornaliero.
    Autenticazione: admin JWT oppure header "Secret {SECRET_KEY}".

    Per ogni subscription attiva con next_billing_date <= now e monthly_amount > 0:
    1. Crea ordine Revolut usando customer_id (se disponibile)
    2. Aggiorna next_billing_date += 30 giorni
    3. Registra PaymentHistory con status "pending"
    """
    if not _verify_recurring_auth(authorization or ""):
        raise HTTPException(status_code=401, detail="Autenticazione richiesta (admin o secret key)")

    if not settings.REVOLUT_API_KEY:
        raise HTTPException(status_code=503, detail="Pagamenti non configurati")

    now = datetime.now(timezone.utc)

    # Trova subscription attive con billing scaduto
    due_subscriptions = (
        db.query(UserSubscription)
        .filter(
            UserSubscription.status == "active",
            UserSubscription.monthly_amount_cents > 0,
            UserSubscription.next_billing_date <= now,
        )
        .all()
    )

    if not due_subscriptions:
        return {"processed": 0, "failed": 0, "details": [], "message": "Nessun pagamento ricorrente da processare"}

    processed = 0
    failed = 0
    details = []

    for sub in due_subscriptions:
        # Carica utente
        user = db.query(User).filter(User.id == sub.user_id).first()
        if not user:
            failed += 1
            details.append({
                "subscription_id": sub.id,
                "error": f"Utente non trovato: {sub.user_id}",
            })
            continue

        # Carica servizio per il nome
        service = db.query(ServiceCatalog).filter(ServiceCatalog.slug == sub.service_slug).first()
        service_name = service.name if service else sub.service_slug

        try:
            # Crea ordine Revolut per il rinnovo mensile
            order_payload = {
                "amount": sub.monthly_amount_cents,
                "currency": "EUR",
                "description": f"Site Builder - {service_name} (Rinnovo mensile)",
                "merchant_order_ext_ref": f"recurring_{sub.user_id}_{sub.service_slug}_{sub.id}_{now.strftime('%Y%m')}",
                "customer_email": user.email,
                "metadata": {
                    "user_id": str(user.id),
                    "service_slug": sub.service_slug,
                    "subscription_id": str(sub.id),
                    "flow": "recurring",
                },
            }

            # Se abbiamo un customer_id Revolut, usiamolo
            customer_id = sub.revolut_customer_id or user.revolut_customer_id
            if customer_id:
                order_payload["customer_id"] = customer_id

            order = await _revolut_create_order(order_payload)
            revolut_order_id = order.get("id", "")

            # Tenta addebito automatico con metodo di pagamento salvato
            auto_charged = False
            payment_method_id = getattr(sub, 'revolut_payment_method_id', None)
            if payment_method_id and revolut_order_id:
                pay_result = await _revolut_pay_order(revolut_order_id, payment_method_id)
                if pay_result:
                    auto_charged = True
                    logger.info(f"Addebito automatico riuscito: sub={sub.id}, order={revolut_order_id}")

            # Registra pagamento
            payment_record = PaymentHistory(
                user_id=user.id,
                subscription_id=sub.id,
                revolut_order_id=revolut_order_id,
                amount_cents=sub.monthly_amount_cents,
                currency="EUR",
                payment_type="monthly",
                status="completed" if auto_charged else "pending",
                description=f"Rinnovo mensile - {service_name}",
            )
            db.add(payment_record)

            # Avanza il periodo di fatturazione
            sub.current_period_start = sub.next_billing_date
            sub.current_period_end = sub.next_billing_date + timedelta(days=30)
            sub.next_billing_date = sub.next_billing_date + timedelta(days=30)

            db.commit()
            processed += 1

            details.append({
                "subscription_id": sub.id,
                "user_id": user.id,
                "user_email": user.email,
                "service": sub.service_slug,
                "amount_cents": sub.monthly_amount_cents,
                "revolut_order_id": revolut_order_id,
                "auto_charged": auto_charged,
                "status": "auto_charged" if auto_charged else "order_created",
            })

            logger.info(
                f"Rinnovo {'auto-addebitato' if auto_charged else 'creato'}: "
                f"subscription={sub.id}, user={user.id}, "
                f"service={sub.service_slug}, amount={sub.monthly_amount_cents}c, order={revolut_order_id}"
            )

        except HTTPException as e:
            failed += 1
            details.append({
                "subscription_id": sub.id,
                "user_id": user.id,
                "error": f"Revolut error: {e.detail}",
            })
            db.rollback()

        except Exception as e:
            failed += 1
            details.append({
                "subscription_id": sub.id,
                "user_id": user.id,
                "error": str(e),
            })
            logger.error(f"Errore rinnovo subscription {sub.id}: {e}")
            db.rollback()

    return {
        "processed": processed,
        "failed": failed,
        "total_due": len(due_subscriptions),
        "details": details,
    }


# ---- LEGACY ENDPOINT: CREATE CHECKOUT (backward compatible) ----

@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Crea un ordine Revolut e ritorna la checkout_url per il pagamento.

    LEGACY: per i piani base/premium. Usare /checkout-service per i nuovi servizi.
    """
    if not settings.REVOLUT_API_KEY:
        raise HTTPException(status_code=503, detail="Pagamenti non configurati")

    plan_name = body.plan.lower()
    if plan_name not in ("base", "premium"):
        raise HTTPException(status_code=400, detail="Piano non valido. Scegli 'base' o 'premium'.")

    # Se l'utente ha gia' un piano pari o superiore, blocca
    plan_hierarchy = {"free": 0, "base": 1, "premium": 2}
    current_level = plan_hierarchy.get(current_user.plan or "free", 0)
    target_level = plan_hierarchy.get(plan_name, 0)
    if current_level >= target_level:
        raise HTTPException(
            status_code=400,
            detail=f"Hai gia' il piano '{PLAN_CONFIG[current_user.plan]['label']}'. Non puoi acquistare un piano inferiore o uguale."
        )

    # URL di ritorno frontend dopo pagamento
    frontend_base = _frontend_base_url()

    # Crea ordine Revolut Merchant API
    # Docs: https://developer.revolut.com/docs/merchant/create-order
    order_payload = {
        "amount": PLAN_PRICES[plan_name],
        "currency": "EUR",
        "description": f"Site Builder - Piano {PLAN_LABELS[plan_name]}",
        "merchant_order_ext_ref": f"user_{current_user.id}_plan_{plan_name}",
        "customer_email": current_user.email,
        "metadata": {
            "user_id": str(current_user.id),
            "plan": plan_name,
        },
        "redirect_url": f"{frontend_base}/dashboard?payment=success&plan={plan_name}",
    }

    order = await _revolut_create_order(order_payload)
    order_id = order.get("id", "")
    checkout_url = order.get("checkout_url", "")

    if not checkout_url:
        logger.error(f"Revolut order senza checkout_url: {order}")
        raise HTTPException(status_code=502, detail="Errore: checkout URL non ricevuto")

    logger.info(f"Revolut order creato: user={current_user.id}, plan={plan_name}, order={order_id}")

    return CheckoutResponse(
        checkout_url=checkout_url,
        order_id=order_id,
    )


# ---- STATUS ENDPOINT (backward compatible) ----

@router.get("/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    current_user: User = Depends(get_current_active_user),
):
    """Ritorna lo stato del piano/pagamento dell'utente corrente."""
    plan = current_user.plan or "free"
    config = PLAN_CONFIG.get(plan, PLAN_CONFIG["free"])

    return PaymentStatusResponse(
        plan=plan,
        plan_label=config["label"],
        has_paid=plan != "free",
        revolut_customer_id=current_user.revolut_customer_id,
    )


# ============ HELPER FUNCTIONS ============

def _apply_service_limits(user: User, service: ServiceCatalog, db: Session, commit: bool = True):
    """Applica i limiti di generazione/refine/pagine dal servizio all'utente.

    Se il servizio ha limiti definiti, li somma ai limiti esistenti dell'utente.
    """
    updated = False

    if service.generations_limit is not None and service.generations_limit > 0:
        current_limit = user.generations_limit or 0
        user.generations_limit = current_limit + service.generations_limit
        updated = True

    if service.refines_limit is not None and service.refines_limit > 0:
        current_limit = user.refines_limit or 0
        user.refines_limit = current_limit + service.refines_limit
        updated = True

    if service.pages_limit is not None and service.pages_limit > 0:
        current_limit = user.pages_limit or 0
        user.pages_limit = current_limit + service.pages_limit
        updated = True

    if updated:
        logger.info(
            f"Limiti utente aggiornati: user={user.id}, "
            f"generations={user.generations_limit}, refines={user.refines_limit}, "
            f"pages={user.pages_limit}"
        )
        if commit:
            db.commit()
