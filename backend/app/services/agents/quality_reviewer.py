"""
Quality Reviewer Agent — validates generated HTML against the Design Brief.

Performs local (non-AI) checks:
1. Anti-bias rules: checks for forbidden patterns in the HTML
2. Animation coverage: verifies GSAP data-animate attributes exist
3. Font compliance: checks that forbidden fonts aren't used
4. Color compliance: checks that forbidden colors aren't used
5. Copy quality: checks for banned generic phrases

Returns a QualityReport with pass/fail and specific issues found.
"""

import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Generic phrases that should never appear
BANNED_PHRASES_IT = [
    "benvenuti", "benvenuto", "benvenuta",
    "siamo un'azienda", "siamo un team",
    "leader nel settore", "leader del settore",
    "eccellenza e innovazione",
    "qualità e professionalità",
    "soluzioni su misura", "soluzioni personalizzate",
    "a 360 gradi", "chiavi in mano",
    "da anni nel settore",
    "non esitare a contattarci",
    "contattaci per maggiori informazioni",
    "i nostri servizi", "cosa offriamo",
    "il nostro team di esperti",
    "scopri di più", "per saperne di più",
]

# Default fonts that indicate lazy generation
DEFAULT_FONTS = ["arial", "helvetica", "times new roman", "system-ui"]

# Minimum expected data-animate attributes per section count
MIN_ANIMATIONS_RATIO = 0.5  # At least 50% of sections should have animations


class QualityReviewer:
    """Validates generated HTML against quality standards and Design Brief."""

    def check(
        self,
        html: str,
        brief: Dict[str, Any],
        sections: List[str],
    ) -> Dict[str, Any]:
        """
        Run all quality checks on the generated HTML.

        Returns:
            {
                "passed": bool,
                "score": float (0-100),
                "issues": [{"severity": "critical|warning|info", "message": str}],
                "stats": {"animations_found": int, "banned_phrases_found": int, ...}
            }
        """
        issues: List[Dict[str, str]] = []
        stats = {}

        # 1. Check for banned copy phrases
        banned_found = self._check_banned_phrases(html)
        stats["banned_phrases_found"] = len(banned_found)
        for phrase in banned_found:
            issues.append({
                "severity": "critical",
                "message": f"Banned phrase found: '{phrase}'",
            })

        # 2. Check animation coverage
        anim_count = len(re.findall(r'data-animate="[^"]+?"', html))
        stats["animations_found"] = anim_count
        expected_min = max(len(sections) * 2, 5)
        if anim_count < expected_min:
            issues.append({
                "severity": "warning",
                "message": f"Low animation count: {anim_count} found, expected at least {expected_min}",
            })

        # 3. Check text-split on headings
        text_split_count = html.count('data-animate="text-split"')
        stats["text_split_headings"] = text_split_count
        if text_split_count < 1:
            issues.append({
                "severity": "warning",
                "message": "No text-split animations on headings (should have at least 1)",
            })

        # 4. Check magnetic on CTAs
        magnetic_count = html.count('data-animate="magnetic"')
        stats["magnetic_ctas"] = magnetic_count
        if magnetic_count < 1:
            issues.append({
                "severity": "info",
                "message": "No magnetic animation on CTA buttons",
            })

        # 5. Check forbidden fonts from brief
        forbidden_fonts = brief.get("typography_direction", {}).get("forbidden_fonts", [])
        fonts_found = self._check_forbidden_fonts(html, forbidden_fonts)
        stats["forbidden_fonts_found"] = len(fonts_found)
        for font in fonts_found:
            issues.append({
                "severity": "warning",
                "message": f"Forbidden font used: '{font}'",
            })

        # 6. Check forbidden colors from brief
        forbidden_colors = brief.get("color_direction", {}).get("forbidden_colors", [])
        colors_found = self._check_forbidden_colors(html, forbidden_colors)
        stats["forbidden_colors_found"] = len(colors_found)
        for color in colors_found:
            issues.append({
                "severity": "warning",
                "message": f"Forbidden color used: '{color}'",
            })

        # 7. Check section presence
        section_ids_found = re.findall(r'id="(\w+)"', html)
        missing_sections = [s for s in sections if s not in section_ids_found]
        stats["missing_sections"] = missing_sections
        for sec in missing_sections:
            issues.append({
                "severity": "critical",
                "message": f"Missing section: '{sec}' not found in HTML",
            })

        # 8. Check for default/placeholder content
        placeholder_patterns = [
            r"Lorem ipsum",
            r"placeholder\.com",
            r"example\.com",
            r"John Doe",
            r"Jane Doe",
            r"Acme Corp",
        ]
        for pat in placeholder_patterns:
            if re.search(pat, html, re.IGNORECASE):
                issues.append({
                    "severity": "critical",
                    "message": f"Placeholder content found: '{pat}'",
                })

        # Calculate score
        critical_count = sum(1 for i in issues if i["severity"] == "critical")
        warning_count = sum(1 for i in issues if i["severity"] == "warning")
        score = max(0, 100 - (critical_count * 20) - (warning_count * 5))

        passed = critical_count == 0 and score >= 60

        logger.info(
            "[QualityReviewer] Score: %.0f, passed=%s, criticals=%d, warnings=%d, anims=%d",
            score, passed, critical_count, warning_count, anim_count,
        )

        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "stats": stats,
        }

    def _check_banned_phrases(self, html: str) -> List[str]:
        """Find banned generic phrases in the HTML content."""
        html_lower = html.lower()
        found = []
        for phrase in BANNED_PHRASES_IT:
            if phrase.lower() in html_lower:
                found.append(phrase)
        return found

    def _check_forbidden_fonts(self, html: str, forbidden: List[str]) -> List[str]:
        """Check if forbidden fonts appear in the HTML (in font-family declarations or Google Fonts URLs)."""
        found = []
        html_lower = html.lower()
        all_forbidden = list(set([f.lower() for f in forbidden] + DEFAULT_FONTS))
        for font in all_forbidden:
            # Check in font-family CSS
            if f"font-family.*{font}" in html_lower or f"'{font}'" in html_lower or f'"{font}"' in html_lower:
                found.append(font)
            # Check in Google Fonts URL
            font_url = font.replace(" ", "+")
            if f"family={font_url}" in html_lower:
                found.append(font)
        return found

    def _check_forbidden_colors(self, html: str, forbidden: List[str]) -> List[str]:
        """Check if forbidden hex colors appear in the HTML."""
        found = []
        html_lower = html.lower()
        for color in forbidden:
            if color.lower() in html_lower:
                found.append(color)
        return found
