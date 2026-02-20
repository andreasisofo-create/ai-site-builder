#!/usr/bin/env python3
"""
Batch Template Converter
========================
Converts ThemeForest-style HTML templates into Site Builder component format.
Extracts sections, inlines CSS, replaces colors/fonts with CSS variables,
adds placeholders and GSAP animations.

Usage:
  # Convert a single HTML page (extracts all sections)
  python batch_converter.py "template/pixy/home-1.html" --css "template/pixy/css/style.css" --prefix "pixy"

  # Convert all HTML in a folder
  python batch_converter.py "template/_extracted/restaurant/dinex/" --prefix "dinex" --category restaurant

  # Dry run (analyze without converting)
  python batch_converter.py "path/to/template/" --dry-run
"""

import argparse
import io
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
COMPONENTS_DIR = PROJECT_ROOT / "app" / "components"
REGISTRY_PATH = COMPONENTS_DIR / "components.json"

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(message)s",
)
log = logging.getLogger("batch_converter")

# ── Section Detection ────────────────────────────────────────────────────────

# Section keywords used to detect section types from IDs, classes, or comments
SECTION_KEYWORDS = [
    "hero", "about", "services", "team", "contact", "portfolio", "gallery",
    "testimonials", "pricing", "faq", "stats", "cta", "features", "blog",
    "footer", "nav", "header", "menu", "process", "timeline", "video",
    "awards", "partners", "clients", "newsletter", "booking", "reservations",
    "schedule", "comparison", "listings", "social-proof", "app-download",
    "donations", "counter", "skill", "why-us", "banner", "funfact",
]

# Map variant keywords to canonical section types
SECTION_TYPE_ALIASES = {
    "header": "nav",
    "navbar": "nav",
    "navigation": "nav",
    "banner": "hero",
    "slider": "hero",
    "what-we-do": "services",
    "our-services": "services",
    "service": "services",
    "feature": "features",
    "why-us": "features",
    "why-choose-us": "features",
    "funfact": "stats",
    "fun-fact": "stats",
    "counter": "stats",
    "skill": "about",
    "our-team": "team",
    "member": "team",
    "testimonial": "testimonials",
    "review": "testimonials",
    "client": "testimonials",
    "partner": "testimonials",
    "portfolio-section": "gallery",
    "work": "gallery",
    "project": "gallery",
    "price": "pricing",
    "plan": "pricing",
    "subscribe": "newsletter",
    "newsletter": "cta",
    "call-to-action": "cta",
    "action": "cta",
    "question": "faq",
    "blog-section": "blog",
    "news": "blog",
    "article": "blog",
    "post": "blog",
    "booking": "contact",
    "reservation": "contact",
}

# ── Color Mapping ────────────────────────────────────────────────────────────

# We group hex colors by luminance ranges for smart replacement
def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert #rrggbb to (r, g, b)."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color[0]*2 + hex_color[1]*2 + hex_color[2]*2
    if len(hex_color) != 6:
        return (128, 128, 128)
    return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def _luminance(r: int, g: int, b: int) -> float:
    """Relative luminance 0..1."""
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def _is_chromatic(r: int, g: int, b: int) -> bool:
    """Check if color has saturation (not gray)."""
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    if max_c == 0:
        return False
    return (max_c - min_c) / max_c > 0.15


# Well-known hex colors from popular ThemeForest templates
KNOWN_PRIMARY_COLORS = {
    # Common blues
    "#0062ff", "#0066cc", "#007bff", "#2563eb", "#3b82f6", "#4f46e5",
    "#5b6cf7", "#6366f1", "#0d6efd",
    # Common greens
    "#10b981", "#22c55e", "#059669", "#16a34a",
    # Common oranges/reds
    "#f59e0b", "#f97316", "#ef4444", "#dc2626", "#e11d48",
    # Common purples
    "#7c3aed", "#8b5cf6", "#a855f7",
    # Common teals
    "#06b6d4", "#0891b2", "#14b8a6",
}

# ── Font Mapping ─────────────────────────────────────────────────────────────

HEADING_FONTS = [
    "Playfair Display", "DM Serif Display", "Space Grotesk", "Sora",
    "Poppins", "Montserrat", "Raleway", "Oswald", "Nunito",
    "Merriweather", "Lora", "Cormorant Garamond", "Josefin Sans",
    "Abril Fatface", "Crimson Text", "Bitter", "Libre Baskerville",
]

BODY_FONTS = [
    "Inter", "Roboto", "Open Sans", "Lato", "Nunito Sans",
    "Source Sans Pro", "Work Sans", "DM Sans", "Manrope",
    "Plus Jakarta Sans", "IBM Plex Sans",
]

ALL_FONTS = set(HEADING_FONTS + BODY_FONTS)

# ── GSAP Animation Rules ────────────────────────────────────────────────────

GSAP_ANIMATION_MAP = {
    "h1": {"data-animate": "text-split", "data-split-type": "words"},
    "h2": {"data-animate": "text-split", "data-split-type": "words"},
    "h3": {"data-animate": "fade-up"},
    "h4": {"data-animate": "fade-up"},
    "p": {"data-animate": "blur-slide", "data-delay": "0.2"},
    "img": {"data-animate": "scale-in", "data-delay": "0.3"},
    "section": {"data-animate": "fade-up"},
    "footer": {"data-animate": "fade-up"},
    "nav": {"data-animate": "fade-down"},
}

# ── Placeholder Naming ──────────────────────────────────────────────────────

# Same as stitch_converter.py
PLACEHOLDER_PATTERNS = {
    "hero": {
        "h1": "HERO_TITLE", "h2": "HERO_SUBTITLE", "p": "HERO_DESCRIPTION",
        "img_src": "HERO_IMAGE_URL", "img_alt": "HERO_IMAGE_ALT",
        "cta": "HERO_CTA_TEXT", "cta_href": "HERO_CTA_URL",
    },
    "about": {
        "h2": "ABOUT_TITLE", "h3": "ABOUT_SUBTITLE", "p": "ABOUT_TEXT",
        "img_src": "ABOUT_IMAGE_URL", "img_alt": "ABOUT_IMAGE_ALT",
    },
    "services": {
        "h2": "SERVICES_TITLE", "p_intro": "SERVICES_SUBTITLE",
        "item_h": "SERVICE_TITLE", "item_p": "SERVICE_DESCRIPTION",
        "item_icon": "SERVICE_ICON",
    },
    "testimonials": {
        "h2": "TESTIMONIALS_TITLE", "p_intro": "TESTIMONIALS_SUBTITLE",
        "item_p": "TESTIMONIAL_TEXT", "item_h": "TESTIMONIAL_AUTHOR",
        "item_sub": "TESTIMONIAL_ROLE", "item_img": "TESTIMONIAL_AVATAR_URL",
    },
    "contact": {
        "h2": "CONTACT_TITLE", "p_intro": "CONTACT_SUBTITLE",
        "cta": "CONTACT_CTA_TEXT",
    },
    "gallery": {
        "h2": "GALLERY_TITLE", "p_intro": "GALLERY_SUBTITLE",
        "item_img": "GALLERY_IMAGE_URL", "item_img_alt": "GALLERY_IMAGE_ALT",
    },
    "pricing": {
        "h2": "PRICING_TITLE", "p_intro": "PRICING_SUBTITLE",
        "item_h": "PLAN_NAME", "item_price": "PLAN_PRICE",
        "item_p": "PLAN_DESCRIPTION", "item_feature": "PLAN_FEATURE",
        "cta": "PLAN_CTA_TEXT",
    },
    "faq": {
        "h2": "FAQ_TITLE", "p_intro": "FAQ_SUBTITLE",
        "item_h": "FAQ_QUESTION", "item_p": "FAQ_ANSWER",
    },
    "team": {
        "h2": "TEAM_TITLE", "p_intro": "TEAM_SUBTITLE",
        "item_h": "MEMBER_NAME", "item_p": "MEMBER_ROLE",
        "item_img": "MEMBER_IMAGE_URL",
    },
    "stats": {
        "h2": "STATS_TITLE",
        "item_num": "STAT_NUMBER", "item_label": "STAT_LABEL",
    },
    "cta": {
        "h2": "CTA_TITLE", "p": "CTA_SUBTITLE",
        "cta": "CTA_BUTTON_TEXT", "cta_href": "CTA_BUTTON_URL",
    },
    "features": {
        "h2": "FEATURES_TITLE", "p_intro": "FEATURES_SUBTITLE",
        "item_h": "FEATURE_TITLE", "item_p": "FEATURE_DESCRIPTION",
        "item_icon": "FEATURE_ICON",
    },
    "footer": {
        "copyright": "FOOTER_COPYRIGHT",
    },
    "blog": {
        "h2": "BLOG_TITLE", "p_intro": "BLOG_SUBTITLE",
        "item_h": "POST_TITLE", "item_p": "POST_EXCERPT",
        "item_img": "POST_IMAGE_URL",
    },
    "nav": {
        "brand": "BUSINESS_NAME",
    },
}

REPEAT_KEY_MAP = {
    "services": "SERVICES",
    "testimonials": "TESTIMONIALS",
    "pricing": "PLANS",
    "team": "MEMBERS",
    "faq": "FAQS",
    "features": "FEATURES",
    "stats": "STATS",
    "gallery": "GALLERY_ITEMS",
    "blog": "POSTS",
    "menu": "MENU_ITEMS",
    "process": "STEPS",
    "timeline": "EVENTS",
    "partners": "PARTNERS",
}


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class ExtractedSection:
    """A section extracted from a full HTML page."""
    section_type: str
    raw_html: str
    original_id: str = ""
    original_classes: str = ""
    source_line: int = 0
    detection_method: str = ""  # "section-tag", "landmark", "class", "comment"


@dataclass
class ConvertedSection:
    """Result of converting one section."""
    section_type: str
    variant_id: str
    file_path: str
    html: str
    placeholders: list = field(default_factory=list)
    repeat_keys: list = field(default_factory=list)
    animations_added: int = 0
    colors_replaced: int = 0
    css_rules_inlined: int = 0
    registry_entry: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)


# ── CSS Parser ───────────────────────────────────────────────────────────────

class CSSInliner:
    """Extracts and inlines relevant CSS rules for a section HTML fragment."""

    def __init__(self, css_text: str):
        self.rules = self._parse_rules(css_text)
        log.info("Parsed %d CSS rules from stylesheet", len(self.rules))

    def _parse_rules(self, css: str) -> list:
        """Parse CSS into list of (selector_string, declarations_string)."""
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Remove @import, @charset, @font-face blocks
        css = re.sub(r'@import[^;]+;', '', css)
        css = re.sub(r'@charset[^;]+;', '', css)
        css = re.sub(r'@font-face\s*\{[^}]*\}', '', css, flags=re.DOTALL)

        rules = []
        # Handle @media blocks: flatten them (keep rules inside)
        media_pattern = r'@media[^{]*\{((?:[^{}]*|\{[^{}]*\})*)\}'
        for media_match in re.finditer(media_pattern, css, re.DOTALL):
            media_content = media_match.group(1)
            inner_rules = self._extract_rules(media_content)
            # Wrap with @media query for the output
            media_query = media_match.group(0).split('{')[0].strip()
            for sel, decl in inner_rules:
                rules.append((sel, decl, media_query))

        # Remove @media blocks from css to parse remaining
        css_no_media = re.sub(media_pattern, '', css, flags=re.DOTALL)
        for sel, decl in self._extract_rules(css_no_media):
            rules.append((sel, decl, None))

        return rules

    def _extract_rules(self, css: str) -> list:
        """Extract (selector, declarations) pairs from a CSS block."""
        results = []
        # Match selector { declarations }
        pattern = r'([^{}]+?)\{([^{}]+)\}'
        for m in re.finditer(pattern, css):
            selector = m.group(1).strip()
            declarations = m.group(2).strip()
            if selector and declarations and not selector.startswith('@'):
                results.append((selector, declarations))
        return results

    def get_relevant_css(self, section_html: str) -> str:
        """Extract CSS rules relevant to the given section HTML."""
        matched_rules = []
        media_rules = {}  # media_query -> list of rules

        # Extract all class names, IDs, and tag names from the section HTML
        classes = set(re.findall(r'class="([^"]*)"', section_html))
        all_classes = set()
        for cls_str in classes:
            for c in cls_str.split():
                all_classes.add(c)

        ids = set(re.findall(r'id="([^"]*)"', section_html))
        tags_in_html = set(re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)\b', section_html))
        tags_lower = {t.lower() for t in tags_in_html}

        for selector, declarations, media_query in self.rules:
            if self._selector_matches(selector, all_classes, ids, tags_lower):
                if media_query:
                    media_rules.setdefault(media_query, []).append(
                        f"  {selector} {{ {declarations} }}"
                    )
                else:
                    matched_rules.append(f"{selector} {{ {declarations} }}")

        if not matched_rules and not media_rules:
            return ""

        parts = []
        if matched_rules:
            parts.extend(matched_rules)
        for mq, rules in media_rules.items():
            parts.append(f"{mq} {{")
            parts.extend(rules)
            parts.append("}")

        return "\n".join(parts)

    def _selector_matches(self, selector: str, classes: set, ids: set, tags: set) -> bool:
        """Check if a CSS selector is likely relevant to the section HTML."""
        # Split compound selectors (e.g. ".foo, .bar")
        parts = [s.strip() for s in selector.split(',')]
        for part in parts:
            # Check for class selectors
            for cls in re.findall(r'\.([a-zA-Z_][\w-]*)', part):
                if cls in classes:
                    return True
            # Check for ID selectors
            for id_val in re.findall(r'#([a-zA-Z_][\w-]*)', part):
                if id_val in ids:
                    return True
            # Check for tag selectors (bare tags at start or after combinators)
            tag_parts = re.findall(r'(?:^|\s|>|\+|~)([a-zA-Z][a-zA-Z0-9]*)', part)
            for t in tag_parts:
                if t.lower() in tags:
                    return True
        return False


# ── Main Converter ───────────────────────────────────────────────────────────

class BatchConverter:
    """Converts ThemeForest HTML templates into Site Builder component format."""

    def __init__(self, components_dir: Optional[Path] = None):
        self.components_dir = components_dir or COMPONENTS_DIR
        self.registry_path = self.components_dir / "components.json"
        self._registry = None
        self._primary_color = None  # Detected dominant brand color

    @property
    def registry(self) -> dict:
        if self._registry is None:
            if self.registry_path.exists():
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    self._registry = json.load(f)
            else:
                self._registry = {"version": "2.0.0", "categories": {}}
        return self._registry

    # ── Section Extraction ───────────────────────────────────────────────

    def extract_sections(self, html: str) -> list:
        """
        Parse a full HTML page and extract individual sections.

        Detection strategies (in order):
        1. <section> tags with IDs
        2. Major landmark elements (<header>, <footer>, <nav>)
        3. Div containers with section class names
        4. Comment markers like <!-- Hero Section -->
        """
        sections = []

        # Remove DOCTYPE, html/head wrappers but keep body content
        html_body = self._extract_body(html)

        # Strategy 1: Find <section> tags
        section_pattern = r'(<section\b[^>]*>)(.*?)(</section>)'
        for match in re.finditer(section_pattern, html_body, re.DOTALL):
            open_tag = match.group(1)
            inner = match.group(2)
            full = match.group(0)

            sec_id = self._get_attr(open_tag, "id")
            sec_classes = self._get_attr(open_tag, "class")
            sec_type = self._detect_section_type(sec_id, sec_classes, inner)

            if sec_type:
                sections.append(ExtractedSection(
                    section_type=sec_type,
                    raw_html=full,
                    original_id=sec_id,
                    original_classes=sec_classes,
                    detection_method="section-tag",
                ))

        # Strategy 2: Landmark elements (<header>, <nav>, <footer>)
        for tag, sec_type in [("header", "nav"), ("nav", "nav"), ("footer", "footer")]:
            pattern = rf'(<{tag}\b[^>]*>)(.*?)(</{tag}>)'
            for match in re.finditer(pattern, html_body, re.DOTALL):
                full = match.group(0)
                # Skip if already captured inside a <section>
                if any(full in s.raw_html for s in sections):
                    continue
                # Skip if this tag is inside an already-extracted section
                start_pos = match.start()
                if self._is_inside_captured(start_pos, sections, html_body):
                    continue

                sections.append(ExtractedSection(
                    section_type=sec_type,
                    raw_html=full,
                    original_id=self._get_attr(match.group(1), "id"),
                    original_classes=self._get_attr(match.group(1), "class"),
                    detection_method="landmark",
                ))

        # Strategy 3: Divs with section-related classes or IDs
        # We track positions already captured to avoid picking up items inside sections
        captured_ranges = []
        for s in sections:
            s_start = html_body.find(s.raw_html[:80])
            if s_start >= 0:
                captured_ranges.append((s_start, s_start + len(s.raw_html)))

        for kw in SECTION_KEYWORDS:
            # Find divs with id or class containing the keyword
            id_pattern = rf'<div\b[^>]*(?:id|class)="[^"]*\b{re.escape(kw)}\b[^"]*"[^>]*>'
            for match in re.finditer(id_pattern, html_body, re.IGNORECASE):
                start = match.start()
                # Skip if inside an already-captured range
                if any(a <= start < b for a, b in captured_ranges):
                    continue
                full_div = self._extract_balanced_tag(html_body, start, "div")
                # Skip tiny divs (likely individual items, not full sections)
                if full_div and len(full_div) > 500:
                    sec_type = SECTION_TYPE_ALIASES.get(kw, kw)
                    # Don't duplicate
                    if not any(s.raw_html == full_div for s in sections):
                        sections.append(ExtractedSection(
                            section_type=sec_type,
                            raw_html=full_div,
                            original_id=self._get_attr(match.group(0), "id"),
                            original_classes=self._get_attr(match.group(0), "class"),
                            detection_method="class-keyword",
                        ))
                        # Add to captured ranges to prevent children from matching
                        captured_ranges.append((start, start + len(full_div)))

        # Sort by position in original HTML
        sections.sort(key=lambda s: html_body.find(s.raw_html[:80]))

        # Deduplicate overlapping sections (prefer section-tag over class-keyword)
        sections = self._deduplicate_sections(sections, html_body)

        # Merge multiple same-type small sections into one parent section
        sections = self._merge_same_type_items(sections, html_body)

        log.info("Extracted %d sections from HTML", len(sections))
        for s in sections:
            log.info(
                "  [%s] %s (id=%s, classes=%s, method=%s, %d chars)",
                s.section_type, s.section_type,
                s.original_id or "-", s.original_classes[:40] if s.original_classes else "-",
                s.detection_method, len(s.raw_html),
            )

        return sections

    def _extract_body(self, html: str) -> str:
        """Extract body content from full HTML page."""
        # Remove DOCTYPE
        html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)
        # Extract body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
        if body_match:
            return body_match.group(1)
        # Remove html/head tags
        html = re.sub(r'<html[^>]*>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'</html>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<head\b[^>]*>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)
        return html.strip()

    def _detect_section_type(self, sec_id: str, sec_classes: str, inner_html: str) -> str:
        """Detect the section type from id, classes, or content."""
        combined = f"{sec_id} {sec_classes}".lower()

        # Direct keyword match
        for kw in SECTION_KEYWORDS:
            if kw in combined:
                return SECTION_TYPE_ALIASES.get(kw, kw)

        # Check inner HTML for heading keywords
        heading_match = re.search(r'<h[1-3][^>]*>(.*?)</h[1-3]>', inner_html, re.DOTALL | re.IGNORECASE)
        if heading_match:
            heading_text = re.sub(r'<[^>]+>', '', heading_match.group(1)).strip().lower()
            for kw in SECTION_KEYWORDS:
                if kw in heading_text:
                    return SECTION_TYPE_ALIASES.get(kw, kw)

        # Check for forms -> contact
        if '<form' in inner_html.lower():
            return "contact"

        # Check for grids with images -> gallery
        img_count = len(re.findall(r'<img\b', inner_html, re.IGNORECASE))
        if img_count >= 4:
            return "gallery"

        # Default: unknown (will be tagged as generic)
        return ""

    def _get_attr(self, tag: str, attr: str) -> str:
        """Extract attribute value from an HTML opening tag."""
        match = re.search(rf'{attr}="([^"]*)"', tag, re.IGNORECASE)
        return match.group(1) if match else ""

    def _extract_balanced_tag(self, html: str, start: int, tag: str) -> Optional[str]:
        """Extract a balanced HTML tag from start position."""
        close_tag = f'</{tag}>'
        open_pattern = rf'<{tag}\b'
        depth = 0
        i = start

        while i < len(html):
            open_match = re.search(open_pattern, html[i:], re.IGNORECASE)
            close_idx = html.lower().find(close_tag.lower(), i)

            if close_idx == -1:
                return None

            if open_match and (i + open_match.start()) < close_idx:
                depth += 1
                i = i + open_match.start() + 1
            else:
                depth -= 1
                if depth == 0:
                    return html[start:close_idx + len(close_tag)]
                i = close_idx + len(close_tag)

        return None

    def _is_inside_captured(self, pos: int, sections: list, html: str) -> bool:
        """Check if a position in the HTML is inside an already-captured section."""
        for s in sections:
            s_start = html.find(s.raw_html[:80])
            if s_start >= 0 and s_start < pos < s_start + len(s.raw_html):
                return True
        return False

    def _deduplicate_sections(self, sections: list, html: str) -> list:
        """Remove sections that are subsets of other sections."""
        to_remove = set()
        for i, a in enumerate(sections):
            for j, b in enumerate(sections):
                if i == j:
                    continue
                # If a's HTML is contained within b's HTML, remove a
                # (unless a was detected with a higher-priority method)
                if a.raw_html in b.raw_html and i != j:
                    priority = {"section-tag": 3, "landmark": 2, "class-keyword": 1}
                    if priority.get(a.detection_method, 0) <= priority.get(b.detection_method, 0):
                        to_remove.add(i)
        return [s for i, s in enumerate(sections) if i not in to_remove]

    def _merge_same_type_items(self, sections: list, html: str) -> list:
        """
        When multiple sections of the same type are detected (e.g., 4 team cards),
        find their common parent container and use that as the single section instead.
        """
        from collections import Counter
        type_counts = Counter(s.section_type for s in sections)

        merged = []
        processed_types = set()

        for s in sections:
            if s.section_type in processed_types:
                continue

            if type_counts[s.section_type] > 1:
                # Multiple sections of same type -> find common parent
                same_type = [x for x in sections if x.section_type == s.section_type]
                parent_html = self._find_common_parent(same_type, html)
                if parent_html and len(parent_html) > max(len(x.raw_html) for x in same_type):
                    merged.append(ExtractedSection(
                        section_type=s.section_type,
                        raw_html=parent_html,
                        original_id=s.original_id,
                        original_classes="merged-parent",
                        detection_method="merged",
                    ))
                else:
                    # Couldn't find parent, keep only the first one
                    merged.append(same_type[0])
                    log.warning(
                        "Found %d '%s' items but no common parent; keeping first only",
                        len(same_type), s.section_type,
                    )
                processed_types.add(s.section_type)
            else:
                merged.append(s)

        return merged

    def _find_common_parent(self, sections: list, html: str) -> Optional[str]:
        """Find the common parent element that contains all sections of a type."""
        if not sections:
            return None

        # Find positions of all sections in the HTML
        positions = []
        for s in sections:
            pos = html.find(s.raw_html[:80])
            if pos >= 0:
                positions.append((pos, pos + len(s.raw_html)))

        if len(positions) < 2:
            return None

        # The parent must start before the first item and end after the last item
        first_start = min(p[0] for p in positions)
        last_end = max(p[1] for p in positions)

        # Walk backwards from the first item to find a container element
        search_start = max(0, first_start - 2000)
        prefix = html[search_start:first_start]

        # Find the last opening div/section tag before the first item
        parent_candidates = list(re.finditer(r'<(?:div|section)\b[^>]*>', prefix))
        if not parent_candidates:
            return None

        # Try each candidate (from closest to the items)
        for candidate in reversed(parent_candidates):
            tag_start = search_start + candidate.start()
            tag_name = "section" if candidate.group(0).startswith("<section") else "div"
            full_parent = self._extract_balanced_tag(html, tag_start, tag_name)
            if full_parent and tag_start + len(full_parent) >= last_end:
                # This parent contains all items
                # Skip if it's basically the entire page (> 80% of body)
                if len(full_parent) > len(html) * 0.8:
                    continue
                return full_parent

        return None

    # ── Color Detection ──────────────────────────────────────────────────

    def detect_primary_color(self, css_text: str, html: str) -> Optional[str]:
        """Detect the primary brand color from CSS and HTML."""
        # Collect all hex colors and their frequencies
        hex_colors = re.findall(r'#([0-9a-fA-F]{3,8})\b', css_text + html)
        freq = {}
        for h in hex_colors:
            # Normalize to 6-char hex
            if len(h) == 3:
                h = h[0]*2 + h[1]*2 + h[2]*2
            if len(h) == 6:
                h = h.lower()
                r, g, b = _hex_to_rgb(h)
                # Skip pure white, black, and near-grays
                if _is_chromatic(r, g, b) and 0.1 < _luminance(r, g, b) < 0.85:
                    freq[f"#{h}"] = freq.get(f"#{h}", 0) + 1

        if not freq:
            return None

        # Check if any known primary color is present
        for known in KNOWN_PRIMARY_COLORS:
            if known.lower() in freq:
                log.info("Detected known primary color: %s", known)
                return known.lower()

        # Most frequent chromatic color
        primary = max(freq, key=freq.get)
        log.info("Detected primary color: %s (frequency: %d)", primary, freq[primary])
        return primary

    # ── Section Conversion ───────────────────────────────────────────────

    def convert_section(
        self,
        section: ExtractedSection,
        css_inliner: Optional[CSSInliner],
        prefix: str,
        tags: Optional[list] = None,
        primary_color: Optional[str] = None,
    ) -> ConvertedSection:
        """Convert an extracted section to Site Builder component format."""
        tags = tags or []
        html = section.raw_html
        warnings = []
        colors_replaced = 0
        animations_added = 0
        css_rules_inlined = 0
        placeholders = []
        repeat_keys = []

        sec_type = section.section_type
        if not sec_type:
            warnings.append("Could not detect section type, skipping")
            return ConvertedSection(
                section_type="unknown",
                variant_id="unknown",
                file_path="",
                html=html,
                warnings=warnings,
            )

        # Step 1: Strip all <script> tags and inline JS
        html = self._strip_scripts(html)

        # Step 2: Inline relevant CSS
        if css_inliner:
            relevant_css = css_inliner.get_relevant_css(html)
            if relevant_css:
                css_rules_inlined = relevant_css.count('{')
                # Convert colors and fonts in the CSS too
                if primary_color:
                    relevant_css, _ = self._convert_colors_in_text(relevant_css, primary_color)
                relevant_css = self._convert_fonts_in_text(relevant_css)
                html = f"<style>\n{relevant_css}\n</style>\n{html}"
                log.debug("Inlined %d CSS rules for %s", css_rules_inlined, sec_type)

        # Step 3: Strip external CSS links
        html = re.sub(r'<link[^>]*rel="stylesheet"[^>]*/?\s*>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<link[^>]*href="[^"]*\.css"[^>]*/?\s*>', '', html, flags=re.IGNORECASE)

        # Step 4: Convert colors
        if primary_color:
            html, colors_replaced = self._convert_colors_in_text(html, primary_color)
        else:
            html, colors_replaced = self._convert_colors_generic(html)

        # Step 5: Convert fonts
        html = self._convert_fonts_in_text(html)

        # Step 6: Ensure section wrapper
        html = self._ensure_section_wrapper(html, sec_type)

        # Step 7: Detect and wrap repeat blocks
        html, repeat_keys = self._detect_repeats(html, sec_type)

        # Step 8: Insert placeholders
        html, placeholders = self._add_placeholders(html, sec_type)

        # Step 9: Add GSAP animations
        html, animations_added = self._add_animations(html, sec_type)

        # Step 10: Cleanup
        html = self._cleanup(html)

        # Step 11: Add component header comment
        variant_id = self._generate_variant_id(sec_type, prefix)
        detected_tags = self._auto_detect_tags(section, tags)
        tag_str = ", ".join(detected_tags) if detected_tags else "imported"
        html = f"<!-- Component: {variant_id} -->\n<!-- Tags: {tag_str} -->\n{html}"

        file_path = f"{sec_type}/{variant_id}.html"

        registry_entry = {
            "id": variant_id,
            "file": file_path,
            "name": f"{sec_type.title()} {prefix.title()}",
            "description": f"Componente {sec_type} importato da template {prefix}",
            "placeholders": sorted(set(placeholders)),
            "tags": detected_tags,
        }

        return ConvertedSection(
            section_type=sec_type,
            variant_id=variant_id,
            file_path=file_path,
            html=html,
            placeholders=sorted(set(placeholders)),
            repeat_keys=repeat_keys,
            animations_added=animations_added,
            colors_replaced=colors_replaced,
            css_rules_inlined=css_rules_inlined,
            registry_entry=registry_entry,
            warnings=warnings,
        )

    # ── Internal: Script Stripping ───────────────────────────────────────

    def _strip_scripts(self, html: str) -> str:
        """Remove all script tags, jQuery, inline JS event handlers."""
        # Remove <script> tags
        html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Remove inline event handlers (onclick, onmouseover, etc.)
        html = re.sub(r'\s+on[a-z]+="[^"]*"', '', html, flags=re.IGNORECASE)
        # Remove javascript: hrefs
        html = re.sub(r'href="javascript:[^"]*"', 'href="#"', html, flags=re.IGNORECASE)
        return html

    # ── Internal: Color Conversion ───────────────────────────────────────

    def _convert_colors_in_text(self, text: str, primary_color: str) -> tuple:
        """Replace hardcoded colors with CSS variables, using detected primary."""
        count = 0
        pr, pg, pb = _hex_to_rgb(primary_color)

        def replace_hex(match):
            nonlocal count
            hex_val = match.group(0)
            r, g, b = _hex_to_rgb(hex_val)
            lum = _luminance(r, g, b)

            # Check if close to primary color
            if abs(r - pr) < 40 and abs(g - pg) < 40 and abs(b - pb) < 40:
                count += 1
                return "var(--color-primary)"

            # Pure white / near-white
            if lum > 0.95:
                count += 1
                return "var(--color-bg)"

            # Very light gray -> bg-alt
            if lum > 0.9 and not _is_chromatic(r, g, b):
                count += 1
                return "var(--color-bg-alt)"

            # Very dark -> text color
            if lum < 0.1:
                count += 1
                return "var(--color-text)"

            # Dark gray -> text
            if lum < 0.25 and not _is_chromatic(r, g, b):
                count += 1
                return "var(--color-text)"

            # Medium gray -> text-muted
            if 0.25 <= lum <= 0.6 and not _is_chromatic(r, g, b):
                count += 1
                return "var(--color-text-muted)"

            # Light gray border area
            if 0.7 <= lum <= 0.9 and not _is_chromatic(r, g, b):
                count += 1
                return "var(--color-border)"

            # Chromatic but not primary -> accent
            if _is_chromatic(r, g, b):
                count += 1
                return "var(--color-accent, var(--color-secondary))"

            return hex_val

        # Match 6-digit and 3-digit hex colors (but not inside var(--)  already)
        text = re.sub(
            r'(?<!var\(-)(?<!\w)#([0-9a-fA-F]{6})\b',
            replace_hex,
            text,
        )
        text = re.sub(
            r'(?<!var\(-)(?<!\w)#([0-9a-fA-F]{3})\b(?![0-9a-fA-F])',
            replace_hex,
            text,
        )

        # Replace rgb()/rgba() calls
        def replace_rgb(match):
            nonlocal count
            r_val, g_val, b_val = int(match.group(1)), int(match.group(2)), int(match.group(3))
            lum = _luminance(r_val, g_val, b_val)

            if abs(r_val - pr) < 40 and abs(g_val - pg) < 40 and abs(b_val - pb) < 40:
                count += 1
                if match.group(4):  # rgba
                    return f"rgba(var(--color-primary-rgb), {match.group(4)})"
                return "var(--color-primary)"

            if lum > 0.95:
                count += 1
                return "var(--color-bg)"
            if lum < 0.1:
                count += 1
                return "var(--color-text)"

            return match.group(0)

        text = re.sub(
            r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)',
            replace_rgb,
            text,
        )

        return text, count

    def _convert_colors_generic(self, html: str) -> tuple:
        """Fallback color conversion when no primary color is detected.
        Uses luminance-based heuristics."""
        count = 0

        FALLBACK_HEX_COLORS = {
            # Blues (likely primary)
            r'#(?:3b82f6|2563eb|1d4ed8|4f46e5|6366f1|7c3aed|8b5cf6)': 'var(--color-primary)',
            # Grays for text
            r'#(?:111827|1f2937|0f172a|18181b)': 'var(--color-text)',
            r'#(?:6b7280|64748b|71717a|9ca3af)': 'var(--color-text-muted)',
            # Light grays for backgrounds
            r'#(?:f9fafb|f8fafc|fafafa|f3f4f6|f1f5f9)': 'var(--color-bg-alt)',
            r'#(?:ffffff|fff)': 'var(--color-bg)',
        }

        for pattern, var_name in FALLBACK_HEX_COLORS.items():
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                html = re.sub(pattern, var_name, html, flags=re.IGNORECASE)
                count += len(matches)

        return html, count

    # ── Internal: Font Conversion ────────────────────────────────────────

    def _convert_fonts_in_text(self, text: str) -> str:
        """Replace hardcoded font-family declarations with CSS variables."""
        for font in ALL_FONTS:
            pattern = rf"font-family:\s*['\"]?{re.escape(font)}['\"]?[^;]*"
            text = re.sub(pattern, "font-family: var(--font-heading)", text, count=1, flags=re.IGNORECASE)
            # Second occurrence and beyond -> body font
            text = re.sub(pattern, "font-family: var(--font-body)", text, flags=re.IGNORECASE)
        return text

    # ── Internal: Section Wrapper ────────────────────────────────────────

    def _ensure_section_wrapper(self, html: str, section_type: str) -> str:
        """Ensure content is wrapped in a proper <section> tag."""
        html = html.strip()

        # Already a section tag
        if re.match(r'^<section\b', html, re.IGNORECASE):
            # Ensure it has an id
            if 'id=' not in html[:200]:
                html = re.sub(
                    r'^<section',
                    f'<section id="{section_type}"',
                    html,
                    count=1,
                )
            return html

        # Nav/footer keep their own tags
        if section_type == "nav" and re.match(r'^<nav\b', html, re.IGNORECASE):
            return html
        if section_type == "nav" and re.match(r'^<header\b', html, re.IGNORECASE):
            return html
        if section_type == "footer" and re.match(r'^<footer\b', html, re.IGNORECASE):
            return html

        # Wrap div-based sections
        if re.match(r'^<div\b', html, re.IGNORECASE):
            # Replace outer div with section
            html = re.sub(r'^<div\b', f'<section id="{section_type}"', html, count=1)
            # Replace last </div> with </section>
            html = html[::-1].replace('>vid/<', '>noitces/<', 1)[::-1]
            return html

        # Wrap bare content
        return f'<section id="{section_type}" class="py-24 px-6" style="background: var(--color-bg)">\n  <div class="max-w-7xl mx-auto">\n{html}\n  </div>\n</section>'

    # ── Internal: Repeat Detection ───────────────────────────────────────

    def _detect_repeats(self, html: str, section_type: str) -> tuple:
        """Detect repeating patterns (grid children) and wrap in REPEAT blocks."""
        repeat_keys = []

        if section_type not in REPEAT_KEY_MAP:
            return html, repeat_keys

        repeat_key = REPEAT_KEY_MAP[section_type]

        # Find grid/flex containers or lists
        grid_patterns = [
            r'<(?:div|ul)\b[^>]*(?:class="[^"]*(?:grid|flex|row|columns|items)[^"]*")[^>]*>',
            r'<(?:div|ul)\b[^>]*(?:style="[^"]*(?:display:\s*(?:grid|flex))[^"]*")[^>]*>',
        ]

        for gp in grid_patterns:
            grid_match = re.search(gp, html, re.IGNORECASE)
            if grid_match:
                container_start = grid_match.start()
                container_open = grid_match.group(0)
                container_tag = "ul" if container_open.startswith("<ul") else "div"

                container_full = self._extract_balanced_tag(html, container_start, container_tag)
                if not container_full:
                    continue

                # Extract direct children
                inner = container_full[len(container_open):-len(f'</{container_tag}>')]
                child_tag = "li" if container_tag == "ul" else "div"
                children = self._find_direct_children(inner, child_tag)

                if len(children) < 2:
                    continue

                # Use first child as template
                first_item = children[0]

                # Add stagger-item class
                if 'class="' in first_item:
                    first_item = re.sub(
                        r'class="([^"]*)"',
                        r'class="\1 stagger-item"',
                        first_item,
                        count=1,
                    )
                else:
                    first_item = first_item.replace(f'<{child_tag}', f'<{child_tag} class="stagger-item"', 1)

                repeat_block = (
                    f"{container_open}\n"
                    f"      <!-- REPEAT:{repeat_key} -->\n"
                    f"      {first_item}\n"
                    f"      <!-- /REPEAT:{repeat_key} -->\n"
                    f"    </{container_tag}>"
                )

                html = html.replace(container_full, repeat_block)
                repeat_keys.append(repeat_key)
                break  # Only wrap the first matching grid

        return html, repeat_keys

    def _find_direct_children(self, html: str, tag: str) -> list:
        """Find direct child elements of a given tag type."""
        children = []
        pos = 0
        while pos < len(html):
            match = re.search(rf'<{tag}\b', html[pos:], re.IGNORECASE)
            if not match:
                break
            child_start = pos + match.start()
            child_full = self._extract_balanced_tag(html, child_start, tag)
            if child_full:
                children.append(child_full)
                pos = child_start + len(child_full)
            else:
                pos = child_start + 1
        return children

    # ── Internal: Placeholder Insertion ──────────────────────────────────

    def _add_placeholders(self, html: str, section_type: str) -> tuple:
        """Replace hardcoded text and images with {{PLACEHOLDER}} syntax."""
        placeholders = []
        patterns = PLACEHOLDER_PATTERNS.get(section_type, {})
        section_upper = section_type.upper()

        # Track counters
        counters = {}

        def next_ph(base: str) -> str:
            counters[base] = counters.get(base, 0) + 1
            if counters[base] == 1:
                return base
            return f"{base}_{counters[base]}"

        def in_repeat(pos: int) -> bool:
            before = html[:pos]
            opens = len(re.findall(r'<!-- REPEAT:\w+ -->', before))
            closes = len(re.findall(r'<!-- /REPEAT:\w+ -->', before))
            return opens > closes

        # ── Replace content inside REPEAT blocks first ───────────────────
        repeat_pattern = r'(<!-- REPEAT:(\w+) -->)(.*?)(<!-- /REPEAT:\2 -->)'
        for rmatch in re.finditer(repeat_pattern, html, re.DOTALL):
            repeat_open, repeat_key, repeat_content, repeat_close = rmatch.groups()

            # Determine item-level placeholder names
            item_h_name = patterns.get("item_h", f"{repeat_key[:-1]}_TITLE" if repeat_key.endswith("S") else f"{repeat_key}_TITLE")
            item_p_name = patterns.get("item_p", f"{repeat_key[:-1]}_DESCRIPTION" if repeat_key.endswith("S") else f"{repeat_key}_TEXT")
            item_icon_name = patterns.get("item_icon", f"{repeat_key[:-1]}_ICON" if repeat_key.endswith("S") else f"{repeat_key}_ICON")
            item_img_name = patterns.get("item_img", f"{repeat_key[:-1]}_IMAGE_URL" if repeat_key.endswith("S") else f"{repeat_key}_IMAGE_URL")
            item_img_alt_name = patterns.get("item_img_alt", f"{repeat_key[:-1]}_IMAGE_ALT" if repeat_key.endswith("S") else f"{repeat_key}_IMAGE_ALT")

            # Replace headings inside repeat
            for htag in ['h2', 'h3', 'h4', 'h5']:
                def _replace_rh(m, _name=item_h_name):
                    ot, content, ct = m.groups()
                    if '{{' in content:
                        return m.group(0)
                    text = re.sub(r'<[^>]+>', '', content).strip()
                    if not text:
                        return m.group(0)
                    placeholders.append(_name)
                    return f"{ot}{{{{{_name}}}}}{ct}"
                repeat_content = re.sub(rf'(<{htag}\b[^>]*>)(.*?)(</{htag}>)', _replace_rh, repeat_content, flags=re.DOTALL)

            # Replace paragraphs inside repeat
            def _replace_rp(m):
                ot, content, ct = m.groups()
                if '{{' in content:
                    return m.group(0)
                text = re.sub(r'<[^>]+>', '', content).strip()
                if not text or len(text) < 3:
                    return m.group(0)
                placeholders.append(item_p_name)
                return f"{ot}{{{{{item_p_name}}}}}{ct}"
            repeat_content = re.sub(r'(<p\b[^>]*>)(.*?)(</p>)', _replace_rp, repeat_content, flags=re.DOTALL)

            # Replace images inside repeat
            def _replace_rimg(m):
                tag = m.group(0)
                if '{{' in tag:
                    return tag
                placeholders.append(item_img_name)
                placeholders.append(item_img_alt_name)
                tag = re.sub(r'src="[^"]*"', f'src="{{{{{item_img_name}}}}}"', tag)
                if 'alt=' in tag:
                    tag = re.sub(r'alt="[^"]*"', f'alt="{{{{{item_img_alt_name}}}}}"', tag)
                return tag
            repeat_content = re.sub(r'<img\b[^>]*/?\s*>', _replace_rimg, repeat_content)

            # Replace icon spans/i tags inside repeat
            def _replace_ricon(m):
                tag = m.group(0)
                if '{{' in tag:
                    return tag
                placeholders.append(item_icon_name)
                # Replace the icon class/content with placeholder
                return re.sub(r'>(.*?)</', f'>{{{{{item_icon_name}}}}}</', tag, count=1, flags=re.DOTALL)
            repeat_content = re.sub(r'<(?:i|span)\b[^>]*class="[^"]*(?:icon|fa-|ti-|ion-)[^"]*"[^>]*>.*?</(?:i|span)>', _replace_ricon, repeat_content, flags=re.DOTALL)

            new_block = f"{repeat_open}{repeat_content}{repeat_close}"
            html = html.replace(rmatch.group(0), new_block)

        # ── Replace headings outside REPEAT ──────────────────────────────
        for tag in ['h1', 'h2', 'h3']:
            base_name = patterns.get(tag, f"{section_upper}_TITLE" if tag in ('h1', 'h2') else f"{section_upper}_SUBTITLE")

            def _replace_heading(m, _base=base_name):
                if in_repeat(m.start()):
                    return m.group(0)
                ot, content, ct = m.groups()
                if '{{' in content:
                    return m.group(0)
                text = re.sub(r'<[^>]+>', '', content).strip()
                if not text:
                    return m.group(0)
                name = next_ph(_base)
                placeholders.append(name)
                return f"{ot}{{{{{name}}}}}{ct}"

            html = re.sub(rf'(<{tag}\b[^>]*>)(.*?)(</{tag}>)', _replace_heading, html, flags=re.DOTALL)

        # ── Replace paragraphs outside REPEAT ────────────────────────────
        p_base = patterns.get("p", f"{section_upper}_TEXT")
        p_intro_base = patterns.get("p_intro", f"{section_upper}_SUBTITLE")
        p_count = [0]

        def _replace_p(m):
            if in_repeat(m.start()):
                return m.group(0)
            ot, content, ct = m.groups()
            if '{{' in content:
                return m.group(0)
            text = re.sub(r'<[^>]+>', '', content).strip()
            if not text or len(text) < 5:
                return m.group(0)
            p_count[0] += 1
            # First paragraph after section title is usually a subtitle/intro
            if p_count[0] == 1 and section_type in ("services", "testimonials", "pricing", "faq", "team", "features", "blog", "gallery", "stats"):
                name = next_ph(p_intro_base)
            else:
                name = next_ph(p_base)
            placeholders.append(name)
            return f"{ot}{{{{{name}}}}}{ct}"

        html = re.sub(r'(<p\b[^>]*>)(.*?)(</p>)', _replace_p, html, flags=re.DOTALL)

        # ── Replace images outside REPEAT ────────────────────────────────
        img_src_base = patterns.get("img_src", f"{section_upper}_IMAGE_URL")
        img_alt_base = patterns.get("img_alt", f"{section_upper}_IMAGE_ALT")

        def _replace_img(m):
            if in_repeat(m.start()):
                return m.group(0)
            tag = m.group(0)
            if '{{' in tag:
                return tag
            src_name = next_ph(img_src_base)
            alt_name = next_ph(img_alt_base)
            placeholders.append(src_name)
            placeholders.append(alt_name)
            tag = re.sub(r'src="[^"]*"', f'src="{{{{{src_name}}}}}"', tag)
            if 'alt=' in tag:
                tag = re.sub(r'alt="[^"]*"', f'alt="{{{{{alt_name}}}}}"', tag)
            else:
                tag = tag.rstrip('/>').rstrip('>').rstrip() + f' alt="{{{{{alt_name}}}}}">'
            return tag

        html = re.sub(r'<img\b[^>]*/?\s*>', _replace_img, html)

        # ── Replace CTA buttons/links ────────────────────────────────────
        cta_text_base = patterns.get("cta", f"{section_upper}_CTA_TEXT")
        cta_href_base = patterns.get("cta_href", f"{section_upper}_CTA_URL")

        def _replace_cta(m):
            if in_repeat(m.start()):
                return m.group(0)
            tag = m.group(0)
            if '{{' in tag:
                return tag
            # Only process links that look like buttons/CTAs
            if not re.search(r'class="[^"]*(?:btn|button|cta|action|primary)', tag, re.IGNORECASE):
                return tag
            text_match = re.search(r'>([^<]+)</a>', tag)
            if text_match:
                text = text_match.group(1).strip()
                if 1 < len(text) < 50:
                    txt_name = next_ph(cta_text_base)
                    href_name = next_ph(cta_href_base)
                    placeholders.extend([txt_name, href_name])
                    tag = re.sub(r'href="[^"]*"', f'href="{{{{{href_name}}}}}"', tag)
                    tag = re.sub(r'>([^<]+)</a>', f'>{{{{{txt_name}}}}}</a>', tag)
            return tag

        html = re.sub(r'<a\b[^>]*>[^<]*</a>', _replace_cta, html)

        return html, placeholders

    # ── Internal: GSAP Animations ────────────────────────────────────────

    def _add_animations(self, html: str, section_type: str) -> tuple:
        """Add data-animate attributes to elements."""
        count = 0

        # Section wrapper
        if re.search(r'<section\b[^>]*>', html):
            section_tag_match = re.search(r'<section\b[^>]*>', html)
            if section_tag_match and 'data-animate' not in section_tag_match.group(0):
                html = re.sub(
                    r'(<section\b[^>]*)(>)',
                    r'\1 data-animate="fade-up"\2',
                    html,
                    count=1,
                )
                count += 1

        # H1/H2 -> text-split
        for tag in ['h1', 'h2']:
            for match in re.finditer(rf'<{tag}\b[^>]*>', html):
                t = match.group(0)
                if 'data-animate' not in t:
                    new_t = t.replace(f'<{tag}', f'<{tag} data-animate="text-split" data-split-type="words"', 1)
                    html = html.replace(t, new_t, 1)
                    count += 1

        # H3/H4 -> fade-up
        for tag in ['h3', 'h4']:
            for match in re.finditer(rf'<{tag}\b[^>]*>', html):
                t = match.group(0)
                if 'data-animate' not in t:
                    new_t = t.replace(f'<{tag}', f'<{tag} data-animate="fade-up"', 1)
                    html = html.replace(t, new_t, 1)
                    count += 1

        # Paragraphs -> blur-slide (limit to first 4 to avoid overdoing it)
        p_anim_count = 0
        for match in re.finditer(r'<p\b[^>]*>', html):
            if p_anim_count >= 4:
                break
            t = match.group(0)
            if 'data-animate' not in t:
                new_t = t.replace('<p', '<p data-animate="blur-slide" data-delay="0.2"', 1)
                html = html.replace(t, new_t, 1)
                count += 1
                p_anim_count += 1

        # Images -> scale-in
        for match in re.finditer(r'<img\b[^>]*>', html):
            t = match.group(0)
            if 'data-animate' not in t:
                new_t = t.replace('<img', '<img data-animate="scale-in" data-delay="0.3"', 1)
                html = html.replace(t, new_t, 1)
                count += 1

        # CTA buttons -> magnetic
        for match in re.finditer(r'<a\b[^>]*>', html):
            t = match.group(0)
            if 'data-animate' not in t and re.search(r'class="[^"]*(?:btn|button|cta)', t, re.IGNORECASE):
                new_t = t.replace('<a', '<a data-animate="magnetic"', 1)
                html = html.replace(t, new_t, 1)
                count += 1

        # Grid/flex containers -> stagger
        for match in re.finditer(r'<(?:div|ul)\b[^>]*(?:grid|flex|row)[^>]*>', html, re.IGNORECASE):
            t = match.group(0)
            if 'data-animate' not in t:
                tag_name = 'ul' if t.startswith('<ul') else 'div'
                new_t = t.replace(f'<{tag_name}', f'<{tag_name} data-animate="stagger"', 1)
                html = html.replace(t, new_t, 1)
                count += 1

        return html, count

    # ── Internal: Cleanup ────────────────────────────────────────────────

    def _cleanup(self, html: str) -> str:
        """Clean up the HTML output."""
        # Remove empty class/style attributes
        html = re.sub(r'\s+class=""', '', html)
        html = re.sub(r'\s+style=""', '', html)
        # Remove data-wow, data-aos, and other third-party animation attrs
        html = re.sub(r'\s+data-(?:wow|aos|sal|sr)-[a-z-]+="[^"]*"', '', html)
        html = re.sub(r'\s+data-(?:wow|aos|sal|sr)="[^"]*"', '', html)
        # Remove trailing whitespace per line
        lines = html.split('\n')
        lines = [line.rstrip() for line in lines]
        html = '\n'.join(lines)
        # Remove excessive blank lines
        html = re.sub(r'\n{3,}', '\n\n', html)
        return html.strip() + '\n'

    # ── Internal: Tag Detection ──────────────────────────────────────────

    def _auto_detect_tags(self, section: ExtractedSection, extra_tags: list) -> list:
        """Auto-detect style tags from the section content."""
        tags = list(extra_tags)
        html_lower = section.raw_html.lower()

        # Layout detection
        if 'grid' in html_lower:
            tags.append("grid")
        if 'flex' in html_lower:
            tags.append("flex")
        if any(x in html_lower for x in ['split', 'col-6', 'grid-cols-2']):
            tags.append("split-layout")

        # Style detection
        if 'dark' in (section.original_classes or '').lower():
            tags.append("dark")
        if 'gradient' in html_lower:
            tags.append("gradient")
        if 'parallax' in html_lower:
            tags.append("parallax")
        if 'card' in html_lower:
            tags.append("cards")
        if 'slider' in html_lower or 'swiper' in html_lower or 'carousel' in html_lower:
            tags.append("slider")
        if 'accordion' in html_lower:
            tags.append("accordion")
        if 'tab' in html_lower and ('tab-content' in html_lower or 'tab-pane' in html_lower):
            tags.append("tabs")
        if any(x in html_lower for x in ['animate', 'animation', 'motion']):
            tags.append("animated")

        return list(dict.fromkeys(tags))  # deduplicate preserving order

    # ── Internal: Variant ID ─────────────────────────────────────────────

    def _generate_variant_id(self, section_type: str, prefix: str) -> str:
        """Generate the next available variant ID."""
        category = self.registry.get("categories", {}).get(section_type, {})
        existing = [v["id"] for v in category.get("variants", [])]

        # Also check filesystem
        section_dir = self.components_dir / section_type
        if section_dir.exists():
            for f in section_dir.glob("*.html"):
                vid = f.stem
                if vid not in existing:
                    existing.append(vid)

        # Find next number for this prefix
        prefix_nums = []
        for vid in existing:
            match = re.search(rf'-{re.escape(prefix)}-(\d+)$', vid)
            if match:
                prefix_nums.append(int(match.group(1)))

        next_num = max(prefix_nums, default=0) + 1
        return f"{section_type}-{prefix}-{next_num:02d}"

    # ── Registry Update ──────────────────────────────────────────────────

    def _update_registry(self, result: ConvertedSection):
        """Add converted component to components.json."""
        registry = self.registry
        sec_type = result.section_type

        if sec_type not in registry.get("categories", {}):
            registry["categories"][sec_type] = {
                "label": sec_type.title(),
                "required": False,
                "variants": [],
            }

        variants = registry["categories"][sec_type]["variants"]
        existing_ids = {v["id"] for v in variants}

        if result.variant_id not in existing_ids:
            variants.append(result.registry_entry)

    def save_registry(self):
        """Write the registry to disk."""
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
        log.info("Updated components.json registry")

    # ── Save Section ─────────────────────────────────────────────────────

    def save_section(self, result: ConvertedSection, dry_run: bool = False) -> dict:
        """Save a converted section to disk and update registry."""
        actions = []

        # Create section directory
        section_dir = self.components_dir / result.section_type
        if not section_dir.exists():
            if not dry_run:
                section_dir.mkdir(parents=True, exist_ok=True)
            actions.append(f"Created directory: {section_dir}")

        # Write HTML file
        file_path = self.components_dir / result.file_path
        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.html)
        actions.append(f"Wrote: {file_path}")

        # Update registry
        if not dry_run:
            self._update_registry(result)
        actions.append(f"Registered: {result.variant_id}")

        return {
            "variant_id": result.variant_id,
            "file": str(file_path),
            "actions": actions,
        }

    # ── Main Batch Convert ───────────────────────────────────────────────

    def convert_file(
        self,
        html_path: Path,
        css_paths: Optional[list] = None,
        prefix: str = "imported",
        category: Optional[str] = None,
        tags: Optional[list] = None,
        dry_run: bool = False,
    ) -> list:
        """
        Convert a single HTML file, extracting all sections.

        Returns list of ConvertedSection results.
        """
        log.info("=" * 60)
        log.info("Converting: %s", html_path)
        log.info("=" * 60)

        # Read HTML
        with open(html_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()

        # Read and combine CSS files
        css_text = ""
        if css_paths:
            for css_path in css_paths:
                css_p = Path(css_path)
                if css_p.exists():
                    with open(css_p, "r", encoding="utf-8", errors="replace") as f:
                        css_text += f.read() + "\n"
                    log.info("Loaded CSS: %s (%d chars)", css_p.name, len(css_text))
                else:
                    log.warning("CSS file not found: %s", css_path)
        else:
            # Auto-detect CSS files in same directory or css/ subdirectory
            css_dir = html_path.parent
            for pattern in ["*.css", "css/*.css", "styles/*.css", "assets/css/*.css"]:
                for css_file in css_dir.glob(pattern):
                    with open(css_file, "r", encoding="utf-8", errors="replace") as f:
                        css_text += f.read() + "\n"
                    log.info("Auto-detected CSS: %s", css_file.name)

        # Create CSS inliner
        css_inliner = CSSInliner(css_text) if css_text else None

        # Detect primary color
        primary_color = self.detect_primary_color(css_text, html) if css_text else None

        # Extract sections
        sections = self.extract_sections(html)

        if not sections:
            log.warning("No sections detected in %s", html_path.name)
            return []

        # Filter by category if specified
        if category:
            # Only convert sections relevant to the category
            pass  # Keep all sections - they're all from this template

        # Convert each section
        results = []
        for section in sections:
            if not section.section_type:
                log.warning("Skipping unidentified section (classes: %s)", section.original_classes[:60])
                continue

            log.info("Converting section: %s", section.section_type)
            result = self.convert_section(
                section=section,
                css_inliner=css_inliner,
                prefix=prefix,
                tags=tags or [],
                primary_color=primary_color,
            )

            if result.warnings:
                for w in result.warnings:
                    log.warning("  %s: %s", result.section_type, w)

            # Save
            if result.section_type != "unknown":
                save_result = self.save_section(result, dry_run=dry_run)
                for action in save_result["actions"]:
                    log.info("  %s", action)
                results.append(result)

        # Save registry once at the end
        if not dry_run and results:
            self.save_registry()

        return results

    def convert_folder(
        self,
        folder_path: Path,
        prefix: str = "imported",
        category: Optional[str] = None,
        tags: Optional[list] = None,
        dry_run: bool = False,
    ) -> list:
        """Convert all HTML files in a folder."""
        all_results = []

        html_files = list(folder_path.glob("*.html")) + list(folder_path.glob("*.htm"))
        # Skip common non-page files
        skip_names = {"mail", "email", "404", "500", "blank", "coming-soon"}
        html_files = [f for f in html_files if not any(s in f.stem.lower() for s in skip_names)]

        if not html_files:
            log.warning("No HTML files found in %s", folder_path)
            return []

        log.info("Found %d HTML files in %s", len(html_files), folder_path)

        # Find CSS files
        css_paths = []
        for pattern in ["*.css", "css/*.css", "styles/*.css", "assets/css/*.css"]:
            css_paths.extend(folder_path.glob(pattern))

        for html_file in sorted(html_files):
            results = self.convert_file(
                html_path=html_file,
                css_paths=[str(p) for p in css_paths] if css_paths else None,
                prefix=prefix,
                category=category,
                tags=tags,
                dry_run=dry_run,
            )
            all_results.extend(results)

        return all_results


# ── CLI ──────────────────────────────────────────────────────────────────────

def print_report(results: list, dry_run: bool = False):
    """Print a summary report of all conversions."""
    print("\n" + "=" * 60)
    print("  Batch Conversion Report")
    print("=" * 60)

    if not results:
        print("  No sections converted.")
        return

    total_placeholders = 0
    total_animations = 0
    total_colors = 0
    total_css = 0

    for r in results:
        print(f"\n  [{r.section_type}] {r.variant_id}")
        print(f"    File: {r.file_path}")
        print(f"    Placeholders: {len(r.placeholders)}")
        for p in r.placeholders[:8]:
            print(f"      - {{{{{p}}}}}")
        if len(r.placeholders) > 8:
            print(f"      ... and {len(r.placeholders) - 8} more")
        print(f"    REPEAT blocks: {len(r.repeat_keys)}")
        for rk in r.repeat_keys:
            print(f"      - <!-- REPEAT:{rk} -->")
        print(f"    Animations: {r.animations_added}")
        print(f"    Colors replaced: {r.colors_replaced}")
        print(f"    CSS rules inlined: {r.css_rules_inlined}")
        if r.warnings:
            for w in r.warnings:
                print(f"    WARNING: {w}")

        total_placeholders += len(r.placeholders)
        total_animations += r.animations_added
        total_colors += r.colors_replaced
        total_css += r.css_rules_inlined

    print(f"\n  {'=' * 56}")
    print(f"  TOTALS:")
    print(f"    Sections converted: {len(results)}")
    print(f"    Total placeholders: {total_placeholders}")
    print(f"    Total animations:   {total_animations}")
    print(f"    Total colors:       {total_colors}")
    print(f"    Total CSS inlined:  {total_css}")

    if dry_run:
        print(f"\n  [DRY RUN] No files written. Remove --dry-run to save.")
    else:
        print(f"\n  All sections saved to components directory.")
        print(f"  Registry updated in components.json.")


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert ThemeForest HTML templates to Site Builder components",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single HTML page (extracts all sections)
  python batch_converter.py "template/pixy/home-1.html" --css "template/pixy/css/style.css" --prefix "pixy"

  # Convert all HTML files in a folder
  python batch_converter.py "template/_extracted/restaurant/dinex/" --prefix "dinex" --category restaurant

  # Dry run (analyze without saving)
  python batch_converter.py "path/to/template/" --dry-run

  # With custom tags
  python batch_converter.py "template/agency/" --prefix "agency" --tags "agency,modern,dark"
        """,
    )

    parser.add_argument("input", help="Path to HTML file or folder of HTML files")
    parser.add_argument("--css", nargs="*", help="Path(s) to CSS file(s). Auto-detected if not provided.")
    parser.add_argument("--prefix", "-p", default="imported", help="Prefix for variant IDs (e.g., 'pixy', 'dinex')")
    parser.add_argument("--category", "-c", default=None, help="Template category (restaurant, saas, portfolio, etc.)")
    parser.add_argument("--tags", "-t", default="", help="Comma-separated style tags (modern, dark, elegant)")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without saving files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Path not found: {input_path}")
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    converter = BatchConverter()

    if input_path.is_file():
        results = converter.convert_file(
            html_path=input_path,
            css_paths=args.css,
            prefix=args.prefix,
            category=args.category,
            tags=tags,
            dry_run=args.dry_run,
        )
    elif input_path.is_dir():
        results = converter.convert_folder(
            folder_path=input_path,
            prefix=args.prefix,
            category=args.category,
            tags=tags,
            dry_run=args.dry_run,
        )
    else:
        print(f"Error: {input_path} is not a file or directory")
        sys.exit(1)

    print_report(results, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
