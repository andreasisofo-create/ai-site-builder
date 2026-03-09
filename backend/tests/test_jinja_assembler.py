"""Tests for the Jinja2-based template assembler.

Covers:
- Single component rendering
- Missing variable handling (StrictUndefined)
- Auto-escaping (XSS prevention)
- Image fallback conditionals
- Loop rendering (services, gallery, testimonials, stats)
- Full page assembly
- Data normalization from old uppercase format
"""

import pytest

from app.services.jinja_assembler import JinjaAssembler, _hex_to_rgb, _css_gradient_fallback


@pytest.fixture
def assembler() -> JinjaAssembler:
    """Create a JinjaAssembler pointing at the components_v2 directory."""
    return JinjaAssembler()


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

class TestHexToRgb:
    def test_valid_hex(self) -> None:
        assert _hex_to_rgb("#3b82f6") == "59,130,246"

    def test_shorthand_hex(self) -> None:
        assert _hex_to_rgb("#fff") == "255,255,255"

    def test_no_hash(self) -> None:
        assert _hex_to_rgb("3b82f6") == "59,130,246"

    def test_invalid_returns_fallback(self) -> None:
        assert _hex_to_rgb("invalid") == "99,102,241"

    def test_empty_returns_fallback(self) -> None:
        assert _hex_to_rgb("") == "99,102,241"


class TestCssGradientFallback:
    def test_hero_gradient(self) -> None:
        result = _css_gradient_fallback("hero", "#ff0000")
        assert "ff0000" in result
        assert "linear-gradient" in result

    def test_unknown_section(self) -> None:
        result = _css_gradient_fallback("unknown")
        assert "linear-gradient" in result


# ---------------------------------------------------------------------------
# Component rendering tests
# ---------------------------------------------------------------------------

class TestRenderComponent:
    def test_hero_classic_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "business_name": "Trattoria Test",
            "hero_title": "Welcome",
            "hero_subtitle": "A fine place",
            "hero_image_url": "https://example.com/hero.jpg",
            "hero_image_alt": "Hero image",
            "hero_cta_text": "Book Now",
            "hero_cta_url": "#contact",
        }
        html = assembler.render_component("hero-classic-01", data)
        assert "Trattoria Test" in html
        assert "Welcome" in html
        assert "Book Now" in html
        assert 'src="https://example.com/hero.jpg"' in html
        assert "<!-- ERROR" not in html

    def test_hero_without_image_shows_fallback(self, assembler: JinjaAssembler) -> None:
        data = {
            "business_name": "Test",
            "hero_title": "Title",
            "hero_subtitle": "",
            "hero_image_url": "",
            "hero_image_alt": "",
            "hero_cta_text": "",
            "hero_cta_url": "",
        }
        html = assembler.render_component("hero-classic-01", data)
        assert "<img" not in html
        assert "bg-gradient-to-br" in html

    def test_hero_xss_escaped(self, assembler: JinjaAssembler) -> None:
        data = {
            "business_name": '<script>alert("xss")</script>',
            "hero_title": "Safe",
            "hero_subtitle": "",
            "hero_image_url": "https://example.com/img.jpg",
            "hero_image_alt": "",
            "hero_cta_text": "",
            "hero_cta_url": "",
        }
        html = assembler.render_component("hero-classic-01", data)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_about_magazine_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "about_title": "Our Story",
            "about_subtitle": "Since 1920",
            "about_text": "We are a family restaurant.",
            "about_image_url": "https://example.com/about.jpg",
            "about_image_alt": "About us",
            "business_name": "Trattoria",
            "about_stats": [
                {"stat_number": "50", "stat_label": "Years"},
                {"stat_number": "1000", "stat_label": "Clients"},
            ],
        }
        html = assembler.render_component("about-magazine-01", data)
        assert "Our Story" in html
        assert "Since 1920" in html
        assert 'data-counter="50"' in html
        assert "Years" in html
        assert "Clients" in html

    def test_about_without_stats_hides_section(self, assembler: JinjaAssembler) -> None:
        data = {
            "about_title": "Title",
            "about_subtitle": "",
            "about_text": "Text",
            "about_image_url": "",
            "about_image_alt": "",
            "business_name": "Test",
            "about_stats": [],
        }
        html = assembler.render_component("about-magazine-01", data)
        assert "data-counter" not in html

    def test_services_alternating_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "services_title": "What We Do",
            "services_subtitle": "Our best services",
            "services": [
                {"service_icon": "🍕", "service_title": "Pizza", "service_description": "The best pizza."},
                {"service_icon": "🍝", "service_title": "Pasta", "service_description": "Fresh pasta."},
            ],
        }
        html = assembler.render_component("services-alternating-rows-01", data)
        assert "What We Do" in html
        assert "Pizza" in html
        assert "Pasta" in html

    def test_gallery_spotlight_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "gallery_title": "Our Gallery",
            "gallery_subtitle": "Beautiful moments",
            "gallery_items": [
                {"gallery_image_url": "https://example.com/1.jpg", "gallery_image_alt": "Photo 1", "gallery_caption": "First"},
                {"gallery_image_url": "", "gallery_image_alt": "", "gallery_caption": "No Image"},
            ],
        }
        html = assembler.render_component("gallery-spotlight-01", data)
        assert "Our Gallery" in html
        assert "First" in html
        assert "No Image" in html
        # First item should have img, second should have gradient fallback
        assert 'src="https://example.com/1.jpg"' in html
        assert "bg-gradient-to-br" in html

    def test_testimonials_spotlight_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "testimonials_title": "What They Say",
            "testimonials_subtitle": "Reviews",
            "testimonials": [
                {
                    "testimonial_text": "Amazing food!",
                    "testimonial_author": "Mario Rossi",
                    "testimonial_role": "Food Critic",
                    "testimonial_avatar_url": "https://example.com/avatar.jpg",
                },
            ],
        }
        html = assembler.render_component("testimonials-spotlight-01", data)
        assert "What They Say" in html
        assert "Amazing food!" in html
        assert "Mario Rossi" in html
        assert "Food Critic" in html

    def test_testimonials_avatar_fallback(self, assembler: JinjaAssembler) -> None:
        data = {
            "testimonials_title": "Reviews",
            "testimonials_subtitle": "",
            "testimonials": [
                {
                    "testimonial_text": "Great!",
                    "testimonial_author": "Luca",
                    "testimonial_role": "",
                    "testimonial_avatar_url": "",
                },
            ],
        }
        html = assembler.render_component("testimonials-spotlight-01", data)
        # Should show initial letter fallback instead of broken img
        assert "<img" not in html
        assert ">L<" in html  # Initial letter "L" from "Luca"

    def test_contact_minimal_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "contact_title": "Get in Touch",
            "contact_subtitle": "We'd love to hear from you",
            "contact_email": "info@test.com",
            "contact_phone": "+39 123 456",
            "contact_address": "Via Roma 1, Milano",
        }
        html = assembler.render_component("contact-minimal-01", data)
        assert "Get in Touch" in html
        assert "info@test.com" in html
        assert "+39 123 456" in html
        assert "Via Roma 1, Milano" in html

    def test_contact_hides_empty_fields(self, assembler: JinjaAssembler) -> None:
        data = {
            "contact_title": "Contact",
            "contact_subtitle": "",
            "contact_email": "",
            "contact_phone": "",
            "contact_address": "",
        }
        html = assembler.render_component("contact-minimal-01", data)
        assert "mailto:" not in html
        assert "tel:" not in html

    def test_footer_centered_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "business_name": "My Business",
            "logo_url": "https://example.com/logo.png",
            "footer_description": "A great business",
            "business_phone": "+39 000",
            "business_email": "a@b.com",
            "business_address": "Via Test",
            "current_year": "2026",
            "nav_links": [
                {"href": "#about", "label": "Chi Siamo"},
                {"href": "#services", "label": "Servizi"},
            ],
        }
        html = assembler.render_component("footer-centered-01", data)
        assert "My Business" in html
        assert "A great business" in html
        assert "Chi Siamo" in html
        assert "2026" in html

    def test_nav_classic_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "business_name": "Nav Test",
            "logo_url": "https://example.com/logo.png",
            "nav_links": [
                {"href": "#about", "label": "About"},
                {"href": "#contact", "label": "Contact"},
            ],
        }
        html = assembler.render_component("nav-classic-01", data)
        assert "Nav Test" in html
        assert "About" in html
        assert "Contact" in html
        assert "nav-classic-toggle" in html

    def test_cta_gradient_renders(self, assembler: JinjaAssembler) -> None:
        data = {
            "cta_title": "Ready to Start?",
            "cta_subtitle": "Join us today",
            "cta_button_text": "Get Started",
            "cta_button_url": "#contact",
        }
        html = assembler.render_component("cta-gradient-animated-01", data)
        assert "Ready to Start?" in html
        assert "Join us today" in html
        assert "Get Started" in html

    def test_template_not_found(self, assembler: JinjaAssembler) -> None:
        html = assembler.render_component("nonexistent-variant-99", {})
        assert html == ""


# ---------------------------------------------------------------------------
# Data normalization tests
# ---------------------------------------------------------------------------

class TestNormalizeSiteData:
    def test_uppercase_to_lowercase(self) -> None:
        old = {"HERO_TITLE": "Hello", "BUSINESS_NAME": "Test"}
        result = JinjaAssembler.normalize_site_data(old)
        assert result == {"hero_title": "Hello", "business_name": "Test"}

    def test_list_items_normalized(self) -> None:
        old = {
            "GALLERY_ITEMS": [
                {"GALLERY_IMAGE_URL": "url1", "GALLERY_CAPTION": "cap1"},
                {"GALLERY_IMAGE_URL": "url2", "GALLERY_CAPTION": "cap2"},
            ]
        }
        result = JinjaAssembler.normalize_site_data(old)
        assert "gallery_items" in result
        assert result["gallery_items"][0]["gallery_image_url"] == "url1"
        assert result["gallery_items"][1]["gallery_caption"] == "cap2"

    def test_empty_dict(self) -> None:
        assert JinjaAssembler.normalize_site_data({}) == {}

    def test_non_list_non_dict_values(self) -> None:
        old = {"COUNT": 42, "FLAG": True, "EMPTY": None}
        result = JinjaAssembler.normalize_site_data(old)
        assert result == {"count": 42, "flag": True, "empty": None}


# ---------------------------------------------------------------------------
# Variant path resolution tests
# ---------------------------------------------------------------------------

class TestVariantToPath:
    def test_hero_variant(self) -> None:
        assert JinjaAssembler._variant_to_path("hero-classic-01") == "hero/hero-classic-01.html"

    def test_cta_variant(self) -> None:
        assert JinjaAssembler._variant_to_path("cta-gradient-animated-01") == "cta/cta-gradient-animated-01.html"

    def test_about_variant(self) -> None:
        assert JinjaAssembler._variant_to_path("about-magazine-01") == "about/about-magazine-01.html"

    def test_single_word(self) -> None:
        assert JinjaAssembler._variant_to_path("hero") == "hero/hero.html"


# ---------------------------------------------------------------------------
# Full assembly tests
# ---------------------------------------------------------------------------

class TestAssemble:
    def test_full_page_assembly(self, assembler: JinjaAssembler) -> None:
        site_data = {
            "head": {
                "BUSINESS_NAME": "Test Restaurant",
                "PRIMARY_COLOR": "#c8102e",
                "SECONDARY_COLOR": "#1a1a2e",
                "ACCENT_COLOR": "#c8102e",
                "BG_COLOR": "#faf9f6",
                "BG_ALT_COLOR": "#f0ede8",
                "TEXT_COLOR": "#1a1a2e",
                "TEXT_MUTED_COLOR": "#6b7280",
                "HEADING_FONT": "Playfair Display",
                "BODY_FONT": "Inter",
            },
            "sections": {
                "hero": {
                    "variant": "hero-classic-01",
                    "data": {
                        "business_name": "Test Restaurant",
                        "hero_title": "Fine Dining",
                        "hero_subtitle": "Since 1920",
                        "hero_image_url": "https://example.com/hero.jpg",
                        "hero_image_alt": "Restaurant",
                        "hero_cta_text": "Reserve",
                        "hero_cta_url": "#contact",
                    },
                },
                "contact": {
                    "variant": "contact-minimal-01",
                    "data": {
                        "contact_title": "Contact Us",
                        "contact_subtitle": "",
                        "contact_email": "info@test.com",
                        "contact_phone": "+39 000",
                        "contact_address": "Via Roma 1",
                    },
                },
            },
        }
        html = assembler.assemble(site_data)
        assert "<!DOCTYPE html>" in html
        assert "Test Restaurant" in html
        assert "Fine Dining" in html
        assert "Contact Us" in html
        assert "Playfair+Display" in html
        assert "--color-primary: #c8102e" in html

    def test_empty_sections(self, assembler: JinjaAssembler) -> None:
        site_data = {"head": {}, "sections": {}}
        html = assembler.assemble(site_data)
        assert "<!DOCTYPE html>" in html
