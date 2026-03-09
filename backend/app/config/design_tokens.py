"""Design Token System -- W3C DTCG-inspired tokens for consistent design.

Three-tier architecture:
1. Reference tokens: Raw values (color.blue.500 = #0066cc)
2. Semantic tokens: Purpose-mapped (color.primary = color.blue.500)
3. Component tokens: Context-specific (button.bg = color.primary)
"""

from typing import Dict, List, Any


# =========================================================
# SPACING SCALES
# =========================================================

SPACING_TIGHT: Dict[str, Any] = {
    "base": 4,
    "scale": [4, 8, 12, 16, 24, 32, 48, 64],
}

SPACING_COMFORTABLE: Dict[str, Any] = {
    "base": 8,
    "scale": [8, 16, 24, 32, 48, 64, 96, 128],
}

SPACING_GENEROUS: Dict[str, Any] = {
    "base": 12,
    "scale": [12, 24, 36, 48, 72, 96, 144, 192],
}

# =========================================================
# TYPOGRAPHY SCALES
# =========================================================

TYPE_SCALE_MINOR_THIRD: float = 1.2       # Conservative
TYPE_SCALE_MAJOR_THIRD: float = 1.25      # Balanced (recommended)
TYPE_SCALE_PERFECT_FOURTH: float = 1.333  # Dramatic

# =========================================================
# BORDER RADIUS PRESETS
# =========================================================

RADIUS_SHARP: str = "0"
RADIUS_SUBTLE: str = "0.375rem"
RADIUS_ROUNDED: str = "0.75rem"
RADIUS_PILL: str = "9999px"

# =========================================================
# SHADOW PRESETS
# =========================================================

SHADOW_NONE: str = "none"
SHADOW_SUBTLE: str = "0 1px 3px rgba(0,0,0,0.08)"
SHADOW_MEDIUM: str = "0 4px 12px rgba(0,0,0,0.1)"
SHADOW_DRAMATIC: str = "0 12px 40px rgba(0,0,0,0.15)"

# =========================================================
# CURATED FONT PAIRINGS (heading + body)
# All fonts are available on Google Fonts.
# =========================================================

FONT_PAIRINGS: List[Dict[str, str]] = [
    {"heading": "Playfair Display", "body": "Inter", "mood": "elegant"},
    {"heading": "Space Grotesk", "body": "DM Sans", "mood": "modern"},
    {"heading": "Sora", "body": "Plus Jakarta Sans", "mood": "clean"},
    {"heading": "DM Serif Display", "body": "Outfit", "mood": "editorial"},
    {"heading": "Clash Display", "body": "Satoshi", "mood": "bold"},
    {"heading": "Cabinet Grotesk", "body": "General Sans", "mood": "minimal"},
    {"heading": "Fraunces", "body": "Commissioner", "mood": "warm"},
    {"heading": "Unbounded", "body": "Figtree", "mood": "playful"},
    {"heading": "Instrument Serif", "body": "Instrument Sans", "mood": "refined"},
    {"heading": "Bricolage Grotesque", "body": "Geist", "mood": "tech"},
    {"heading": "Young Serif", "body": "Inter", "mood": "classic"},
    {"heading": "Libre Baskerville", "body": "Source Sans 3", "mood": "literary"},
    {"heading": "Archivo Black", "body": "Work Sans", "mood": "strong"},
    {"heading": "Cormorant Garamond", "body": "Lato", "mood": "luxury"},
    {"heading": "Bitter", "body": "Raleway", "mood": "professional"},
    {"heading": "Josefin Sans", "body": "Nunito Sans", "mood": "friendly"},
    {"heading": "Prata", "body": "Montserrat", "mood": "sophisticated"},
    {"heading": "Bodoni Moda", "body": "DM Sans", "mood": "fashion"},
    {"heading": "Vollkorn", "body": "Open Sans", "mood": "readable"},
    {"heading": "Darker Grotesque", "body": "IBM Plex Sans", "mood": "industrial"},
    {"heading": "Epilogue", "body": "Source Sans 3", "mood": "geometric"},
    {"heading": "Albert Sans", "body": "Karla", "mood": "swiss"},
    {"heading": "Outfit", "body": "Nunito Sans", "mood": "rounded"},
    {"heading": "Manrope", "body": "Inter", "mood": "balanced"},
    {"heading": "Lexend", "body": "Mulish", "mood": "accessible"},
]

# =========================================================
# DESIGN TOKEN PRESETS (complete themes)
# =========================================================

TOKEN_PRESETS: Dict[str, Dict[str, Any]] = {
    "tight-modern": {
        "spacing": SPACING_TIGHT,
        "type_scale": TYPE_SCALE_MINOR_THIRD,
        "radius": RADIUS_SUBTLE,
        "shadow": SHADOW_SUBTLE,
    },
    "comfortable-balanced": {
        "spacing": SPACING_COMFORTABLE,
        "type_scale": TYPE_SCALE_MAJOR_THIRD,
        "radius": RADIUS_ROUNDED,
        "shadow": SHADOW_MEDIUM,
    },
    "generous-dramatic": {
        "spacing": SPACING_GENEROUS,
        "type_scale": TYPE_SCALE_PERFECT_FOURTH,
        "radius": RADIUS_ROUNDED,
        "shadow": SHADOW_DRAMATIC,
    },
}
