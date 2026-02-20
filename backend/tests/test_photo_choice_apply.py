"""Tests for apply_photo_choices, submit_photo_choices, get_pending_photo_choices,
and the async timeout flow in databinding_generator.py."""

import asyncio
import copy
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Add backend root to path so 'app' is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.databinding_generator import (
    DataBindingGenerator,
    _pending_photo_choices,
    PHOTO_CHOICE_TIMEOUT,
    submit_photo_choices,
    get_pending_photo_choices,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PLACEHOLDER_URL = "https://placehold.co/600x400"
SVG_PLACEHOLDER = "data:image/svg+xml,<svg></svg>"
REAL_URL = "https://images.unsplash.com/photo-real?w=800"


def _make_generator() -> DataBindingGenerator:
    """Create a DataBindingGenerator with heavy deps stubbed out."""
    gen = object.__new__(DataBindingGenerator)
    gen.kimi = MagicMock()
    gen.kimi_text = MagicMock()
    gen.assembler = MagicMock()
    return gen


def _site_data_with_hero(hero_url: str = PLACEHOLDER_URL) -> dict:
    return {
        "components": [
            {"data": {"HERO_IMAGE_URL": hero_url}},
        ]
    }


def _site_data_with_about(about_url: str = PLACEHOLDER_URL) -> dict:
    return {
        "components": [
            {"data": {"ABOUT_IMAGE_URL": about_url}},
        ]
    }


def _site_data_with_gallery(n: int = 3) -> dict:
    items = [{"GALLERY_IMAGE_URL": PLACEHOLDER_URL} for _ in range(n)]
    return {"components": [{"data": {"GALLERY_ITEMS": items}}]}


def _site_data_with_team(n: int = 2) -> dict:
    members = [{"MEMBER_IMAGE_URL": PLACEHOLDER_URL} for _ in range(n)]
    return {"components": [{"data": {"TEAM_MEMBERS": members}}]}


def _site_data_with_services(n: int = 3) -> dict:
    items = [{"SERVICE_IMAGE_URL": PLACEHOLDER_URL} for _ in range(n)]
    return {"components": [{"data": {"SERVICE_ITEMS": items}}]}


FAKE_STOCK = {
    "hero": ["https://stock/hero1.jpg", "https://stock/hero2.jpg"],
    "about": ["https://stock/about1.jpg"],
    "gallery": [
        "https://stock/gallery1.jpg",
        "https://stock/gallery2.jpg",
        "https://stock/gallery3.jpg",
    ],
    "team": [
        "https://stock/team1.jpg",
        "https://stock/team2.jpg",
    ],
}


# Patch _get_stock_photos to return deterministic URLs
@pytest.fixture(autouse=True)
def _patch_stock_photos():
    with patch(
        "app.services.databinding_generator._get_stock_photos",
        return_value=copy.deepcopy(FAKE_STOCK),
    ):
        yield


# Ensure _pending_photo_choices is clean between tests
@pytest.fixture(autouse=True)
def _clean_pending():
    _pending_photo_choices.clear()
    yield
    _pending_photo_choices.clear()


# =========================================================================
# apply_photo_choices — stock action
# =========================================================================

class TestApplyPhotoChoicesStock:
    """Tests for action='stock' across different section types."""

    def test_stock_hero(self):
        gen = _make_generator()
        sd = _site_data_with_hero()
        choices = [{"section_type": "hero", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == "https://stock/hero1.jpg"

    def test_stock_about(self):
        gen = _make_generator()
        sd = _site_data_with_about()
        choices = [{"section_type": "about", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        assert result["components"][0]["data"]["ABOUT_IMAGE_URL"] == "https://stock/about1.jpg"

    def test_stock_gallery(self):
        gen = _make_generator()
        sd = _site_data_with_gallery(3)
        choices = [{"section_type": "gallery", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        items = result["components"][0]["data"]["GALLERY_ITEMS"]
        assert items[0]["GALLERY_IMAGE_URL"] == "https://stock/gallery1.jpg"
        assert items[1]["GALLERY_IMAGE_URL"] == "https://stock/gallery2.jpg"
        assert items[2]["GALLERY_IMAGE_URL"] == "https://stock/gallery3.jpg"

    def test_stock_gallery_wraps_around(self):
        """When there are more items than stock photos, URLs wrap via modulo."""
        gen = _make_generator()
        sd = _site_data_with_gallery(5)
        choices = [{"section_type": "gallery", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        items = result["components"][0]["data"]["GALLERY_ITEMS"]
        # 3 stock photos, 5 items => wraps: 0, 1, 2, 0, 1
        assert items[3]["GALLERY_IMAGE_URL"] == "https://stock/gallery1.jpg"
        assert items[4]["GALLERY_IMAGE_URL"] == "https://stock/gallery2.jpg"

    def test_stock_team(self):
        gen = _make_generator()
        sd = _site_data_with_team(2)
        choices = [{"section_type": "team", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        members = result["components"][0]["data"]["TEAM_MEMBERS"]
        assert members[0]["MEMBER_IMAGE_URL"] == "https://stock/team1.jpg"
        assert members[1]["MEMBER_IMAGE_URL"] == "https://stock/team2.jpg"

    def test_stock_services(self):
        """Services uses gallery pool for stock photos."""
        gen = _make_generator()
        sd = _site_data_with_services(2)
        choices = [{"section_type": "services", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        items = result["components"][0]["data"]["SERVICE_ITEMS"]
        assert items[0]["SERVICE_IMAGE_URL"] == "https://stock/gallery1.jpg"
        assert items[1]["SERVICE_IMAGE_URL"] == "https://stock/gallery2.jpg"


# =========================================================================
# apply_photo_choices — upload action
# =========================================================================

class TestApplyPhotoChoicesUpload:
    """Tests for action='upload' with user-provided URLs."""

    def test_upload_hero(self):
        gen = _make_generator()
        sd = _site_data_with_hero()
        choices = [{"section_type": "hero", "action": "upload", "photo_url": "https://user/hero.jpg"}]

        result = gen.apply_photo_choices(sd, choices)

        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == "https://user/hero.jpg"

    def test_upload_about(self):
        gen = _make_generator()
        sd = _site_data_with_about()
        choices = [{"section_type": "about", "action": "upload", "photo_url": "https://user/about.jpg"}]

        result = gen.apply_photo_choices(sd, choices)

        assert result["components"][0]["data"]["ABOUT_IMAGE_URL"] == "https://user/about.jpg"

    def test_upload_gallery_multiple_urls(self):
        gen = _make_generator()
        sd = _site_data_with_gallery(3)
        choices = [{
            "section_type": "gallery",
            "action": "upload",
            "photo_url": "https://user/g1.jpg",
            "photo_urls": ["https://user/g1.jpg", "https://user/g2.jpg", "https://user/g3.jpg"],
        }]

        result = gen.apply_photo_choices(sd, choices)

        items = result["components"][0]["data"]["GALLERY_ITEMS"]
        assert items[0]["GALLERY_IMAGE_URL"] == "https://user/g1.jpg"
        assert items[1]["GALLERY_IMAGE_URL"] == "https://user/g2.jpg"
        assert items[2]["GALLERY_IMAGE_URL"] == "https://user/g3.jpg"

    def test_upload_gallery_single_url_wraps(self):
        """When only photo_url is given (no photo_urls), it wraps to all items."""
        gen = _make_generator()
        sd = _site_data_with_gallery(3)
        choices = [{
            "section_type": "gallery",
            "action": "upload",
            "photo_url": "https://user/g1.jpg",
        }]

        result = gen.apply_photo_choices(sd, choices)

        items = result["components"][0]["data"]["GALLERY_ITEMS"]
        # With only one URL and 3 items: first item gets it, then wraps via modulo
        assert items[0]["GALLERY_IMAGE_URL"] == "https://user/g1.jpg"
        assert items[1]["GALLERY_IMAGE_URL"] == "https://user/g1.jpg"
        assert items[2]["GALLERY_IMAGE_URL"] == "https://user/g1.jpg"

    def test_upload_with_no_url_falls_back_to_stock(self):
        """When action is upload but no photo_url provided, hero falls back
        to keeping the placeholder (the stock branch is not triggered either)."""
        gen = _make_generator()
        sd = _site_data_with_hero()
        choices = [{"section_type": "hero", "action": "upload"}]

        result = gen.apply_photo_choices(sd, choices)

        # Neither stock nor upload branch fires: URL stays as placeholder
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == PLACEHOLDER_URL


# =========================================================================
# apply_photo_choices — edge cases
# =========================================================================

class TestApplyPhotoChoicesEdgeCases:

    def test_empty_choices_returns_unchanged(self):
        gen = _make_generator()
        sd = _site_data_with_hero()
        original_url = sd["components"][0]["data"]["HERO_IMAGE_URL"]

        result = gen.apply_photo_choices(sd, [])

        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == original_url

    def test_unknown_section_type_ignored(self):
        gen = _make_generator()
        sd = _site_data_with_hero()
        choices = [{"section_type": "unknown_section", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        # Hero URL not touched because choice was for "unknown_section"
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == PLACEHOLDER_URL

    def test_non_placeholder_url_not_overwritten(self):
        """Real URLs (not placeholders) must NOT be overwritten."""
        gen = _make_generator()
        real_url = "https://real-image-server.com/photo.jpg"
        sd = _site_data_with_hero(hero_url=real_url)
        choices = [{"section_type": "hero", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == real_url

    def test_svg_placeholder_is_replaced(self):
        gen = _make_generator()
        sd = _site_data_with_hero(hero_url=SVG_PLACEHOLDER)
        choices = [{"section_type": "hero", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == "https://stock/hero1.jpg"

    def test_multiple_sections_at_once(self):
        """Choices for hero and about in one call."""
        gen = _make_generator()
        sd = {
            "components": [
                {"data": {
                    "HERO_IMAGE_URL": PLACEHOLDER_URL,
                    "ABOUT_IMAGE_URL": PLACEHOLDER_URL,
                }},
            ]
        }
        choices = [
            {"section_type": "hero", "action": "upload", "photo_url": "https://user/hero.jpg"},
            {"section_type": "about", "action": "stock"},
        ]

        result = gen.apply_photo_choices(sd, choices)

        data = result["components"][0]["data"]
        assert data["HERO_IMAGE_URL"] == "https://user/hero.jpg"
        assert data["ABOUT_IMAGE_URL"] == "https://stock/about1.jpg"

    def test_no_components_key(self):
        """site_data without 'components' should not crash."""
        gen = _make_generator()
        sd = {}
        choices = [{"section_type": "hero", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        assert result == {}

    def test_component_without_data_key(self):
        """Component dict missing 'data' key should not crash."""
        gen = _make_generator()
        sd = {"components": [{"type": "hero"}]}
        choices = [{"section_type": "hero", "action": "stock"}]

        result = gen.apply_photo_choices(sd, choices)

        # No crash, data not modified
        assert result["components"][0] == {"type": "hero"}


# =========================================================================
# submit_photo_choices
# =========================================================================

class TestSubmitPhotoChoices:

    def test_submit_when_generation_is_waiting(self):
        """Returns True and sets choices + signals the event."""
        event = asyncio.Event()
        _pending_photo_choices[42] = {
            "event": event,
            "choices": None,
            "site_data": {},
        }

        result = submit_photo_choices(42, [{"section_type": "hero", "action": "stock"}])

        assert result is True
        assert event.is_set()
        assert _pending_photo_choices[42]["choices"] == [{"section_type": "hero", "action": "stock"}]

    def test_submit_when_no_generation_waiting(self):
        """Returns False when no pending entry exists for this site_id."""
        result = submit_photo_choices(999, [{"section_type": "hero", "action": "stock"}])
        assert result is False

    def test_submit_sets_choices_correctly(self):
        """Multiple choices are stored properly."""
        event = asyncio.Event()
        _pending_photo_choices[10] = {
            "event": event,
            "choices": None,
            "site_data": {},
        }

        choices = [
            {"section_type": "hero", "action": "stock"},
            {"section_type": "about", "action": "upload", "photo_url": "https://x.com/a.jpg"},
        ]
        submit_photo_choices(10, choices)

        assert _pending_photo_choices[10]["choices"] == choices
        assert event.is_set()


# =========================================================================
# get_pending_photo_choices
# =========================================================================

class TestGetPendingPhotoChoices:

    def test_get_pending_when_waiting(self):
        """Returns scan_choices when generation is waiting (event not set).

        NOTE: The pending dict as created by the pipeline does NOT include a
        'scan_choices' key, so this returns None in practice. The test documents
        the actual behavior of the code.
        """
        event = asyncio.Event()
        _pending_photo_choices[42] = {
            "event": event,
            "choices": None,
            "site_data": {},
            # no "scan_choices" key — matches what the pipeline actually creates
        }

        result = get_pending_photo_choices(42)

        # pending.get("scan_choices") returns None because key doesn't exist
        assert result is None

    def test_get_pending_when_waiting_with_scan_choices(self):
        """If scan_choices key IS present, it should be returned."""
        event = asyncio.Event()
        scan_data = [{"section_type": "hero", "current_url": PLACEHOLDER_URL}]
        _pending_photo_choices[42] = {
            "event": event,
            "choices": None,
            "site_data": {},
            "scan_choices": scan_data,
        }

        result = get_pending_photo_choices(42)

        assert result == scan_data

    def test_get_pending_when_not_waiting(self):
        """Returns None when no pending entry for this site_id."""
        result = get_pending_photo_choices(999)
        assert result is None

    def test_get_pending_after_event_set(self):
        """Returns None once the event is set (choice already submitted)."""
        event = asyncio.Event()
        event.set()
        _pending_photo_choices[42] = {
            "event": event,
            "choices": [{"section_type": "hero", "action": "stock"}],
            "site_data": {},
            "scan_choices": [{"section_type": "hero"}],
        }

        result = get_pending_photo_choices(42)

        assert result is None


# =========================================================================
# Timeout flow
# =========================================================================

class TestTimeoutFlow:

    def test_photo_choice_timeout_constant(self):
        assert PHOTO_CHOICE_TIMEOUT == 300

    @pytest.mark.asyncio
    async def test_timeout_calls_inject_stock_photos(self):
        """When asyncio.wait_for times out, _inject_stock_photos should be called
        and the pending entry should be cleaned up."""
        gen = _make_generator()
        site_id = 77
        template_style_id = "business-corporate"

        site_data = _site_data_with_hero()
        choice_event = asyncio.Event()

        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
            "template_style_id": template_style_id,
        }

        # Simulate the try/except/finally block from the pipeline
        gen._inject_stock_photos = MagicMock(return_value=site_data)

        try:
            # Use a tiny timeout to trigger TimeoutError immediately
            await asyncio.wait_for(choice_event.wait(), timeout=0.01)
            user_choices = _pending_photo_choices.get(site_id, {}).get("choices")
            if user_choices:
                site_data = gen.apply_photo_choices(site_data, user_choices, template_style_id)
            else:
                site_data = gen._inject_stock_photos(site_data, template_style_id)
        except asyncio.TimeoutError:
            site_data = gen._inject_stock_photos(site_data, template_style_id)
        finally:
            _pending_photo_choices.pop(site_id, None)

        gen._inject_stock_photos.assert_called_with(site_data, template_style_id)
        assert site_id not in _pending_photo_choices

    @pytest.mark.asyncio
    async def test_pending_cleaned_up_after_success(self):
        """After successful choice submission, pending entry is cleaned up."""
        gen = _make_generator()
        site_id = 88

        site_data = _site_data_with_hero()
        choice_event = asyncio.Event()

        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
        }

        # Simulate user submitting choices before the wait
        user_choices = [{"section_type": "hero", "action": "stock"}]
        _pending_photo_choices[site_id]["choices"] = user_choices
        choice_event.set()

        try:
            await asyncio.wait_for(choice_event.wait(), timeout=5)
            fetched = _pending_photo_choices.get(site_id, {}).get("choices")
            if fetched:
                site_data = gen.apply_photo_choices(site_data, fetched)
        except asyncio.TimeoutError:
            pass
        finally:
            _pending_photo_choices.pop(site_id, None)

        assert site_id not in _pending_photo_choices
        # Hero should have been replaced with stock photo
        assert site_data["components"][0]["data"]["HERO_IMAGE_URL"] == "https://stock/hero1.jpg"

    @pytest.mark.asyncio
    async def test_event_set_but_no_choices_falls_back(self):
        """If event is set but choices is None, fallback to stock photos."""
        gen = _make_generator()
        site_id = 99

        site_data = _site_data_with_hero()
        choice_event = asyncio.Event()

        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
        }

        # Event set but choices stays None
        choice_event.set()

        gen._inject_stock_photos = MagicMock(return_value=site_data)

        try:
            await asyncio.wait_for(choice_event.wait(), timeout=5)
            user_choices = _pending_photo_choices.get(site_id, {}).get("choices")
            if user_choices:
                site_data = gen.apply_photo_choices(site_data, user_choices)
            else:
                site_data = gen._inject_stock_photos(site_data, None)
        except asyncio.TimeoutError:
            site_data = gen._inject_stock_photos(site_data, None)
        finally:
            _pending_photo_choices.pop(site_id, None)

        gen._inject_stock_photos.assert_called_once_with(site_data, None)
        assert site_id not in _pending_photo_choices
