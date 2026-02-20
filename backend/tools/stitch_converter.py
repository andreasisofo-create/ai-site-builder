#!/usr/bin/env python3
"""
Stitch-to-Template Converter
=============================
Converts Google Stitch HTML/CSS export into Site Builder component templates.

Usage:
  python stitch_converter.py input.html --section hero --name "Split Parallax" --tags modern,bold
  python stitch_converter.py input.html --section services --name "Icon Grid" --detect-repeats
  python stitch_converter.py input.html --section about --name "Timeline" --interactive

Workflow:
  1. Export HTML from Google Stitch (HTML/CSS or Tailwind)
  2. Run this script on the exported file
  3. Review the generated template in backend/app/components/{section}/
  4. Template is auto-registered in components.json
"""

import argparse
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
COMPONENTS_DIR = PROJECT_ROOT / "app" / "components"
REGISTRY_PATH = COMPONENTS_DIR / "components.json"


# ─── Color Mapping ────────────────────────────────────────────────────────────

# Common color patterns to CSS variable mappings
COLOR_VAR_MAP = {
    # Primary colors (blues, brand colors)
    "primary": "var(--color-primary)",
    "primary-rgb": "var(--color-primary-rgb)",
    # Secondary
    "secondary": "var(--color-secondary)",
    "secondary-rgb": "var(--color-secondary-rgb)",
    # Accent
    "accent": "var(--color-accent)",
    "accent-rgb": "var(--color-accent-rgb)",
    # Backgrounds
    "bg": "var(--color-bg)",
    "bg-alt": "var(--color-bg-alt)",
    "bg-rgb": "var(--color-bg-rgb)",
    # Text
    "text": "var(--color-text)",
    "text-muted": "var(--color-text-muted)",
    # Surfaces
    "surface-1": "var(--color-surface-1)",
    "surface-2": "var(--color-surface-2)",
    "border": "var(--color-border)",
    "border-hover": "var(--color-border-hover)",
}

# Tailwind color classes to replace
TAILWIND_COLOR_REPLACEMENTS = {
    # Text colors
    r'text-(?:blue|indigo|violet|purple)-(?:500|600|700)': 'style="color: var(--color-primary)"',
    r'text-(?:gray|slate|zinc)-(?:900|800)': 'style="color: var(--color-text)"',
    r'text-(?:gray|slate|zinc)-(?:500|600|400)': 'style="color: var(--color-text-muted)"',
    r'text-white': 'style="color: #ffffff"',
    # Background colors
    r'bg-(?:blue|indigo|violet|purple)-(?:500|600|700)': 'style="background: var(--color-primary)"',
    r'bg-(?:gray|slate|zinc)-(?:50|100)': 'style="background: var(--color-bg-alt)"',
    r'bg-white': 'style="background: var(--color-bg)"',
    r'bg-(?:gray|slate|zinc)-(?:900|950)': 'style="background: var(--color-bg)"',
    # Border colors
    r'border-(?:blue|indigo|violet|purple)-(?:500|600)': 'style="border-color: var(--color-primary)"',
    r'border-(?:gray|slate|zinc)-(?:200|300)': 'style="border-color: var(--color-border)"',
}

# Hex color patterns commonly used
COMMON_HEX_COLORS = {
    # Blues (likely primary)
    r'#(?:3b82f6|2563eb|1d4ed8|4f46e5|6366f1|7c3aed|8b5cf6)': 'var(--color-primary)',
    # Grays for text
    r'#(?:111827|1f2937|0f172a|18181b)': 'var(--color-text)',
    r'#(?:6b7280|64748b|71717a|9ca3af)': 'var(--color-text-muted)',
    # Light grays for backgrounds
    r'#(?:f9fafb|f8fafc|fafafa|f3f4f6|f1f5f9)': 'var(--color-bg-alt)',
    r'#(?:ffffff|fff)': 'var(--color-bg)',
}


# ─── GSAP Animation Rules ────────────────────────────────────────────────────

GSAP_RULES = {
    # Element type -> recommended animation
    "h1": ('text-split', {'data-split-type': 'words'}),
    "h2": ('text-split', {'data-split-type': 'words'}),
    "h3": ('fade-up', {}),
    "p": ('blur-slide', {'data-delay': '0.2', 'data-duration': '1.2'}),
    "img": ('scale-in', {'data-delay': '0.3'}),
    "a[cta]": ('magnetic', {}),
    "section": ('fade-up', {}),
    "nav": ('fade-down', {}),
    "footer": ('fade-up', {}),
    # Grid/list containers
    "grid": ('stagger', {}),
    "grid-item": ('stagger-item-class', {}),  # Add class="stagger-item"
    # Cards
    "card": ('tilt', {}),
    # Counters/stats
    "counter": ('data-counter', {}),
}

# ─── Placeholder Detection ───────────────────────────────────────────────────

# Section-specific placeholder naming conventions
PLACEHOLDER_PATTERNS = {
    "hero": {
        "h1": "HERO_TITLE",
        "h2": "HERO_SUBTITLE",
        "p.subtitle": "HERO_SUBTITLE",
        "p": "HERO_DESCRIPTION",
        "a.cta": "HERO_CTA_TEXT",
        "a.cta[href]": "HERO_CTA_URL",
        "img[src]": "HERO_IMAGE_URL",
        "img[alt]": "HERO_IMAGE_ALT",
    },
    "about": {
        "h2": "ABOUT_TITLE",
        "h3": "ABOUT_SUBTITLE",
        "p.subtitle": "ABOUT_SUBTITLE",
        "p": "ABOUT_TEXT",
        "img[src]": "ABOUT_IMAGE_URL",
        "img[alt]": "ABOUT_IMAGE_ALT",
        "span.number": "ABOUT_HIGHLIGHT_NUM",
        "span.label": "ABOUT_HIGHLIGHT",
    },
    "services": {
        "h2": "SERVICES_TITLE",
        "p.subtitle": "SERVICES_SUBTITLE",
        "h3.item": "SERVICE_TITLE",
        "p.item": "SERVICE_DESCRIPTION",
        "span.icon": "SERVICE_ICON",
        "a.cta": "SERVICES_CTA_TEXT",
        "a.cta[href]": "SERVICES_CTA_URL",
    },
    "testimonials": {
        "h2": "TESTIMONIALS_TITLE",
        "p.subtitle": "TESTIMONIALS_SUBTITLE",
        "p.quote": "TESTIMONIAL_TEXT",
        "span.author": "TESTIMONIAL_AUTHOR",
        "span.role": "TESTIMONIAL_ROLE",
        "img[src]": "TESTIMONIAL_AVATAR_URL",
    },
    "contact": {
        "h2": "CONTACT_TITLE",
        "p.subtitle": "CONTACT_SUBTITLE",
        "span.phone": "CONTACT_PHONE",
        "span.email": "CONTACT_EMAIL",
        "span.address": "CONTACT_ADDRESS",
    },
    "gallery": {
        "h2": "GALLERY_TITLE",
        "p.subtitle": "GALLERY_SUBTITLE",
        "img[src]": "GALLERY_IMAGE_URL",
        "img[alt]": "GALLERY_IMAGE_ALT",
    },
    "pricing": {
        "h2": "PRICING_TITLE",
        "p.subtitle": "PRICING_SUBTITLE",
        "h3.plan": "PLAN_NAME",
        "span.price": "PLAN_PRICE",
        "p.plan-desc": "PLAN_DESCRIPTION",
        "li.feature": "PLAN_FEATURE",
        "a.cta": "PLAN_CTA_TEXT",
    },
    "faq": {
        "h2": "FAQ_TITLE",
        "p.subtitle": "FAQ_SUBTITLE",
        "h3.question": "FAQ_QUESTION",
        "p.answer": "FAQ_ANSWER",
    },
    "team": {
        "h2": "TEAM_TITLE",
        "p.subtitle": "TEAM_SUBTITLE",
        "h3.member": "MEMBER_NAME",
        "p.role": "MEMBER_ROLE",
        "img[src]": "MEMBER_IMAGE_URL",
    },
    "stats": {
        "h2": "STATS_TITLE",
        "span.number": "STAT_NUMBER",
        "span.label": "STAT_LABEL",
    },
    "cta": {
        "h2": "CTA_TITLE",
        "p": "CTA_SUBTITLE",
        "a.cta": "CTA_BUTTON_TEXT",
        "a.cta[href]": "CTA_BUTTON_URL",
    },
    "footer": {
        "span.copyright": "FOOTER_COPYRIGHT",
        "a.social": "SOCIAL_URL",
        "span.social-label": "SOCIAL_LABEL",
    },
}


@dataclass
class ConversionResult:
    """Result of converting a Stitch HTML file."""
    html: str
    variant_id: str
    file_path: str
    placeholders: list = field(default_factory=list)
    has_repeats: bool = False
    repeat_keys: list = field(default_factory=list)
    animations_added: int = 0
    colors_replaced: int = 0
    registry_entry: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)


class StitchConverter:
    """Converts Google Stitch HTML output to Site Builder template format."""

    def __init__(self, components_dir: Optional[Path] = None):
        self.components_dir = components_dir or COMPONENTS_DIR
        self.registry_path = self.components_dir / "components.json"
        self._registry = None

    @property
    def registry(self) -> dict:
        if self._registry is None:
            if self.registry_path.exists():
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    self._registry = json.load(f)
            else:
                self._registry = {"version": "2.0.0", "categories": {}}
        return self._registry

    def convert(
        self,
        html_input: str,
        section_type: str,
        name: str,
        description: str = "",
        tags: Optional[list] = None,
        detect_repeats: bool = True,
        add_animations: bool = True,
        convert_colors: bool = True,
        interactive: bool = False,
    ) -> ConversionResult:
        """
        Convert Stitch HTML to a Site Builder template.

        Args:
            html_input: Raw HTML from Google Stitch export
            section_type: Target section type (hero, about, services, etc.)
            name: Human-readable name for the component
            description: Italian description
            tags: Style tags (modern, bold, elegant, etc.)
            detect_repeats: Auto-detect repeating patterns
            add_animations: Add data-animate attributes
            convert_colors: Replace hardcoded colors with CSS vars
            interactive: Prompt user for placeholder names
        """
        tags = tags or []
        html = html_input
        placeholders = []
        warnings = []
        colors_replaced = 0
        animations_added = 0
        repeat_keys = []

        # Step 1: Extract the main content (strip head/body wrappers)
        html = self._extract_content(html)

        # Step 2: Convert colors to CSS variables
        if convert_colors:
            html, colors_replaced = self._convert_colors(html)

        # Step 3: Convert fonts
        html = self._convert_fonts(html)

        # Step 4: Add section wrapper if missing
        html = self._ensure_section_wrapper(html, section_type)

        # Step 5: Detect and wrap repeating patterns
        if detect_repeats:
            html, repeat_keys_found = self._detect_repeats(html, section_type)
            repeat_keys.extend(repeat_keys_found)

        # Step 6: Replace text content with placeholders
        html, placeholders = self._add_placeholders(html, section_type, interactive)

        # Step 7: Add GSAP animations
        if add_animations:
            html, animations_added = self._add_animations(html, section_type)

        # Step 8: Clean up and format
        html = self._cleanup(html)

        # Step 9: Generate variant ID and file path
        variant_id = self._generate_variant_id(section_type)
        file_name = f"{variant_id}.html"
        file_path = f"{section_type}/{file_name}"

        # Step 10: Build registry entry
        registry_entry = {
            "id": variant_id,
            "file": file_path,
            "name": name,
            "description": description or f"Componente {section_type} importato da Stitch",
            "placeholders": sorted(set(placeholders)),
            "tags": tags,
        }

        return ConversionResult(
            html=html,
            variant_id=variant_id,
            file_path=file_path,
            placeholders=sorted(set(placeholders)),
            has_repeats=len(repeat_keys) > 0,
            repeat_keys=repeat_keys,
            animations_added=animations_added,
            colors_replaced=colors_replaced,
            registry_entry=registry_entry,
            warnings=warnings,
        )

    def save(self, result: ConversionResult, dry_run: bool = False) -> dict:
        """Save the converted template and update the registry."""
        actions = []

        # Create section directory if needed
        section_dir = self.components_dir / result.file_path.split("/")[0]
        if not section_dir.exists():
            if not dry_run:
                section_dir.mkdir(parents=True, exist_ok=True)
            actions.append(f"Created directory: {section_dir}")

        # Write template file
        template_path = self.components_dir / result.file_path
        if not dry_run:
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(result.html)
        actions.append(f"Wrote template: {template_path}")

        # Update registry
        if not dry_run:
            self._update_registry(result)
        actions.append(f"Registered: {result.variant_id} in components.json")

        return {
            "variant_id": result.variant_id,
            "file": str(template_path),
            "actions": actions,
            "dry_run": dry_run,
        }

    # ─── Internal Methods ─────────────────────────────────────────────────

    def _extract_content(self, html: str) -> str:
        """Extract main content, removing DOCTYPE, html, head, body wrappers."""
        # Remove DOCTYPE
        html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)

        # Extract body content if present
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
        if body_match:
            html = body_match.group(1)

        # Remove <html>, <head> tags and their content
        html = re.sub(r'<html[^>]*>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'</html>', '', html, flags=re.IGNORECASE)
        html = re.sub(r'<head>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove Stitch-specific scripts and styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Keep <style> blocks but we'll process them

        return html.strip()

    def _convert_colors(self, html: str) -> tuple:
        """Replace hardcoded colors with CSS variables."""
        count = 0

        # Replace hex colors in inline styles
        for pattern, var_name in COMMON_HEX_COLORS.items():
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                html = re.sub(pattern, var_name, html, flags=re.IGNORECASE)
                count += len(matches)

        # Replace rgba with CSS variable RGB variants
        # rgba(59, 130, 246, 0.1) -> rgba(var(--color-primary-rgb), 0.1)
        rgba_pattern = r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)'
        for match in re.finditer(rgba_pattern, html):
            r, g, b, a = match.groups()
            hex_color = f'#{int(r):02x}{int(g):02x}{int(b):02x}'
            for pattern, var_name in COMMON_HEX_COLORS.items():
                if re.match(pattern, hex_color, re.IGNORECASE):
                    rgb_var = var_name.replace(')', '-rgb)')
                    old = match.group(0)
                    new = f'rgba({rgb_var}, {a})'
                    html = html.replace(old, new)
                    count += 1
                    break

        # Convert Tailwind color classes to inline styles with CSS vars
        for tw_pattern, replacement in TAILWIND_COLOR_REPLACEMENTS.items():
            tw_matches = re.findall(tw_pattern, html)
            if tw_matches:
                for tw_class in tw_matches:
                    # Remove the Tailwind class and add style attribute
                    html = html.replace(tw_class, '')
                    count += 1

        # Replace common gradient patterns
        # linear-gradient(to right, #3b82f6, #8b5cf6) -> linear-gradient(135deg, var(--color-primary), var(--color-secondary))
        gradient_pattern = r'linear-gradient\([^)]*(?:#[0-9a-fA-F]{3,8})[^)]*\)'
        for match in re.finditer(gradient_pattern, html):
            old_gradient = match.group(0)
            new_gradient = 'linear-gradient(135deg, var(--color-primary), var(--color-secondary, var(--color-primary)))'
            html = html.replace(old_gradient, new_gradient)
            count += 1

        return html, count

    def _convert_fonts(self, html: str) -> str:
        """Replace hardcoded font families with CSS variables."""
        # Common font families used in Stitch
        heading_fonts = [
            'Inter', 'Poppins', 'Montserrat', 'Roboto', 'Open Sans',
            'Lato', 'Nunito', 'Raleway', 'Oswald', 'Merriweather',
            'Playfair Display', 'DM Serif Display', 'Space Grotesk', 'Sora',
        ]
        body_fonts = heading_fonts  # Same set, context determines usage

        for font in heading_fonts:
            # In font-family declarations
            pattern = rf"font-family:\s*['\"]?{re.escape(font)}['\"]?"
            if re.search(pattern, html, re.IGNORECASE):
                # Keep the first one as heading, rest as body
                html = re.sub(
                    pattern,
                    "font-family: var(--font-heading)",
                    html,
                    count=1,
                    flags=re.IGNORECASE
                )
                html = re.sub(
                    pattern,
                    "font-family: var(--font-body)",
                    html,
                    flags=re.IGNORECASE
                )

        return html

    def _ensure_section_wrapper(self, html: str, section_type: str) -> str:
        """Ensure the content is wrapped in a <section> with proper ID."""
        html = html.strip()

        # Check if already wrapped in a section
        if re.match(r'^<section\b', html, re.IGNORECASE):
            # Add id if missing
            if 'id=' not in html[:100]:
                html = re.sub(
                    r'^<section',
                    f'<section id="{section_type}"',
                    html,
                    count=1
                )
            return html

        # Special cases: nav, footer don't use <section>
        if section_type == 'nav' and re.match(r'^<nav\b', html, re.IGNORECASE):
            return html
        if section_type == 'footer' and re.match(r'^<footer\b', html, re.IGNORECASE):
            return html

        # Wrap in section
        html = f'<section id="{section_type}" class="py-24 px-6" style="background: var(--color-bg)">\n  <div class="max-w-7xl mx-auto">\n{html}\n  </div>\n</section>'
        return html

    def _detect_repeats(self, html: str, section_type: str) -> tuple:
        """Detect repeating HTML patterns and wrap in REPEAT blocks."""
        repeat_keys = []

        # Repeatable section types and their expected array keys
        repeat_map = {
            "services": "SERVICES",
            "testimonials": "TESTIMONIALS",
            "pricing": "PLANS",
            "team": "MEMBERS",
            "faq": "FAQS",
            "gallery": "GALLERY_ITEMS",
            "features": "FEATURES",
            "stats": "STATS",
            "menu": "MENU_ITEMS",
            "process": "STEPS",
            "blog": "POSTS",
            "timeline": "EVENTS",
        }

        if section_type not in repeat_map:
            return html, repeat_keys

        repeat_key = repeat_map[section_type]

        def _extract_balanced_tag(html_str: str, start_pos: int, tag: str) -> Optional[str]:
            """Extract a balanced HTML tag, handling nested tags of the same type."""
            close_tag = f'</{tag}>'
            depth = 0
            i = start_pos

            while i < len(html_str):
                open_match = re.search(rf'<{tag}\b', html_str[i:])
                close_idx = html_str.find(close_tag, i)

                if close_idx == -1:
                    return None  # Unbalanced

                if open_match and (i + open_match.start()) < close_idx:
                    # Found an opening tag before the next close
                    depth += 1
                    i = i + open_match.start() + 1  # Move past '<'
                else:
                    # Found a closing tag
                    depth -= 1
                    if depth == 0:
                        return html_str[start_pos:close_idx + len(close_tag)]
                    i = close_idx + len(close_tag)

            return None

        # Find grid/flex containers
        grid_match = re.search(r'<div[^>]*(?:grid|flex)[^>]*>', html)
        if not grid_match:
            return html, repeat_keys

        container_start = grid_match.start()
        container_open = grid_match.group(0)

        # Extract the full container with balanced tags
        container_full = _extract_balanced_tag(html, container_start, 'div')
        if not container_full:
            return html, repeat_keys

        # Find direct children (top-level divs inside the container)
        inner_html = container_full[len(container_open):-len('</div>')]
        children = []
        pos = 0
        while pos < len(inner_html):
            child_match = re.search(r'<div\b', inner_html[pos:])
            if not child_match:
                break
            child_start = pos + child_match.start()
            child_full = _extract_balanced_tag(inner_html, child_start, 'div')
            if child_full:
                children.append(child_full)
                pos = child_start + len(child_full)
            else:
                break

        if len(children) < 2:
            return html, repeat_keys

        # Use the first child as the repeat template
        first_item = children[0]

        # Add stagger-item class to the first child
        if 'class=' in first_item:
            first_item = re.sub(
                r'class="([^"]*)"',
                r'class="\1 stagger-item"',
                first_item,
                count=1
            )
        else:
            first_item = first_item.replace('<div', '<div class="stagger-item"', 1)

        # Build repeat block
        repeat_block = (
            f"{container_open}\n"
            f"    <!-- REPEAT:{repeat_key} -->\n"
            f"    {first_item}\n"
            f"    <!-- /REPEAT:{repeat_key} -->\n"
            f"  </div>"
        )

        html = html.replace(container_full, repeat_block)
        repeat_keys.append(repeat_key)

        return html, repeat_keys

    def _add_placeholders(self, html: str, section_type: str, interactive: bool = False) -> tuple:
        """Replace text content with {{PLACEHOLDER}} syntax."""
        placeholders = []
        patterns = PLACEHOLDER_PATTERNS.get(section_type, {})

        # Item-level placeholder names for content inside REPEAT blocks
        REPEAT_ITEM_NAMES = {
            "SERVICES": {"h3": "SERVICE_TITLE", "p": "SERVICE_DESCRIPTION", "span.icon": "SERVICE_ICON"},
            "TESTIMONIALS": {"h3": "TESTIMONIAL_AUTHOR", "p.quote": "TESTIMONIAL_TEXT", "span.role": "TESTIMONIAL_ROLE"},
            "PLANS": {"h3": "PLAN_NAME", "p": "PLAN_DESCRIPTION", "span.price": "PLAN_PRICE"},
            "MEMBERS": {"h3": "MEMBER_NAME", "p": "MEMBER_ROLE"},
            "FAQS": {"h3": "FAQ_QUESTION", "p": "FAQ_ANSWER"},
            "FEATURES": {"h3": "FEATURE_TITLE", "p": "FEATURE_DESCRIPTION"},
            "STATS": {"span.number": "STAT_NUMBER", "span.label": "STAT_LABEL"},
            "MENU_ITEMS": {"h3": "ITEM_NAME", "p": "ITEM_DESCRIPTION", "span.price": "ITEM_PRICE"},
            "STEPS": {"h3": "STEP_TITLE", "p": "STEP_DESCRIPTION"},
            "POSTS": {"h3": "POST_TITLE", "p": "POST_EXCERPT"},
            "EVENTS": {"h3": "EVENT_TITLE", "p": "EVENT_DESCRIPTION"},
            "GALLERY_ITEMS": {"img[src]": "GALLERY_IMAGE_URL", "img[alt]": "GALLERY_IMAGE_ALT"},
        }

        # First: process REPEAT blocks separately with item-level names
        repeat_pattern = r'(<!-- REPEAT:(\w+) -->)(.*?)(<!-- /REPEAT:\2 -->)'
        for rmatch in re.finditer(repeat_pattern, html, re.DOTALL):
            repeat_open, repeat_key, repeat_content, repeat_close = rmatch.groups()
            item_names = REPEAT_ITEM_NAMES.get(repeat_key, {})

            # Replace h3 inside repeat
            h3_name = item_names.get("h3", f"{repeat_key[:-1]}_TITLE" if repeat_key.endswith("S") else f"{repeat_key}_TITLE")
            def replace_repeat_h3(m):
                ot, content, ct = m.groups()
                if '{{' in content:
                    return m.group(0)
                text_only = re.sub(r'<[^>]+>', '', content).strip()
                if not text_only:
                    return m.group(0)
                placeholders.append(h3_name)
                return f"{ot}{{{{{h3_name}}}}}{ct}"
            repeat_content = re.sub(r'(<h3\b[^>]*>)(.*?)(</h3>)', replace_repeat_h3, repeat_content, flags=re.DOTALL)

            # Replace p inside repeat
            p_name = item_names.get("p", f"{repeat_key[:-1]}_DESCRIPTION" if repeat_key.endswith("S") else f"{repeat_key}_TEXT")
            def replace_repeat_p(m):
                ot, content, ct = m.groups()
                if '{{' in content:
                    return m.group(0)
                text_only = re.sub(r'<[^>]+>', '', content).strip()
                if not text_only or len(text_only) < 5:
                    return m.group(0)
                placeholders.append(p_name)
                return f"{ot}{{{{{p_name}}}}}{ct}"
            repeat_content = re.sub(r'(<p\b[^>]*>)(.*?)(</p>)', replace_repeat_p, repeat_content, flags=re.DOTALL)

            # Replace img inside repeat
            img_src_name = item_names.get("img[src]", f"{repeat_key[:-1]}_IMAGE_URL" if repeat_key.endswith("S") else f"{repeat_key}_IMAGE_URL")
            img_alt_name = item_names.get("img[alt]", f"{repeat_key[:-1]}_IMAGE_ALT" if repeat_key.endswith("S") else f"{repeat_key}_IMAGE_ALT")
            def replace_repeat_img(m):
                tag = m.group(0)
                if '{{' in tag:
                    return tag
                placeholders.append(img_src_name)
                placeholders.append(img_alt_name)
                tag = re.sub(r'src="[^"]*"', f'src="{{{{{img_src_name}}}}}"', tag)
                if 'alt=' in tag:
                    tag = re.sub(r'alt="[^"]*"', f'alt="{{{{{img_alt_name}}}}}"', tag)
                return tag
            repeat_content = re.sub(r'<img\b[^>]*/?\s*>', replace_repeat_img, repeat_content)

            # Rebuild the repeat block
            new_block = f"{repeat_open}{repeat_content}{repeat_close}"
            html = html.replace(rmatch.group(0), new_block)

        # Track counters for numbered placeholders (for non-repeat content)
        counters = {}

        def get_placeholder(base_name: str) -> str:
            """Get next available placeholder name."""
            if base_name not in counters:
                counters[base_name] = 0
            counters[base_name] += 1
            if counters[base_name] == 1:
                return base_name
            return f"{base_name}_{counters[base_name]}"

        def _in_repeat_block(pos: int) -> bool:
            """Check if a position is inside a REPEAT block."""
            before = html[:pos]
            opens = len(re.findall(r'<!-- REPEAT:\w+ -->', before))
            closes = len(re.findall(r'<!-- /REPEAT:\w+ -->', before))
            return opens > closes

        # Process headings (h1-h6) OUTSIDE repeat blocks
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            placeholder_key = f"{tag}"
            base_name = patterns.get(placeholder_key)
            if not base_name:
                section_upper = section_type.upper()
                if tag == 'h1':
                    base_name = f"{section_upper}_TITLE"
                elif tag == 'h2':
                    base_name = f"{section_upper}_TITLE"
                elif tag == 'h3':
                    base_name = f"{section_upper}_SUBTITLE"
                else:
                    base_name = f"{section_upper}_HEADING"

            tag_pattern = rf'(<{tag}\b[^>]*>)(.*?)(</{tag}>)'

            def replace_heading(m, _base=base_name):
                # Skip if inside REPEAT block
                if _in_repeat_block(m.start()):
                    return m.group(0)
                open_tag, content, close_tag = m.groups()
                if '{{' in content:
                    return m.group(0)
                text_only = re.sub(r'<[^>]+>', '', content).strip()
                if not text_only:
                    return m.group(0)
                name = get_placeholder(_base)
                placeholders.append(name)
                return f"{open_tag}{{{{{name}}}}}{close_tag}"

            html = re.sub(tag_pattern, replace_heading, html, flags=re.DOTALL)

        # Process paragraphs (outside REPEAT blocks)
        p_base = patterns.get("p", f"{section_type.upper()}_TEXT")

        def replace_paragraph(m):
            if _in_repeat_block(m.start()):
                return m.group(0)
            open_tag, content, close_tag = m.groups()
            if '{{' in content:
                return m.group(0)
            text_only = re.sub(r'<[^>]+>', '', content).strip()
            if not text_only or len(text_only) < 5:
                return m.group(0)
            name = get_placeholder(p_base)
            placeholders.append(name)
            return f"{open_tag}{{{{{name}}}}}{close_tag}"

        html = re.sub(r'(<p\b[^>]*>)(.*?)(</p>)', replace_paragraph, html, flags=re.DOTALL)

        # Process images (outside REPEAT blocks)
        img_src = patterns.get("img[src]", f"{section_type.upper()}_IMAGE_URL")
        img_alt = patterns.get("img[alt]", f"{section_type.upper()}_IMAGE_ALT")

        def replace_img(m):
            if _in_repeat_block(m.start()):
                return m.group(0)
            tag = m.group(0)
            if '{{' in tag:
                return tag
            src_name = get_placeholder(img_src)
            placeholders.append(src_name)
            tag = re.sub(r'src="[^"]*"', f'src="{{{{{src_name}}}}}"', tag)
            alt_name = get_placeholder(img_alt)
            placeholders.append(alt_name)
            if 'alt=' in tag:
                tag = re.sub(r'alt="[^"]*"', f'alt="{{{{{alt_name}}}}}"', tag)
            else:
                tag = tag.replace('/>', f'alt="{{{{{alt_name}}}}}" />')
                tag = tag.replace('>', f' alt="{{{{{alt_name}}}}}">', 1) if '/>' not in tag else tag
            return tag

        html = re.sub(r'<img\b[^>]*/?\s*>', replace_img, html)

        # Process CTA links (buttons/links with text)
        cta_text = patterns.get("a.cta", f"{section_type.upper()}_CTA_TEXT")
        cta_url = patterns.get("a.cta[href]", f"{section_type.upper()}_CTA_URL")

        def replace_cta(m):
            tag = m.group(0)
            if '{{' in tag:
                return tag
            # Only process links that look like CTAs (have classes like btn, button, etc.)
            # or are inside known CTA contexts
            href_match = re.search(r'href="([^"]*)"', tag)
            text_match = re.search(r'>([^<]+)</a>', tag)
            if href_match and text_match:
                text = text_match.group(1).strip()
                if len(text) > 1 and len(text) < 50:
                    url_name = get_placeholder(cta_url)
                    txt_name = get_placeholder(cta_text)
                    placeholders.extend([url_name, txt_name])
                    tag = re.sub(r'href="[^"]*"', f'href="{{{{{url_name}}}}}"', tag)
                    tag = re.sub(r'>([^<]+)</a>', f'>{{{{{txt_name}}}}}</a>', tag)
            return tag

        html = re.sub(r'<a\b[^>]*>[^<]*</a>', replace_cta, html)

        return html, placeholders

    def _add_animations(self, html: str, section_type: str) -> tuple:
        """Add data-animate attributes to elements."""
        count = 0

        # Section wrapper
        section_anim = 'fade-down' if section_type == 'nav' else 'fade-up'
        if re.search(r'<section\b[^>]*(?<!data-animate)', html):
            html = re.sub(
                r'(<section\b[^>]*)(>)',
                rf'\1 data-animate="{section_anim}"\2',
                html,
                count=1
            )
            count += 1

        # H1/H2 -> text-split
        for tag in ['h1', 'h2']:
            pattern = rf'(<{tag}\b[^>]*?)(?<!data-animate[^>])(>)'
            if re.search(pattern, html) and 'data-animate' not in re.search(rf'<{tag}[^>]*>', html).group(0):
                html = re.sub(
                    rf'(<{tag}\b[^>]*)(>)',
                    rf'\1 data-animate="text-split" data-split-type="words"\2',
                    html,
                    count=1
                )
                count += 1

        # H3 -> fade-up
        for match in re.finditer(r'<h3\b[^>]*>', html):
            tag = match.group(0)
            if 'data-animate' not in tag:
                new_tag = tag.replace('<h3', '<h3 data-animate="fade-up"', 1)
                html = html.replace(tag, new_tag, 1)
                count += 1

        # Paragraphs -> blur-slide
        for match in re.finditer(r'<p\b[^>]*>', html):
            tag = match.group(0)
            if 'data-animate' not in tag:
                new_tag = tag.replace('<p', '<p data-animate="blur-slide" data-delay="0.2"', 1)
                html = html.replace(tag, new_tag, 1)
                count += 1
                # Only animate first 3 paragraphs to avoid overdoing it
                if count > 5:
                    break

        # Images -> scale-in
        for match in re.finditer(r'<img\b[^>]*>', html):
            tag = match.group(0)
            if 'data-animate' not in tag:
                new_tag = tag.replace('<img', '<img data-animate="scale-in" data-delay="0.3"', 1)
                html = html.replace(tag, new_tag, 1)
                count += 1

        # CTA links -> magnetic
        for match in re.finditer(r'<a\b[^>]*>', html):
            tag = match.group(0)
            if 'data-animate' not in tag and ('btn' in tag.lower() or 'button' in tag.lower() or 'cta' in tag.lower()):
                new_tag = tag.replace('<a', '<a data-animate="magnetic"', 1)
                html = html.replace(tag, new_tag, 1)
                count += 1

        # Grid/flex containers -> stagger
        for match in re.finditer(r'<div\b[^>]*(?:grid|flex)[^>]*>', html):
            tag = match.group(0)
            if 'data-animate' not in tag and 'REPEAT' not in html[max(0, match.start()-50):match.start()]:
                new_tag = tag.replace('>', ' data-animate="stagger">', 1)
                html = html.replace(tag, new_tag, 1)
                count += 1

        return html, count

    def _cleanup(self, html: str) -> str:
        """Clean up the HTML: fix whitespace, remove empty attributes."""
        # Remove empty class attributes
        html = re.sub(r'\s+class=""', '', html)
        # Remove empty style attributes
        html = re.sub(r'\s+style=""', '', html)
        # Fix double spaces in attributes
        html = re.sub(r'\s{2,}', ' ', html)
        # Fix attribute ordering (data-animate before other data-)
        # Remove trailing whitespace per line
        lines = html.split('\n')
        lines = [line.rstrip() for line in lines]
        html = '\n'.join(lines)
        # Remove excessive blank lines
        html = re.sub(r'\n{3,}', '\n\n', html)
        return html.strip() + '\n'

    def _generate_variant_id(self, section_type: str) -> str:
        """Generate the next available variant ID for a section type."""
        # Check existing variants
        category = self.registry.get("categories", {}).get(section_type, {})
        existing = [v["id"] for v in category.get("variants", [])]

        # Also check filesystem
        section_dir = self.components_dir / section_type
        if section_dir.exists():
            for f in section_dir.glob("*.html"):
                vid = f.stem
                if vid not in existing:
                    existing.append(vid)

        # Find next stitch number
        stitch_nums = []
        for vid in existing:
            match = re.search(r'-stitch-(\d+)$', vid)
            if match:
                stitch_nums.append(int(match.group(1)))

        next_num = max(stitch_nums, default=0) + 1
        return f"{section_type}-stitch-{next_num:02d}"

    def _update_registry(self, result: ConversionResult):
        """Update components.json with the new variant."""
        registry = self.registry
        section_type = result.file_path.split("/")[0]

        if section_type not in registry.get("categories", {}):
            registry["categories"][section_type] = {
                "label": section_type.title(),
                "required": False,
                "variants": [],
            }

        # Check if variant already exists
        variants = registry["categories"][section_type]["variants"]
        existing_ids = {v["id"] for v in variants}

        if result.variant_id not in existing_ids:
            variants.append(result.registry_entry)

        # Save
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convert Google Stitch HTML to Site Builder template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stitch_converter.py hero.html --section hero --name "Parallax Split" --tags modern,bold
  python stitch_converter.py services.html --section services --name "Icon Cards" --detect-repeats
  python stitch_converter.py about.html --section about --name "Timeline" --dry-run
  python stitch_converter.py pricing.html --section pricing --name "3-Tier Cards" --tags elegant,saas
        """
    )

    parser.add_argument("input", help="Path to Stitch HTML file")
    parser.add_argument("--section", "-s", required=True,
                       choices=["hero", "about", "services", "testimonials", "contact",
                               "gallery", "pricing", "faq", "team", "stats", "cta",
                               "footer", "nav", "features", "menu", "process", "blog",
                               "timeline", "social-proof", "app-download", "reservations",
                               "booking", "schedule", "video", "awards", "donations",
                               "comparison", "listings"],
                       help="Target section type")
    parser.add_argument("--name", "-n", required=True, help="Component name (e.g., 'Split Parallax')")
    parser.add_argument("--description", "-d", default="", help="Italian description")
    parser.add_argument("--tags", "-t", default="", help="Comma-separated tags (modern,bold,elegant)")
    parser.add_argument("--no-repeats", action="store_true", help="Disable repeat detection")
    parser.add_argument("--no-animations", action="store_true", help="Don't add data-animate")
    parser.add_argument("--no-colors", action="store_true", help="Don't convert colors")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        html_input = f.read()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    # Convert
    converter = StitchConverter()
    result = converter.convert(
        html_input=html_input,
        section_type=args.section,
        name=args.name,
        description=args.description,
        tags=tags,
        detect_repeats=not args.no_repeats,
        add_animations=not args.no_animations,
        convert_colors=not args.no_colors,
        interactive=args.interactive,
    )

    # Print report
    print("=" * 60)
    print(f"  Stitch -> Template Conversion Report")
    print("=" * 60)
    print(f"  Variant ID:      {result.variant_id}")
    print(f"  File:            {result.file_path}")
    print(f"  Placeholders:    {len(result.placeholders)}")
    for p in result.placeholders:
        print(f"                   - {{{{{p}}}}}")
    print(f"  Repeat blocks:   {len(result.repeat_keys)}")
    for r in result.repeat_keys:
        print(f"                   - <!-- REPEAT:{r} -->")
    print(f"  Animations:      {result.animations_added} added")
    print(f"  Colors replaced: {result.colors_replaced}")

    if result.warnings:
        print(f"\n  Warnings:")
        for w in result.warnings:
            print(f"    - {w}")

    print("\n  Registry entry:")
    print(f"    {json.dumps(result.registry_entry, indent=4, ensure_ascii=False)}")

    # Preview HTML (first 50 lines)
    print(f"\n  Preview ({len(result.html)} chars, first 40 lines):")
    print("  " + "-" * 56)
    for i, line in enumerate(result.html.split("\n")[:40]):
        print(f"  {line}")
    if len(result.html.split("\n")) > 40:
        print(f"  ... ({len(result.html.split(chr(10)))} total lines)")

    # Save
    if not args.dry_run:
        print(f"\n  Saving...")
        save_result = converter.save(result)
        for action in save_result["actions"]:
            print(f"    {action}")
        print(f"\n  Done! Template saved as {result.variant_id}")
    else:
        print(f"\n  [DRY RUN] No files written. Remove --dry-run to save.")


if __name__ == "__main__":
    main()
