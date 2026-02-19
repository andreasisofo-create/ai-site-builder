"""
Color Palette Generator — Adobe Color-style harmony schemes.

Given a single base color, generates a full 7-token palette using color theory:
  primary, secondary, accent, bg, bg_alt, text, text_muted

Supports 5 harmony schemes:
  - complementary (180° hue shift)
  - analogous (±30° hue shifts)
  - triadic (120° / 240° hue shifts)
  - split_complementary (150° / 210° hue shifts)
  - monochromatic (same hue, vary S/L)

Auto-selects scheme based on business category for optimal results.
"""

import math
from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# HSL ↔ Hex conversion
# ---------------------------------------------------------------------------

def _hex_to_hsl(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to HSL (h: 0-360, s: 0-100, l: 0-100)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
    max_c, min_c = max(r, g, b), min(r, g, b)
    l = (max_c + min_c) / 2
    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return round(h * 360), round(s * 100), round(l * 100)


def _hsl_to_hex(h: int, s: int, l: int) -> str:
    """Convert HSL (h: 0-360, s: 0-100, l: 0-100) to hex color."""
    h_f, s_f, l_f = h / 360, s / 100, l / 100
    if s_f == 0:
        r = g = b = l_f
    else:
        def hue2rgb(p: float, q: float, t: float) -> float:
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        q = l_f * (1 + s_f) if l_f < 0.5 else l_f + s_f - l_f * s_f
        p = 2 * l_f - q
        r = hue2rgb(p, q, h_f + 1/3)
        g = hue2rgb(p, q, h_f)
        b = hue2rgb(p, q, h_f - 1/3)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


# ---------------------------------------------------------------------------
# WCAG contrast helpers
# ---------------------------------------------------------------------------

def _relative_luminance(hex_color: str) -> float:
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
    r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = _relative_luminance(hex1)
    l2 = _relative_luminance(hex2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _ensure_contrast(text_hex: str, bg_hex: str, min_ratio: float = 4.5) -> str:
    """Adjust text color lightness until it meets min contrast ratio."""
    if _contrast_ratio(text_hex, bg_hex) >= min_ratio:
        return text_hex
    bg_lum = _relative_luminance(bg_hex)
    h, s, l = _hex_to_hsl(text_hex)
    direction = 1 if bg_lum < 0.5 else -1
    for _ in range(50):
        l = min(100, max(0, l + direction * 2))
        candidate = _hsl_to_hex(h, s, l)
        if _contrast_ratio(candidate, bg_hex) >= min_ratio:
            return candidate
    return "#F1F5F9" if bg_lum < 0.5 else "#1A1A2E"


# ---------------------------------------------------------------------------
# Harmony scheme generators
# ---------------------------------------------------------------------------

def _complementary(h: int, s: int, l: int) -> Dict[str, Tuple[int, int, int]]:
    """180° hue shift. Bold, high-energy contrast."""
    return {
        "primary": (h, s, l),
        "secondary": ((h + 180) % 360, max(s - 10, 30), _clamp_l(l, -5)),
        "accent": ((h + 180) % 360, min(s + 15, 100), _clamp_l(l, 10)),
    }


def _analogous(h: int, s: int, l: int) -> Dict[str, Tuple[int, int, int]]:
    """±30° hue shifts. Harmonious, warm feel."""
    return {
        "primary": (h, s, l),
        "secondary": ((h + 30) % 360, max(s - 5, 30), _clamp_l(l, -8)),
        "accent": ((h - 30) % 360, min(s + 10, 100), _clamp_l(l, 5)),
    }


def _triadic(h: int, s: int, l: int) -> Dict[str, Tuple[int, int, int]]:
    """120° / 240° shifts. Vibrant, balanced."""
    return {
        "primary": (h, s, l),
        "secondary": ((h + 120) % 360, max(s - 10, 30), _clamp_l(l, -5)),
        "accent": ((h + 240) % 360, min(s + 5, 100), _clamp_l(l, 5)),
    }


def _split_complementary(h: int, s: int, l: int) -> Dict[str, Tuple[int, int, int]]:
    """150° / 210° shifts. Bold but more balanced than pure complementary."""
    return {
        "primary": (h, s, l),
        "secondary": ((h + 150) % 360, max(s - 10, 30), _clamp_l(l, -5)),
        "accent": ((h + 210) % 360, min(s + 10, 100), _clamp_l(l, 8)),
    }


def _monochromatic(h: int, s: int, l: int) -> Dict[str, Tuple[int, int, int]]:
    """Same hue, vary saturation and lightness. Elegant, cohesive."""
    return {
        "primary": (h, s, l),
        "secondary": (h, max(s - 20, 20), _clamp_l(l, -15)),
        "accent": (h, min(s + 15, 100), _clamp_l(l, 15)),
    }


def _clamp_l(l: int, shift: int) -> int:
    return max(15, min(85, l + shift))


# Scheme registry
_SCHEMES = {
    "complementary": _complementary,
    "analogous": _analogous,
    "triadic": _triadic,
    "split_complementary": _split_complementary,
    "monochromatic": _monochromatic,
}


# ---------------------------------------------------------------------------
# Auto-select scheme based on category
# ---------------------------------------------------------------------------

CATEGORY_SCHEME_MAP: Dict[str, str] = {
    # Restaurants: warm, harmonious
    "restaurant": "analogous",
    "ristorante": "analogous",
    # SaaS: bold, energetic
    "saas": "split_complementary",
    "tech": "split_complementary",
    # Portfolio: vibrant, creative
    "portfolio": "triadic",
    "creative": "triadic",
    # E-commerce: attention-grabbing
    "ecommerce": "complementary",
    "shop": "complementary",
    # Business: professional, cohesive
    "business": "monochromatic",
    "corporate": "monochromatic",
    "studio_professionale": "monochromatic",
    # Blog: balanced
    "blog": "analogous",
    # Event: vibrant, festive
    "event": "triadic",
    # Beauty: elegant
    "bellezza": "analogous",
    "beauty": "analogous",
    # Health: trustworthy
    "salute": "split_complementary",
    "health": "split_complementary",
    # Fitness: energetic
    "fitness": "complementary",
    # Artisan: warm, earthy
    "artigiani": "analogous",
    # Agency: creative, bold
    "agenzia": "split_complementary",
}


# ---------------------------------------------------------------------------
# Background generation from base color
# ---------------------------------------------------------------------------

def _derive_bg(h: int, s: int, l: int, dark: bool) -> Tuple[str, str]:
    """Generate bg and bg_alt from primary HSL. Returns (bg_hex, bg_alt_hex)."""
    if dark:
        # Dark mode: tinted near-black
        bg = _hsl_to_hex(h, max(s - 50, 5), 8)
        bg_alt = _hsl_to_hex(h, max(s - 45, 8), 14)
    else:
        # Light mode: tinted near-white
        bg = _hsl_to_hex(h, max(s - 60, 5), 97)
        bg_alt = _hsl_to_hex(h, max(s - 55, 8), 93)
    return bg, bg_alt


def _derive_text(h: int, s: int, dark: bool) -> Tuple[str, str]:
    """Generate text and text_muted colors. Returns (text_hex, text_muted_hex)."""
    if dark:
        text = _hsl_to_hex(h, max(s - 60, 5), 93)
        muted = _hsl_to_hex(h, max(s - 55, 8), 72)
    else:
        text = _hsl_to_hex(h, max(s - 50, 10), 12)
        muted = _hsl_to_hex(h, max(s - 45, 8), 38)
    return text, muted


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_palette(
    base_hex: str,
    scheme: str = "auto",
    category: str = "",
    dark_mode: Optional[bool] = None,
) -> Dict[str, str]:
    """
    Generate a complete 7-token color palette from a single base color.

    Args:
        base_hex: Base/primary hex color (e.g. "#E63946")
        scheme: Harmony scheme or "auto" for category-based selection
        category: Business category (used for auto scheme selection)
        dark_mode: Force dark/light. None = auto-detect from base color lightness.

    Returns:
        Dict with keys: primary_color, secondary_color, accent_color,
        bg_color, bg_alt_color, text_color, text_muted_color
    """
    h, s, l = _hex_to_hsl(base_hex)

    # Auto-select scheme
    if scheme == "auto":
        scheme = CATEGORY_SCHEME_MAP.get(category.lower(), "split_complementary")

    scheme_fn = _SCHEMES.get(scheme, _split_complementary)
    colors = scheme_fn(h, s, l)

    # Convert HSL tuples to hex
    primary = _hsl_to_hex(*colors["primary"])
    secondary = _hsl_to_hex(*colors["secondary"])
    accent = _hsl_to_hex(*colors["accent"])

    # Auto-detect dark mode: if primary is dark (l < 40), assume dark site
    if dark_mode is None:
        dark_mode = l < 40

    bg, bg_alt = _derive_bg(h, s, l, dark_mode)
    text, text_muted = _derive_text(h, s, dark_mode)

    # WCAG contrast enforcement
    text = _ensure_contrast(text, bg, 4.5)
    text = _ensure_contrast(text, bg_alt, 4.5)
    text_muted = _ensure_contrast(text_muted, bg_alt, 4.5)
    text_muted = _ensure_contrast(text_muted, bg, 3.5)

    # Ensure accent pops against bg
    accent = _ensure_contrast(accent, bg, 3.0)

    return {
        "primary_color": primary,
        "secondary_color": secondary,
        "accent_color": accent,
        "bg_color": bg,
        "bg_alt_color": bg_alt,
        "text_color": text,
        "text_muted_color": text_muted,
    }


def get_all_schemes(base_hex: str, dark_mode: Optional[bool] = None) -> Dict[str, Dict[str, str]]:
    """
    Generate palettes for ALL 5 schemes from a single color.
    Useful for frontend preview where user picks their favorite scheme.

    Returns dict of {scheme_name: palette_dict}
    """
    return {
        name: generate_palette(base_hex, scheme=name, dark_mode=dark_mode)
        for name in _SCHEMES
    }
