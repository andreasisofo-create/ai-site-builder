"""Jinja2-based template assembler — replaces regex-based {{PLACEHOLDER}} system.

Key improvements over the old system:
- Auto-escaping prevents XSS
- {% if %} conditionals hide empty sections/images
- {% for %} loops replace REPEAT blocks
- Undefined variable errors caught at render time
- Template inheritance via {% extends %}

Usage:
    assembler = JinjaAssembler()
    html = assembler.render_component("hero-classic-01", {"business_name": "Trattoria"})
    # or full page:
    html = assembler.assemble(site_data)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import jinja2

logger = logging.getLogger(__name__)


# Section labels for navigation (Italian)
_SECTION_NAV_LABELS: Dict[str, Optional[str]] = {
    "hero": None,
    "about": "Chi Siamo",
    "services": "Servizi",
    "features": "Funzionalità",
    "gallery": "Galleria",
    "testimonials": "Testimonianze",
    "team": "Team",
    "pricing": "Prezzi",
    "faq": "FAQ",
    "blog": "Blog",
    "contact": "Contatti",
    "cta": None,
    "footer": None,
    "stats": "Numeri",
    "process": "Processo",
}


def _hex_to_rgb(hex_color: str) -> str:
    """Convert '#3b82f6' to '59,130,246' for use in rgba()."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return "99,102,241"
    try:
        r, g, b = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
        return f"{r},{g},{b}"
    except ValueError:
        return "99,102,241"


def _css_gradient_fallback(section_type: str, primary_color: str = "#6366f1") -> str:
    """Generate a CSS gradient placeholder for missing images."""
    gradients = {
        "hero": f"linear-gradient(135deg, {primary_color}22, {primary_color}08)",
        "about": f"linear-gradient(160deg, {primary_color}15, {primary_color}05)",
        "gallery": f"linear-gradient(135deg, {primary_color}18, {primary_color}06)",
        "services": f"linear-gradient(180deg, {primary_color}10, {primary_color}04)",
        "testimonials": f"linear-gradient(135deg, {primary_color}12, {primary_color}04)",
    }
    return gradients.get(section_type, f"linear-gradient(135deg, {primary_color}15, {primary_color}05)")


def _default_image_filter(url: Optional[str], fallback: str = "") -> str:
    """Return URL if valid, otherwise return fallback string.

    Jinja2 usage: {{ image_url | default_image('/fallback.png') }}
    """
    if not url or url.startswith("data:image/svg"):
        return fallback
    return url


def _is_valid_image(url: Optional[str]) -> bool:
    """Check if an image URL looks valid (not empty, not a placeholder SVG).

    Jinja2 usage: {% if image_url | is_valid_image %}
    """
    if not url:
        return False
    if url.startswith("data:image/svg"):
        return False
    return True


class JinjaAssembler:
    """Assembles HTML pages from Jinja2 component templates.

    The v2 component templates live in components_v2/ and use Jinja2 syntax
    instead of the old {{PLACEHOLDER}} regex system.

    This assembler is designed to coexist with the old TemplateAssembler.
    Both can be used in the same codebase during migration.
    """

    def __init__(self, components_dir: Optional[str] = None) -> None:
        if components_dir is None:
            components_dir = str(Path(__file__).parent.parent / "components_v2")

        self._components_dir = Path(components_dir)

        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self._components_dir)),
            autoescape=jinja2.select_autoescape(["html"]),
            undefined=jinja2.Undefined,  # Permissive: missing vars render as empty string
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self.env.filters["default_image"] = _default_image_filter
        self.env.filters["is_valid_image"] = _is_valid_image
        self.env.filters["hex_to_rgb"] = _hex_to_rgb

        # Register global functions
        self.env.globals["css_gradient_fallback"] = _css_gradient_fallback

    def render_component(
        self,
        variant_id: str,
        data: Dict[str, Any],
    ) -> str:
        """Render a single component template with data.

        Args:
            variant_id: Component variant ID, e.g. "hero-classic-01".
            data: Template data dict with lowercase keys.

        Returns:
            Rendered HTML string, or an HTML comment on error.
        """
        template_path = self._variant_to_path(variant_id)
        try:
            template = self.env.get_template(template_path)
            return template.render(**data)
        except jinja2.UndefinedError as e:
            logger.error("Missing variable in %s: %s", variant_id, e)
            return f"<!-- ERROR: {variant_id} missing data: {e} -->"
        except jinja2.TemplateNotFound:
            logger.error("Template not found: %s", template_path)
            return ""
        except jinja2.TemplateSyntaxError as e:
            logger.error("Syntax error in %s: %s (line %d)", variant_id, e.message, e.lineno)
            return f"<!-- ERROR: {variant_id} syntax error: {e.message} -->"

    def assemble(
        self,
        site_data: Dict[str, Any],
        section_order: Optional[List[str]] = None,
    ) -> str:
        """Assemble a complete HTML page from site_data.

        Args:
            site_data: Full site data dict. Expected structure:
                {
                    "head": {"PRIMARY_COLOR": "#...", "BG_COLOR": "#...", ...},
                    "sections": {
                        "hero": {"variant": "hero-classic-01", "data": {...}},
                        "about": {"variant": "about-magazine-01", "data": {...}},
                        ...
                    }
                }
            section_order: Optional list of section keys in render order.
                Defaults to: nav, hero, about, services, gallery, testimonials,
                cta, contact, footer.

        Returns:
            Complete HTML document string.
        """
        head_data = site_data.get("head", {})
        sections = site_data.get("sections", {})

        if section_order is None:
            section_order = [
                "nav", "hero", "about", "services", "features",
                "gallery", "testimonials", "team", "pricing",
                "faq", "blog", "cta", "contact", "footer",
            ]

        # Build nav links from active sections
        nav_links = self._build_nav_links(sections, section_order)

        # Render each section
        rendered_sections: List[str] = []
        for section_key in section_order:
            if section_key not in sections:
                continue

            section_info = sections[section_key]
            variant_id = section_info.get("variant", "")
            section_data = dict(section_info.get("data", {}))

            # Inject common data into every section
            section_data.setdefault("business_name", head_data.get("BUSINESS_NAME", ""))
            section_data.setdefault("nav_links", nav_links)
            section_data.setdefault("nav_links_mobile", nav_links)

            html = self.render_component(variant_id, section_data)
            if html:
                rendered_sections.append(html)

        body_html = "\n\n".join(rendered_sections)

        return self._wrap_in_document(body_html, head_data)

    def _build_nav_links(
        self,
        sections: Dict[str, Any],
        section_order: List[str],
    ) -> List[Dict[str, str]]:
        """Build navigation link list from active sections."""
        links: List[Dict[str, str]] = []
        for section_key in section_order:
            if section_key not in sections:
                continue
            label = _SECTION_NAV_LABELS.get(section_key)
            if label is None:
                continue
            links.append({"href": f"#{section_key}", "label": label})
        return links

    def _wrap_in_document(self, body_html: str, head_data: Dict[str, Any]) -> str:
        """Wrap rendered sections in a complete HTML document with head template."""
        primary = head_data.get("PRIMARY_COLOR", "#6366f1")
        secondary = head_data.get("SECONDARY_COLOR", "#1e40af")
        accent = head_data.get("ACCENT_COLOR", primary)
        bg = head_data.get("BG_COLOR", "#ffffff")
        bg_alt = head_data.get("BG_ALT_COLOR", "#f8fafc")
        text_color = head_data.get("TEXT_COLOR", "#1e293b")
        text_muted = head_data.get("TEXT_MUTED_COLOR", "#64748b")
        heading_font = head_data.get("HEADING_FONT", "Playfair Display")
        body_font = head_data.get("BODY_FONT", "Inter")

        primary_rgb = _hex_to_rgb(primary)
        bg_rgb = _hex_to_rgb(bg)

        return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{head_data.get('BUSINESS_NAME', 'Site')}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family={heading_font.replace(' ', '+')}:wght@400;600;700&family={body_font.replace(' ', '+')}:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
<style>
:root {{
  --color-primary: {primary};
  --color-secondary: {secondary};
  --color-accent: {accent};
  --color-bg: {bg};
  --color-bg-alt: {bg_alt};
  --color-text: {text_color};
  --color-text-muted: {text_muted};
  --color-primary-rgb: {primary_rgb};
  --color-bg-rgb: {bg_rgb};
}}
body {{
  font-family: '{body_font}', sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  margin: 0;
}}
.font-heading {{ font-family: '{heading_font}', serif; }}
.font-body {{ font-family: '{body_font}', sans-serif; }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

    @staticmethod
    def _variant_to_path(variant_id: str) -> str:
        """Convert variant ID to template file path.

        Examples:
            "hero-classic-01" -> "hero/hero-classic-01.html"
            "about-magazine-01" -> "about/about-magazine-01.html"
            "cta-gradient-animated-01" -> "cta/cta-gradient-animated-01.html"
        """
        # The category is the first word of the variant ID
        parts = variant_id.split("-")
        if len(parts) >= 2:
            category = parts[0]
        else:
            category = variant_id
        return f"{category}/{variant_id}.html"

    @staticmethod
    def normalize_site_data(old_format_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert old-format uppercase PLACEHOLDER data to Jinja2 lowercase format.

        This bridges the gap between databinding_generator output (uppercase keys)
        and Jinja2 templates (lowercase keys).

        Args:
            old_format_data: Dict with uppercase keys like "HERO_TITLE", "GALLERY_ITEMS".

        Returns:
            Dict with lowercase keys like "hero_title", "gallery_items".
            List items are also normalized recursively.
        """
        result: Dict[str, Any] = {}
        for key, value in old_format_data.items():
            lower_key = key.lower()
            if isinstance(value, list):
                normalized_list = []
                for item in value:
                    if isinstance(item, dict):
                        normalized_list.append(
                            {k.lower(): v for k, v in item.items()}
                        )
                    else:
                        normalized_list.append(item)
                result[lower_key] = normalized_list
            else:
                result[lower_key] = value
        return result
