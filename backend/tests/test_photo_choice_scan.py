"""Comprehensive unit tests for DataBindingGenerator._scan_placeholder_photos().

Tests all section types (hero, about, gallery, team, services, blog),
edge cases (empty URLs, SVG data URIs, placehold.co, None, real URLs),
deduplication via seen_sections, and correct population of stock_preview_url
and section_label.

IMPORTANT BEHAVIOR NOTE:
The scan method checks ALL image keys on EVERY component. A component missing
a key like HERO_IMAGE_URL will get `data.get("HERO_IMAGE_URL", "")` -> ""
which IS a placeholder. Tests must account for this by either:
  a) Asserting only on specific section_type entries via filtering, or
  b) Providing real URLs for keys that should NOT produce a choice.
"""
import sys
import os
import pytest
from unittest.mock import patch

# Add backend root to path so 'app' package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FAKE_STOCK_PHOTOS = {
    "hero": ["https://images.unsplash.com/hero-1"],
    "about": ["https://images.unsplash.com/about-1"],
    "gallery": ["https://images.unsplash.com/gallery-1"],
    "team": ["https://images.unsplash.com/team-1"],
}

PHOTO_CHOICE_LABELS = {
    "hero": "Sezione Hero (immagine principale)",
    "about": "Chi Siamo",
    "gallery": "Gallery / Portfolio",
    "team": "Il Nostro Team",
    "services": "Servizi",
    "blog": "Blog",
}

# A real URL for suppressing unwanted placeholder detections.
REAL = "https://example.com/real.jpg"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_component(variant_id: str, data: dict) -> dict:
    return {"variant_id": variant_id, "data": data}


def _make_site_data(*components) -> dict:
    return {"components": list(components)}


def _base_data(**overrides) -> dict:
    """Return component data with real URLs for hero/about (suppresses those checks).
    Caller can override specific keys to test placeholder detection."""
    base = {
        "HERO_IMAGE_URL": REAL,
        "ABOUT_IMAGE_URL": REAL,
    }
    base.update(overrides)
    return base


def _find_choice(choices, section_type):
    """Find a specific section_type in the choices list."""
    return [c for c in choices if c["section_type"] == section_type]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def generator():
    """Create a DataBindingGenerator instance with mocked heavy dependencies."""
    with patch("app.services.databinding_generator.kimi"), \
         patch("app.services.databinding_generator.kimi_text"), \
         patch("app.services.databinding_generator.template_assembler"):
        from app.services.databinding_generator import DataBindingGenerator
        return DataBindingGenerator()


@pytest.fixture(autouse=True)
def _mock_stock_and_labels():
    """Mock _get_stock_photos and SiteQuestioner.get_photo_choice_label for all tests."""
    with patch(
        "app.services.databinding_generator._get_stock_photos",
        return_value=FAKE_STOCK_PHOTOS,
    ), patch(
        "app.services.site_questioner.SiteQuestioner.get_photo_choice_label",
        side_effect=lambda section_type: PHOTO_CHOICE_LABELS.get(
            section_type, section_type.replace("_", " ").title()
        ),
    ):
        yield


# ===========================================================================
# _is_placeholder_url tests
# ===========================================================================


class TestIsPlaceholderUrl:
    """Tests for the static method _is_placeholder_url."""

    @pytest.fixture(autouse=True)
    def _get_class(self):
        with patch("app.services.databinding_generator.kimi"), \
             patch("app.services.databinding_generator.kimi_text"), \
             patch("app.services.databinding_generator.template_assembler"):
            from app.services.databinding_generator import DataBindingGenerator
            self.cls = DataBindingGenerator

    def test_empty_string_is_placeholder(self):
        assert self.cls._is_placeholder_url("") is True

    def test_none_is_placeholder(self):
        assert self.cls._is_placeholder_url(None) is True

    def test_whitespace_only_is_placeholder(self):
        assert self.cls._is_placeholder_url("   ") is True

    def test_placehold_co_is_placeholder(self):
        assert self.cls._is_placeholder_url("https://placehold.co/800x600") is True

    def test_svg_data_uri_is_placeholder(self):
        assert self.cls._is_placeholder_url("data:image/svg+xml,<svg></svg>") is True

    def test_template_placeholder_double_braces(self):
        assert self.cls._is_placeholder_url("{{HERO_IMAGE}}") is True

    def test_hash_is_placeholder(self):
        assert self.cls._is_placeholder_url("#") is True

    def test_placeholder_word(self):
        assert self.cls._is_placeholder_url("placeholder") is True

    def test_placeholder_jpg(self):
        assert self.cls._is_placeholder_url("placeholder.jpg") is True

    def test_real_url_not_placeholder(self):
        assert self.cls._is_placeholder_url("https://example.com/photo.jpg") is False

    def test_real_unsplash_url_not_placeholder(self):
        assert self.cls._is_placeholder_url("https://images.unsplash.com/photo-123") is False


# ===========================================================================
# _scan_placeholder_photos -- individual section types
# ===========================================================================


class TestScanHero:
    """Hero section scanning."""

    def test_hero_placeholder_svg(self, generator):
        """SVG data URI in HERO_IMAGE_URL should produce a hero choice."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", _base_data(
                HERO_IMAGE_URL="data:image/svg+xml,<svg></svg>",
            ))
        )
        choices = generator._scan_placeholder_photos(site_data, "restaurant-elegant")
        hero = _find_choice(choices, "hero")
        assert len(hero) == 1
        assert hero[0]["placeholder_key"] == "HERO_IMAGE_URL"
        assert hero[0]["stock_preview_url"] == "https://images.unsplash.com/hero-1"
        assert hero[0]["section_label"] == "Sezione Hero (immagine principale)"
        assert hero[0]["current_url"] == "data:image/svg+xml,<svg></svg>"

    def test_hero_real_url_no_choice(self, generator):
        """Real URL in HERO_IMAGE_URL should NOT produce a hero choice."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", _base_data(
                HERO_IMAGE_URL="https://example.com/real-hero.jpg",
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        hero = _find_choice(choices, "hero")
        assert len(hero) == 0

    def test_hero_empty_string(self, generator):
        """Empty string HERO_IMAGE_URL is a placeholder."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", _base_data(
                HERO_IMAGE_URL="",
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        hero = _find_choice(choices, "hero")
        assert len(hero) == 1

    def test_hero_placehold_co(self, generator):
        """placehold.co URL is a placeholder."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", _base_data(
                HERO_IMAGE_URL="https://placehold.co/1200x600",
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        hero = _find_choice(choices, "hero")
        assert len(hero) == 1

    def test_hero_missing_key_treated_as_empty(self, generator):
        """When HERO_IMAGE_URL key is absent, data.get returns '', which is placeholder."""
        # Explicitly omit HERO_IMAGE_URL but supply real ABOUT_IMAGE_URL
        site_data = _make_site_data(
            _make_component("hero-classic-01", {"ABOUT_IMAGE_URL": REAL})
        )
        choices = generator._scan_placeholder_photos(site_data)
        hero = _find_choice(choices, "hero")
        assert len(hero) == 1


class TestScanAbout:
    """About section scanning."""

    def test_about_placeholder(self, generator):
        """SVG data URI in ABOUT_IMAGE_URL should produce an about choice."""
        site_data = _make_site_data(
            _make_component("about-magazine-01", _base_data(
                ABOUT_IMAGE_URL="data:image/svg+xml,<svg></svg>",
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        about = _find_choice(choices, "about")
        assert len(about) == 1
        assert about[0]["placeholder_key"] == "ABOUT_IMAGE_URL"
        assert about[0]["stock_preview_url"] == "https://images.unsplash.com/about-1"
        assert about[0]["section_label"] == "Chi Siamo"

    def test_about_real_url_no_choice(self, generator):
        """Real URL in ABOUT_IMAGE_URL should NOT produce an about choice."""
        site_data = _make_site_data(
            _make_component("about-magazine-01", _base_data(
                ABOUT_IMAGE_URL="https://example.com/real-about.jpg",
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        about = _find_choice(choices, "about")
        assert len(about) == 0


class TestScanGallery:
    """Gallery section scanning."""

    def test_gallery_with_placeholder_items(self, generator):
        """Gallery with at least one placeholder item should produce a gallery choice."""
        site_data = _make_site_data(
            _make_component("gallery-grid-01", _base_data(
                GALLERY_ITEMS=[
                    {"GALLERY_IMAGE_URL": "data:image/svg+xml,<svg></svg>"},
                    {"GALLERY_IMAGE_URL": "https://example.com/real.jpg"},
                ],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        gallery = _find_choice(choices, "gallery")
        assert len(gallery) == 1
        assert gallery[0]["placeholder_key"] == "GALLERY_IMAGE_URL"
        assert gallery[0]["stock_preview_url"] == "https://images.unsplash.com/gallery-1"
        assert gallery[0]["section_label"] == "Gallery / Portfolio"
        assert gallery[0]["current_url"] == ""

    def test_gallery_all_real_no_choice(self, generator):
        """Gallery where all items have real URLs should NOT produce a choice."""
        site_data = _make_site_data(
            _make_component("gallery-grid-01", _base_data(
                GALLERY_ITEMS=[
                    {"GALLERY_IMAGE_URL": "https://example.com/1.jpg"},
                    {"GALLERY_IMAGE_URL": "https://example.com/2.jpg"},
                ],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        gallery = _find_choice(choices, "gallery")
        assert len(gallery) == 0

    def test_gallery_empty_list_no_choice(self, generator):
        """Empty gallery list should NOT produce a choice."""
        site_data = _make_site_data(
            _make_component("gallery-grid-01", _base_data(
                GALLERY_ITEMS=[],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        gallery = _find_choice(choices, "gallery")
        assert len(gallery) == 0


class TestScanTeam:
    """Team section scanning."""

    def test_team_with_placeholder_members(self, generator):
        """Team with at least one placeholder member should produce a team choice."""
        site_data = _make_site_data(
            _make_component("team-grid-01", _base_data(
                TEAM_MEMBERS=[
                    {"MEMBER_IMAGE_URL": "https://placehold.co/200x200"},
                    {"MEMBER_IMAGE_URL": "https://example.com/real.jpg"},
                ],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        team = _find_choice(choices, "team")
        assert len(team) == 1
        assert team[0]["placeholder_key"] == "MEMBER_IMAGE_URL"
        assert team[0]["stock_preview_url"] == "https://images.unsplash.com/team-1"
        assert team[0]["section_label"] == "Il Nostro Team"

    def test_team_all_real_no_choice(self, generator):
        """Team where all members have real URLs should NOT produce a choice."""
        site_data = _make_site_data(
            _make_component("team-grid-01", _base_data(
                TEAM_MEMBERS=[
                    {"MEMBER_IMAGE_URL": "https://example.com/person1.jpg"},
                ],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        team = _find_choice(choices, "team")
        assert len(team) == 0


class TestScanServices:
    """Services section scanning."""

    def test_services_with_placeholder(self, generator):
        """Services with at least one placeholder should produce a services choice."""
        site_data = _make_site_data(
            _make_component("services-cards-01", _base_data(
                SERVICE_ITEMS=[
                    {"SERVICE_IMAGE_URL": ""},
                    {"SERVICE_IMAGE_URL": "https://example.com/real.jpg"},
                ],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        services = _find_choice(choices, "services")
        assert len(services) == 1
        assert services[0]["placeholder_key"] == "SERVICE_IMAGE_URL"
        # services uses gallery pool
        assert services[0]["stock_preview_url"] == "https://images.unsplash.com/gallery-1"
        assert services[0]["section_label"] == "Servizi"

    def test_services_all_real_no_choice(self, generator):
        """Services where all items have real URLs should NOT produce a choice."""
        site_data = _make_site_data(
            _make_component("services-cards-01", _base_data(
                SERVICE_ITEMS=[
                    {"SERVICE_IMAGE_URL": "https://example.com/svc.jpg"},
                ],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        services = _find_choice(choices, "services")
        assert len(services) == 0


class TestScanBlog:
    """Blog section scanning."""

    def test_blog_with_placeholder(self, generator):
        """Blog with at least one placeholder should produce a blog choice."""
        site_data = _make_site_data(
            _make_component("blog-grid-01", _base_data(
                BLOG_POSTS=[
                    {"POST_IMAGE_URL": "data:image/svg+xml,<svg></svg>"},
                ],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        blog = _find_choice(choices, "blog")
        assert len(blog) == 1
        assert blog[0]["placeholder_key"] == "POST_IMAGE_URL"
        # blog uses gallery pool
        assert blog[0]["stock_preview_url"] == "https://images.unsplash.com/gallery-1"
        assert blog[0]["section_label"] == "Blog"

    def test_blog_all_real_no_choice(self, generator):
        """Blog where all posts have real URLs should NOT produce a choice."""
        site_data = _make_site_data(
            _make_component("blog-grid-01", _base_data(
                BLOG_POSTS=[
                    {"POST_IMAGE_URL": "https://example.com/post.jpg"},
                ],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        blog = _find_choice(choices, "blog")
        assert len(blog) == 0


# ===========================================================================
# Deduplication
# ===========================================================================


class TestDeduplication:
    """Verify that seen_sections prevents duplicate entries."""

    def test_duplicate_hero_in_two_components(self, generator):
        """Two components both with HERO_IMAGE_URL placeholder -> only ONE hero choice."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", _base_data(
                HERO_IMAGE_URL="data:image/svg+xml,<svg></svg>",
            )),
            _make_component("hero-bold-01", _base_data(
                HERO_IMAGE_URL="",
            )),
        )
        choices = generator._scan_placeholder_photos(site_data)
        hero = _find_choice(choices, "hero")
        assert len(hero) == 1

    def test_duplicate_gallery_in_two_components(self, generator):
        """Two gallery components with placeholders -> only ONE gallery choice."""
        site_data = _make_site_data(
            _make_component("gallery-grid-01", _base_data(
                GALLERY_ITEMS=[{"GALLERY_IMAGE_URL": ""}],
            )),
            _make_component("gallery-spotlight-01", _base_data(
                GALLERY_ITEMS=[{"GALLERY_IMAGE_URL": ""}],
            )),
        )
        choices = generator._scan_placeholder_photos(site_data)
        gallery = _find_choice(choices, "gallery")
        assert len(gallery) == 1

    def test_duplicate_about_in_two_components(self, generator):
        """Two components both with ABOUT_IMAGE_URL placeholder -> only ONE about choice."""
        site_data = _make_site_data(
            _make_component("about-magazine-01", _base_data(
                ABOUT_IMAGE_URL="data:image/svg+xml,<svg></svg>",
            )),
            _make_component("about-split-01", _base_data(
                ABOUT_IMAGE_URL="",
            )),
        )
        choices = generator._scan_placeholder_photos(site_data)
        about = _find_choice(choices, "about")
        assert len(about) == 1


# ===========================================================================
# Edge cases
# ===========================================================================


class TestEdgeCases:
    """Various edge cases."""

    def test_no_components_returns_empty(self, generator):
        site_data = {"components": []}
        choices = generator._scan_placeholder_photos(site_data)
        assert choices == []

    def test_missing_components_key_returns_empty(self, generator):
        site_data = {}
        choices = generator._scan_placeholder_photos(site_data)
        assert choices == []

    def test_component_no_data_key(self, generator):
        """Component with missing 'data' key -> data defaults to {},
        hero/about get empty string from .get() which is placeholder."""
        site_data = _make_site_data({"variant_id": "hero-classic-01"})
        choices = generator._scan_placeholder_photos(site_data)
        # Both hero and about will be detected as placeholder (empty string default)
        hero = _find_choice(choices, "hero")
        about = _find_choice(choices, "about")
        assert len(hero) == 1
        assert len(about) == 1

    def test_none_url_value_in_hero(self, generator):
        """HERO_IMAGE_URL set to None -> str(None) = 'None', which is NOT a placeholder
        since 'None' doesn't match any placeholder pattern."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", _base_data(
                HERO_IMAGE_URL=None,
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        hero = _find_choice(choices, "hero")
        # str(None) = "None" which is not empty, not placehold.co, not svg, etc.
        assert len(hero) == 0

    def test_empty_stock_photos_pool(self, generator):
        """When stock photos pool is empty, stock_preview_url should be ''."""
        with patch(
            "app.services.databinding_generator._get_stock_photos",
            return_value={"hero": [], "about": [], "gallery": [], "team": []},
        ):
            site_data = _make_site_data(
                _make_component("hero-classic-01", _base_data(
                    HERO_IMAGE_URL="",
                ))
            )
            choices = generator._scan_placeholder_photos(site_data)
            hero = _find_choice(choices, "hero")
            assert len(hero) == 1
            assert hero[0]["stock_preview_url"] == ""

    def test_template_style_id_none_defaults(self, generator):
        """When template_style_id is None, should pass 'default' to _get_stock_photos."""
        with patch(
            "app.services.databinding_generator._get_stock_photos",
            return_value=FAKE_STOCK_PHOTOS,
        ) as mock_get:
            site_data = _make_site_data(
                _make_component("hero-classic-01", _base_data(HERO_IMAGE_URL=""))
            )
            generator._scan_placeholder_photos(site_data, None)
            mock_get.assert_called_once_with("default")

    def test_template_style_id_passed_through(self, generator):
        """When template_style_id is provided, should be passed as-is."""
        with patch(
            "app.services.databinding_generator._get_stock_photos",
            return_value=FAKE_STOCK_PHOTOS,
        ) as mock_get:
            site_data = _make_site_data(
                _make_component("hero-classic-01", _base_data(HERO_IMAGE_URL=""))
            )
            generator._scan_placeholder_photos(site_data, "restaurant-elegant")
            mock_get.assert_called_once_with("restaurant-elegant")

    def test_gallery_items_not_a_list(self, generator):
        """If GALLERY_ITEMS is not a list (e.g. string), it should be skipped."""
        site_data = _make_site_data(
            _make_component("gallery-grid-01", _base_data(
                GALLERY_ITEMS="not-a-list",
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        gallery = _find_choice(choices, "gallery")
        assert len(gallery) == 0

    def test_team_members_not_a_list(self, generator):
        """If TEAM_MEMBERS is not a list, it should be skipped."""
        site_data = _make_site_data(
            _make_component("team-grid-01", _base_data(
                TEAM_MEMBERS="not-a-list",
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        team = _find_choice(choices, "team")
        assert len(team) == 0

    def test_gallery_items_with_non_dict_entries(self, generator):
        """Gallery items that are not dicts should be ignored (no crash)."""
        site_data = _make_site_data(
            _make_component("gallery-grid-01", _base_data(
                GALLERY_ITEMS=["not-a-dict", 42, None],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        gallery = _find_choice(choices, "gallery")
        # None of these are dicts, so `any(isinstance(item, dict) and ...)` is False
        assert len(gallery) == 0


# ===========================================================================
# Mixed scenarios
# ===========================================================================


class TestMixedSections:
    """Multiple sections combined."""

    def test_all_six_section_types(self, generator):
        """All 6 section types with placeholders -> 6 choices returned."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", {
                "HERO_IMAGE_URL": "",
                "ABOUT_IMAGE_URL": "data:image/svg+xml,<svg></svg>",
                "GALLERY_ITEMS": [{"GALLERY_IMAGE_URL": ""}],
                "TEAM_MEMBERS": [{"MEMBER_IMAGE_URL": "https://placehold.co/100x100"}],
                "SERVICE_ITEMS": [{"SERVICE_IMAGE_URL": "placeholder"}],
                "BLOG_POSTS": [{"POST_IMAGE_URL": "placeholder.jpg"}],
            }),
        )
        choices = generator._scan_placeholder_photos(site_data, "business-corporate")
        assert len(choices) == 6
        section_types = {c["section_type"] for c in choices}
        assert section_types == {"hero", "about", "gallery", "team", "services", "blog"}

    def test_mixed_some_placeholder_some_real(self, generator):
        """Only sections with placeholders should appear in choices."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", {
                "HERO_IMAGE_URL": "https://example.com/real-hero.jpg",  # real
                "ABOUT_IMAGE_URL": "",  # placeholder
            }),
            _make_component("gallery-grid-01", {
                "HERO_IMAGE_URL": REAL,
                "ABOUT_IMAGE_URL": REAL,
                "GALLERY_ITEMS": [
                    {"GALLERY_IMAGE_URL": "https://example.com/real.jpg"},  # all real
                ],
            }),
            _make_component("team-grid-01", {
                "HERO_IMAGE_URL": REAL,
                "ABOUT_IMAGE_URL": REAL,
                "TEAM_MEMBERS": [
                    {"MEMBER_IMAGE_URL": "https://placehold.co/200"},  # placeholder
                ],
            }),
        )
        choices = generator._scan_placeholder_photos(site_data)
        section_types = {c["section_type"] for c in choices}
        assert "about" in section_types
        assert "team" in section_types
        assert "hero" not in section_types

    def test_hero_and_about_in_same_component(self, generator):
        """A single component can have both HERO_IMAGE_URL and ABOUT_IMAGE_URL."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", {
                "HERO_IMAGE_URL": "",
                "ABOUT_IMAGE_URL": "data:image/svg+xml,<svg></svg>",
            })
        )
        choices = generator._scan_placeholder_photos(site_data)
        hero = _find_choice(choices, "hero")
        about = _find_choice(choices, "about")
        assert len(hero) == 1
        assert len(about) == 1

    def test_order_follows_scan_order(self, generator):
        """Choices should follow the order: hero, about, gallery, team, services, blog
        (as they appear within each component's checks)."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", {
                "HERO_IMAGE_URL": "",
                "ABOUT_IMAGE_URL": "",
                "GALLERY_ITEMS": [{"GALLERY_IMAGE_URL": ""}],
                "TEAM_MEMBERS": [{"MEMBER_IMAGE_URL": ""}],
                "SERVICE_ITEMS": [{"SERVICE_IMAGE_URL": ""}],
                "BLOG_POSTS": [{"POST_IMAGE_URL": ""}],
            }),
        )
        choices = generator._scan_placeholder_photos(site_data)
        types_in_order = [c["section_type"] for c in choices]
        assert types_in_order == ["hero", "about", "gallery", "team", "services", "blog"]

    def test_separate_components_per_section(self, generator):
        """Each section type in its own component, with real URLs for other keys."""
        site_data = _make_site_data(
            _make_component("hero-classic-01", _base_data(HERO_IMAGE_URL="")),
            _make_component("about-magazine-01", _base_data(ABOUT_IMAGE_URL="")),
            _make_component("gallery-grid-01", _base_data(
                GALLERY_ITEMS=[{"GALLERY_IMAGE_URL": ""}],
            )),
            _make_component("team-grid-01", _base_data(
                TEAM_MEMBERS=[{"MEMBER_IMAGE_URL": ""}],
            )),
            _make_component("services-cards-01", _base_data(
                SERVICE_ITEMS=[{"SERVICE_IMAGE_URL": ""}],
            )),
            _make_component("blog-grid-01", _base_data(
                BLOG_POSTS=[{"POST_IMAGE_URL": ""}],
            )),
        )
        choices = generator._scan_placeholder_photos(site_data)
        assert len(choices) == 6
        section_types = {c["section_type"] for c in choices}
        assert section_types == {"hero", "about", "gallery", "team", "services", "blog"}


# ===========================================================================
# stock_preview_url correctness
# ===========================================================================


class TestStockPreviewUrl:
    """Verify stock_preview_url is populated from the right pool."""

    def test_hero_uses_hero_pool(self, generator):
        site_data = _make_site_data(
            _make_component("hero-classic-01", _base_data(HERO_IMAGE_URL=""))
        )
        choices = generator._scan_placeholder_photos(site_data)
        hero = _find_choice(choices, "hero")
        assert hero[0]["stock_preview_url"] == "https://images.unsplash.com/hero-1"

    def test_about_uses_about_pool(self, generator):
        site_data = _make_site_data(
            _make_component("about-magazine-01", _base_data(ABOUT_IMAGE_URL=""))
        )
        choices = generator._scan_placeholder_photos(site_data)
        about = _find_choice(choices, "about")
        assert about[0]["stock_preview_url"] == "https://images.unsplash.com/about-1"

    def test_gallery_uses_gallery_pool(self, generator):
        site_data = _make_site_data(
            _make_component("gallery-grid-01", _base_data(
                GALLERY_ITEMS=[{"GALLERY_IMAGE_URL": ""}],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        gallery = _find_choice(choices, "gallery")
        assert gallery[0]["stock_preview_url"] == "https://images.unsplash.com/gallery-1"

    def test_team_uses_team_pool(self, generator):
        site_data = _make_site_data(
            _make_component("team-grid-01", _base_data(
                TEAM_MEMBERS=[{"MEMBER_IMAGE_URL": ""}],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        team = _find_choice(choices, "team")
        assert team[0]["stock_preview_url"] == "https://images.unsplash.com/team-1"

    def test_services_uses_gallery_pool(self, generator):
        """Services falls back to gallery pool for stock photos."""
        site_data = _make_site_data(
            _make_component("services-cards-01", _base_data(
                SERVICE_ITEMS=[{"SERVICE_IMAGE_URL": ""}],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        services = _find_choice(choices, "services")
        assert services[0]["stock_preview_url"] == "https://images.unsplash.com/gallery-1"

    def test_blog_uses_gallery_pool(self, generator):
        """Blog falls back to gallery pool for stock photos."""
        site_data = _make_site_data(
            _make_component("blog-grid-01", _base_data(
                BLOG_POSTS=[{"POST_IMAGE_URL": ""}],
            ))
        )
        choices = generator._scan_placeholder_photos(site_data)
        blog = _find_choice(choices, "blog")
        assert blog[0]["stock_preview_url"] == "https://images.unsplash.com/gallery-1"


# ===========================================================================
# section_label correctness
# ===========================================================================


class TestSectionLabels:
    """Verify section_label comes from SiteQuestioner.get_photo_choice_label."""

    def test_all_labels_correct(self, generator):
        """All 6 section types should have the correct Italian labels."""
        site_data = _make_site_data(
            _make_component("all-in-one", {
                "HERO_IMAGE_URL": "",
                "ABOUT_IMAGE_URL": "",
                "GALLERY_ITEMS": [{"GALLERY_IMAGE_URL": ""}],
                "TEAM_MEMBERS": [{"MEMBER_IMAGE_URL": ""}],
                "SERVICE_ITEMS": [{"SERVICE_IMAGE_URL": ""}],
                "BLOG_POSTS": [{"POST_IMAGE_URL": ""}],
            }),
        )
        choices = generator._scan_placeholder_photos(site_data)
        labels = {c["section_type"]: c["section_label"] for c in choices}
        assert labels["hero"] == "Sezione Hero (immagine principale)"
        assert labels["about"] == "Chi Siamo"
        assert labels["gallery"] == "Gallery / Portfolio"
        assert labels["team"] == "Il Nostro Team"
        assert labels["services"] == "Servizi"
        assert labels["blog"] == "Blog"
