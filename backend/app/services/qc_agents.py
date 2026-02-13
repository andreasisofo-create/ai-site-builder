"""
QC Fix Agents - Specialized functions that auto-fix specific quality issues.

Each agent targets a specific category of issues and applies deterministic
or AI-assisted fixes to the HTML output.

All fix methods return a tuple of (modified_html, QCFixResult) so the
orchestrator can chain HTML modifications across agents.
"""

import logging
import re
import json
from typing import List, Dict, Any, Optional, Tuple

from app.models.qc_report import QCIssue, QCFixResult

logger = logging.getLogger(__name__)


# =========================================================
# Animation Fix Agent
# =========================================================
class AnimationFixAgent:
    """Adds missing GSAP data-animate attributes to key elements."""

    def fix(self, html: str, issues: List[QCIssue]) -> Tuple[str, QCFixResult]:
        """Add missing data-animate attributes. Returns (modified_html, result)."""
        fixed_count = 0

        # Fix h1 tags missing text-split
        h1_issues = [i for i in issues if "h1" in i.element.lower() and "text-split" in i.description]
        if h1_issues:
            html, count = self._add_animate_to_tag(html, "h1", "text-split", 'data-split-type="words"')
            fixed_count += count

        # Fix h2 tags missing text-split
        h2_issues = [i for i in issues if "h2" in i.element.lower() and "text-split" in i.description]
        if h2_issues:
            html, count = self._add_animate_to_tag(html, "h2", "text-split", 'data-split-type="words"')
            fixed_count += count

        # Fix CTA buttons missing magnetic
        cta_issues = [i for i in issues if "magnetic" in i.description.lower()]
        if cta_issues:
            html, count = self._add_magnetic_to_ctas(html)
            fixed_count += count

        # Fix cards missing fade-up
        card_issues = [i for i in issues if "card" in i.element.lower() and "fade-up" in i.description]
        if card_issues:
            html, count = self._add_animate_to_cards(html)
            fixed_count += count

        # Fix images missing animation
        img_issues = [i for i in issues if "img" in i.element.lower() and i.type == "animation"]
        if img_issues:
            html, count = self._add_animate_to_images(html)
            fixed_count += count

        result = QCFixResult(
            issue_type="animation",
            issues_fixed=fixed_count,
            description=f"Added data-animate to {fixed_count} elements",
            success=fixed_count > 0,
        )
        return html, result

    def _add_animate_to_tag(self, html: str, tag: str, animate_value: str, extra_attrs: str = "") -> Tuple[str, int]:
        """Add data-animate to tags that don't have it."""
        count = 0
        pattern = re.compile(
            rf'(<{tag}\b)(?![^>]*data-animate)([^>]*>)',
            re.IGNORECASE
        )

        def replacer(m):
            nonlocal count
            count += 1
            extra = f' {extra_attrs}' if extra_attrs else ''
            return f'{m.group(1)} data-animate="{animate_value}"{extra}{m.group(2)}'

        html = pattern.sub(replacer, html)
        return html, count

    def _add_magnetic_to_ctas(self, html: str) -> Tuple[str, int]:
        """Add data-animate="magnetic" to CTA-like links/buttons."""
        count = 0
        # Match <a> tags with CTA-like classes that don't already have data-animate
        cta_pattern = re.compile(
            r'(<a\b)(?![^>]*data-animate)([^>]*(?:bg-\[var\(--color-primary\)\]|btn|cta|bg-primary)[^>]*>)',
            re.IGNORECASE
        )

        def replacer(m):
            nonlocal count
            count += 1
            return f'{m.group(1)} data-animate="magnetic"{m.group(2)}'

        html = cta_pattern.sub(replacer, html)

        # Also match <button> tags without data-animate
        btn_pattern = re.compile(
            r'(<button\b)(?![^>]*data-animate)([^>]*>)',
            re.IGNORECASE
        )

        def btn_replacer(m):
            nonlocal count
            count += 1
            return f'{m.group(1)} data-animate="magnetic"{m.group(2)}'

        html = btn_pattern.sub(btn_replacer, html)
        return html, count

    def _add_animate_to_cards(self, html: str) -> Tuple[str, int]:
        """Add fade-up to card-like div containers."""
        count = 0
        card_pattern = re.compile(
            r'(<div\b)(?![^>]*data-animate)([^>]*(?:rounded-(?:xl|2xl|3xl)|shadow-(?:lg|xl|2xl)|card)[^>]*>)',
            re.IGNORECASE
        )

        def replacer(m):
            nonlocal count
            count += 1
            return f'{m.group(1)} data-animate="fade-up"{m.group(2)}'

        html = card_pattern.sub(replacer, html)
        return html, count

    def _add_animate_to_images(self, html: str) -> Tuple[str, int]:
        """Add fade-up to non-icon images that don't have animation."""
        count = 0
        img_pattern = re.compile(
            r'(<img\b)(?![^>]*data-animate)([^>]*>)',
            re.IGNORECASE
        )

        def replacer(m):
            nonlocal count
            tag_content = m.group(2)
            # Skip tiny images (logos, icons)
            if any(x in tag_content for x in ['h-6', 'h-8', 'h-10', 'w-6', 'w-8', 'w-10', 'h-4', 'w-4']):
                return m.group(0)
            count += 1
            return f'{m.group(1)} data-animate="fade-up"{m.group(2)}'

        html = img_pattern.sub(replacer, html)
        return html, count


# =========================================================
# Color Coherence Agent
# =========================================================
class ColorCoherenceAgent:
    """Fixes color incoherences by replacing off-palette colors with theme variables."""

    def fix(self, html: str, theme_config: Dict[str, Any], issues: List[QCIssue]) -> Tuple[str, QCFixResult]:
        """Replace off-palette inline colors. Returns (modified_html, result)."""
        fixed_count = 0

        for issue in issues:
            if issue.type != "color":
                continue

            color_match = re.search(r'#[0-9a-fA-F]{3,8}', issue.description)
            if not color_match:
                continue

            bad_color = color_match.group(0)
            closest_var = self._find_closest_theme_var(bad_color, theme_config)
            if not closest_var:
                continue

            old_pattern = re.escape(bad_color)
            new_html = re.sub(
                rf'(?:color|background-color|background|border-color)\s*:\s*{old_pattern}',
                lambda m: m.group(0).replace(bad_color, f'var(--color-{closest_var})'),
                html
            )

            if new_html != html:
                fixed_count += 1
                html = new_html

        result = QCFixResult(
            issue_type="color",
            issues_fixed=fixed_count,
            description=f"Replaced {fixed_count} off-palette colors with theme variables",
            success=fixed_count > 0,
        )
        return html, result

    def _find_closest_theme_var(self, hex_color: str, theme: Dict[str, Any]) -> Optional[str]:
        """Find the closest theme color variable name for a given hex."""
        color_map = {
            "primary": theme.get("primary_color", ""),
            "secondary": theme.get("secondary_color", ""),
            "accent": theme.get("accent_color", ""),
            "bg": theme.get("bg_color", ""),
            "bg-alt": theme.get("bg_alt_color", ""),
            "text": theme.get("text_color", ""),
            "text-muted": theme.get("text_muted_color", ""),
        }

        hex_color = hex_color.lower().strip()
        min_dist = float("inf")
        closest = None

        for var_name, theme_hex in color_map.items():
            if not theme_hex:
                continue
            dist = self._color_distance(hex_color, theme_hex.lower())
            if dist < min_dist:
                min_dist = dist
                closest = var_name

        return closest if closest and min_dist < 500 else None

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        h = hex_color.lstrip('#')
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        if len(h) < 6:
            return (128, 128, 128)
        try:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        except ValueError:
            return (128, 128, 128)

    def _color_distance(self, hex1: str, hex2: str) -> float:
        r1, g1, b1 = self._hex_to_rgb(hex1)
        r2, g2, b2 = self._hex_to_rgb(hex2)
        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


# =========================================================
# Text Quality Agent
# =========================================================
class TextQualityAgent:
    """Detects and replaces banned generic Italian phrases."""

    BANNED_PHRASES = [
        "benvenuti",
        "benvenuto",
        "siamo un'azienda",
        "siamo un azienda",
        "leader nel settore",
        "a 360 gradi",
        "offriamo servizi",
        "il nostro team",
        "qualita e professionalita",
        "qualit\u00e0 e professionalit\u00e0",
        "la nostra azienda",
        "benvenuti nel nostro sito",
        "benvenuti sul nostro sito",
    ]

    # Deterministic replacements (longer phrases first to avoid partial matches)
    REPLACEMENTS = {
        "benvenuti nel nostro sito": "Scopri cosa ci rende unici",
        "benvenuti sul nostro sito": "Scopri cosa ci rende unici",
        "benvenuti": "Scopri",
        "benvenuto": "Esplora",
        "siamo un'azienda": "La nostra missione \u00e8",
        "siamo un azienda": "La nostra missione \u00e8",
        "leader nel settore": "punto di riferimento",
        "a 360 gradi": "completo e personalizzato",
        "offriamo servizi": "Mettiamo a disposizione soluzioni",
        "il nostro team": "Il gruppo di esperti",
        "qualita e professionalita": "eccellenza e dedizione",
        "qualit\u00e0 e professionalit\u00e0": "eccellenza e dedizione",
        "la nostra azienda": "La nostra realt\u00e0",
    }

    async def fix(self, html: str, issues: List[QCIssue], kimi_client=None) -> Tuple[str, QCFixResult]:
        """Replace banned generic phrases. Returns (modified_html, result)."""
        fixed_count = 0

        # Collect banned phrases found via issues
        found_phrases = []
        for issue in issues:
            if issue.type != "text":
                continue
            for phrase in self.BANNED_PHRASES:
                if phrase.lower() in issue.description.lower():
                    found_phrases.append(phrase)

        # Also scan HTML directly
        if not found_phrases:
            html_lower = html.lower()
            for phrase in self.BANNED_PHRASES:
                if phrase.lower() in html_lower:
                    found_phrases.append(phrase)

        if not found_phrases:
            return html, QCFixResult(
                issue_type="text", issues_fixed=0,
                description="No banned phrases found", success=True,
            )

        # Try AI-powered replacement first
        if kimi_client:
            try:
                ai_html = await self._ai_replace(html, found_phrases, kimi_client)
                if ai_html:
                    return ai_html, QCFixResult(
                        issue_type="text",
                        issues_fixed=len(found_phrases),
                        description=f"AI replaced {len(found_phrases)} generic phrases",
                        success=True,
                    )
            except Exception as e:
                logger.warning(f"[TextQualityAgent] AI replacement failed: {e}, using fallback")

        # Deterministic fallback
        # Sort by phrase length descending to replace longer phrases first
        sorted_phrases = sorted(found_phrases, key=len, reverse=True)
        for phrase in sorted_phrases:
            replacement = self.REPLACEMENTS.get(phrase.lower())
            if replacement:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                new_html = pattern.sub(replacement, html)
                if new_html != html:
                    fixed_count += 1
                    html = new_html

        result = QCFixResult(
            issue_type="text",
            issues_fixed=fixed_count,
            description=f"Replaced {fixed_count} generic phrases with alternatives",
            success=fixed_count > 0,
        )
        return html, result

    async def _ai_replace(self, html: str, phrases: List[str], kimi_client) -> Optional[str]:
        """Use Kimi for contextual replacements of banned phrases."""
        contexts = []
        for phrase in phrases[:5]:
            idx = html.lower().find(phrase.lower())
            if idx >= 0:
                start = max(0, idx - 100)
                end = min(len(html), idx + len(phrase) + 100)
                contexts.append(html[start:end])

        if not contexts:
            return None

        prompt = f"""Sei un copywriter italiano esperto. Sostituisci queste frasi generiche con alternative creative e specifiche.
Rispondi SOLO con un JSON oggetto dove le chiavi sono le frasi originali e i valori sono le sostituzioni.

FRASI DA SOSTITUIRE:
{json.dumps(phrases[:5], ensure_ascii=False)}

CONTESTO (porzioni di HTML dove appaiono):
{chr(10).join(contexts[:3])}

REGOLE:
- Le sostituzioni devono essere evocative e specifiche
- Mantieni la stessa lunghezza approssimativa
- Non usare altre frasi generiche
- Rispondi SOLO con il JSON"""

        result = await kimi_client.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500, thinking=False, timeout=30.0,
        )

        if not result.get("success"):
            return None

        try:
            content = result["content"]
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                replacements = json.loads(json_match.group(0))
                for old_phrase, new_phrase in replacements.items():
                    pattern = re.compile(re.escape(old_phrase), re.IGNORECASE)
                    html = pattern.sub(new_phrase, html)
                return html
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"[TextQualityAgent] Failed to parse AI replacements: {e}")

        return None


# =========================================================
# Accessibility Agent
# =========================================================
class AccessibilityAgent:
    """Fixes accessibility issues: missing alt tags, heading hierarchy."""

    def fix(self, html: str, issues: List[QCIssue]) -> Tuple[str, QCFixResult]:
        """Apply accessibility fixes. Returns (modified_html, result)."""
        fixed_count = 0

        alt_issues = [i for i in issues if "alt" in i.description.lower()]
        if alt_issues:
            html, count = self._fix_missing_alt(html)
            fixed_count += count

        result = QCFixResult(
            issue_type="accessibility",
            issues_fixed=fixed_count,
            description=f"Fixed {fixed_count} accessibility issues",
            success=fixed_count > 0,
        )
        return html, result

    def _fix_missing_alt(self, html: str) -> Tuple[str, int]:
        """Add alt attribute to img tags that are missing it."""
        count = 0
        pattern = re.compile(r'(<img\b)(?![^>]*\balt\b)([^>]*)(>|/>)', re.IGNORECASE)

        def replacer(m):
            nonlocal count
            count += 1
            src_match = re.search(r'src="([^"]*)"', m.group(0))
            alt_text = ""
            if src_match:
                src = src_match.group(1)
                if "placehold" in src:
                    text_match = re.search(r'text=([^&"]+)', src)
                    if text_match:
                        alt_text = text_match.group(1).replace('+', ' ')
                elif src:
                    name = src.rsplit('/', 1)[-1].rsplit('.', 1)[0]
                    alt_text = name.replace('-', ' ').replace('_', ' ')

            return f'{m.group(1)} alt="{alt_text}"{m.group(2)}{m.group(3)}'

        html = pattern.sub(replacer, html)
        return html, count


# =========================================================
# Layout Fix Agent
# =========================================================
class LayoutFixAgent:
    """Fixes structural/layout HTML issues: duplicate IDs, unreplaced placeholders."""

    def fix(self, html: str, issues: List[QCIssue]) -> Tuple[str, QCFixResult]:
        """Apply layout/structure fixes. Returns (modified_html, result)."""
        fixed_count = 0

        dup_issues = [i for i in issues if "duplicate" in i.description.lower() and "id" in i.description.lower()]
        if dup_issues:
            html, count = self._fix_duplicate_ids(html)
            fixed_count += count

        placeholder_issues = [i for i in issues if "placeholder" in i.description.lower() or "{{" in i.description]
        if placeholder_issues:
            html, count = self._fix_placeholders(html)
            fixed_count += count

        result = QCFixResult(
            issue_type="layout",
            issues_fixed=fixed_count,
            description=f"Fixed {fixed_count} layout/structure issues",
            success=fixed_count > 0,
        )
        return html, result

    def _fix_duplicate_ids(self, html: str) -> Tuple[str, int]:
        """Remove duplicate id attributes, keeping the first occurrence."""
        count = 0
        seen_ids = set()
        id_pattern = re.compile(r'(\bid="([^"]*)")')

        def replacer(m):
            nonlocal count
            id_value = m.group(2)
            if id_value in seen_ids:
                count += 1
                return ''
            seen_ids.add(id_value)
            return m.group(1)

        html = id_pattern.sub(replacer, html)
        return html, count

    def _fix_placeholders(self, html: str) -> Tuple[str, int]:
        """Replace remaining {{PLACEHOLDER}} with sensible defaults."""
        count = 0
        placeholder_pattern = re.compile(r'\{\{(\w+)\}\}')

        defaults = {
            "LOGO_URL": "",
            "BUSINESS_NAME": "Business Name",
            "HERO_TITLE": "Il Tuo Titolo",
            "HERO_SUBTITLE": "La tua descrizione qui",
            "HERO_CTA_TEXT": "Scopri di Pi\u00f9",
            "HERO_CTA_URL": "#contact",
            "HERO_IMAGE_URL": "https://placehold.co/800x600/eee/999?text=Immagine",
            "HERO_IMAGE_ALT": "Immagine principale",
            "CONTACT_EMAIL": "",
            "CONTACT_PHONE": "",
            "CONTACT_ADDRESS": "",
            "CURRENT_YEAR": "2026",
        }

        def replacer(m):
            nonlocal count
            key = m.group(1)
            count += 1
            return defaults.get(key, "")

        html = placeholder_pattern.sub(replacer, html)
        return html, count


# =========================================================
# Section Fix Agent
# =========================================================
class SectionFixAgent:
    """Handles missing sections. Flags for re-generation rather than attempting to build HTML."""

    async def fix(
        self,
        html: str,
        missing_sections: List[str],
        theme_config: Dict[str, Any],
        style_id: str,
        kimi_client=None,
    ) -> Tuple[str, QCFixResult]:
        """Flag missing sections. Returns (unmodified_html, result)."""
        if not missing_sections:
            return html, QCFixResult(
                issue_type="section", issues_fixed=0,
                description="No missing sections", success=True,
            )

        logger.warning(
            f"[SectionFixAgent] Missing sections: {missing_sections}. "
            f"Style: {style_id}. These need re-generation."
        )

        return html, QCFixResult(
            issue_type="section", issues_fixed=0,
            description=f"Missing sections detected: {', '.join(missing_sections)}. Flagged for re-generation.",
            success=False,
        )
