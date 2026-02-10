"""Revolut Merchant API - pagamenti una tantum per piani Base e Premium

Flow:
1. POST /create-checkout: crea ordine Revolut, ritorna checkout_url
2. Utente paga sulla hosted checkout page di Revolut
3. Revolut invia webhook ORDER_COMPLETED con order_id
4. Webhook handler recupera l'ordine via API per ottenere metadata (user_id, plan)
5. Chiama user.activate_plan() per attivare il piano

Docs: https://developer.revolut.com/docs/merchant/merchant-api
"""

import hashlib
import hmac
import json
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, PLAN_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter()

# Prezzi in centesimi EUR (minor currency units)
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
        return "https://sandbox-merchant.revolut.com/api/orders"
    return "https://merchant.revolut.com/api/orders"


def _revolut_headers() -> dict:
    """Headers per chiamate Revolut Merchant API."""
    return {
        "Authorization": f"Bearer {settings.REVOLUT_API_KEY}",
        "Content-Type": "application/json",
    }


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
    revolut_customer_id: str | None


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

async def _revolut_get_order(order_id: str) -> dict | None:
    """Recupera un ordine da Revolut per ottenere metadata e stato."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{_revolut_base_url()}/{order_id}",
                headers=_revolut_headers(),
            )
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Revolut get order {order_id}: {resp.status_code} - {resp.text}")
    except httpx.RequestError as e:
        logger.error(f"Revolut get order errore connessione: {e}")
    return None


# ============ ENDPOINTS ============

@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Crea un ordine Revolut e ritorna la checkout_url per il pagamento."""
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
    frontend_base = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"

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

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                _revolut_base_url(),
                headers=_revolut_headers(),
                json=order_payload,
            )

        if resp.status_code not in (200, 201):
            logger.error(f"Revolut create order error: {resp.status_code} - {resp.text}")
            raise HTTPException(status_code=502, detail="Errore creazione ordine di pagamento")

        order = resp.json()
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

    except httpx.RequestError as e:
        logger.error(f"Errore connessione Revolut: {e}")
        raise HTTPException(status_code=502, detail="Errore comunicazione con il sistema di pagamento")


@router.post("/webhook")
async def revolut_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook Revolut - riceve eventi di pagamento completato.
    NOTA: Questo endpoint NON richiede autenticazione JWT (Revolut lo chiama direttamente).

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

    # Rispondi 200 (Revolut accetta 2xx)
    return {"received": True}


async def _handle_order_completed(order_id: str, db: Session):
    """Processa un pagamento completato: recupera ordine e attiva il piano dell'utente."""
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

    # Estrai metadata
    metadata = order.get("metadata", {})
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
        db.commit()
        logger.info(f"Piano attivato via Revolut: user={user_id}, plan={plan_name}, email={user.email}")
    except ValueError as e:
        logger.error(f"Errore attivazione piano: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Errore DB durante attivazione piano: {e}")
        db.rollback()


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
