"""Image fallback system — CSS gradients and patterns for missing images.

When no image is available, generates attractive CSS-based placeholders
instead of broken <img> tags or empty white space.

Each fallback is designed to look intentional, not broken. The gradients
and patterns use the site's own color palette so they blend naturally.

Usage:
    from app.services.images.fallback import get_css_fallback, get_fallback_html

    style = get_css_fallback("hero", {"primary": "#2563EB", "secondary": "#7C3AED"})
    # -> "background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%); ..."

    html = get_fallback_html("hero", {"primary": "#2563EB", "secondary": "#7C3AED"})
    # -> '<div style="..." aria-hidden="true"></div>'
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default colors (used when palette is incomplete)
# ---------------------------------------------------------------------------

_DEFAULTS = {
    "primary": "#2563EB",
    "secondary": "#7C3AED",
    "accent": "#F59E0B",
    "bg": "#0F172A",
    "bg_alt": "#1E293B",
    "text": "#F8FAFC",
}


# ---------------------------------------------------------------------------
# CSS fallback generators (one per section type)
# ---------------------------------------------------------------------------

def _hero_fallback(colors: Dict[str, str]) -> str:
    """Full-screen gradient mesh for hero sections.

    Creates a rich, multi-stop gradient that fills the entire hero area.
    Uses primary and secondary colors with strategic opacity stops.
    """
    primary = colors.get("primary", _DEFAULTS["primary"])
    secondary = colors.get("secondary", _DEFAULTS["secondary"])
    bg = colors.get("bg", _DEFAULTS["bg"])

    return (
        f"background: {bg}; "
        f"background-image: "
        f"radial-gradient(ellipse at 20% 50%, {primary}33 0%, transparent 50%), "
        f"radial-gradient(ellipse at 80% 20%, {secondary}44 0%, transparent 50%), "
        f"radial-gradient(ellipse at 50% 80%, {primary}22 0%, transparent 60%), "
        f"linear-gradient(135deg, {bg} 0%, {_darken(bg)} 100%); "
        f"min-height: 60vh;"
    )


def _gallery_fallback(colors: Dict[str, str]) -> str:
    """Subtle repeating pattern with primary color tint for gallery sections.

    Creates a soft geometric pattern that suggests visual content
    without looking like an error state.
    """
    primary = colors.get("primary", _DEFAULTS["primary"])
    bg_alt = colors.get("bg_alt", _DEFAULTS["bg_alt"])

    return (
        f"background-color: {bg_alt}; "
        f"background-image: "
        f"linear-gradient(30deg, {primary}0A 12%, transparent 12.5%, transparent 87%, {primary}0A 87.5%, {primary}0A), "
        f"linear-gradient(150deg, {primary}0A 12%, transparent 12.5%, transparent 87%, {primary}0A 87.5%, {primary}0A), "
        f"linear-gradient(30deg, {primary}0A 12%, transparent 12.5%, transparent 87%, {primary}0A 87.5%, {primary}0A), "
        f"linear-gradient(150deg, {primary}0A 12%, transparent 12.5%, transparent 87%, {primary}0A 87.5%, {primary}0A), "
        f"linear-gradient(60deg, {primary}14 25%, transparent 25.5%, transparent 75%, {primary}14 75%, {primary}14), "
        f"linear-gradient(60deg, {primary}14 25%, transparent 25.5%, transparent 75%, {primary}14 75%, {primary}14); "
        f"background-size: 80px 140px; "
        f"background-position: 0 0, 0 0, 40px 70px, 40px 70px, 0 0, 40px 70px; "
        f"min-height: 300px;"
    )


def _about_fallback(colors: Dict[str, str]) -> str:
    """Split gradient from primary to bg-alt for about sections.

    A clean diagonal split that adds visual interest without
    competing with text content.
    """
    primary = colors.get("primary", _DEFAULTS["primary"])
    bg_alt = colors.get("bg_alt", _DEFAULTS["bg_alt"])

    return (
        f"background: linear-gradient(160deg, {primary}1A 0%, {bg_alt} 40%, {bg_alt} 100%); "
        f"min-height: 400px;"
    )


def _testimonials_fallback(colors: Dict[str, str]) -> str:
    """Radial gradient with accent for testimonial sections.

    A centered radial gradient that creates a soft spotlight effect,
    drawing attention to the testimonial content.
    """
    accent = colors.get("accent", _DEFAULTS["accent"])
    bg = colors.get("bg", _DEFAULTS["bg"])

    return (
        f"background: "
        f"radial-gradient(circle at 50% 50%, {accent}15 0%, transparent 60%), "
        f"linear-gradient(180deg, {bg} 0%, {_darken(bg)} 100%); "
        f"min-height: 300px;"
    )


def _services_fallback(colors: Dict[str, str]) -> str:
    """Subtle dot pattern for services sections.

    A minimal dot grid that suggests structured content
    and professional presentation.
    """
    primary = colors.get("primary", _DEFAULTS["primary"])
    bg = colors.get("bg", _DEFAULTS["bg"])

    return (
        f"background-color: {bg}; "
        f"background-image: radial-gradient({primary}15 1px, transparent 1px); "
        f"background-size: 20px 20px; "
        f"min-height: 400px;"
    )


def _team_fallback(colors: Dict[str, str]) -> str:
    """Soft circular gradient for team/portrait placeholders.

    Creates a gentle circular highlight that works well as a
    placeholder for headshot images.
    """
    primary = colors.get("primary", _DEFAULTS["primary"])
    secondary = colors.get("secondary", _DEFAULTS["secondary"])

    return (
        f"background: "
        f"radial-gradient(circle at 50% 40%, {primary}20 0%, {secondary}10 50%, transparent 70%); "
        f"background-color: {_DEFAULTS['bg_alt']}; "
        f"aspect-ratio: 1; "
        f"border-radius: 50%;"
    )


def _generic_fallback(colors: Dict[str, str]) -> str:
    """Generic gradient fallback for unknown section types."""
    primary = colors.get("primary", _DEFAULTS["primary"])
    bg = colors.get("bg", _DEFAULTS["bg"])

    return (
        f"background: linear-gradient(135deg, {bg} 0%, {primary}1A 100%); "
        f"min-height: 200px;"
    )


# ---------------------------------------------------------------------------
# Section type to fallback function mapping
# ---------------------------------------------------------------------------

_FALLBACK_MAP = {
    "hero": _hero_fallback,
    "gallery": _gallery_fallback,
    "about": _about_fallback,
    "testimonials": _testimonials_fallback,
    "services": _services_fallback,
    "team": _team_fallback,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_css_fallback(section_type: str, colors: Optional[Dict[str, str]] = None) -> str:
    """Get a CSS background style string for a missing image.

    Args:
        section_type: Section type (hero, gallery, about, team, etc.).
        colors: Color palette dict with keys like primary, secondary, accent,
                bg, bg_alt. Missing keys are filled with defaults.

    Returns:
        CSS inline style string (without surrounding quotes).
        Ready for use in style="..." attribute.
    """
    merged_colors = {**_DEFAULTS, **(colors or {})}
    fallback_fn = _FALLBACK_MAP.get(section_type, _generic_fallback)

    try:
        return fallback_fn(merged_colors)
    except Exception as exc:
        logger.error("Fallback generation failed for '%s': %s", section_type, exc)
        return _generic_fallback(merged_colors)


def get_fallback_html(
    section_type: str,
    colors: Optional[Dict[str, str]] = None,
    extra_class: str = "",
) -> str:
    """Get a complete HTML div with CSS fallback background.

    Args:
        section_type: Section type.
        colors: Color palette dict.
        extra_class: Additional CSS class(es) for the div.

    Returns:
        HTML string: '<div style="..." class="..." aria-hidden="true"></div>'
    """
    style = get_css_fallback(section_type, colors)
    cls = f'class="{extra_class}" ' if extra_class else ""
    return f'<div {cls}style="{style}" aria-hidden="true"></div>'


# ---------------------------------------------------------------------------
# Color utilities
# ---------------------------------------------------------------------------

def _darken(hex_color: str, factor: float = 0.15) -> str:
    """Darken a hex color by a factor (0.0 = no change, 1.0 = black).

    Args:
        hex_color: CSS hex color like "#2563EB" or "#fff".
        factor: Darkening factor.

    Returns:
        Darkened hex color string.
    """
    hex_color = hex_color.lstrip("#")

    # Expand shorthand (#fff -> #ffffff)
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)

    if len(hex_color) != 6:
        return f"#{hex_color}"

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))

        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError:
        return f"#{hex_color}"
