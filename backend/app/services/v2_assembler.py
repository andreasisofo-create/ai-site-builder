"""
V2 Assembler - Builds complete HTML from DB-stored components + Style DNA.

Unlike the v1 TemplateAssembler which reads from files, this reads
component HTML from the ComponentV2 database records and injects
CSS variables from the Style DNA color palette.
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Section labels for navigation (Italian)
_SECTION_NAV_LABELS = {
    "hero": None,
    "about": "Chi Siamo",
    "services": "Servizi",
    "features": "Funzionalita'",
    "gallery": "Galleria",
    "menu": "Menu'",
    "testimonials": "Testimonianze",
    "team": "Team",
    "pricing": "Prezzi",
    "faq": "FAQ",
    "contact": "Contatti",
    "cta": None,
    "footer": None,
    "stats": "Numeri",
    "process": "Processo",
    "programs": "Programmi",
    "products": "Prodotti",
    "portfolio": "Portfolio",
    "booking": "Prenota",
    "cases": "Casi Studio",
}


def _hex_to_rgb(hex_color: str) -> str:
    """Convert '#3b82f6' to '59,130,246' for rgba()."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return "99,102,241"
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r},{g},{b}"
    except ValueError:
        return "99,102,241"


def _load_head_template() -> str:
    """Load head-template.html from components directory."""
    head_path = Path(__file__).parent.parent / "components" / "head" / "head-template.html"
    return head_path.read_text(encoding="utf-8")


def _load_gsap_script() -> str:
    """Load gsap-universal.js from components directory."""
    js_path = Path(__file__).parent.parent / "components" / "gsap-universal.js"
    return js_path.read_text(encoding="utf-8")


def _build_nav_html(sections: List[str], business_name: str) -> str:
    """Build a simple responsive nav from section list."""
    links = []
    for sec in sections:
        label = _SECTION_NAV_LABELS.get(sec)
        if label:
            links.append(f'<a href="#{sec}" class="nav-link">{label}</a>')

    if not links:
        return ""

    return f"""<nav class="site-nav" data-animate="fade-down" style="
        position:fixed; top:0; left:0; right:0; z-index:100;
        padding:1rem 2rem; display:flex; align-items:center;
        justify-content:space-between;
        background:rgba(var(--color-bg-rgb),0.85);
        backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
        border-bottom:1px solid rgba(var(--color-primary-rgb),0.08);
        transition: all 0.3s;" data-scroll-nav>
        <a href="#hero" class="nav-logo" style="
            font-family:var(--font-heading); font-weight:700;
            font-size:1.2rem; color:var(--color-text);
            text-decoration:none;">{business_name}</a>
        <div style="display:flex; gap:1.5rem; align-items:center;">
            {''.join(links)}
        </div>
    </nav>
    <style>
        .nav-link {{
            font-family:var(--font-body); font-size:0.85rem;
            color:var(--color-text-muted); text-decoration:none;
            transition: color 0.3s;
        }}
        .nav-link:hover {{ color:var(--color-primary); }}
        @media (max-width:768px) {{
            .site-nav > div {{ display:none; }}
        }}
    </style>"""


def assemble(
    style_dna: Dict[str, Any],
    section_htmls: Dict[str, str],
    section_order: List[str],
    business_name: str = "",
    meta_title: str = "",
    meta_description: str = "",
) -> str:
    """Assemble complete HTML page from Style DNA + section HTMLs.

    Args:
        style_dna: Style DNA JSON with color_palette, typography, etc.
        section_htmls: Dict mapping section_type -> filled HTML (placeholders already replaced)
        section_order: Ordered list of section types to include
        business_name: For nav and meta tags
        meta_title: Page title
        meta_description: Meta description
    Returns:
        Complete HTML string
    """
    # Extract colors from DNA
    palette = style_dna.get("color_palette", ["#3b82f6", "#1e40af", "#f59e0b", "#ffffff", "#111827"])
    primary = palette[0] if len(palette) > 0 else "#3b82f6"
    secondary = palette[1] if len(palette) > 1 else "#1e40af"
    accent = palette[2] if len(palette) > 2 else "#f59e0b"
    bg = palette[3] if len(palette) > 3 else "#ffffff"
    text_color = palette[4] if len(palette) > 4 else "#111827"

    # Determine bg-alt and text-muted
    bg_alt = _lighten_or_darken(bg, 0.03)
    text_muted = _lighten_or_darken(text_color, 0.4)

    font_heading = style_dna.get("typography_heading", "Inter")
    font_body = style_dna.get("typography_body", "Inter")

    # Density-based spacing
    density = style_dna.get("density", "balanced")
    spacing_map = {"minimal": "clamp(6rem,12vw,10rem)", "balanced": "clamp(5rem,10vw,8rem)", "dense": "clamp(3rem,6vw,5rem)"}
    radius_map = {"minimal": {"sm": "2px", "md": "4px", "lg": "8px"}, "balanced": {"sm": "6px", "md": "12px", "lg": "20px"}, "dense": {"sm": "8px", "md": "16px", "lg": "24px"}}
    max_width_map = {"minimal": "1100px", "balanced": "1200px", "dense": "1400px"}

    radii = radius_map.get(density, radius_map["balanced"])

    # Build head
    head_html = _load_head_template()

    # Replace head placeholders
    replacements = {
        "{{META_TITLE}}": meta_title or business_name or "Sito Web",
        "{{META_DESCRIPTION}}": meta_description or "",
        "{{OG_TITLE}}": meta_title or business_name or "Sito Web",
        "{{OG_DESCRIPTION}}": meta_description or "",
        "{{FONT_HEADING_URL}}": font_heading.replace(" ", "+"),
        "{{FONT_BODY_URL}}": font_body.replace(" ", "+"),
        "{{FONT_HEADING}}": font_heading,
        "{{FONT_BODY}}": font_body,
        "{{PRIMARY_COLOR}}": primary,
        "{{SECONDARY_COLOR}}": secondary,
        "{{ACCENT_COLOR}}": accent,
        "{{BG_COLOR}}": bg,
        "{{BG_ALT_COLOR}}": bg_alt,
        "{{TEXT_COLOR}}": text_color,
        "{{TEXT_MUTED_COLOR}}": text_muted,
        "{{PRIMARY_COLOR_RGB}}": _hex_to_rgb(primary),
        "{{BG_COLOR_RGB}}": _hex_to_rgb(bg),
        "{{RADIUS_SM}}": radii["sm"],
        "{{RADIUS_MD}}": radii["md"],
        "{{RADIUS_LG}}": radii["lg"],
        "{{SPACE_SECTION}}": spacing_map.get(density, spacing_map["balanced"]),
        "{{MAX_WIDTH}}": max_width_map.get(density, max_width_map["balanced"]),
    }

    for placeholder, value in replacements.items():
        head_html = head_html.replace(placeholder, value)

    # Build nav
    nav_html = _build_nav_html(section_order, business_name)

    # Assemble sections in order
    body_parts = []
    for section_type in section_order:
        html = section_htmls.get(section_type)
        if html:
            body_parts.append(html)

    # Load GSAP
    gsap_js = _load_gsap_script()

    # Compose full page
    full_html = f"""{head_html}
<body>
{nav_html}

{''.join(body_parts)}

<script>
{gsap_js}
</script>
</body>
</html>"""

    return full_html


def replace_placeholders(html: str, data: Dict[str, str]) -> str:
    """Replace {{PLACEHOLDER}} patterns in HTML with provided data.

    Handles both simple and REPEAT blocks:
      <!-- REPEAT:ITEMS -->...{{ITEM_FIELD}}...<!-- /REPEAT:ITEMS -->
    """
    # Handle REPEAT blocks first
    repeat_pattern = re.compile(
        r'<!-- REPEAT:(\w+) -->(.*?)<!-- /REPEAT:\1 -->',
        re.DOTALL
    )

    def expand_repeat(match):
        key = match.group(1)
        template = match.group(2)
        items = data.get(key)
        if not items or not isinstance(items, list):
            return ""
        parts = []
        for item in items:
            block = template
            if isinstance(item, dict):
                for k, v in item.items():
                    block = block.replace(f"{{{{{k}}}}}", str(v))
            parts.append(block)
        return "".join(parts)

    result = repeat_pattern.sub(expand_repeat, html)

    # Replace simple placeholders
    for key, value in data.items():
        if isinstance(value, str):
            result = result.replace(f"{{{{{key}}}}}", value)

    # Clean up any remaining unreplaced placeholders
    result = re.sub(r'\{\{[A-Z_]+\}\}', '', result)

    return result


def _lighten_or_darken(hex_color: str, amount: float) -> str:
    """Lighten (if dark bg) or darken (if light bg) a hex color."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return "#f5f5f5"
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        if luminance > 0.5:
            # Light bg -> darken
            r = max(0, int(r * (1 - amount)))
            g = max(0, int(g * (1 - amount)))
            b = max(0, int(b * (1 - amount)))
        else:
            # Dark bg -> lighten
            r = min(255, int(r + (255 - r) * amount))
            g = min(255, int(g + (255 - g) * amount))
            b = min(255, int(b + (255 - b) * amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError:
        return "#f5f5f5"
