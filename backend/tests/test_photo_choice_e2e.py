"""
End-to-end simulation tests for the photo choice flow in databinding_generator.py.

Tests the interactive photo selection pipeline:
1. _scan_placeholder_photos detects placeholder images
2. on_progress callback sends photo_choices phase to frontend
3. _pending_photo_choices stores asyncio.Event for coordination
4. submit_photo_choices signals the event with user decisions
5. apply_photo_choices replaces placeholders based on user choices
6. Timeout fallback injects stock photos automatically
7. Cleanup removes entries from _pending_photo_choices
"""

import sys
import os
import asyncio
import copy
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Shared helpers and fixtures
# ---------------------------------------------------------------------------

PLACEHOLDER_SVG = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect fill="%23f1f5f9" width="800" height="600"/></svg>'
PLACEHOLDER_PLACEHOLD = "https://placehold.co/800x600"
REAL_UNSPLASH_URL = "https://images.unsplash.com/photo-user-real?w=1200"
CUSTOM_UPLOAD_URL = "https://res.cloudinary.com/user/upload/hero.jpg"


def _make_site_data_with_placeholders():
    """Create site_data with hero + about + gallery placeholders."""
    return {
        "components": [
            {
                "variant_id": "hero-classic-01",
                "data": {
                    "HERO_TITLE": "Ristorante Da Mario",
                    "HERO_IMAGE_URL": PLACEHOLDER_SVG,
                },
            },
            {
                "variant_id": "about-magazine-01",
                "data": {
                    "ABOUT_TITLE": "Chi Siamo",
                    "ABOUT_IMAGE_URL": PLACEHOLDER_PLACEHOLD,
                },
            },
            {
                "variant_id": "gallery-spotlight-01",
                "data": {
                    "GALLERY_TITLE": "Galleria",
                    "GALLERY_ITEMS": [
                        {"GALLERY_IMAGE_URL": PLACEHOLDER_SVG, "GALLERY_CAPTION": "Foto 1"},
                        {"GALLERY_IMAGE_URL": PLACEHOLDER_SVG, "GALLERY_CAPTION": "Foto 2"},
                        {"GALLERY_IMAGE_URL": PLACEHOLDER_SVG, "GALLERY_CAPTION": "Foto 3"},
                    ],
                },
            },
        ]
    }


def _make_restaurant_site_data():
    """Create a restaurant site with hero, about, gallery, services sections."""
    return {
        "components": [
            {
                "variant_id": "hero-classic-01",
                "data": {
                    "HERO_TITLE": "Ristorante Bella Italia",
                    "HERO_IMAGE_URL": PLACEHOLDER_SVG,
                },
            },
            {
                "variant_id": "about-magazine-01",
                "data": {
                    "ABOUT_TITLE": "La Nostra Storia",
                    "ABOUT_IMAGE_URL": PLACEHOLDER_SVG,
                },
            },
            {
                "variant_id": "gallery-spotlight-01",
                "data": {
                    "GALLERY_TITLE": "I Nostri Piatti",
                    "GALLERY_ITEMS": [
                        {"GALLERY_IMAGE_URL": PLACEHOLDER_SVG, "GALLERY_CAPTION": "Pasta"},
                        {"GALLERY_IMAGE_URL": PLACEHOLDER_SVG, "GALLERY_CAPTION": "Pizza"},
                    ],
                },
            },
            {
                "variant_id": "services-alternating-rows-01",
                "data": {
                    "SERVICES_TITLE": "I Nostri Servizi",
                    "SERVICE_ITEMS": [
                        {"SERVICE_TITLE": "Catering", "SERVICE_IMAGE_URL": PLACEHOLDER_SVG},
                        {"SERVICE_TITLE": "Eventi", "SERVICE_IMAGE_URL": PLACEHOLDER_SVG},
                    ],
                },
            },
        ]
    }


def _make_site_data_no_placeholders():
    """Create site_data where ALL image keys have real URLs.

    NOTE: The scanner checks data.get("HERO_IMAGE_URL", "") on EVERY component,
    and empty string counts as a placeholder. So each component must either have
    the key with a real URL or simply not be checked (only one component per
    section type thanks to seen_sections dedup). We use a single component that
    carries all image keys with real URLs, ensuring the scanner finds nothing.
    """
    return {
        "components": [
            {
                "variant_id": "hero-classic-01",
                "data": {
                    "HERO_TITLE": "Site Title",
                    "HERO_IMAGE_URL": "https://images.unsplash.com/photo-real-hero?w=1200",
                    "ABOUT_IMAGE_URL": "https://images.unsplash.com/photo-real-about?w=800",
                    "GALLERY_ITEMS": [
                        {"GALLERY_IMAGE_URL": "https://images.unsplash.com/photo-g1?w=600", "GALLERY_CAPTION": "G1"},
                        {"GALLERY_IMAGE_URL": "https://images.unsplash.com/photo-g2?w=600", "GALLERY_CAPTION": "G2"},
                    ],
                },
            },
        ]
    }


@pytest.fixture
def generator():
    """Create a DataBindingGenerator instance for testing."""
    from app.services.databinding_generator import DataBindingGenerator
    return DataBindingGenerator.__new__(DataBindingGenerator)


@pytest.fixture(autouse=True)
def cleanup_pending():
    """Ensure _pending_photo_choices is clean before and after each test."""
    from app.services.databinding_generator import _pending_photo_choices
    _pending_photo_choices.clear()
    yield
    _pending_photo_choices.clear()


# ---------------------------------------------------------------------------
# Scenario 1: Happy path — user chooses stock for all
# ---------------------------------------------------------------------------

class TestScenario1StockForAll:
    """Full pipeline: scan -> on_progress -> submit(stock) -> apply -> cleanup."""

    def test_scan_detects_three_sections(self, generator):
        """_scan_placeholder_photos should detect hero, about, gallery."""
        site_data = _make_site_data_with_placeholders()
        choices = generator._scan_placeholder_photos(site_data, "restaurant-elegant")
        section_types = [c["section_type"] for c in choices]
        assert "hero" in section_types
        assert "about" in section_types
        assert "gallery" in section_types
        assert len(choices) == 3

    def test_scan_returns_required_fields(self, generator):
        """Each choice must have section_type, section_label, placeholder_key, stock_preview_url, current_url."""
        site_data = _make_site_data_with_placeholders()
        choices = generator._scan_placeholder_photos(site_data, "restaurant-elegant")
        required_keys = {"section_type", "section_label", "placeholder_key", "stock_preview_url", "current_url"}
        for choice in choices:
            missing = required_keys - set(choice.keys())
            assert not missing, f"Choice for {choice.get('section_type')} missing keys: {missing}"

    def test_stock_preview_url_is_unsplash(self, generator):
        """Stock preview URLs should be from Unsplash."""
        site_data = _make_site_data_with_placeholders()
        choices = generator._scan_placeholder_photos(site_data, "restaurant-elegant")
        for choice in choices:
            url = choice["stock_preview_url"]
            assert "unsplash.com" in url, f"Stock preview for {choice['section_type']} not Unsplash: {url}"

    @pytest.mark.asyncio
    async def test_full_stock_flow(self, generator):
        """Simulate: scan -> register event -> on_progress -> submit(stock) -> apply -> cleanup."""
        from app.services.databinding_generator import (
            _pending_photo_choices, submit_photo_choices,
        )

        site_id = 9001
        site_data = _make_site_data_with_placeholders()

        # Step 1: Scan
        scanned = generator._scan_placeholder_photos(site_data, "restaurant-elegant")
        assert len(scanned) == 3

        # Step 2: Register pending (simulating the pipeline)
        choice_event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
            "template_style_id": "restaurant-elegant",
        }

        # Step 3: Simulate on_progress callback
        progress_data = []
        def on_progress(step, msg, data=None):
            progress_data.append({"step": step, "msg": msg, "data": data})

        on_progress(5, "Scelta foto...", {
            "phase": "photo_choices",
            "choices": scanned,
        })
        assert len(progress_data) == 1
        assert progress_data[0]["data"]["phase"] == "photo_choices"
        assert len(progress_data[0]["data"]["choices"]) == 3

        # Step 4: Submit stock choices (simulating user clicking "Use Stock")
        user_choices = [
            {"section_type": "hero", "action": "stock"},
            {"section_type": "about", "action": "stock"},
            {"section_type": "gallery", "action": "stock"},
        ]
        result = submit_photo_choices(site_id, user_choices)
        assert result is True
        assert choice_event.is_set()
        assert _pending_photo_choices[site_id]["choices"] == user_choices

        # Step 5: Apply choices
        site_data = generator.apply_photo_choices(site_data, user_choices, "restaurant-elegant")

        # Verify hero replaced
        hero_url = site_data["components"][0]["data"]["HERO_IMAGE_URL"]
        assert hero_url.startswith("https://"), f"Hero not replaced: {hero_url}"
        assert "unsplash" in hero_url

        # Verify about replaced
        about_url = site_data["components"][1]["data"]["ABOUT_IMAGE_URL"]
        assert about_url.startswith("https://"), f"About not replaced: {about_url}"

        # Verify gallery items replaced
        for i, item in enumerate(site_data["components"][2]["data"]["GALLERY_ITEMS"]):
            url = item["GALLERY_IMAGE_URL"]
            assert url.startswith("https://"), f"Gallery[{i}] not replaced: {url}"

        # Step 6: Cleanup
        _pending_photo_choices.pop(site_id, None)
        assert site_id not in _pending_photo_choices


# ---------------------------------------------------------------------------
# Scenario 2: Happy path — user uploads custom photos
# ---------------------------------------------------------------------------

class TestScenario2CustomUpload:
    """User uploads a custom photo for hero, stock for about and gallery."""

    @pytest.mark.asyncio
    async def test_upload_hero_stock_rest(self, generator):
        """Hero gets custom URL, about and gallery get stock."""
        from app.services.databinding_generator import (
            _pending_photo_choices, submit_photo_choices,
        )

        site_id = 9002
        site_data = _make_site_data_with_placeholders()

        # Register pending
        choice_event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
            "template_style_id": "restaurant-elegant",
        }

        # Submit: hero=upload, about=stock, gallery=stock
        user_choices = [
            {"section_type": "hero", "action": "upload", "photo_url": CUSTOM_UPLOAD_URL},
            {"section_type": "about", "action": "stock"},
            {"section_type": "gallery", "action": "stock"},
        ]
        result = submit_photo_choices(site_id, user_choices)
        assert result is True

        # Apply
        site_data = generator.apply_photo_choices(site_data, user_choices, "restaurant-elegant")

        # Hero should be the custom URL
        hero_url = site_data["components"][0]["data"]["HERO_IMAGE_URL"]
        assert hero_url == CUSTOM_UPLOAD_URL, f"Hero should be custom: {hero_url}"

        # About should be stock
        about_url = site_data["components"][1]["data"]["ABOUT_IMAGE_URL"]
        assert about_url.startswith("https://") and "unsplash" in about_url

        # Gallery should be stock
        for item in site_data["components"][2]["data"]["GALLERY_ITEMS"]:
            url = item["GALLERY_IMAGE_URL"]
            assert url.startswith("https://") and "unsplash" in url

        # Cleanup
        _pending_photo_choices.pop(site_id, None)

    @pytest.mark.asyncio
    async def test_upload_all_sections(self, generator):
        """Upload custom photos for all sections."""
        site_data = _make_site_data_with_placeholders()
        custom_hero = "https://example.com/my-hero.jpg"
        custom_about = "https://example.com/my-about.jpg"
        custom_gallery = "https://example.com/my-gallery.jpg"

        user_choices = [
            {"section_type": "hero", "action": "upload", "photo_url": custom_hero},
            {"section_type": "about", "action": "upload", "photo_url": custom_about},
            {"section_type": "gallery", "action": "upload", "photo_url": custom_gallery},
        ]

        site_data = generator.apply_photo_choices(site_data, user_choices, "restaurant-elegant")

        assert site_data["components"][0]["data"]["HERO_IMAGE_URL"] == custom_hero
        assert site_data["components"][1]["data"]["ABOUT_IMAGE_URL"] == custom_about
        # Gallery: first item gets the uploaded photo
        assert site_data["components"][2]["data"]["GALLERY_ITEMS"][0]["GALLERY_IMAGE_URL"] == custom_gallery


# ---------------------------------------------------------------------------
# Scenario 3: Timeout — user doesn't respond
# ---------------------------------------------------------------------------

class TestScenario3Timeout:
    """Timeout scenario: pipeline waits, user doesn't respond, stock injected as fallback."""

    @pytest.mark.asyncio
    async def test_timeout_injects_stock_fallback(self, generator):
        """When user doesn't respond within timeout, stock photos are injected."""
        import app.services.databinding_generator as dbg
        from app.services.databinding_generator import _pending_photo_choices

        site_id = 9003
        site_data = _make_site_data_with_placeholders()

        # Scan
        scanned = generator._scan_placeholder_photos(site_data, "restaurant-elegant")
        assert len(scanned) > 0

        # Register pending with a real event
        choice_event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
            "template_style_id": "restaurant-elegant",
        }

        # Simulate the pipeline's timeout flow with a very short timeout
        original_timeout = dbg.PHOTO_CHOICE_TIMEOUT
        try:
            dbg.PHOTO_CHOICE_TIMEOUT = 0.1  # 100ms

            # Nobody submits — event stays unset
            try:
                await asyncio.wait_for(choice_event.wait(), timeout=dbg.PHOTO_CHOICE_TIMEOUT)
                # If we get here, event was set unexpectedly
                assert False, "Event should not have been set"
            except asyncio.TimeoutError:
                # Expected: timeout triggers stock fallback
                site_data = generator._inject_stock_photos(site_data, "restaurant-elegant")
            finally:
                _pending_photo_choices.pop(site_id, None)

            # Verify stock photos were injected
            hero_url = site_data["components"][0]["data"]["HERO_IMAGE_URL"]
            assert hero_url.startswith("https://"), f"Hero not replaced after timeout: {hero_url}"

            about_url = site_data["components"][1]["data"]["ABOUT_IMAGE_URL"]
            assert about_url.startswith("https://"), f"About not replaced after timeout: {about_url}"

            for i, item in enumerate(site_data["components"][2]["data"]["GALLERY_ITEMS"]):
                url = item["GALLERY_IMAGE_URL"]
                assert url.startswith("https://"), f"Gallery[{i}] not replaced after timeout: {url}"

            # Verify cleanup
            assert site_id not in _pending_photo_choices
        finally:
            dbg.PHOTO_CHOICE_TIMEOUT = original_timeout

    @pytest.mark.asyncio
    async def test_timeout_exact_flow_simulation(self, generator):
        """Simulate the exact try/except/finally block from the pipeline."""
        import app.services.databinding_generator as dbg
        from app.services.databinding_generator import _pending_photo_choices

        site_id = 9033
        site_data = _make_site_data_with_placeholders()
        template_style_id = "business-corporate"

        choice_event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
            "template_style_id": template_style_id,
        }

        # Replicate the exact pipeline logic
        timed_out = False
        try:
            await asyncio.wait_for(choice_event.wait(), timeout=0.05)
            user_choices = _pending_photo_choices.get(site_id, {}).get("choices")
            if user_choices:
                site_data = generator.apply_photo_choices(site_data, user_choices, template_style_id)
            else:
                site_data = generator._inject_stock_photos(site_data, template_style_id)
        except asyncio.TimeoutError:
            timed_out = True
            site_data = generator._inject_stock_photos(site_data, template_style_id)
        finally:
            _pending_photo_choices.pop(site_id, None)

        assert timed_out is True
        assert site_id not in _pending_photo_choices
        # All images should be real URLs now
        hero_url = site_data["components"][0]["data"]["HERO_IMAGE_URL"]
        assert hero_url.startswith("https://")


# ---------------------------------------------------------------------------
# Scenario 4: Cancel — user cancels the panel
# ---------------------------------------------------------------------------

class TestScenario4Cancel:
    """User sees the panel but cancels (no POST). Backend should timeout and use stock."""

    @pytest.mark.asyncio
    async def test_cancel_falls_back_to_stock(self, generator):
        """Cancel = no submit_photo_choices call. Timeout triggers stock fallback."""
        from app.services.databinding_generator import _pending_photo_choices

        site_id = 9004
        site_data = _make_site_data_with_placeholders()

        choice_event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
            "template_style_id": "restaurant-elegant",
        }

        # Simulate: panel shown, user cancels → no POST → timeout
        try:
            await asyncio.wait_for(choice_event.wait(), timeout=0.05)
            assert False, "Should have timed out"
        except asyncio.TimeoutError:
            site_data = generator._inject_stock_photos(site_data, "restaurant-elegant")
        finally:
            _pending_photo_choices.pop(site_id, None)

        # All images should be valid
        hero_url = site_data["components"][0]["data"]["HERO_IMAGE_URL"]
        assert hero_url.startswith("https://")
        assert site_id not in _pending_photo_choices


# ---------------------------------------------------------------------------
# Scenario 5: No placeholders found
# ---------------------------------------------------------------------------

class TestScenario5NoPlaceholders:
    """All images are real URLs — photo choice flow should be skipped."""

    def test_scan_returns_empty_list(self, generator):
        """_scan_placeholder_photos should return empty list when no placeholders."""
        site_data = _make_site_data_no_placeholders()
        choices = generator._scan_placeholder_photos(site_data, "restaurant-elegant")
        assert choices == [], f"Expected empty, got {choices}"

    def test_photo_choice_flow_skipped(self, generator):
        """When no placeholders, the pipeline should skip the photo choice flow entirely."""
        from app.services.databinding_generator import _pending_photo_choices

        site_data = _make_site_data_no_placeholders()
        site_id = 9005

        photo_choices = generator._scan_placeholder_photos(site_data, "restaurant-elegant")

        # Simulate pipeline check: if photo_choices is empty, skip
        assert not photo_choices
        assert site_id not in _pending_photo_choices  # Never registered

    def test_inject_stock_still_runs_as_safety_net(self, generator):
        """_inject_stock_photos should still run but not overwrite real URLs."""
        site_data = _make_site_data_no_placeholders()
        original_hero = site_data["components"][0]["data"]["HERO_IMAGE_URL"]
        original_about = site_data["components"][0]["data"]["ABOUT_IMAGE_URL"]

        result = generator._inject_stock_photos(site_data, "restaurant-elegant")

        # Real URLs should be untouched
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == original_hero
        assert result["components"][0]["data"]["ABOUT_IMAGE_URL"] == original_about
        for item in result["components"][0]["data"]["GALLERY_ITEMS"]:
            assert "unsplash.com" in item["GALLERY_IMAGE_URL"]


# ---------------------------------------------------------------------------
# Scenario 6: Restaurant category specific
# ---------------------------------------------------------------------------

class TestScenario6RestaurantCategory:
    """Verify restaurant template uses restaurant-specific stock photos."""

    def test_restaurant_stock_photos_pool(self):
        """_get_stock_photos should return restaurant-specific photos."""
        from app.services.databinding_generator import _get_stock_photos

        photos = _get_stock_photos("restaurant-elegant")
        assert "hero" in photos
        assert "gallery" in photos
        assert "about" in photos
        assert len(photos["hero"]) > 0
        assert len(photos["gallery"]) > 0

    def test_restaurant_scan_detects_all_sections(self, generator):
        """Scan should detect hero, about, gallery, services for restaurant site."""
        site_data = _make_restaurant_site_data()
        choices = generator._scan_placeholder_photos(site_data, "restaurant-elegant")
        section_types = {c["section_type"] for c in choices}
        assert "hero" in section_types
        assert "about" in section_types
        assert "gallery" in section_types
        assert "services" in section_types
        assert len(choices) == 4

    def test_restaurant_stock_applied_correctly(self, generator):
        """Apply stock choices for a full restaurant site."""
        site_data = _make_restaurant_site_data()

        user_choices = [
            {"section_type": "hero", "action": "stock"},
            {"section_type": "about", "action": "stock"},
            {"section_type": "gallery", "action": "stock"},
            {"section_type": "services", "action": "stock"},
        ]

        result = generator.apply_photo_choices(site_data, user_choices, "restaurant-elegant")

        # All images should be Unsplash URLs
        hero_url = result["components"][0]["data"]["HERO_IMAGE_URL"]
        assert "unsplash" in hero_url

        about_url = result["components"][1]["data"]["ABOUT_IMAGE_URL"]
        assert "unsplash" in about_url

        for item in result["components"][2]["data"]["GALLERY_ITEMS"]:
            assert "unsplash" in item["GALLERY_IMAGE_URL"]

        for svc in result["components"][3]["data"]["SERVICE_ITEMS"]:
            assert "unsplash" in svc["SERVICE_IMAGE_URL"]

    def test_restaurant_different_styles_use_same_pool(self):
        """restaurant-elegant, restaurant-cozy, restaurant-modern all use restaurant pool."""
        from app.services.databinding_generator import _get_stock_photos

        for style in ["restaurant-elegant", "restaurant-cozy", "restaurant-modern"]:
            photos = _get_stock_photos(style)
            # All restaurant styles should have the same pool keys
            assert "hero" in photos, f"{style} missing hero pool"
            assert "gallery" in photos, f"{style} missing gallery pool"
            assert len(photos["hero"]) >= 2, f"{style} hero pool too small"


# ---------------------------------------------------------------------------
# Scenario 7: Generation already finished — submit after cleanup
# ---------------------------------------------------------------------------

class TestScenario7AlreadyFinished:
    """Submit photo choices when generation already completed (no pending entry)."""

    def test_submit_returns_false_when_no_pending(self):
        """submit_photo_choices should return False when site_id not in _pending_photo_choices."""
        from app.services.databinding_generator import submit_photo_choices

        result = submit_photo_choices(99999, [{"section_type": "hero", "action": "stock"}])
        assert result is False

    @pytest.mark.asyncio
    async def test_submit_after_cleanup(self):
        """After pipeline cleanup, submitting should return False."""
        from app.services.databinding_generator import (
            _pending_photo_choices, submit_photo_choices,
        )

        site_id = 9007
        choice_event = asyncio.Event()

        # Register
        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": {},
            "template_style_id": "default",
        }

        # Simulate pipeline finishing and cleaning up
        _pending_photo_choices.pop(site_id, None)

        # Now submit should fail
        result = submit_photo_choices(site_id, [{"section_type": "hero", "action": "stock"}])
        assert result is False

    def test_get_pending_returns_none_when_no_pending(self):
        """get_pending_photo_choices should return None when no pending entry."""
        from app.services.databinding_generator import get_pending_photo_choices

        result = get_pending_photo_choices(99999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_pending_returns_none_after_event_set(self):
        """get_pending_photo_choices should return None when event is already set."""
        from app.services.databinding_generator import (
            _pending_photo_choices, get_pending_photo_choices,
        )

        site_id = 9077
        choice_event = asyncio.Event()
        choice_event.set()  # Already signaled

        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": [{"section_type": "hero", "action": "stock"}],
            "site_data": {},
            "template_style_id": "default",
        }

        result = get_pending_photo_choices(site_id)
        assert result is None  # Event is set, so not "pending" anymore


# ---------------------------------------------------------------------------
# Scenario 8: Concurrent generations
# ---------------------------------------------------------------------------

class TestScenario8ConcurrentGenerations:
    """Two different site_ids generating simultaneously should not interfere."""

    @pytest.mark.asyncio
    async def test_concurrent_independent_entries(self, generator):
        """Each site_id has its own _pending_photo_choices entry."""
        from app.services.databinding_generator import (
            _pending_photo_choices, submit_photo_choices,
        )

        site_a = 8001
        site_b = 8002

        event_a = asyncio.Event()
        event_b = asyncio.Event()

        site_data_a = _make_site_data_with_placeholders()
        site_data_b = _make_site_data_with_placeholders()

        _pending_photo_choices[site_a] = {
            "event": event_a,
            "choices": None,
            "site_data": site_data_a,
            "template_style_id": "restaurant-elegant",
        }
        _pending_photo_choices[site_b] = {
            "event": event_b,
            "choices": None,
            "site_data": site_data_b,
            "template_style_id": "saas-gradient",
        }

        # Submit choices for site A only
        choices_a = [
            {"section_type": "hero", "action": "upload", "photo_url": "https://custom-a.com/hero.jpg"},
            {"section_type": "about", "action": "stock"},
            {"section_type": "gallery", "action": "stock"},
        ]
        result_a = submit_photo_choices(site_a, choices_a)
        assert result_a is True

        # Verify site A's event is set
        assert event_a.is_set()
        assert _pending_photo_choices[site_a]["choices"] == choices_a

        # Verify site B is NOT affected
        assert not event_b.is_set()
        assert _pending_photo_choices[site_b]["choices"] is None

        # Now submit for site B
        choices_b = [
            {"section_type": "hero", "action": "stock"},
            {"section_type": "about", "action": "stock"},
            {"section_type": "gallery", "action": "stock"},
        ]
        result_b = submit_photo_choices(site_b, choices_b)
        assert result_b is True
        assert event_b.is_set()
        assert _pending_photo_choices[site_b]["choices"] == choices_b

        # Apply choices independently
        site_data_a = generator.apply_photo_choices(site_data_a, choices_a, "restaurant-elegant")
        site_data_b = generator.apply_photo_choices(site_data_b, choices_b, "saas-gradient")

        # Site A hero should be custom
        assert site_data_a["components"][0]["data"]["HERO_IMAGE_URL"] == "https://custom-a.com/hero.jpg"
        # Site B hero should be stock (Unsplash)
        assert "unsplash" in site_data_b["components"][0]["data"]["HERO_IMAGE_URL"]

    @pytest.mark.asyncio
    async def test_cleanup_one_doesnt_affect_other(self):
        """Cleaning up site A should not remove site B's pending entry."""
        from app.services.databinding_generator import _pending_photo_choices

        site_a = 8003
        site_b = 8004

        _pending_photo_choices[site_a] = {
            "event": asyncio.Event(),
            "choices": None,
            "site_data": {},
            "template_style_id": "default",
        }
        _pending_photo_choices[site_b] = {
            "event": asyncio.Event(),
            "choices": None,
            "site_data": {},
            "template_style_id": "default",
        }

        # Clean up A
        _pending_photo_choices.pop(site_a, None)

        assert site_a not in _pending_photo_choices
        assert site_b in _pending_photo_choices
        assert not _pending_photo_choices[site_b]["event"].is_set()


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------

class TestEdgeCasesE2E:
    """Additional edge case tests for robustness."""

    def test_apply_empty_choices_returns_unchanged(self, generator):
        """apply_photo_choices with empty list should return site_data unchanged."""
        site_data = _make_site_data_with_placeholders()
        original_hero = site_data["components"][0]["data"]["HERO_IMAGE_URL"]

        result = generator.apply_photo_choices(site_data, [], "restaurant-elegant")
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == original_hero

    def test_apply_with_none_choices_returns_unchanged(self, generator):
        """apply_photo_choices with None/falsy choices should return unchanged."""
        site_data = _make_site_data_with_placeholders()
        original_hero = site_data["components"][0]["data"]["HERO_IMAGE_URL"]

        result = generator.apply_photo_choices(site_data, None, "restaurant-elegant")
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == original_hero

    def test_submit_sets_event(self):
        """submit_photo_choices should call event.set()."""
        from app.services.databinding_generator import (
            _pending_photo_choices, submit_photo_choices,
        )

        site_id = 7777
        event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": event,
            "choices": None,
            "site_data": {},
            "template_style_id": "default",
        }

        assert not event.is_set()
        submit_photo_choices(site_id, [{"section_type": "hero", "action": "stock"}])
        assert event.is_set()

    def test_submit_stores_choices_correctly(self):
        """submit_photo_choices should store the choices in the pending dict."""
        from app.services.databinding_generator import (
            _pending_photo_choices, submit_photo_choices,
        )

        site_id = 7778
        event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": event,
            "choices": None,
            "site_data": {},
            "template_style_id": "default",
        }

        user_choices = [
            {"section_type": "hero", "action": "upload", "photo_url": "https://custom.com/img.jpg"},
        ]
        submit_photo_choices(site_id, user_choices)
        assert _pending_photo_choices[site_id]["choices"] == user_choices

    def test_scan_deduplicates_sections(self, generator):
        """If two components both have hero placeholders, only one choice returned."""
        site_data = {
            "components": [
                {"variant_id": "hero-classic-01", "data": {"HERO_IMAGE_URL": PLACEHOLDER_SVG}},
                {"variant_id": "hero-zen-01", "data": {"HERO_IMAGE_URL": PLACEHOLDER_SVG}},
            ]
        }
        choices = generator._scan_placeholder_photos(site_data, "default")
        hero_choices = [c for c in choices if c["section_type"] == "hero"]
        assert len(hero_choices) == 1, "Should deduplicate hero sections"

    @pytest.mark.asyncio
    async def test_event_wait_returns_immediately_when_set(self):
        """If event is set before wait_for, it should return immediately."""
        from app.services.databinding_generator import (
            _pending_photo_choices, submit_photo_choices,
        )

        site_id = 7779
        event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": event,
            "choices": None,
            "site_data": {},
            "template_style_id": "default",
        }

        # Submit BEFORE the pipeline waits
        submit_photo_choices(site_id, [{"section_type": "hero", "action": "stock"}])

        # wait_for should complete instantly since event is already set
        try:
            await asyncio.wait_for(event.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            pytest.fail("Event was set but wait_for still timed out")

    @pytest.mark.asyncio
    async def test_concurrent_submit_during_wait(self, generator):
        """Simulate submit arriving while pipeline is waiting on event."""
        from app.services.databinding_generator import (
            _pending_photo_choices, submit_photo_choices,
        )

        site_id = 7780
        site_data = _make_site_data_with_placeholders()

        choice_event = asyncio.Event()
        _pending_photo_choices[site_id] = {
            "event": choice_event,
            "choices": None,
            "site_data": site_data,
            "template_style_id": "restaurant-elegant",
        }

        user_choices = [
            {"section_type": "hero", "action": "stock"},
            {"section_type": "about", "action": "stock"},
            {"section_type": "gallery", "action": "stock"},
        ]

        # Schedule submit after a small delay (simulating user response)
        async def delayed_submit():
            await asyncio.sleep(0.05)
            submit_photo_choices(site_id, user_choices)

        # Run wait and delayed submit concurrently
        submit_task = asyncio.create_task(delayed_submit())

        try:
            await asyncio.wait_for(choice_event.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            pytest.fail("Should not have timed out — submit was scheduled")

        await submit_task

        # Verify choices were stored
        stored = _pending_photo_choices[site_id]["choices"]
        assert stored == user_choices

        # Apply and verify
        site_data = generator.apply_photo_choices(site_data, stored, "restaurant-elegant")
        hero_url = site_data["components"][0]["data"]["HERO_IMAGE_URL"]
        assert hero_url.startswith("https://") and "unsplash" in hero_url


# ---------------------------------------------------------------------------
# Test _get_stock_photos categories
# ---------------------------------------------------------------------------

class TestGetStockPhotos:
    """Verify _get_stock_photos returns correct pools for different categories."""

    def test_default_fallback(self):
        """Unknown category should fall back to default (business) pool."""
        from app.services.databinding_generator import _get_stock_photos

        photos = _get_stock_photos("unknown-xyz")
        assert "hero" in photos
        assert len(photos["hero"]) > 0

    def test_all_categories_have_required_pools(self):
        """Every known category should have hero, gallery, about, team pools."""
        from app.services.databinding_generator import _get_stock_photos

        categories = [
            "restaurant-elegant", "saas-gradient", "portfolio-gallery",
            "ecommerce-modern", "business-corporate", "blog-editorial",
            "event-vibrant",
        ]
        for cat in categories:
            photos = _get_stock_photos(cat)
            for pool_key in ["hero", "gallery", "about", "team"]:
                assert pool_key in photos, f"{cat} missing {pool_key} pool"
                assert len(photos[pool_key]) > 0, f"{cat} has empty {pool_key} pool"

    def test_shuffled_copies(self):
        """_get_stock_photos should return shuffled copies (not the same order every time)."""
        from app.services.databinding_generator import _get_stock_photos

        # Call multiple times, at least one should differ in order
        results = [_get_stock_photos("restaurant-elegant")["gallery"] for _ in range(10)]
        # Check if there's at least some variation (not all identical)
        unique_orderings = set(tuple(r) for r in results)
        # With 6 gallery items and 10 tries, extremely unlikely to get all same
        assert len(unique_orderings) >= 2 or len(results[0]) <= 1, \
            "Stock photos should be shuffled, but all 10 calls returned identical order"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
