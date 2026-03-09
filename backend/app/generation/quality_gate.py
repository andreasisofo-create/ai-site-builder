"""Unified Quality Gate -- validates AI output before assembly.

Replaces the 3 previous systems:
- quality_reviewer.py (post-HTML, non-blocking)
- pre_delivery_check.py (post-HTML, non-blocking)
- quality_control.py (post-HTML, non-blocking)

This gate operates on STRUCTURED DATA before assembly,
so issues can be fixed by retrying the AI call.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from pydantic import ValidationError

from app.generation.schemas.theme import ThemeSchema
from app.generation.schemas.validators import (
    SECTION_SCHEMA_MAP,
    fix_common_ai_errors,
)
from app.services.banned_phrases import BANNED_PHRASES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# WCAG contrast helpers (inlined from color_palette.py to avoid circular deps)
# ---------------------------------------------------------------------------

def _relative_luminance(hex_color: str) -> float:
    """Calculate WCAG 2.0 relative luminance from a hex color."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return 0.0
    try:
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
    except ValueError:
        return 0.0
    r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate WCAG contrast ratio between two hex colors."""
    l1 = _relative_luminance(hex1)
    l2 = _relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MINIMUM_SCORE = 60  # Below this, the gate fails

# Banned system/default fonts (must match ThemeSchema validator)
_BANNED_FONTS = frozenset({
    "arial", "helvetica", "times new roman", "times", "verdana",
    "georgia", "system-ui", "sans-serif", "serif", "monospace",
    "cursive", "tahoma", "courier", "courier new", "lucida console",
    "comic sans ms", "impact", "trebuchet ms",
})

# Minimum word counts per section type
_MIN_WORDS = {
    "hero": {"title": 3, "subtitle": 0, "description": 0},
    "about": {"title": 3, "text": 10, "description": 10},
    "services": {"title": 3},
    "features": {"title": 3},
    "testimonials": {"title": 3},
    "contact": {"title": 3},
    "cta": {"title": 3},
    "pricing": {"title": 3},
    "faq": {"title": 3},
    "team": {"title": 3},
    "gallery": {"title": 3},
    "menu": {"title": 3},
    "process": {"title": 3},
    "blog": {"title": 3},
}

# Map section field suffixes to the key used in data dicts
_FIELD_SUFFIX_MAP = {
    "title": ["_TITLE", "HERO_TITLE", "ABOUT_TITLE", "SERVICES_TITLE",
              "FEATURES_TITLE", "TESTIMONIALS_TITLE", "CONTACT_TITLE",
              "CTA_TITLE", "PRICING_TITLE", "FAQ_TITLE", "TEAM_TITLE",
              "GALLERY_TITLE", "MENU_TITLE", "PROCESS_TITLE", "BLOG_TITLE"],
    "subtitle": ["_SUBTITLE"],
    "text": ["ABOUT_TEXT"],
    "description": ["ABOUT_DESCRIPTION", "HERO_DESCRIPTION"],
}

# Required structural sections
_REQUIRED_SECTIONS = {"hero", "footer"}
_MIN_CONTENT_SECTIONS = 2  # At least 2 content sections besides hero/footer/nav


# ---------------------------------------------------------------------------
# Quality Report
# ---------------------------------------------------------------------------

@dataclass
class QualityReport:
    """Result of quality gate validation."""

    passed: bool
    score: int  # 0-100
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    failed_sections: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Quality Gate
# ---------------------------------------------------------------------------

class QualityGate:
    """Unified quality gate for site generation.

    Validates structured site data (theme + section content) BEFORE
    HTML assembly.  All checks are local and fast (no AI calls).
    """

    def __init__(self) -> None:
        self._banned_patterns = [
            re.compile(re.escape(phrase), re.IGNORECASE)
            for phrase in BANNED_PHRASES
        ]

    # ------------------------------------------------------------------
    # Theme validation
    # ------------------------------------------------------------------

    def validate_theme(self, theme_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate theme configuration against ThemeSchema + WCAG contrast.

        Returns (is_valid, list_of_error_strings).
        """
        errors: List[str] = []

        # 1. Pydantic schema validation
        try:
            ThemeSchema.model_validate(theme_data)
        except ValidationError as exc:
            for err in exc.errors():
                loc = " -> ".join(str(part) for part in err["loc"])
                errors.append(f"[theme] {loc}: {err['msg']}")

        # 2. Font checks (redundant with schema but catches edge cases)
        for font_key in ("FONT_HEADING", "FONT_BODY", "font_heading", "font_body"):
            font_val = theme_data.get(font_key, "")
            if isinstance(font_val, str) and font_val.lower().strip() in _BANNED_FONTS:
                errors.append(
                    f"[theme] Font '{font_val}' is a system default. "
                    "Use a Google Font like Playfair Display, Space Grotesk, Inter."
                )

        # 3. WCAG AA contrast checks (4.5:1 for normal text)
        bg_color = theme_data.get("BG_COLOR") or theme_data.get("bg_color", "#FFFFFF")
        text_color = theme_data.get("TEXT_COLOR") or theme_data.get("text_color", "")
        text_muted = theme_data.get("TEXT_MUTED_COLOR") or theme_data.get("text_muted_color", "")

        if bg_color and text_color:
            ratio = _contrast_ratio(text_color, bg_color)
            if ratio < 4.5:
                errors.append(
                    f"[theme] WCAG fail: TEXT_COLOR ({text_color}) on BG_COLOR ({bg_color}) "
                    f"has contrast ratio {ratio:.2f} (minimum 4.5:1)"
                )

        if bg_color and text_muted:
            ratio = _contrast_ratio(text_muted, bg_color)
            if ratio < 3.0:
                errors.append(
                    f"[theme] WCAG fail: TEXT_MUTED_COLOR ({text_muted}) on BG_COLOR ({bg_color}) "
                    f"has contrast ratio {ratio:.2f} (minimum 3.0:1 for large/muted text)"
                )

        return len(errors) == 0, errors

    # ------------------------------------------------------------------
    # Section validation
    # ------------------------------------------------------------------

    def validate_section(
        self, section_type: str, content: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate a single section's content.

        Uses Pydantic schemas, banned phrase detection, and text length checks.
        Returns (is_valid, list_of_error_strings).
        """
        errors: List[str] = []

        # 1. Pydantic schema validation (includes auto-fix)
        schema_cls = SECTION_SCHEMA_MAP.get(section_type)
        if schema_cls is not None:
            fixed_content = fix_common_ai_errors(content, section_type=section_type)
            try:
                schema_cls.model_validate(fixed_content)
            except ValidationError as exc:
                for err in exc.errors():
                    loc = " -> ".join(str(part) for part in err["loc"])
                    errors.append(f"[{section_type}] {loc}: {err['msg']}")

        # 2. Banned phrase detection
        banned_found = self._find_banned_phrases(content)
        for phrase, field_name in banned_found:
            errors.append(
                f"[{section_type}] Banned phrase '{phrase}' found in field '{field_name}'. "
                "Use creative, specific copy instead."
            )

        # 3. Minimum text length checks
        min_words = _MIN_WORDS.get(section_type, {})
        for field_role, min_count in min_words.items():
            if min_count <= 0:
                continue
            text_value = self._find_field_value(content, section_type, field_role)
            if text_value is not None:
                word_count = len(text_value.split())
                if word_count < min_count:
                    errors.append(
                        f"[{section_type}] '{field_role}' has {word_count} words "
                        f"(minimum {min_count})"
                    )

        return len(errors) == 0, errors

    # ------------------------------------------------------------------
    # Full site validation
    # ------------------------------------------------------------------

    def validate_site(self, site_data: Dict[str, Any]) -> QualityReport:
        """Validate complete site data before assembly.

        Checks theme, each section, structure, and content quality.
        Returns a QualityReport with score and error/warning lists.
        """
        report = QualityReport(passed=True, score=100)

        # 1. Theme validation
        theme = site_data.get("theme", {})
        theme_ok, theme_errors = self.validate_theme(theme)
        if not theme_ok:
            report.errors.extend(theme_errors)
            report.score -= min(20, len(theme_errors) * 5)

        # 2. Section validation
        components = site_data.get("components", [])
        section_types_seen: List[str] = []

        for component in components:
            variant_id = component.get("variant_id", "")
            # Extract section type from variant_id (e.g. "hero-bold-01" -> "hero")
            section_type = variant_id.split("-")[0] if variant_id else ""
            if not section_type or section_type.startswith("_"):
                continue

            section_types_seen.append(section_type)
            content = component.get("data", {})

            section_ok, section_errors = self.validate_section(section_type, content)
            if not section_ok:
                report.warnings.extend(section_errors)
                if section_type not in report.failed_sections:
                    report.failed_sections.append(section_type)
                report.score -= min(10, len(section_errors) * 3)

        # 3. Structural validation
        structural_errors = self._validate_structure(section_types_seen)
        if structural_errors:
            report.errors.extend(structural_errors)
            report.score -= len(structural_errors) * 5

        # 4. Cross-section banned phrase check on global data
        global_data = site_data.get("global", {})
        global_banned = self._find_banned_phrases(global_data)
        for phrase, field_name in global_banned:
            report.warnings.append(
                f"[global] Banned phrase '{phrase}' in '{field_name}'"
            )
            report.score -= 2

        # Clamp score
        report.score = max(0, min(100, report.score))
        report.passed = report.score >= MINIMUM_SCORE
        return report

    # ------------------------------------------------------------------
    # Retry prompt generation
    # ------------------------------------------------------------------

    def generate_retry_prompt(
        self, report: QualityReport, original_prompt: str
    ) -> str:
        """Generate an improved prompt for retrying failed sections.

        Appends specific fix instructions to the original prompt.
        """
        fixes: List[str] = []
        for error in report.errors:
            fixes.append(f"- FIX: {error}")
        for warning in report.warnings[:10]:  # Cap to avoid prompt bloat
            fixes.append(f"- IMPROVE: {warning}")
        for section in report.failed_sections:
            fixes.append(
                f"- Section '{section}' had validation errors, regenerate it"
            )

        if not fixes:
            return original_prompt

        fixes_text = "\n".join(fixes)
        return (
            f"{original_prompt}\n\n"
            f"IMPORTANT CORRECTIONS NEEDED:\n{fixes_text}\n\n"
            "Please fix these issues in your response."
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_banned_phrases(
        self, data: Dict[str, Any]
    ) -> List[Tuple[str, str]]:
        """Find banned phrases in all string values of a dict.

        Returns list of (banned_phrase, field_name) tuples.
        """
        found: List[Tuple[str, str]] = []
        for key, value in data.items():
            if isinstance(value, str):
                for i, pattern in enumerate(self._banned_patterns):
                    if pattern.search(value):
                        found.append((BANNED_PHRASES[i], key))
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        for sub_key, sub_val in item.items():
                            if isinstance(sub_val, str):
                                for i, pattern in enumerate(self._banned_patterns):
                                    if pattern.search(sub_val):
                                        found.append(
                                            (BANNED_PHRASES[i], f"{key}[{idx}].{sub_key}")
                                        )
        return found

    def _find_field_value(
        self, content: Dict[str, Any], section_type: str, field_role: str
    ) -> str | None:
        """Find the value of a field by its role (title, subtitle, text, description).

        Searches for UPPER_SNAKE_CASE keys matching the section type and role.
        """
        prefix = section_type.upper()
        suffix = field_role.upper()

        # Try direct match first: e.g. HERO_TITLE, ABOUT_TEXT
        direct_key = f"{prefix}_{suffix}"
        if direct_key in content:
            val = content[direct_key]
            return val if isinstance(val, str) else None

        # Try all keys that end with the suffix
        for key, val in content.items():
            if isinstance(val, str) and key.upper().endswith(f"_{suffix}"):
                return val

        return None

    def _validate_structure(self, section_types: List[str]) -> List[str]:
        """Validate structural requirements of the site.

        Checks for required sections and minimum content section count.
        """
        errors: List[str] = []
        section_set = set(section_types)

        # Check required sections
        for required in _REQUIRED_SECTIONS:
            if required not in section_set:
                errors.append(
                    f"[structure] Missing required section: '{required}'"
                )

        # Check minimum content sections (exclude nav, hero, footer, cta)
        structural_sections = {"nav", "hero", "footer", "cta"}
        content_sections = [s for s in section_types if s not in structural_sections]
        if len(content_sections) < _MIN_CONTENT_SECTIONS:
            errors.append(
                f"[structure] Only {len(content_sections)} content section(s) found "
                f"(minimum {_MIN_CONTENT_SECTIONS}). Add more sections like about, "
                "services, testimonials, etc."
            )

        return errors
