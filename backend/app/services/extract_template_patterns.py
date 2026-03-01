"""
Extract design patterns from professional HTML templates in template/_extracted/.

Scans index.html files, extracts:
- Section structure (hero, about, services, gallery, etc.)
- Color palettes (hex, rgba, CSS custom properties)
- Font families
- CSS layout patterns (grid, flexbox)
- Animation/transition patterns
- Responsive breakpoints

Formats extracted data as knowledge DB patterns and saves via design_knowledge.py.
Idempotent: uses INSERT OR REPLACE, safe to re-run.

Usage:
    python -m app.services.extract_template_patterns
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_TEMPLATE_DIR = _PROJECT_ROOT / "template" / "_extracted"

# ---------------------------------------------------------------------------
# Category mapping: directory name -> business category
# ---------------------------------------------------------------------------
DIRECTORY_CATEGORY_MAP = {
    "agency": "agency",
    "restaurant": "restaurant",
    "pack1": "mixed",
    "pack2": "portfolio",
    "pack3": "mixed",
}

# ---------------------------------------------------------------------------
# Regex patterns for extraction
# ---------------------------------------------------------------------------
_HEX_COLOR_RE = re.compile(r"#([0-9a-fA-F]{3,8})\b")
_RGBA_RE = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+)?\s*\)")
_HSL_RE = re.compile(r"hsla?\(\s*(\d+)\s*,\s*(\d+)%?\s*,\s*(\d+)%?\s*(?:,\s*[\d.]+)?\s*\)")
_CSS_VAR_COLOR_RE = re.compile(r"--[\w-]*(?:color|bg|background|text|primary|secondary|accent)[\w-]*\s*:\s*([^;]+)")
_FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}{]+)")
_GOOGLE_FONT_RE = re.compile(r"fonts\.googleapis\.com/css2?\?family=([^\"'&]+)")
_SECTION_ID_RE = re.compile(r'(?:id|class)\s*=\s*["\']([^"\']*(?:hero|about|service|portfolio|gallery|contact|footer|testimonial|feature|pricing|team|faq|blog|menu|cta|banner|header|stat|counter|client|partner|work|project|skill|experience|education|booking|reservation)[^"\']*)["\']', re.IGNORECASE)
_SECTION_TAG_RE = re.compile(r"<section[^>]*>", re.IGNORECASE)
_ANIMATION_RE = re.compile(r"(?:animation|transition)\s*:\s*([^;}{]+)", re.IGNORECASE)
_KEYFRAMES_RE = re.compile(r"@keyframes\s+([\w-]+)", re.IGNORECASE)
_GRID_RE = re.compile(r"(?:display\s*:\s*grid|grid-template|grid-gap|grid-area)", re.IGNORECASE)
_FLEXBOX_RE = re.compile(r"display\s*:\s*flex", re.IGNORECASE)
_MEDIA_QUERY_RE = re.compile(r"@media[^{]*\(\s*(?:min|max)-width\s*:\s*(\d+)(?:px|rem|em)", re.IGNORECASE)
_TRANSFORM_RE = re.compile(r"transform\s*:\s*([^;}{]+)", re.IGNORECASE)
_BACKDROP_FILTER_RE = re.compile(r"backdrop-filter\s*:\s*([^;}{]+)", re.IGNORECASE)
_BOX_SHADOW_RE = re.compile(r"box-shadow\s*:\s*([^;}{]+)", re.IGNORECASE)
_GRADIENT_RE = re.compile(r"(?:linear|radial|conic)-gradient\s*\([^)]+\)", re.IGNORECASE)
_TAILWIND_CLASS_RE = re.compile(r'class="([^"]*(?:flex|grid|gap|rounded|shadow|backdrop|blur|gradient)[^"]*)"')

# Common boilerplate colors to skip
_SKIP_COLORS = {
    "000", "000000", "fff", "ffffff", "333", "333333", "666", "666666",
    "999", "999999", "ccc", "cccccc", "ddd", "dddddd", "eee", "eeeeee",
    "f5f5f5", "f8f8f8", "fafafa", "e5e5e5", "d9d9d9", "111", "111111",
    "222", "222222", "444", "444444", "555", "555555", "777", "777777",
    "888", "888888", "aaa", "aaaaaa", "bbb", "bbbbbb",
}

# Generic fonts to skip
_SKIP_FONTS = {
    "sans-serif", "serif", "monospace", "cursive", "fantasy", "system-ui",
    "inherit", "initial", "unset", "-apple-system", "blinkmacsystemfont",
    "segoe ui", "arial", "helvetica", "helvetica neue", "times new roman",
    "verdana", "tahoma", "georgia", "trebuchet ms", "courier new",
    "consolas", "menlo", "liberation mono", "apple color emoji",
    "segoe ui emoji", "segoe ui symbol", "noto color emoji",
    "sfmono-regular", "sf mono", "ionicons", "fontawesome",
    "font awesome", "icomoon", "flaticon", "themify", "baskerville",
}


# ---------------------------------------------------------------------------
# HTML file discovery
# ---------------------------------------------------------------------------

def find_template_index_files() -> List[Tuple[Path, str]]:
    """Find main index.html files in template/_extracted/, skipping docs.

    Returns list of (path, category) tuples.
    """
    if not _TEMPLATE_DIR.exists():
        logger.warning(f"Template directory not found: {_TEMPLATE_DIR}")
        return []

    results = []
    skip_names = {"documentation", "doc", "docs", "how to use"}

    for category_dir in sorted(_TEMPLATE_DIR.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        category = DIRECTORY_CATEGORY_MAP.get(category_dir.name, "mixed")

        for html_file in category_dir.rglob("index.html"):
            # Skip documentation directories
            parts_lower = [p.lower() for p in html_file.parts]
            if any(skip in parts_lower for skip in skip_names):
                continue
            # Skip email templates, banner ads, font previews
            path_str = str(html_file).lower()
            if any(x in path_str for x in ("email", "banner", "gwd_preview", "font", "rtl")):
                continue

            results.append((html_file, category))

    logger.info(f"Found {len(results)} template index.html files")
    return results


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def _read_file_safe(path: Path, max_size: int = 500_000) -> str:
    """Read an HTML file, capping at max_size bytes to avoid memory issues."""
    try:
        size = path.stat().st_size
        if size > max_size:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_size)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        logger.debug(f"Could not read {path}: {e}")
        return ""


def _read_css_files(html_path: Path) -> str:
    """Read CSS files referenced from an HTML file (in same directory tree)."""
    html_dir = html_path.parent
    html_content = _read_file_safe(html_path)
    css_refs = re.findall(r'href=["\']([^"\']*\.css)["\']', html_content)

    css_content = []
    for ref in css_refs:
        if ref.startswith(("http://", "https://", "//")):
            continue
        css_path = (html_dir / ref).resolve()
        if css_path.exists() and css_path.stat().st_size < 300_000:
            css_content.append(_read_file_safe(css_path, 300_000))

    return "\n".join(css_content)


def extract_colors(html: str, css: str) -> List[str]:
    """Extract unique, interesting hex colors from HTML+CSS."""
    combined = html + "\n" + css
    hex_colors = set()

    for match in _HEX_COLOR_RE.finditer(combined):
        color = match.group(1).lower()
        # Normalize 3-char hex to 6-char
        if len(color) == 3:
            color = color[0] * 2 + color[1] * 2 + color[2] * 2
        if color not in _SKIP_COLORS and len(color) in (6, 8):
            hex_colors.add(f"#{color[:6]}")

    # Also extract from CSS custom properties
    for match in _CSS_VAR_COLOR_RE.finditer(combined):
        val = match.group(1).strip()
        hex_match = _HEX_COLOR_RE.search(val)
        if hex_match:
            c = hex_match.group(1).lower()
            if len(c) == 3:
                c = c[0] * 2 + c[1] * 2 + c[2] * 2
            if c not in _SKIP_COLORS:
                hex_colors.add(f"#{c[:6]}")

    return sorted(hex_colors)[:12]  # Cap at 12 most unique colors


def extract_fonts(html: str, css: str) -> List[str]:
    """Extract font family names from HTML+CSS."""
    combined = html + "\n" + css
    fonts = set()

    # From Google Fonts links
    for match in _GOOGLE_FONT_RE.finditer(combined):
        font_str = match.group(1)
        for part in font_str.split("|"):
            font_name = part.split(":")[0].replace("+", " ").strip()
            if font_name and font_name.lower() not in _SKIP_FONTS:
                fonts.add(font_name)

    # From CSS font-family declarations
    for match in _FONT_FAMILY_RE.finditer(combined):
        families = match.group(1).split(",")
        for fam in families:
            name = fam.strip().strip("'\"").strip()
            if name and name.lower() not in _SKIP_FONTS and len(name) > 2:
                fonts.add(name)

    return sorted(fonts)[:8]


def extract_sections(html: str) -> List[str]:
    """Extract section types from HTML structure."""
    sections = set()

    for match in _SECTION_ID_RE.finditer(html):
        value = match.group(1).lower()
        # Map to canonical section names
        section_map = {
            "hero": "hero", "banner": "hero", "slider": "hero",
            "about": "about", "story": "about",
            "service": "services", "feature": "features",
            "portfolio": "portfolio", "work": "portfolio", "project": "portfolio",
            "gallery": "gallery",
            "testimonial": "testimonials", "review": "testimonials",
            "team": "team", "member": "team",
            "pricing": "pricing", "plan": "pricing",
            "contact": "contact",
            "footer": "footer",
            "blog": "blog", "news": "blog", "article": "blog",
            "faq": "faq",
            "counter": "stats", "stat": "stats",
            "client": "clients", "partner": "clients",
            "menu": "menu",
            "cta": "cta",
            "booking": "booking", "reservation": "booking",
            "skill": "skills",
            "experience": "experience", "education": "experience",
        }
        for keyword, canonical in section_map.items():
            if keyword in value:
                sections.add(canonical)
                break

    # Count section tags as a measure of page complexity
    section_count = len(_SECTION_TAG_RE.findall(html))

    return sorted(sections), section_count


def extract_css_patterns(html: str, css: str) -> Dict[str, any]:
    """Extract notable CSS patterns and techniques."""
    combined = html + "\n" + css
    patterns = {}

    # Layout patterns
    grid_count = len(_GRID_RE.findall(combined))
    flex_count = len(_FLEXBOX_RE.findall(combined))
    patterns["uses_grid"] = grid_count > 0
    patterns["uses_flexbox"] = flex_count > 0
    patterns["grid_count"] = grid_count
    patterns["flex_count"] = flex_count

    # Animations
    animations = _ANIMATION_RE.findall(combined)
    keyframes = _KEYFRAMES_RE.findall(combined)
    patterns["animation_count"] = len(animations)
    patterns["keyframe_names"] = list(set(keyframes))[:10]

    # Modern CSS features
    patterns["uses_backdrop_filter"] = bool(_BACKDROP_FILTER_RE.search(combined))
    patterns["uses_transforms"] = bool(_TRANSFORM_RE.search(combined))
    patterns["uses_gradients"] = bool(_GRADIENT_RE.search(combined))
    has_shadows = _BOX_SHADOW_RE.findall(combined)
    patterns["shadow_count"] = len(has_shadows)

    # Tailwind detection
    patterns["uses_tailwind"] = "tailwindcss" in combined.lower() or bool(_TAILWIND_CLASS_RE.search(html))

    # Responsive breakpoints
    breakpoints = set()
    for match in _MEDIA_QUERY_RE.finditer(combined):
        bp = int(match.group(1))
        if 300 < bp < 2000:
            breakpoints.add(bp)
    patterns["breakpoints"] = sorted(breakpoints)

    return patterns


def extract_template_name(html_path: Path) -> str:
    """Derive a human-readable template name from the file path."""
    parts = html_path.parts
    for i, part in enumerate(parts):
        if part == "_extracted" and i + 2 < len(parts):
            # Return the template folder name (e.g. "cleo-agency-landing-page-template-...")
            raw_name = parts[i + 2]
            # Strip the date suffix
            name = re.sub(r"-\d{4}-\d{2}-\d{2}.*$", "", raw_name)
            return name
    return html_path.stem


# ---------------------------------------------------------------------------
# Pattern formatting
# ---------------------------------------------------------------------------

def format_layout_pattern(
    name: str,
    category: str,
    sections: List[str],
    section_count: int,
    colors: List[str],
    fonts: List[str],
    css_patterns: Dict,
) -> Dict:
    """Format extracted data as a layout_patterns knowledge entry."""
    parts = [f"Professional template: {name} ({category})"]

    if sections:
        parts.append(f"Section flow: {' -> '.join(sections)}")

    if fonts:
        parts.append(f"Typography: {', '.join(fonts)}")

    if colors:
        parts.append(f"Color palette: {', '.join(colors[:6])}")

    layout_parts = []
    if css_patterns.get("uses_grid"):
        layout_parts.append(f"CSS Grid ({css_patterns['grid_count']}x)")
    if css_patterns.get("uses_flexbox"):
        layout_parts.append(f"Flexbox ({css_patterns['flex_count']}x)")
    if css_patterns.get("uses_tailwind"):
        layout_parts.append("Tailwind CSS")
    if css_patterns.get("uses_backdrop_filter"):
        layout_parts.append("backdrop-filter/glassmorphism")
    if css_patterns.get("uses_gradients"):
        layout_parts.append("CSS gradients")
    if layout_parts:
        parts.append(f"CSS techniques: {', '.join(layout_parts)}")

    if css_patterns.get("keyframe_names"):
        parts.append(f"Animations: {', '.join(css_patterns['keyframe_names'][:5])}")

    if css_patterns.get("breakpoints"):
        parts.append(f"Breakpoints: {', '.join(str(b) + 'px' for b in css_patterns['breakpoints'][:5])}")

    parts.append(f"Sections: {section_count}")

    # Build tags
    tags = [category, f"{section_count}-sections"]
    if css_patterns.get("uses_tailwind"):
        tags.append("tailwind")
    if css_patterns.get("uses_grid"):
        tags.append("css-grid")
    if css_patterns.get("uses_backdrop_filter"):
        tags.append("glassmorphism")
    if css_patterns.get("animation_count", 0) > 5:
        tags.append("animated")
    for s in sections[:4]:
        tags.append(s)

    return {
        "id": f"tpl_{name.replace('-', '_')[:60]}",
        "content": ". ".join(parts),
        "category": "layout_patterns",
        "tags": tags,
        "complexity": "high" if section_count > 8 else "medium",
        "impact_score": min(10, 5 + len(sections) // 2 + (1 if css_patterns.get("uses_gradients") else 0)),
    }


def format_color_pattern(
    name: str,
    category: str,
    colors: List[str],
) -> Optional[Dict]:
    """Format extracted colors as a color_palettes knowledge entry."""
    if len(colors) < 3:
        return None

    content = (
        f"Color palette from professional {category} template '{name}': "
        f"{', '.join(colors[:8])}. "
        f"Use as inspiration for {category} websites."
    )

    return {
        "id": f"tpl_colors_{name.replace('-', '_')[:50]}",
        "content": content,
        "category": "color_palettes",
        "tags": [category, "extracted", "professional"],
        "complexity": "low",
        "impact_score": 6,
    }


def format_typography_pattern(
    name: str,
    category: str,
    fonts: List[str],
) -> Optional[Dict]:
    """Format extracted fonts as a typography knowledge entry."""
    if not fonts:
        return None

    if len(fonts) >= 2:
        content = (
            f"Font pairing from professional {category} template '{name}': "
            f"heading '{fonts[0]}' + body '{fonts[1]}'"
        )
        if len(fonts) > 2:
            content += f" (also: {', '.join(fonts[2:])})"
        content += f". Proven combination for {category} websites."
    else:
        content = (
            f"Typography from professional {category} template '{name}': "
            f"'{fonts[0]}'. Used in real {category} websites."
        )

    return {
        "id": f"tpl_typo_{name.replace('-', '_')[:50]}",
        "content": content,
        "category": "typography",
        "tags": [category, "extracted", "font-pairing"] + [f.lower().replace(" ", "-") for f in fonts[:3]],
        "complexity": "low",
        "impact_score": 7,
    }


def format_section_flow_pattern(
    name: str,
    category: str,
    sections: List[str],
) -> Optional[Dict]:
    """Format section flow as a professional_blueprints entry."""
    if len(sections) < 3:
        return None

    content = (
        f"Section flow from professional {category} template '{name}': "
        f"{' -> '.join(sections)}. "
        f"This is a proven section order for {category} websites. "
        f"Total {len(sections)} sections."
    )

    return {
        "id": f"tpl_flow_{name.replace('-', '_')[:50]}",
        "content": content,
        "category": "professional_blueprints",
        "tags": [category, "section-flow", "extracted"] + sections[:4],
        "complexity": "medium",
        "impact_score": 8,
    }


# ---------------------------------------------------------------------------
# Main extraction pipeline
# ---------------------------------------------------------------------------

def extract_all_patterns() -> List[Dict]:
    """Scan all templates and extract design patterns.

    Returns a list of pattern dicts ready for the knowledge DB.
    """
    template_files = find_template_index_files()
    if not template_files:
        logger.warning("No template files found to extract.")
        return []

    all_patterns = []
    seen_names: Set[str] = set()

    # Track aggregates for category-level patterns
    category_fonts: Dict[str, Counter] = {}
    category_sections: Dict[str, Counter] = {}
    category_colors: Dict[str, Counter] = {}

    for html_path, category in template_files:
        name = extract_template_name(html_path)

        # Deduplicate: only process one index.html per template
        dedup_key = f"{category}_{name}"
        if dedup_key in seen_names:
            continue
        seen_names.add(dedup_key)

        logger.debug(f"Extracting: {name} ({category})")

        html = _read_file_safe(html_path)
        if not html or len(html) < 500:
            continue

        css = _read_css_files(html_path)
        combined_for_analysis = html + "\n" + css

        # Extract components
        colors = extract_colors(html, css)
        fonts = extract_fonts(html, css)
        sections, section_count = extract_sections(html)
        css_patterns = extract_css_patterns(html, css)

        # Track category aggregates
        category_fonts.setdefault(category, Counter())
        for f in fonts:
            category_fonts[category][f] += 1

        category_sections.setdefault(category, Counter())
        for s in sections:
            category_sections[category][s] += 1

        category_colors.setdefault(category, Counter())
        for c in colors:
            category_colors[category][c] += 1

        # Generate pattern entries
        layout_pattern = format_layout_pattern(
            name, category, sections, section_count, colors, fonts, css_patterns
        )
        all_patterns.append(layout_pattern)

        color_pattern = format_color_pattern(name, category, colors)
        if color_pattern:
            all_patterns.append(color_pattern)

        typo_pattern = format_typography_pattern(name, category, fonts)
        if typo_pattern:
            all_patterns.append(typo_pattern)

        flow_pattern = format_section_flow_pattern(name, category, sections)
        if flow_pattern:
            all_patterns.append(flow_pattern)

    # Generate category-aggregate patterns
    for cat, font_counter in category_fonts.items():
        top_fonts = [f for f, _ in font_counter.most_common(10)]
        if len(top_fonts) >= 3:
            all_patterns.append({
                "id": f"tpl_catfonts_{cat}",
                "content": (
                    f"Most popular fonts in professional {cat} templates: "
                    f"{', '.join(top_fonts)}. "
                    f"These are proven choices from {len(seen_names)} real templates."
                ),
                "category": "typography",
                "tags": [cat, "aggregate", "popular-fonts"],
                "complexity": "low",
                "impact_score": 9,
            })

    for cat, section_counter in category_sections.items():
        top_sections = [s for s, _ in section_counter.most_common(12)]
        if top_sections:
            all_patterns.append({
                "id": f"tpl_catsections_{cat}",
                "content": (
                    f"Most common sections in professional {cat} templates (by frequency): "
                    f"{', '.join(top_sections)}. "
                    f"Use this as a guide for section selection and ordering."
                ),
                "category": "professional_blueprints",
                "tags": [cat, "aggregate", "section-frequency"],
                "complexity": "low",
                "impact_score": 9,
            })

    logger.info(f"Extracted {len(all_patterns)} patterns from {len(seen_names)} templates")
    return all_patterns


# ---------------------------------------------------------------------------
# Database seeding
# ---------------------------------------------------------------------------

def seed_extracted_patterns() -> int:
    """Extract patterns from templates and save to the knowledge DB.

    Returns the number of patterns saved.
    """
    from app.services.design_knowledge import add_pattern, get_collection_stats

    patterns = extract_all_patterns()
    if not patterns:
        logger.info("No patterns extracted.")
        return 0

    saved = 0
    for p in patterns:
        try:
            add_pattern(
                pattern_id=p["id"],
                content=p["content"],
                category=p["category"],
                tags=p.get("tags"),
                complexity=p.get("complexity", "medium"),
                impact_score=p.get("impact_score", 5),
            )
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save pattern {p['id']}: {e}")

    stats = get_collection_stats()
    logger.info(
        f"Saved {saved}/{len(patterns)} extracted patterns. "
        f"Total DB patterns: {stats.get('total_patterns', '?')}"
    )
    return saved


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    count = seed_extracted_patterns()
    print(f"Done. Saved {count} patterns from professional templates.")
