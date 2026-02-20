"""
Tests for POST /api/generate/{site_id}/photo-choices endpoint.

Covers:
- Pydantic schema validation (valid/invalid payloads)
- Authorization (no token, wrong user, correct user)
- Business logic (site status, not found, no pending generation, valid submission)
- URL validation (SSRF protection: https, data:, javascript:, file://)
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.site import Site


# ============ FIXTURES ============

def _make_user(id=1, is_active=True):
    """Create a mock User object."""
    user = MagicMock(spec=User)
    user.id = id
    user.email = "test@example.com"
    user.is_active = is_active
    user.is_premium = False
    user.is_superuser = False
    return user


def _make_site(id=10, owner_id=1, status="generating"):
    """Create a mock Site object."""
    site = MagicMock(spec=Site)
    site.id = id
    site.owner_id = owner_id
    site.status = status
    return site


@pytest.fixture()
def mock_user():
    return _make_user()


@pytest.fixture()
def mock_db():
    """Return a mock DB session."""
    return MagicMock()


@pytest.fixture()
def client(mock_user, mock_db):
    """TestClient with auth and DB dependencies overridden."""

    async def _override_auth():
        return mock_user

    def _override_db():
        yield mock_db

    app.dependency_overrides[get_current_active_user] = _override_auth
    app.dependency_overrides[get_db] = _override_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def unauth_client():
    """TestClient with NO auth override (token required)."""
    app.dependency_overrides.pop(get_current_active_user, None)
    app.dependency_overrides.pop(get_db, None)
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


# ============ HELPERS ============

ENDPOINT = "/api/generate/{site_id}/photo-choices"

VALID_PAYLOAD = {
    "choices": [
        {"section_type": "hero", "action": "stock"},
    ]
}


def _setup_site_found(mock_db, site):
    """Configure mock_db so query().filter().first() returns the given site."""
    query = MagicMock()
    mock_db.query.return_value = query
    query.filter.return_value = query
    query.first.return_value = site


def _setup_site_not_found(mock_db):
    """Configure mock_db so query().filter().first() returns None."""
    query = MagicMock()
    mock_db.query.return_value = query
    query.filter.return_value = query
    query.first.return_value = None


# ============ SCHEMA VALIDATION (Pydantic) ============

class TestSchemaValidation:
    """Pydantic validation of PhotoChoiceRequest body."""

    @patch("app.api.routes.generate.submit_photo_choices", return_value=True, create=True)
    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_valid_payload_returns_200(self, mock_submit_mod, mock_submit_route, client, mock_db):
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        resp = client.post(ENDPOINT.format(site_id=10), json=VALID_PAYLOAD)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["choices_count"] == 1

    def test_wrong_key_decisions_returns_422(self, client):
        """Using 'decisions' instead of 'choices' must fail validation."""
        resp = client.post(
            ENDPOINT.format(site_id=10),
            json={"decisions": [{"section_type": "hero", "action": "stock"}]},
        )
        assert resp.status_code == 422

    def test_missing_action_field_returns_422(self, client):
        resp = client.post(
            ENDPOINT.format(site_id=10),
            json={"choices": [{"section_type": "hero"}]},
        )
        assert resp.status_code == 422

    def test_missing_section_type_returns_422(self, client):
        resp = client.post(
            ENDPOINT.format(site_id=10),
            json={"choices": [{"action": "stock"}]},
        )
        assert resp.status_code == 422

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_empty_choices_array_returns_200(self, mock_submit, client, mock_db):
        """Empty choices list is structurally valid."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        resp = client.post(ENDPOINT.format(site_id=10), json={"choices": []})
        assert resp.status_code == 200
        assert resp.json()["choices_count"] == 0

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_extra_fields_ignored(self, mock_submit, client, mock_db):
        """Extra fields in the payload should be silently ignored by Pydantic."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [{"section_type": "hero", "action": "stock"}],
            "extra_field": "should be ignored",
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200

    def test_completely_empty_body_returns_422(self, client):
        resp = client.post(ENDPOINT.format(site_id=10), json={})
        assert resp.status_code == 422

    def test_no_body_returns_422(self, client):
        resp = client.post(
            ENDPOINT.format(site_id=10),
            content=b"",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422


# ============ AUTHORIZATION ============

class TestAuthorization:

    def test_no_auth_token_returns_401(self, unauth_client):
        """Requests without Bearer token should be rejected."""
        resp = unauth_client.post(
            ENDPOINT.format(site_id=10),
            json=VALID_PAYLOAD,
        )
        assert resp.status_code == 401

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_correct_user_gets_200(self, mock_submit, client, mock_db, mock_user):
        """Authenticated user who owns the site gets 200."""
        site = _make_site(id=10, owner_id=mock_user.id, status="generating")
        _setup_site_found(mock_db, site)

        resp = client.post(ENDPOINT.format(site_id=10), json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_wrong_user_site_not_found_returns_404(self, client, mock_db, mock_user):
        """Authenticated user who does NOT own the site gets 404."""
        # DB returns None because owner_id filter doesn't match
        _setup_site_not_found(mock_db)

        resp = client.post(ENDPOINT.format(site_id=999), json=VALID_PAYLOAD)
        assert resp.status_code == 404


# ============ BUSINESS LOGIC ============

class TestBusinessLogic:

    def test_site_not_found_returns_404(self, client, mock_db):
        _setup_site_not_found(mock_db)

        resp = client.post(ENDPOINT.format(site_id=999), json=VALID_PAYLOAD)
        assert resp.status_code == 404
        assert "non trovato" in resp.json()["detail"]

    def test_site_status_not_generating_returns_400(self, client, mock_db):
        site = _make_site(id=10, owner_id=1, status="ready")
        _setup_site_found(mock_db, site)

        resp = client.post(ENDPOINT.format(site_id=10), json=VALID_PAYLOAD)
        assert resp.status_code == 400
        assert "generazione" in resp.json()["detail"]

    def test_site_status_draft_returns_400(self, client, mock_db):
        site = _make_site(id=10, owner_id=1, status="draft")
        _setup_site_found(mock_db, site)

        resp = client.post(ENDPOINT.format(site_id=10), json=VALID_PAYLOAD)
        assert resp.status_code == 400

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=False)
    def test_no_pending_generation_returns_409(self, mock_submit, client, mock_db):
        """When pipeline is NOT waiting for choices, submit returns False -> 409."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        resp = client.post(ENDPOINT.format(site_id=10), json=VALID_PAYLOAD)
        assert resp.status_code == 409
        assert "attesa" in resp.json()["detail"]

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_valid_submission_returns_200(self, mock_submit, client, mock_db):
        """Happy path: pipeline is waiting, choices accepted."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {"section_type": "hero", "action": "stock"},
                {"section_type": "about", "action": "upload", "photo_url": "https://example.com/photo.jpg"},
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["choices_count"] == 2
        # Verify submit_photo_choices was called with correct args
        mock_submit.assert_called_once()
        call_args = mock_submit.call_args
        assert call_args[0][0] == 10  # site_id
        assert len(call_args[0][1]) == 2  # 2 choices

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_multiple_sections_in_single_request(self, mock_submit, client, mock_db):
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {"section_type": "hero", "action": "stock"},
                {"section_type": "about", "action": "stock"},
                {"section_type": "gallery", "action": "upload", "photo_urls": [
                    "https://example.com/a.jpg",
                    "https://example.com/b.jpg",
                ]},
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        assert resp.json()["choices_count"] == 3


# ============ URL VALIDATION (SSRF PROTECTION) ============

class TestURLValidation:

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_upload_with_valid_https_url(self, mock_submit, client, mock_db):
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {
                    "section_type": "hero",
                    "action": "upload",
                    "photo_url": "https://images.unsplash.com/photo-123.jpg",
                }
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        # URL should be preserved in the validated choices
        submitted = mock_submit.call_args[0][1]
        assert submitted[0]["action"] == "upload"
        assert submitted[0]["photo_url"] == "https://images.unsplash.com/photo-123.jpg"

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_upload_with_valid_data_url(self, mock_submit, client, mock_db):
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        data_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEU"
        payload = {
            "choices": [
                {"section_type": "hero", "action": "upload", "photo_url": data_url}
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        submitted = mock_submit.call_args[0][1]
        assert submitted[0]["action"] == "upload"
        assert submitted[0]["photo_url"] == data_url

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_upload_with_javascript_url_falls_back_to_stock(self, mock_submit, client, mock_db):
        """javascript: URLs must be rejected (SSRF). Action should fall back to stock."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {"section_type": "hero", "action": "upload", "photo_url": "javascript:alert(1)"}
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        submitted = mock_submit.call_args[0][1]
        # Should have fallen back to stock because URL was invalid
        assert submitted[0]["action"] == "stock"

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_upload_with_file_url_falls_back_to_stock(self, mock_submit, client, mock_db):
        """file:// URLs must be rejected (SSRF)."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {"section_type": "hero", "action": "upload", "photo_url": "file:///etc/passwd"}
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        submitted = mock_submit.call_args[0][1]
        assert submitted[0]["action"] == "stock"

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_upload_with_no_url_falls_back_to_stock(self, mock_submit, client, mock_db):
        """Upload without any photo_url should fall back to stock."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {"section_type": "hero", "action": "upload"}
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        submitted = mock_submit.call_args[0][1]
        assert submitted[0]["action"] == "stock"

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_upload_with_localhost_url_falls_back_to_stock(self, mock_submit, client, mock_db):
        """Internal network URLs (localhost) must be blocked."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {"section_type": "hero", "action": "upload", "photo_url": "http://localhost:8080/admin"}
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        submitted = mock_submit.call_args[0][1]
        assert submitted[0]["action"] == "stock"

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_upload_with_private_ip_falls_back_to_stock(self, mock_submit, client, mock_db):
        """Private IP ranges (192.168.x.x, 10.x.x.x) must be blocked."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {"section_type": "hero", "action": "upload", "photo_url": "http://192.168.1.1/image.jpg"}
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        submitted = mock_submit.call_args[0][1]
        assert submitted[0]["action"] == "stock"

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_upload_multiple_urls_filters_invalid(self, mock_submit, client, mock_db):
        """photo_urls list: invalid URLs should be filtered out, valid ones kept."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {
                    "section_type": "gallery",
                    "action": "upload",
                    "photo_urls": [
                        "https://example.com/valid.jpg",
                        "javascript:alert(1)",
                        "https://example.com/also-valid.jpg",
                        "file:///etc/shadow",
                    ],
                }
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        submitted = mock_submit.call_args[0][1]
        # Only the 2 valid HTTPS URLs should remain
        assert submitted[0]["action"] == "upload"
        valid_urls = submitted[0]["photo_urls"]
        assert len(valid_urls) == 2
        assert "https://example.com/valid.jpg" in valid_urls
        assert "https://example.com/also-valid.jpg" in valid_urls

    @patch("app.services.databinding_generator.submit_photo_choices", return_value=True)
    def test_stock_action_ignores_photo_url(self, mock_submit, client, mock_db):
        """When action=stock, photo_url is not validated/included."""
        site = _make_site(id=10, owner_id=1, status="generating")
        _setup_site_found(mock_db, site)

        payload = {
            "choices": [
                {"section_type": "hero", "action": "stock", "photo_url": "javascript:alert(1)"}
            ]
        }
        resp = client.post(ENDPOINT.format(site_id=10), json=payload)
        assert resp.status_code == 200
        submitted = mock_submit.call_args[0][1]
        # Action stays stock; the malicious URL is not processed
        assert submitted[0]["action"] == "stock"
        assert "photo_url" not in submitted[0]


# ============ _validate_image_url UNIT TESTS ============

class TestValidateImageUrl:
    """Direct unit tests for the _validate_image_url helper."""

    def setup_method(self):
        from app.api.routes.generate import _validate_image_url
        self.validate = _validate_image_url

    def test_https_url_valid(self):
        assert self.validate("https://images.unsplash.com/photo.jpg") is True

    def test_http_url_valid(self):
        assert self.validate("http://example.com/photo.jpg") is True

    def test_data_image_url_valid(self):
        assert self.validate("data:image/png;base64,abc123") is True

    def test_data_non_image_invalid(self):
        # data:text/html should NOT be accepted
        assert self.validate("data:text/html,<script>alert(1)</script>") is False

    def test_javascript_url_invalid(self):
        assert self.validate("javascript:alert(1)") is False

    def test_file_url_invalid(self):
        assert self.validate("file:///etc/passwd") is False

    def test_ftp_url_invalid(self):
        assert self.validate("ftp://example.com/image.jpg") is False

    def test_localhost_blocked(self):
        assert self.validate("http://localhost/img.jpg") is False

    def test_127_0_0_1_blocked(self):
        assert self.validate("http://127.0.0.1/img.jpg") is False

    def test_private_192_168_blocked(self):
        assert self.validate("http://192.168.1.1/img.jpg") is False

    def test_private_10_blocked(self):
        assert self.validate("http://10.0.0.1/img.jpg") is False

    def test_private_172_16_blocked(self):
        assert self.validate("http://172.16.0.1/img.jpg") is False

    def test_metadata_169_254_blocked(self):
        assert self.validate("http://169.254.169.254/latest/meta-data/") is False

    def test_ipv6_loopback_blocked(self):
        # IPv6 loopback is blocked — validator checks for both "::1" and "[::1]"
        assert self.validate("http://[::1]/img.jpg") is False
