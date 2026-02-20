"""
Test Photo Pipeline — Simulates the full image flow in databinding_generator.py.

Tests that images are properly injected at every stage:
1. _is_placeholder_url() correctly detects all placeholder types
2. _inject_stock_photos() replaces ALL placeholder images (hero, about, gallery, team, blog, services)
3. _inject_user_photos() overrides stock photos with user uploads
4. Stock photos run ALWAYS (not gated by should_generate_images)
5. Numbered about images (ABOUT_IMAGE_URL_2 through _10) are handled
"""

import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# PHASE 1: _is_placeholder_url detection
# ---------------------------------------------------------------------------

class TestIsPlaceholderUrl:
    """Test that _is_placeholder_url correctly identifies all placeholder types."""

    @staticmethod
    def _check(url):
        from app.services.databinding_generator import DataBindingGenerator
        return DataBindingGenerator._is_placeholder_url(url)

    # --- Should detect as placeholder (return True) ---

    def test_empty_string(self):
        assert self._check("") is True

    def test_none(self):
        assert self._check(None) is True

    def test_whitespace_only(self):
        assert self._check("   ") is True

    def test_placehold_co(self):
        assert self._check("https://placehold.co/800x600") is True

    def test_svg_data_uri(self):
        svg = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect fill="%23f1f5f9" width="800" height="600"/></svg>'
        assert self._check(svg) is True

    def test_template_var(self):
        assert self._check("{{HERO_IMAGE_URL}}") is True

    def test_hash(self):
        assert self._check("#") is True

    def test_placeholder_text(self):
        assert self._check("placeholder") is True
        assert self._check("placeholder.jpg") is True

    def test_integer_zero(self):
        assert self._check(0) is True

    def test_boolean_false(self):
        assert self._check(False) is True

    # --- Should NOT detect as placeholder (return False) ---

    def test_unsplash_url(self):
        assert self._check("https://images.unsplash.com/photo-abc?w=1200") is False

    def test_user_upload_url(self):
        assert self._check("https://res.cloudinary.com/my-upload/image.jpg") is False

    def test_regular_url(self):
        assert self._check("https://example.com/photo.jpg") is False

    def test_relative_path(self):
        assert self._check("/images/hero.jpg") is False


# ---------------------------------------------------------------------------
# PHASE 2: _inject_stock_photos coverage
# ---------------------------------------------------------------------------

class TestInjectStockPhotos:
    """Test that stock photos are injected into ALL supported image fields."""

    @classmethod
    def setup_class(cls):
        from app.services.databinding_generator import DataBindingGenerator
        cls.generator = DataBindingGenerator.__new__(DataBindingGenerator)

    def _make_site_data(self, components):
        return {"components": components}

    def test_hero_image_replaced(self):
        """Hero image placeholder should be replaced with Unsplash URL."""
        site_data = self._make_site_data([{
            "section_type": "hero",
            "data": {"HERO_IMAGE_URL": ""}
        }])
        result = self.generator._inject_stock_photos(site_data, "restaurant-elegant")
        hero_url = result["components"][0]["data"]["HERO_IMAGE_URL"]
        assert hero_url.startswith("https://"), f"Hero URL not replaced: {hero_url}"
        assert "unsplash" in hero_url or "images" in hero_url, f"Not a stock photo: {hero_url}"

    def test_about_image_replaced(self):
        """About image placeholder should be replaced."""
        site_data = self._make_site_data([{
            "section_type": "about",
            "data": {"ABOUT_IMAGE_URL": ""}
        }])
        result = self.generator._inject_stock_photos(site_data, "restaurant-elegant")
        about_url = result["components"][0]["data"]["ABOUT_IMAGE_URL"]
        assert about_url.startswith("https://"), f"About URL not replaced: {about_url}"

    def test_numbered_about_images_replaced(self):
        """ABOUT_IMAGE_URL_2 through _5 should be replaced."""
        site_data = self._make_site_data([{
            "section_type": "about",
            "data": {
                "ABOUT_IMAGE_URL": "",
                "ABOUT_IMAGE_URL_2": "",
                "ABOUT_IMAGE_URL_3": "",
                "ABOUT_IMAGE_URL_4": "",
                "ABOUT_IMAGE_URL_5": "",
            }
        }])
        result = self.generator._inject_stock_photos(site_data, "restaurant-elegant")
        data = result["components"][0]["data"]
        for n in range(2, 6):
            key = f"ABOUT_IMAGE_URL_{n}"
            assert data[key].startswith("https://"), f"{key} not replaced: {data[key]}"

    def test_gallery_items_replaced(self):
        """Gallery image placeholders should all be replaced."""
        site_data = self._make_site_data([{
            "section_type": "gallery",
            "data": {
                "GALLERY_ITEMS": [
                    {"GALLERY_IMAGE_URL": "", "GALLERY_CAPTION": "Foto 1"},
                    {"GALLERY_IMAGE_URL": "data:image/svg+xml,<svg></svg>", "GALLERY_CAPTION": "Foto 2"},
                    {"GALLERY_IMAGE_URL": "", "GALLERY_CAPTION": "Foto 3"},
                ]
            }
        }])
        result = self.generator._inject_stock_photos(site_data, "restaurant-elegant")
        items = result["components"][0]["data"]["GALLERY_ITEMS"]
        for i, item in enumerate(items):
            assert item["GALLERY_IMAGE_URL"].startswith("https://"), f"Gallery {i} not replaced"

    def test_team_members_replaced(self):
        """Team member photos should be replaced."""
        site_data = self._make_site_data([{
            "section_type": "team",
            "data": {
                "TEAM_MEMBERS": [
                    {"MEMBER_IMAGE_URL": "", "MEMBER_NAME": "Mario"},
                    {"MEMBER_IMAGE_URL": "", "MEMBER_NAME": "Luigi"},
                ]
            }
        }])
        result = self.generator._inject_stock_photos(site_data, "business-corporate")
        members = result["components"][0]["data"]["TEAM_MEMBERS"]
        for m in members:
            assert m["MEMBER_IMAGE_URL"].startswith("https://"), f"Team member not replaced"

    def test_blog_posts_replaced(self):
        """Blog post images should be replaced."""
        site_data = self._make_site_data([{
            "section_type": "blog",
            "data": {
                "BLOG_POSTS": [
                    {"POST_IMAGE_URL": "", "POST_TITLE": "Post 1"},
                    {"POST_IMAGE_URL": "", "POST_TITLE": "Post 2"},
                ]
            }
        }])
        result = self.generator._inject_stock_photos(site_data, "blog-editorial")
        posts = result["components"][0]["data"]["BLOG_POSTS"]
        for p in posts:
            assert p["POST_IMAGE_URL"].startswith("https://"), f"Blog post not replaced"

    def test_service_images_replaced(self):
        """Service item images should be replaced."""
        site_data = self._make_site_data([{
            "section_type": "services",
            "data": {
                "SERVICE_ITEMS": [
                    {"SERVICE_IMAGE_URL": "", "SERVICE_TITLE": "Servizio 1"},
                    {"SERVICE_IMAGE_URL": "", "SERVICE_TITLE": "Servizio 2"},
                ]
            }
        }])
        result = self.generator._inject_stock_photos(site_data, "business-corporate")
        items = result["components"][0]["data"]["SERVICE_ITEMS"]
        for s in items:
            assert s["SERVICE_IMAGE_URL"].startswith("https://"), f"Service not replaced"

    def test_listing_images_replaced(self):
        """Listing images should be replaced."""
        site_data = self._make_site_data([{
            "section_type": "listings",
            "data": {
                "LISTING_ITEMS": [
                    {"LISTING_IMAGE_URL": "", "LISTING_TITLE": "Item 1"},
                ]
            }
        }])
        result = self.generator._inject_stock_photos(site_data, "ecommerce-modern")
        items = result["components"][0]["data"]["LISTING_ITEMS"]
        assert items[0]["LISTING_IMAGE_URL"].startswith("https://"), "Listing not replaced"

    def test_app_image_replaced(self):
        """App download image should be replaced."""
        site_data = self._make_site_data([{
            "section_type": "app",
            "data": {"APP_IMAGE_URL": ""}
        }])
        result = self.generator._inject_stock_photos(site_data, "saas-gradient")
        assert result["components"][0]["data"]["APP_IMAGE_URL"].startswith("https://")

    def test_real_urls_not_overwritten(self):
        """Real Unsplash URLs should NOT be overwritten by stock injection."""
        real_url = "https://images.unsplash.com/photo-user-provided?w=1200"
        site_data = self._make_site_data([{
            "section_type": "hero",
            "data": {"HERO_IMAGE_URL": real_url}
        }])
        result = self.generator._inject_stock_photos(site_data, "restaurant-elegant")
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == real_url

    def test_logo_svg_placeholder(self):
        """Logo placeholders should get SVG placeholder (not stock photo)."""
        site_data = self._make_site_data([{
            "section_type": "logos",
            "data": {
                "LOGOS_ITEMS": [
                    {"LOGO_IMAGE_URL": "", "LOGO_NAME": "Partner ABC"},
                ]
            }
        }])
        result = self.generator._inject_stock_photos(site_data, "default")
        logo_url = result["components"][0]["data"]["LOGOS_ITEMS"][0]["LOGO_IMAGE_URL"]
        assert logo_url.startswith("data:image/svg+xml,"), f"Logo should be SVG: {logo_url[:50]}"


# ---------------------------------------------------------------------------
# PHASE 3: _inject_user_photos override
# ---------------------------------------------------------------------------

class TestInjectUserPhotos:
    """Test that user photos override stock photos correctly."""

    @classmethod
    def setup_class(cls):
        from app.services.databinding_generator import DataBindingGenerator
        cls.generator = DataBindingGenerator.__new__(DataBindingGenerator)

    def test_user_photos_override_hero(self):
        """User photo should replace stock photo in hero."""
        site_data = {"components": [{
            "section_type": "hero",
            "data": {"HERO_IMAGE_URL": "https://images.unsplash.com/stock"}
        }]}
        user_urls = ["https://mysite.com/my-hero.jpg"]
        result = self.generator._inject_user_photos(site_data, user_urls)
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == user_urls[0]

    def test_user_photos_override_about(self):
        """User photo should replace about image too."""
        site_data = {"components": [
            {"section_type": "hero", "data": {"HERO_IMAGE_URL": "stock1"}},
            {"section_type": "about", "data": {"ABOUT_IMAGE_URL": "stock2"}},
        ]}
        user_urls = ["https://mysite.com/photo1.jpg", "https://mysite.com/photo2.jpg"]
        result = self.generator._inject_user_photos(site_data, user_urls)
        # First photo goes to hero, second to about
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == user_urls[0]
        assert result["components"][1]["data"]["ABOUT_IMAGE_URL"] == user_urls[1]

    def test_no_user_photos_returns_unchanged(self):
        """Empty user_urls should not change site_data."""
        site_data = {"components": [{
            "section_type": "hero",
            "data": {"HERO_IMAGE_URL": "https://images.unsplash.com/stock"}
        }]}
        result = self.generator._inject_user_photos(site_data, [])
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == "https://images.unsplash.com/stock"


# ---------------------------------------------------------------------------
# PHASE 4: Full pipeline simulation (stock always runs)
# ---------------------------------------------------------------------------

class TestStockPhotosAlwaysRun:
    """Verify that stock photos are injected regardless of AI image generation setting."""

    def test_stock_runs_when_ai_images_disabled(self):
        """Stock photos should run when should_generate_images=False."""
        from app.services.databinding_generator import DataBindingGenerator
        gen = DataBindingGenerator.__new__(DataBindingGenerator)

        site_data = {"components": [{
            "section_type": "hero",
            "data": {"HERO_IMAGE_URL": ""}
        }]}

        # Simulate: AI images disabled → stock photos must still run
        result = gen._inject_stock_photos(site_data, "restaurant-elegant")
        hero_url = result["components"][0]["data"]["HERO_IMAGE_URL"]
        assert hero_url.startswith("https://"), f"Stock not injected when AI disabled: {hero_url}"

    def test_stock_runs_after_ai_images_fail(self):
        """Stock photos should fill gaps when AI images fail (return empty)."""
        from app.services.databinding_generator import DataBindingGenerator
        gen = DataBindingGenerator.__new__(DataBindingGenerator)

        # Simulate: AI returned empty strings for all images (failure)
        site_data = {"components": [
            {"section_type": "hero", "data": {"HERO_IMAGE_URL": ""}},
            {"section_type": "about", "data": {"ABOUT_IMAGE_URL": ""}},
            {"section_type": "gallery", "data": {
                "GALLERY_ITEMS": [
                    {"GALLERY_IMAGE_URL": "", "GALLERY_CAPTION": "Foto"},
                ]
            }},
        ]}

        result = gen._inject_stock_photos(site_data, "restaurant-cozy")

        assert result["components"][0]["data"]["HERO_IMAGE_URL"].startswith("https://")
        assert result["components"][1]["data"]["ABOUT_IMAGE_URL"].startswith("https://")
        assert result["components"][2]["data"]["GALLERY_ITEMS"][0]["GALLERY_IMAGE_URL"].startswith("https://")

    def test_stock_does_not_overwrite_ai_successes(self):
        """When AI successfully generates some images, stock should not overwrite them."""
        from app.services.databinding_generator import DataBindingGenerator
        gen = DataBindingGenerator.__new__(DataBindingGenerator)

        ai_url = "https://ai-generated.example.com/hero.webp"
        site_data = {"components": [
            {"section_type": "hero", "data": {"HERO_IMAGE_URL": ai_url}},
            {"section_type": "about", "data": {"ABOUT_IMAGE_URL": ""}},  # AI failed here
        ]}

        result = gen._inject_stock_photos(site_data, "restaurant-elegant")

        # Hero should keep AI-generated URL
        assert result["components"][0]["data"]["HERO_IMAGE_URL"] == ai_url
        # About should get stock photo (AI failed)
        assert result["components"][1]["data"]["ABOUT_IMAGE_URL"].startswith("https://")


# ---------------------------------------------------------------------------
# PHASE 5: Multi-component realistic simulation
# ---------------------------------------------------------------------------

class TestRealisticSiteSimulation:
    """Simulate a full restaurant site with multiple sections — all images must be filled."""

    def test_restaurant_site_all_images_filled(self):
        """Full restaurant site: every image field should have a valid URL after stock injection."""
        from app.services.databinding_generator import DataBindingGenerator
        gen = DataBindingGenerator.__new__(DataBindingGenerator)

        # Simulate what Gemini typically returns: empty strings for all images
        site_data = {"components": [
            {
                "section_type": "hero",
                "data": {
                    "HERO_TITLE": "Ristorante Da Mario",
                    "HERO_SUBTITLE": "Cucina tradizionale",
                    "HERO_IMAGE_URL": "",
                    "HERO_CTA_TEXT": "Prenota un Tavolo",
                }
            },
            {
                "section_type": "about",
                "data": {
                    "ABOUT_TITLE": "La nostra storia",
                    "ABOUT_TEXT": "Dal 1985...",
                    "ABOUT_IMAGE_URL": "",
                    "ABOUT_IMAGE_URL_2": "",
                    "ABOUT_IMAGE_URL_3": "",
                }
            },
            {
                "section_type": "gallery",
                "data": {
                    "GALLERY_TITLE": "I nostri piatti",
                    "GALLERY_ITEMS": [
                        {"GALLERY_IMAGE_URL": "", "GALLERY_CAPTION": "Pasta"},
                        {"GALLERY_IMAGE_URL": "", "GALLERY_CAPTION": "Pizza"},
                        {"GALLERY_IMAGE_URL": "", "GALLERY_CAPTION": "Dolci"},
                        {"GALLERY_IMAGE_URL": "", "GALLERY_CAPTION": "Antipasti"},
                    ]
                }
            },
            {
                "section_type": "team",
                "data": {
                    "TEAM_TITLE": "Il nostro team",
                    "TEAM_MEMBERS": [
                        {"MEMBER_NAME": "Mario Rossi", "MEMBER_ROLE": "Chef", "MEMBER_IMAGE_URL": ""},
                        {"MEMBER_NAME": "Luigi Verdi", "MEMBER_ROLE": "Sous Chef", "MEMBER_IMAGE_URL": ""},
                    ]
                }
            },
            {
                "section_type": "services",
                "data": {
                    "SERVICES_TITLE": "I nostri servizi",
                    "SERVICE_ITEMS": [
                        {"SERVICE_TITLE": "Catering", "SERVICE_IMAGE_URL": ""},
                        {"SERVICE_TITLE": "Eventi", "SERVICE_IMAGE_URL": ""},
                    ]
                }
            },
        ]}

        result = gen._inject_stock_photos(site_data, "restaurant-elegant")

        # Collect all image URLs from result
        issues = []
        comps = result["components"]

        # Hero
        hero_url = comps[0]["data"]["HERO_IMAGE_URL"]
        if not hero_url or not hero_url.startswith("https://"):
            issues.append(f"HERO_IMAGE_URL: '{hero_url}'")

        # About
        for key in ["ABOUT_IMAGE_URL", "ABOUT_IMAGE_URL_2", "ABOUT_IMAGE_URL_3"]:
            url = comps[1]["data"].get(key, "")
            if not url or not url.startswith("https://"):
                issues.append(f"{key}: '{url}'")

        # Gallery
        for i, item in enumerate(comps[2]["data"]["GALLERY_ITEMS"]):
            url = item.get("GALLERY_IMAGE_URL", "")
            if not url or not url.startswith("https://"):
                issues.append(f"GALLERY[{i}]: '{url}'")

        # Team
        for i, m in enumerate(comps[3]["data"]["TEAM_MEMBERS"]):
            url = m.get("MEMBER_IMAGE_URL", "")
            if not url or not url.startswith("https://"):
                issues.append(f"TEAM[{i}]: '{url}'")

        # Services
        for i, s in enumerate(comps[4]["data"]["SERVICE_ITEMS"]):
            url = s.get("SERVICE_IMAGE_URL", "")
            if not url or not url.startswith("https://"):
                issues.append(f"SERVICE[{i}]: '{url}'")

        assert len(issues) == 0, f"Images still missing after stock injection:\n" + "\n".join(issues)

    def test_saas_site_all_images_filled(self):
        """Full SaaS site: hero + about + blog should all have images."""
        from app.services.databinding_generator import DataBindingGenerator
        gen = DataBindingGenerator.__new__(DataBindingGenerator)

        site_data = {"components": [
            {
                "section_type": "hero",
                "data": {"HERO_IMAGE_URL": "", "HERO_TITLE": "SaaS App"}
            },
            {
                "section_type": "about",
                "data": {"ABOUT_IMAGE_URL": "", "ABOUT_TITLE": "About"}
            },
            {
                "section_type": "blog",
                "data": {
                    "BLOG_POSTS": [
                        {"POST_IMAGE_URL": "", "POST_TITLE": "Blog 1"},
                        {"POST_IMAGE_URL": "", "POST_TITLE": "Blog 2"},
                    ]
                }
            },
        ]}

        result = gen._inject_stock_photos(site_data, "saas-gradient")

        assert result["components"][0]["data"]["HERO_IMAGE_URL"].startswith("https://")
        assert result["components"][1]["data"]["ABOUT_IMAGE_URL"].startswith("https://")
        for post in result["components"][2]["data"]["BLOG_POSTS"]:
            assert post["POST_IMAGE_URL"].startswith("https://"), f"Blog post missing: {post}"


# ---------------------------------------------------------------------------
# PHASE 6: Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Test edge cases in the photo pipeline."""

    @classmethod
    def setup_class(cls):
        from app.services.databinding_generator import DataBindingGenerator
        cls.generator = DataBindingGenerator.__new__(DataBindingGenerator)

    def test_empty_components_list(self):
        """Empty components list should not crash."""
        site_data = {"components": []}
        result = self.generator._inject_stock_photos(site_data, "default")
        assert result["components"] == []

    def test_component_without_data(self):
        """Component without data dict should not crash."""
        site_data = {"components": [{"section_type": "hero"}]}
        result = self.generator._inject_stock_photos(site_data, "default")
        assert "data" not in result["components"][0] or result["components"][0].get("data") is None

    def test_gallery_items_not_list(self):
        """Non-list GALLERY_ITEMS should not crash."""
        site_data = {"components": [{
            "section_type": "gallery",
            "data": {"GALLERY_ITEMS": "not a list"}
        }]}
        # Should not raise
        result = self.generator._inject_stock_photos(site_data, "default")
        assert result is not None

    def test_svg_data_uri_in_hero(self):
        """SVG data URI placeholder should be replaced."""
        svg = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect fill="%23f1f5f9" width="800" height="600"/></svg>'
        site_data = {"components": [{
            "section_type": "hero",
            "data": {"HERO_IMAGE_URL": svg}
        }]}
        result = self.generator._inject_stock_photos(site_data, "restaurant-elegant")
        hero_url = result["components"][0]["data"]["HERO_IMAGE_URL"]
        assert not hero_url.startswith("data:"), f"SVG placeholder not replaced: {hero_url[:50]}"

    def test_unknown_style_uses_default(self):
        """Unknown style ID should fall back to default stock photos."""
        site_data = {"components": [{
            "section_type": "hero",
            "data": {"HERO_IMAGE_URL": ""}
        }]}
        result = self.generator._inject_stock_photos(site_data, "unknown-style-xyz")
        hero_url = result["components"][0]["data"]["HERO_IMAGE_URL"]
        # Should still get a URL (from default pool)
        assert hero_url.startswith("https://") or hero_url.startswith("data:"), \
            f"No fallback for unknown style: {hero_url}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
