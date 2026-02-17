"""Comprehensive tests for the payments system.

Tests all endpoints in app/api/routes/payments.py:
  - GET  /api/payments/catalog
  - POST /api/payments/checkout-service
  - GET  /api/payments/my-subscriptions
  - GET  /api/payments/history
  - POST /api/payments/cancel-subscription/{id}
  - POST /api/payments/webhook
  - POST /api/payments/create-checkout  (legacy)
  - GET  /api/payments/status           (legacy)
  - POST /api/payments/process-recurring

All external dependencies (DB, Revolut API, auth) are mocked so tests run
without infrastructure.

Run:  pytest backend/tests/test_payments.py -v
"""

import asyncio
import hashlib
import hmac
import json
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.routes.payments import router as payments_router
from app.core.security import get_current_active_user
from app.core.database import get_db
from app.models.user import User, PLAN_CONFIG
from app.models.service import ServiceCatalog, UserSubscription, PaymentHistory


# ---------------------------------------------------------------------------
# Helpers: factory functions for fake domain objects
# ---------------------------------------------------------------------------

def _make_user(**overrides) -> MagicMock:
    """Return a MagicMock that quacks like a User row."""
    defaults = dict(
        id=1,
        email="test@example.com",
        full_name="Test User",
        plan="free",
        is_active=True,
        is_premium=False,
        is_superuser=False,
        revolut_customer_id=None,
        generations_limit=1,
        refines_limit=3,
        pages_limit=1,
        generations_used=0,
        refines_used=0,
        pages_used=0,
    )
    defaults.update(overrides)
    user = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(user, k, v)
    # plan_config property
    user.plan_config = PLAN_CONFIG.get(defaults["plan"], PLAN_CONFIG["free"])
    return user


def _make_service(**overrides) -> MagicMock:
    """Return a MagicMock that quacks like a ServiceCatalog row."""
    defaults = dict(
        id=1,
        slug="pack-presenza",
        name="Pack Presenza",
        name_en="Presence Pack",
        category="pack",
        setup_price_cents=49900,
        monthly_price_cents=3900,
        yearly_price_cents=None,
        description="Il tuo biglietto da visita digitale.",
        description_en="Your digital business card.",
        features_json=json.dumps(["Homepage AI completa", "3 pagine extra"]),
        features_en_json=json.dumps(["Complete AI Homepage", "3 extra pages"]),
        included_services_json=None,
        is_active=True,
        is_highlighted=False,
        display_order=1,
        generations_limit=3,
        refines_limit=20,
        pages_limit=4,
    )
    defaults.update(overrides)
    svc = MagicMock(spec=ServiceCatalog)
    for k, v in defaults.items():
        setattr(svc, k, v)
    return svc


def _make_subscription(**overrides) -> MagicMock:
    """Return a MagicMock that quacks like a UserSubscription row."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=10,
        user_id=1,
        service_slug="pack-presenza",
        status="active",
        setup_paid=True,
        setup_order_id="rev-order-123",
        monthly_amount_cents=3900,
        revolut_customer_id=None,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
        next_billing_date=now + timedelta(days=30),
        notes=None,
        activated_by="revolut",
        created_at=now,
        updated_at=None,
        cancelled_at=None,
    )
    defaults.update(overrides)
    sub = MagicMock(spec=UserSubscription)
    for k, v in defaults.items():
        setattr(sub, k, v)
    return sub


def _make_payment(**overrides) -> MagicMock:
    """Return a MagicMock that quacks like a PaymentHistory row."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=100,
        user_id=1,
        subscription_id=10,
        revolut_order_id="rev-order-123",
        amount_cents=49900,
        currency="EUR",
        payment_type="setup",
        status="completed",
        description="Setup - Pack Presenza",
        created_at=now,
    )
    defaults.update(overrides)
    pay = MagicMock(spec=PaymentHistory)
    for k, v in defaults.items():
        setattr(pay, k, v)
    return pay


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def fake_user():
    """Default authenticated user."""
    return _make_user()


@pytest.fixture()
def mock_db():
    """A MagicMock that stands in for a SQLAlchemy Session."""
    return MagicMock(spec=Session)


@pytest.fixture()
def app_client(fake_user, mock_db):
    """FastAPI TestClient with auth + db overridden."""
    app = FastAPI()
    app.include_router(payments_router, prefix="/api/payments")

    # Override dependencies
    app.dependency_overrides[get_current_active_user] = lambda: fake_user
    app.dependency_overrides[get_db] = lambda: mock_db

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def unauth_client(mock_db):
    """FastAPI TestClient with NO auth override (requests will lack a token)."""
    app = FastAPI()
    app.include_router(payments_router, prefix="/api/payments")

    # Only override DB, leave auth as-is so 401 is returned
    app.dependency_overrides[get_db] = lambda: mock_db

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


# ===================================================================
#  1. CATALOG
# ===================================================================

class TestCatalog:
    """GET /api/payments/catalog -- public, no auth."""

    def test_catalog_returns_grouped_services(self, app_client, mock_db):
        """Returns services grouped by category with correct fields."""
        svc1 = _make_service(slug="pack-presenza", category="pack", display_order=1)
        svc2 = _make_service(
            slug="homepage-ai", name="Homepage AI", category="site",
            setup_price_cents=29900, monthly_price_cents=0, display_order=10,
            features_json=json.dumps(["1 pagina AI"]),
            features_en_json=None,
        )

        # Chain the ORM query mock
        q = mock_db.query.return_value
        q.filter.return_value.order_by.return_value.all.return_value = [svc1, svc2]

        resp = app_client.get("/api/payments/catalog")
        assert resp.status_code == 200

        data = resp.json()
        assert data["total"] == 2
        catalog = data["catalog"]
        assert "pack" in catalog
        assert "site" in catalog
        assert catalog["pack"][0]["slug"] == "pack-presenza"
        assert catalog["site"][0]["slug"] == "homepage-ai"

    def test_catalog_includes_expected_fields(self, app_client, mock_db):
        """Each service entry contains all documented fields."""
        svc = _make_service()
        q = mock_db.query.return_value
        q.filter.return_value.order_by.return_value.all.return_value = [svc]

        resp = app_client.get("/api/payments/catalog")
        assert resp.status_code == 200

        item = resp.json()["catalog"]["pack"][0]
        for field in (
            "slug", "name", "name_en", "category",
            "setup_price_cents", "monthly_price_cents",
            "description", "description_en",
            "features", "features_en",
            "is_highlighted", "display_order",
        ):
            assert field in item, f"Missing field: {field}"

    def test_catalog_empty(self, app_client, mock_db):
        """Returns empty catalog when no services exist."""
        q = mock_db.query.return_value
        q.filter.return_value.order_by.return_value.all.return_value = []

        resp = app_client.get("/api/payments/catalog")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["catalog"] == {}

    def test_catalog_handles_invalid_features_json(self, app_client, mock_db):
        """Gracefully handles malformed JSON in features fields."""
        svc = _make_service(features_json="NOT VALID JSON", features_en_json="{bad")
        q = mock_db.query.return_value
        q.filter.return_value.order_by.return_value.all.return_value = [svc]

        resp = app_client.get("/api/payments/catalog")
        assert resp.status_code == 200
        item = resp.json()["catalog"]["pack"][0]
        assert item["features"] == []
        assert item["features_en"] == []


# ===================================================================
#  2. CHECKOUT-SERVICE
# ===================================================================

class TestCheckoutService:
    """POST /api/payments/checkout-service"""

    @patch("app.api.routes.payments._revolut_create_order", new_callable=AsyncMock)
    @patch("app.api.routes.payments.settings")
    def test_checkout_paid_service_returns_url(
        self, mock_settings, mock_create_order, app_client, mock_db, fake_user
    ):
        """Checkout for a service with setup_price > 0 creates Revolut order."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"
        mock_settings.REVOLUT_SANDBOX = True
        mock_settings.CORS_ORIGINS = ["http://localhost:3000"]

        service = _make_service(setup_price_cents=49900, monthly_price_cents=3900)

        # DB query chain: find service
        q = mock_db.query.return_value
        q.filter.return_value.first.return_value = service

        # flush gives the subscription an id
        def assign_id(obj=None):
            # The subscription added to the session
            added = mock_db.add.call_args
            if added:
                sub = added[0][0]
                sub.id = 42
        mock_db.flush.side_effect = assign_id

        # Revolut response
        mock_create_order.return_value = {
            "id": "rev-order-abc",
            "checkout_url": "https://pay.revolut.com/abc",
        }

        resp = app_client.post(
            "/api/payments/checkout-service",
            json={"service_slug": "pack-presenza"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["checkout_url"] == "https://pay.revolut.com/abc"
        assert body["order_id"] == "rev-order-abc"
        assert body["activated"] is False
        assert "subscription_id" in body

    @patch("app.api.routes.payments._apply_service_limits")
    @patch("app.api.routes.payments.settings")
    def test_checkout_free_setup_activates_immediately(
        self, mock_settings, mock_apply, app_client, mock_db, fake_user
    ):
        """Service with setup_price_cents=0 activates subscription immediately."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"

        service = _make_service(
            slug="hosting-maintenance",
            setup_price_cents=0,
            monthly_price_cents=3900,
        )

        q = mock_db.query.return_value
        q.filter.return_value.first.return_value = service

        def assign_id(obj=None):
            added = mock_db.add.call_args
            if added:
                sub = added[0][0]
                sub.id = 55
        mock_db.flush.side_effect = assign_id

        resp = app_client.post(
            "/api/payments/checkout-service",
            json={"service_slug": "hosting-maintenance"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["activated"] is True
        assert body["checkout_url"] is None
        assert body["order_id"] is None

    @patch("app.api.routes.payments.settings")
    def test_checkout_invalid_slug_returns_404(
        self, mock_settings, app_client, mock_db
    ):
        """Requesting a non-existent service slug returns 404."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"

        q = mock_db.query.return_value
        q.filter.return_value.first.return_value = None

        resp = app_client.post(
            "/api/payments/checkout-service",
            json={"service_slug": "nonexistent-service"},
        )

        assert resp.status_code == 404
        assert "non trovato" in resp.json()["detail"]

    @patch("app.api.routes.payments.settings")
    def test_checkout_without_revolut_key_returns_503(
        self, mock_settings, app_client, mock_db
    ):
        """Missing REVOLUT_API_KEY returns 503."""
        mock_settings.REVOLUT_API_KEY = ""

        resp = app_client.post(
            "/api/payments/checkout-service",
            json={"service_slug": "pack-presenza"},
        )

        assert resp.status_code == 503
        assert "non configurati" in resp.json()["detail"]

    def test_checkout_without_auth_returns_401(self, unauth_client):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post(
            "/api/payments/checkout-service",
            json={"service_slug": "pack-presenza"},
        )
        assert resp.status_code in (401, 403)


# ===================================================================
#  3. MY SUBSCRIPTIONS
# ===================================================================

class TestMySubscriptions:
    """GET /api/payments/my-subscriptions"""

    def test_returns_user_subscriptions_with_service_info(
        self, app_client, mock_db, fake_user
    ):
        """Returns subscriptions joined with service catalog info."""
        sub = _make_subscription(user_id=fake_user.id)
        service = _make_service()

        # First query: subscriptions
        sub_query = MagicMock()
        sub_query.filter.return_value.order_by.return_value.all.return_value = [sub]

        # Second query: service catalog lookup
        svc_query = MagicMock()
        svc_query.filter.return_value.first.return_value = service

        mock_db.query.side_effect = [sub_query, svc_query]

        resp = app_client.get("/api/payments/my-subscriptions")
        assert resp.status_code == 200

        data = resp.json()
        assert data["total"] == 1
        item = data["subscriptions"][0]
        assert item["service_slug"] == "pack-presenza"
        assert item["service_name"] == "Pack Presenza"
        assert item["service_category"] == "pack"
        assert item["status"] == "active"
        assert "features" in item

    def test_returns_empty_list_for_new_user(self, app_client, mock_db, fake_user):
        """New user with no subscriptions gets empty list."""
        q = mock_db.query.return_value
        q.filter.return_value.order_by.return_value.all.return_value = []

        resp = app_client.get("/api/payments/my-subscriptions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["subscriptions"] == []

    def test_without_auth_returns_401(self, unauth_client):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get("/api/payments/my-subscriptions")
        assert resp.status_code in (401, 403)


# ===================================================================
#  4. PAYMENT HISTORY
# ===================================================================

class TestPaymentHistory:
    """GET /api/payments/history"""

    def test_returns_paginated_history(self, app_client, mock_db, fake_user):
        """Returns payment history with pagination metadata."""
        p1 = _make_payment(id=101)
        p2 = _make_payment(id=102, amount_cents=3900, payment_type="monthly")

        q = mock_db.query.return_value
        q_filtered = q.filter.return_value
        q_ordered = q_filtered.order_by.return_value
        q_ordered.count.return_value = 2
        q_ordered.offset.return_value.limit.return_value.all.return_value = [p1, p2]

        resp = app_client.get("/api/payments/history?limit=10&offset=0")
        assert resp.status_code == 200

        data = resp.json()
        assert data["total"] == 2
        assert data["limit"] == 10
        assert data["offset"] == 0
        assert len(data["payments"]) == 2
        assert data["payments"][0]["id"] == 101

    def test_respects_limit_and_offset(self, app_client, mock_db, fake_user):
        """Limit is clamped to 100 max, offset to >= 0."""
        q = mock_db.query.return_value
        q_filtered = q.filter.return_value
        q_ordered = q_filtered.order_by.return_value
        q_ordered.count.return_value = 0
        q_ordered.offset.return_value.limit.return_value.all.return_value = []

        resp = app_client.get("/api/payments/history?limit=999&offset=-5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["limit"] == 100  # clamped
        assert data["offset"] == 0   # clamped

    def test_empty_for_new_user(self, app_client, mock_db, fake_user):
        """New user has empty payment history."""
        q = mock_db.query.return_value
        q_filtered = q.filter.return_value
        q_ordered = q_filtered.order_by.return_value
        q_ordered.count.return_value = 0
        q_ordered.offset.return_value.limit.return_value.all.return_value = []

        resp = app_client.get("/api/payments/history")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["payments"] == []

    def test_without_auth_returns_401(self, unauth_client):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get("/api/payments/history")
        assert resp.status_code in (401, 403)


# ===================================================================
#  5. CANCEL SUBSCRIPTION
# ===================================================================

class TestCancelSubscription:
    """POST /api/payments/cancel-subscription/{id}"""

    def test_cancel_active_subscription(self, app_client, mock_db, fake_user):
        """Cancelling an active subscription sets status and cancelled_at."""
        sub = _make_subscription(id=10, user_id=fake_user.id, status="active")

        q = mock_db.query.return_value
        q.filter.return_value.first.return_value = sub

        resp = app_client.post("/api/payments/cancel-subscription/10")
        assert resp.status_code == 200

        body = resp.json()
        assert body["id"] == 10
        assert body["status"] == "cancelled"
        assert body["cancelled_at"] is not None
        mock_db.commit.assert_called()

    def test_cancel_nonexistent_subscription_returns_404(
        self, app_client, mock_db, fake_user
    ):
        """Trying to cancel a subscription that doesn't belong to the user returns 404."""
        q = mock_db.query.return_value
        q.filter.return_value.first.return_value = None

        resp = app_client.post("/api/payments/cancel-subscription/999")
        assert resp.status_code == 404
        assert "non trovato" in resp.json()["detail"]

    def test_cancel_other_users_subscription_returns_404(
        self, app_client, mock_db, fake_user
    ):
        """Cannot cancel a subscription owned by another user (query filters by user_id)."""
        # The filter for user_id + subscription_id returns None because it's another user's
        q = mock_db.query.return_value
        q.filter.return_value.first.return_value = None

        resp = app_client.post("/api/payments/cancel-subscription/10")
        assert resp.status_code == 404

    def test_cancel_already_cancelled_returns_400(
        self, app_client, mock_db, fake_user
    ):
        """Cannot cancel an already-cancelled subscription."""
        sub = _make_subscription(id=10, user_id=fake_user.id, status="cancelled")

        q = mock_db.query.return_value
        q.filter.return_value.first.return_value = sub

        resp = app_client.post("/api/payments/cancel-subscription/10")
        assert resp.status_code == 400
        assert "gia' cancellato" in resp.json()["detail"]

    def test_without_auth_returns_401(self, unauth_client):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post("/api/payments/cancel-subscription/10")
        assert resp.status_code in (401, 403)


# ===================================================================
#  6. WEBHOOK
# ===================================================================

class TestWebhook:
    """POST /api/payments/webhook -- called by Revolut, no JWT auth."""

    @patch("app.api.routes.payments._handle_payment_failed", new_callable=AsyncMock)
    @patch("app.api.routes.payments._handle_order_completed", new_callable=AsyncMock)
    @patch("app.api.routes.payments._verify_revolut_signature", return_value=True)
    def test_order_completed_service_flow(
        self, mock_verify, mock_completed, mock_failed, app_client, mock_db
    ):
        """ORDER_COMPLETED event delegates to _handle_order_completed."""
        payload = {
            "event": "ORDER_COMPLETED",
            "order_id": "rev-order-abc",
        }

        resp = app_client.post(
            "/api/payments/webhook",
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        assert resp.status_code == 200
        assert resp.json()["received"] is True
        mock_completed.assert_awaited_once_with("rev-order-abc", mock_db)
        mock_failed.assert_not_awaited()

    @patch("app.api.routes.payments._handle_payment_failed", new_callable=AsyncMock)
    @patch("app.api.routes.payments._handle_order_completed", new_callable=AsyncMock)
    @patch("app.api.routes.payments._verify_revolut_signature", return_value=True)
    def test_payment_failed_event(
        self, mock_verify, mock_completed, mock_failed, app_client, mock_db
    ):
        """ORDER_PAYMENT_FAILED delegates to _handle_payment_failed."""
        payload = {
            "event": "ORDER_PAYMENT_FAILED",
            "order_id": "rev-order-fail",
        }

        resp = app_client.post(
            "/api/payments/webhook",
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        assert resp.status_code == 200
        mock_failed.assert_awaited_once_with("rev-order-fail", mock_db)
        mock_completed.assert_not_awaited()

    @patch("app.api.routes.payments._verify_revolut_signature", return_value=False)
    def test_invalid_signature_returns_400(self, mock_verify, app_client, mock_db):
        """Webhook with an invalid HMAC signature is rejected."""
        payload = {"event": "ORDER_COMPLETED", "order_id": "x"}

        resp = app_client.post(
            "/api/payments/webhook",
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        assert resp.status_code == 400
        assert "Firma non valida" in resp.json()["detail"]

    @patch("app.api.routes.payments._verify_revolut_signature", return_value=True)
    def test_invalid_json_payload_returns_400(self, mock_verify, app_client, mock_db):
        """Malformed JSON body returns 400."""
        resp = app_client.post(
            "/api/payments/webhook",
            content="NOT JSON AT ALL{{{",
            headers={"Content-Type": "application/json"},
        )

        assert resp.status_code == 400
        assert "invalido" in resp.json()["detail"].lower()

    @patch("app.api.routes.payments._handle_order_completed", new_callable=AsyncMock)
    @patch("app.api.routes.payments._verify_revolut_signature", return_value=True)
    def test_unknown_event_returns_200(
        self, mock_verify, mock_completed, app_client, mock_db
    ):
        """Unknown events are acknowledged with 200 but not processed."""
        payload = {"event": "ORDER_AUTHORISED", "order_id": "x"}

        resp = app_client.post(
            "/api/payments/webhook",
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        assert resp.status_code == 200
        mock_completed.assert_not_awaited()


# ===================================================================
#  6b. WEBHOOK INTERNAL HANDLERS (unit tests)
# ===================================================================

class TestWebhookHandlers:
    """Unit tests for _handle_order_completed, _handle_service_order_completed,
    _handle_legacy_order_completed, _handle_payment_failed."""

    @patch("app.api.routes.payments._revolut_get_order", new_callable=AsyncMock)
    def test_handle_service_order_completed(self, mock_get_order):
        """Service flow: activates subscription, records payment, applies limits."""
        from app.api.routes.payments import _handle_order_completed

        mock_get_order.return_value = {
            "id": "rev-order-svc",
            "state": "COMPLETED",
            "amount": 49900,
            "currency": "EUR",
            "customer_id": "cust-123",
            "metadata": {
                "user_id": "1",
                "service_slug": "pack-presenza",
                "subscription_id": "10",
                "flow": "service_checkout",
            },
        }

        sub = _make_subscription(id=10, status="pending_setup", setup_paid=False)
        service = _make_service()
        user = _make_user()

        db = MagicMock(spec=Session)

        # First query: subscription by id
        # Second query: service by slug
        # Third query: user by id
        call_count = [0]

        def query_side_effect(model):
            call_count[0] += 1
            q = MagicMock()
            if model == UserSubscription or call_count[0] == 1:
                q.filter.return_value.first.return_value = sub
            elif model == ServiceCatalog or call_count[0] == 2:
                q.filter.return_value.first.return_value = service
            else:
                q.filter.return_value.first.return_value = user
            return q

        db.query.side_effect = query_side_effect

        asyncio.run(_handle_order_completed("rev-order-svc", db))

        # Subscription should be activated
        assert sub.status == "active"
        assert sub.setup_paid is True
        assert sub.activated_by == "revolut"
        db.add.assert_called()  # PaymentHistory record
        db.commit.assert_called()

    @patch("app.api.routes.payments._revolut_get_order", new_callable=AsyncMock)
    def test_handle_legacy_order_completed(self, mock_get_order):
        """Legacy flow: activates user plan and records payment."""
        from app.api.routes.payments import _handle_order_completed

        mock_get_order.return_value = {
            "id": "rev-order-legacy",
            "state": "COMPLETED",
            "amount": 20000,
            "currency": "EUR",
            "metadata": {
                "user_id": "1",
                "plan": "base",
            },
        }

        user = _make_user(plan="free")

        db = MagicMock(spec=Session)
        q = MagicMock()
        q.filter.return_value.first.return_value = user
        db.query.return_value = q

        asyncio.run(_handle_order_completed("rev-order-legacy", db))

        user.activate_plan.assert_called_once_with("base")
        db.add.assert_called()  # PaymentHistory
        db.commit.assert_called()

    @patch("app.api.routes.payments._revolut_get_order", new_callable=AsyncMock)
    def test_handle_legacy_idempotent_skips_if_already_active(
        self, mock_get_order
    ):
        """If user already has the plan, skip activation (idempotency)."""
        from app.api.routes.payments import _handle_order_completed

        mock_get_order.return_value = {
            "id": "rev-order-legacy",
            "state": "COMPLETED",
            "amount": 20000,
            "currency": "EUR",
            "metadata": {"user_id": "1", "plan": "base"},
        }

        user = _make_user(plan="base")  # already on base

        db = MagicMock(spec=Session)
        q = MagicMock()
        q.filter.return_value.first.return_value = user
        db.query.return_value = q

        asyncio.run(_handle_order_completed("rev-order-legacy", db))

        user.activate_plan.assert_not_called()

    @patch("app.api.routes.payments._revolut_get_order", new_callable=AsyncMock)
    def test_handle_payment_failed_records_failure(self, mock_get_order):
        """Failed payment creates a PaymentHistory record with status=failed."""
        from app.api.routes.payments import _handle_payment_failed

        mock_get_order.return_value = {
            "id": "rev-order-fail",
            "amount": 49900,
            "currency": "EUR",
            "metadata": {
                "user_id": "1",
                "subscription_id": "10",
                "service_slug": "pack-presenza",
                "flow": "service_checkout",
            },
        }

        db = MagicMock(spec=Session)

        asyncio.run(_handle_payment_failed("rev-order-fail", db))

        db.add.assert_called_once()
        payment_record = db.add.call_args[0][0]
        assert payment_record.status == "failed"
        assert payment_record.user_id == 1
        db.commit.assert_called()

    @patch("app.api.routes.payments._revolut_get_order", new_callable=AsyncMock)
    def test_handle_order_completed_no_order_id(self, mock_get_order):
        """_handle_order_completed with empty order_id does nothing."""
        from app.api.routes.payments import _handle_order_completed

        db = MagicMock(spec=Session)
        asyncio.run(_handle_order_completed("", db))

        mock_get_order.assert_not_called()

    @patch("app.api.routes.payments._revolut_get_order", new_callable=AsyncMock)
    def test_handle_order_completed_order_not_found(self, mock_get_order):
        """If Revolut API returns None for the order, handler exits gracefully."""
        from app.api.routes.payments import _handle_order_completed

        mock_get_order.return_value = None

        db = MagicMock(spec=Session)
        asyncio.run(_handle_order_completed("rev-nonexistent", db))

        db.commit.assert_not_called()

    @patch("app.api.routes.payments._revolut_get_order", new_callable=AsyncMock)
    def test_handle_order_completed_order_not_completed_state(
        self, mock_get_order
    ):
        """If order state is not COMPLETED, handler exits without processing."""
        from app.api.routes.payments import _handle_order_completed

        mock_get_order.return_value = {
            "id": "rev-pending",
            "state": "PENDING",
            "metadata": {"user_id": "1", "plan": "base"},
        }

        db = MagicMock(spec=Session)
        asyncio.run(_handle_order_completed("rev-pending", db))

        db.commit.assert_not_called()


# ===================================================================
#  7. LEGACY CREATE-CHECKOUT
# ===================================================================

class TestLegacyCheckout:
    """POST /api/payments/create-checkout -- legacy plan checkout."""

    @patch("app.api.routes.payments._revolut_create_order", new_callable=AsyncMock)
    @patch("app.api.routes.payments.settings")
    def test_create_checkout_base_plan(
        self, mock_settings, mock_create_order, app_client, mock_db, fake_user
    ):
        """Checkout for 'base' plan creates Revolut order and returns URL."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"
        mock_settings.REVOLUT_SANDBOX = True
        mock_settings.CORS_ORIGINS = ["http://localhost:3000"]

        fake_user.plan = "free"

        mock_create_order.return_value = {
            "id": "rev-legacy-123",
            "checkout_url": "https://pay.revolut.com/legacy-123",
        }

        resp = app_client.post(
            "/api/payments/create-checkout",
            json={"plan": "base"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["checkout_url"] == "https://pay.revolut.com/legacy-123"
        assert body["order_id"] == "rev-legacy-123"

    @patch("app.api.routes.payments._revolut_create_order", new_callable=AsyncMock)
    @patch("app.api.routes.payments.settings")
    def test_create_checkout_premium_plan(
        self, mock_settings, mock_create_order, app_client, mock_db, fake_user
    ):
        """Checkout for 'premium' plan works."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"
        mock_settings.REVOLUT_SANDBOX = True
        mock_settings.CORS_ORIGINS = ["http://localhost:3000"]

        fake_user.plan = "free"

        mock_create_order.return_value = {
            "id": "rev-premium-456",
            "checkout_url": "https://pay.revolut.com/premium-456",
        }

        resp = app_client.post(
            "/api/payments/create-checkout",
            json={"plan": "premium"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["order_id"] == "rev-premium-456"

    @patch("app.api.routes.payments.settings")
    def test_create_checkout_invalid_plan_returns_400(
        self, mock_settings, app_client, mock_db, fake_user
    ):
        """Invalid plan name returns 400."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"

        resp = app_client.post(
            "/api/payments/create-checkout",
            json={"plan": "enterprise"},
        )

        assert resp.status_code == 400
        assert "non valido" in resp.json()["detail"]

    @patch("app.api.routes.payments.settings")
    def test_create_checkout_already_on_plan_returns_400(
        self, mock_settings, app_client, mock_db, fake_user
    ):
        """User already on 'base' cannot buy 'base' again."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"

        fake_user.plan = "base"

        resp = app_client.post(
            "/api/payments/create-checkout",
            json={"plan": "base"},
        )

        assert resp.status_code == 400
        assert "gia'" in resp.json()["detail"].lower()

    @patch("app.api.routes.payments.settings")
    def test_create_checkout_downgrade_blocked(
        self, mock_settings, app_client, mock_db, fake_user
    ):
        """User on 'premium' cannot buy 'base' (downgrade blocked)."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"

        fake_user.plan = "premium"

        resp = app_client.post(
            "/api/payments/create-checkout",
            json={"plan": "base"},
        )

        assert resp.status_code == 400

    @patch("app.api.routes.payments.settings")
    def test_create_checkout_without_revolut_key_returns_503(
        self, mock_settings, app_client, mock_db
    ):
        """Missing REVOLUT_API_KEY returns 503."""
        mock_settings.REVOLUT_API_KEY = ""

        resp = app_client.post(
            "/api/payments/create-checkout",
            json={"plan": "base"},
        )

        assert resp.status_code == 503

    def test_create_checkout_without_auth_returns_401(self, unauth_client):
        """Unauthenticated request returns 401."""
        resp = unauth_client.post(
            "/api/payments/create-checkout",
            json={"plan": "base"},
        )
        assert resp.status_code in (401, 403)


# ===================================================================
#  8. PAYMENT STATUS (legacy)
# ===================================================================

class TestPaymentStatus:
    """GET /api/payments/status"""

    def test_status_free_user(self, app_client, fake_user):
        """Free user returns has_paid=False."""
        fake_user.plan = "free"
        fake_user.revolut_customer_id = None

        resp = app_client.get("/api/payments/status")
        assert resp.status_code == 200

        body = resp.json()
        assert body["plan"] == "free"
        assert body["plan_label"] == "Starter"
        assert body["has_paid"] is False

    def test_status_base_user(self, app_client, fake_user):
        """Base user returns has_paid=True with correct label."""
        fake_user.plan = "base"

        resp = app_client.get("/api/payments/status")
        assert resp.status_code == 200

        body = resp.json()
        assert body["plan"] == "base"
        assert body["plan_label"] == "Creazione Sito"
        assert body["has_paid"] is True

    def test_status_premium_user(self, app_client, fake_user):
        """Premium user returns correct info."""
        fake_user.plan = "premium"
        fake_user.revolut_customer_id = "cust-abc"

        resp = app_client.get("/api/payments/status")
        assert resp.status_code == 200

        body = resp.json()
        assert body["plan"] == "premium"
        assert body["has_paid"] is True
        assert body["revolut_customer_id"] == "cust-abc"

    def test_without_auth_returns_401(self, unauth_client):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get("/api/payments/status")
        assert resp.status_code in (401, 403)


# ===================================================================
#  9. PROCESS RECURRING
# ===================================================================

class TestProcessRecurring:
    """POST /api/payments/process-recurring"""

    @patch("app.api.routes.payments._revolut_create_order", new_callable=AsyncMock)
    @patch("app.api.routes.payments._verify_recurring_auth", return_value=True)
    @patch("app.api.routes.payments.settings")
    def test_processes_due_subscriptions(
        self, mock_settings, mock_auth, mock_create_order, app_client, mock_db
    ):
        """Processes subscriptions with next_billing_date <= now."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"

        past = datetime.now(timezone.utc) - timedelta(days=1)
        sub = _make_subscription(
            id=10,
            user_id=1,
            monthly_amount_cents=3900,
            next_billing_date=past,
            status="active",
            revolut_customer_id=None,
        )

        user = _make_user()
        service = _make_service()

        # Query chain for due subscriptions
        due_q = MagicMock()
        due_q.filter.return_value.all.return_value = [sub]

        # Queries for user + service inside the loop
        user_q = MagicMock()
        user_q.filter.return_value.first.return_value = user
        svc_q = MagicMock()
        svc_q.filter.return_value.first.return_value = service

        mock_db.query.side_effect = [due_q, user_q, svc_q]

        mock_create_order.return_value = {
            "id": "rev-recurring-001",
        }

        resp = app_client.post(
            "/api/payments/process-recurring",
            headers={"authorization": "Secret test-key"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["processed"] == 1
        assert body["failed"] == 0

    @patch("app.api.routes.payments._verify_recurring_auth", return_value=True)
    @patch("app.api.routes.payments.settings")
    def test_no_due_subscriptions(
        self, mock_settings, mock_auth, app_client, mock_db
    ):
        """Returns processed=0 when nothing is due."""
        mock_settings.REVOLUT_API_KEY = "sk_test_123"

        q = mock_db.query.return_value
        q.filter.return_value.all.return_value = []

        resp = app_client.post(
            "/api/payments/process-recurring",
            headers={"authorization": "Secret test-key"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["processed"] == 0

    @patch("app.api.routes.payments._verify_recurring_auth", return_value=False)
    def test_requires_admin_auth(self, mock_auth, app_client, mock_db):
        """Request without valid admin auth returns 401."""
        resp = app_client.post(
            "/api/payments/process-recurring",
            headers={"authorization": "Bearer invalid-token"},
        )

        assert resp.status_code == 401
        assert "Autenticazione richiesta" in resp.json()["detail"]

    @patch("app.api.routes.payments._verify_recurring_auth", return_value=True)
    @patch("app.api.routes.payments.settings")
    def test_requires_revolut_key(self, mock_settings, mock_auth, app_client, mock_db):
        """Returns 503 if REVOLUT_API_KEY is not configured."""
        mock_settings.REVOLUT_API_KEY = ""

        resp = app_client.post(
            "/api/payments/process-recurring",
            headers={"authorization": "Secret test-key"},
        )

        assert resp.status_code == 503

    @patch("app.api.routes.payments._revolut_create_order", new_callable=AsyncMock)
    @patch("app.api.routes.payments._verify_recurring_auth", return_value=True)
    @patch("app.api.routes.payments.settings")
    def test_skips_subscriptions_not_yet_due(
        self, mock_settings, mock_auth, mock_create_order, app_client, mock_db
    ):
        """Subscriptions with next_billing_date in the future are not processed.

        The DB query filters next_billing_date <= now, so future ones are excluded.
        """
        mock_settings.REVOLUT_API_KEY = "sk_test_123"

        # The query returns empty because the DB filter excludes future dates
        q = mock_db.query.return_value
        q.filter.return_value.all.return_value = []

        resp = app_client.post(
            "/api/payments/process-recurring",
            headers={"authorization": "Secret test-key"},
        )

        assert resp.status_code == 200
        assert resp.json()["processed"] == 0
        mock_create_order.assert_not_awaited()


# ===================================================================
#  10. SIGNATURE VERIFICATION (unit test)
# ===================================================================

class TestSignatureVerification:
    """Unit tests for _verify_revolut_signature."""

    @patch("app.api.routes.payments.settings")
    def test_valid_signature_accepted(self, mock_settings):
        """Correctly signed payload is accepted."""
        from app.api.routes.payments import _verify_revolut_signature

        secret = "whsec_test_secret_123"
        mock_settings.REVOLUT_WEBHOOK_SECRET = secret

        payload = b'{"event":"ORDER_COMPLETED","order_id":"abc"}'
        timestamp = "1700000000"

        # Compute expected signature
        payload_to_sign = f"v1.{timestamp}.{payload.decode('utf-8')}"
        sig = hmac.new(
            secret.encode("utf-8"),
            payload_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        sig_header = f"v1={sig}"

        assert _verify_revolut_signature(payload, sig_header, timestamp) is True

    @patch("app.api.routes.payments.settings")
    def test_invalid_signature_rejected(self, mock_settings):
        """Tampered signature is rejected."""
        from app.api.routes.payments import _verify_revolut_signature

        mock_settings.REVOLUT_WEBHOOK_SECRET = "whsec_test_secret_123"
        payload = b'{"event":"ORDER_COMPLETED"}'

        assert _verify_revolut_signature(payload, "v1=badhex", "1700000000") is False

    @patch("app.api.routes.payments.settings")
    def test_no_secret_configured_accepts_all(self, mock_settings):
        """When REVOLUT_WEBHOOK_SECRET is empty, all webhooks pass (dev mode)."""
        from app.api.routes.payments import _verify_revolut_signature

        mock_settings.REVOLUT_WEBHOOK_SECRET = ""

        assert _verify_revolut_signature(b"anything", "v1=x", "123") is True

    @patch("app.api.routes.payments.settings")
    def test_missing_headers_rejected(self, mock_settings):
        """Missing sig or timestamp headers are rejected."""
        from app.api.routes.payments import _verify_revolut_signature

        mock_settings.REVOLUT_WEBHOOK_SECRET = "whsec_test"

        assert _verify_revolut_signature(b"data", "", "123") is False
        assert _verify_revolut_signature(b"data", "v1=abc", "") is False

    @patch("app.api.routes.payments.settings")
    def test_multiple_signatures_one_valid(self, mock_settings):
        """Revolut may send multiple comma-separated sigs (key rotation)."""
        from app.api.routes.payments import _verify_revolut_signature

        secret = "whsec_rotate"
        mock_settings.REVOLUT_WEBHOOK_SECRET = secret

        payload = b'{"test":true}'
        timestamp = "999"

        payload_to_sign = f"v1.{timestamp}.{payload.decode('utf-8')}"
        valid_sig = hmac.new(
            secret.encode("utf-8"),
            payload_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Send two signatures: first is wrong, second is correct
        sig_header = f"v1=wronghex, v1={valid_sig}"
        assert _verify_revolut_signature(payload, sig_header, timestamp) is True


# ===================================================================
#  11. REVOLUT API HELPERS (unit tests)
# ===================================================================

class TestRevolutHelpers:
    """Unit tests for _revolut_create_order and _revolut_get_order."""

    @patch("app.api.routes.payments.settings")
    @patch("httpx.AsyncClient")
    def test_revolut_create_order_success(self, mock_client_cls, mock_settings):
        """Successful order creation returns JSON response."""
        from app.api.routes.payments import _revolut_create_order

        mock_settings.REVOLUT_SANDBOX = True
        mock_settings.REVOLUT_API_KEY = "sk_test"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "ord-123", "checkout_url": "https://..."}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_cls.return_value = mock_client

        result = asyncio.run(_revolut_create_order({"amount": 100, "currency": "EUR"}))
        assert result["id"] == "ord-123"

    @patch("app.api.routes.payments.settings")
    @patch("httpx.AsyncClient")
    def test_revolut_get_order_success(self, mock_client_cls, mock_settings):
        """Successful order retrieval returns JSON."""
        from app.api.routes.payments import _revolut_get_order

        mock_settings.REVOLUT_SANDBOX = True
        mock_settings.REVOLUT_API_KEY = "sk_test"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "ord-123", "state": "COMPLETED"}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_cls.return_value = mock_client

        result = asyncio.run(_revolut_get_order("ord-123"))
        assert result is not None
        assert result["state"] == "COMPLETED"

    @patch("app.api.routes.payments.settings")
    @patch("httpx.AsyncClient")
    def test_revolut_get_order_not_found(self, mock_client_cls, mock_settings):
        """404 from Revolut returns None."""
        from app.api.routes.payments import _revolut_get_order

        mock_settings.REVOLUT_SANDBOX = True
        mock_settings.REVOLUT_API_KEY = "sk_test"

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Not found"

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_cls.return_value = mock_client

        result = asyncio.run(_revolut_get_order("nonexistent"))
        assert result is None


# ===================================================================
#  12. ADMIN AUTH HELPER (unit test)
# ===================================================================

class TestRecurringAuth:
    """Unit tests for _verify_recurring_auth."""

    @patch("app.api.routes.payments.settings")
    def test_secret_key_auth_accepted(self, mock_settings):
        """Authorization with correct Secret key passes."""
        from app.api.routes.payments import _verify_recurring_auth

        mock_settings.SECRET_KEY = "my-secret-key"

        assert _verify_recurring_auth("Secret my-secret-key") is True

    @patch("app.api.routes.payments.settings")
    def test_wrong_secret_rejected(self, mock_settings):
        """Wrong secret key is rejected."""
        from app.api.routes.payments import _verify_recurring_auth

        mock_settings.SECRET_KEY = "my-secret-key"

        assert _verify_recurring_auth("Secret wrong-key") is False

    def test_empty_auth_rejected(self):
        """Empty/None authorization is rejected."""
        from app.api.routes.payments import _verify_recurring_auth

        assert _verify_recurring_auth("") is False
        assert _verify_recurring_auth(None) is False


# ===================================================================
#  13. APPLY SERVICE LIMITS HELPER (unit test)
# ===================================================================

class TestApplyServiceLimits:
    """Unit tests for _apply_service_limits."""

    def test_applies_generation_limits(self):
        """Service with generation limits adds to existing user limits."""
        from app.api.routes.payments import _apply_service_limits

        user = _make_user(generations_limit=1, refines_limit=3, pages_limit=1)
        service = _make_service(generations_limit=3, refines_limit=20, pages_limit=4)
        db = MagicMock(spec=Session)

        _apply_service_limits(user, service, db)

        assert user.generations_limit == 4   # 1 + 3
        assert user.refines_limit == 23      # 3 + 20
        assert user.pages_limit == 5         # 1 + 4
        db.commit.assert_called_once()

    def test_no_limits_on_service_does_nothing(self):
        """Service with None limits does not modify user."""
        from app.api.routes.payments import _apply_service_limits

        user = _make_user(generations_limit=5, refines_limit=10, pages_limit=3)
        service = _make_service(
            generations_limit=None, refines_limit=None, pages_limit=None,
        )
        db = MagicMock(spec=Session)

        _apply_service_limits(user, service, db)

        assert user.generations_limit == 5
        assert user.refines_limit == 10
        assert user.pages_limit == 3
        db.commit.assert_not_called()

    def test_commit_false_does_not_commit(self):
        """When commit=False, changes are applied but not committed."""
        from app.api.routes.payments import _apply_service_limits

        user = _make_user(generations_limit=1)
        service = _make_service(generations_limit=5, refines_limit=None, pages_limit=None)
        db = MagicMock(spec=Session)

        _apply_service_limits(user, service, db, commit=False)

        assert user.generations_limit == 6
        db.commit.assert_not_called()
