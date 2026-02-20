"""
Resource Catalog — Intelligent inventory of all HTML component templates.

Scans backend/app/components/ on initialization, analyzes each HTML file,
and merges metadata from components.json. Provides search, filtering, and
coverage reporting for the generation pipeline.

Usage:
    from app.services.resource_catalog import catalog
    inventory = catalog.get_full_inventory()
    results = catalog.search_components("hero", tags=["modern", "bold"])
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns for HTML analysis
# ---------------------------------------------------------------------------

_RE_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
_RE_REPEAT = re.compile(r"<!-- REPEAT:(\w+) -->")
_RE_DATA_ANIMATE = re.compile(r'data-animate="([^"]+)"')
_RE_CSS_VAR = re.compile(r"var\(--([a-zA-Z0-9_-]+)")
_RE_HTML_TAG = re.compile(r"<([a-z][a-z0-9]*)\b", re.IGNORECASE)


def _count_max_depth(html: str) -> int:
    """Estimate maximum nesting depth by counting indent levels."""
    max_depth = 0
    for line in html.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("<") and not stripped.startswith("</") and not stripped.startswith("<!--"):
            indent = len(line) - len(stripped)
            depth = indent // 2  # assume 2-space indent
            if depth > max_depth:
                max_depth = depth
    return max_depth


def _extract_section_type(directory_name: str) -> str:
    """Normalize directory name to section type (e.g. 'hero', 'about')."""
    return directory_name.lower().strip()


# ---------------------------------------------------------------------------
# Component metadata extraction
# ---------------------------------------------------------------------------

def _analyze_html(html: str) -> Dict[str, Any]:
    """Extract metadata from a single HTML component file."""
    placeholders = sorted(set(_RE_PLACEHOLDER.findall(html)))
    repeat_blocks = sorted(set(_RE_REPEAT.findall(html)))
    gsap_animations = sorted(set(_RE_DATA_ANIMATE.findall(html)))
    css_variables = sorted(set(_RE_CSS_VAR.findall(html)))
    html_tags = _RE_HTML_TAG.findall(html)
    element_count = len(html_tags)
    max_depth = _count_max_depth(html)
    line_count = html.count("\n") + 1

    return {
        "placeholders": placeholders,
        "repeat_blocks": repeat_blocks,
        "gsap_animations": gsap_animations,
        "css_variables": css_variables,
        "element_count": element_count,
        "max_depth": max_depth,
        "line_count": line_count,
    }


# ---------------------------------------------------------------------------
# ResourceCatalog
# ---------------------------------------------------------------------------

class ResourceCatalog:
    """Intelligent catalog of all HTML component templates.

    Scans the components directory, merges with components.json metadata,
    and provides querying/reporting methods.
    """

    def __init__(self, components_dir: Optional[str] = None):
        if components_dir is None:
            components_dir = str(Path(__file__).parent.parent / "components")
        self.components_dir = Path(components_dir)

        # Internal storage
        self._components: Dict[str, Dict[str, Any]] = {}  # variant_id -> metadata
        self._registry: Dict[str, Any] = {}  # raw components.json
        self._section_index: Dict[str, List[str]] = {}  # section_type -> [variant_ids]

        self._load()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load components.json and scan all HTML files."""
        self._load_registry()
        self._scan_html_files()
        self._build_section_index()
        logger.info(
            f"[ResourceCatalog] Loaded {len(self._components)} components "
            f"across {len(self._section_index)} section types"
        )

    def _load_registry(self) -> None:
        """Load and index components.json."""
        registry_path = self.components_dir / "components.json"
        if not registry_path.exists():
            logger.warning("[ResourceCatalog] components.json not found")
            return
        with open(registry_path, "r", encoding="utf-8") as f:
            self._registry = json.load(f)

    def _get_registry_variant(self, variant_id: str) -> Optional[Dict]:
        """Look up a variant in the registry by ID."""
        for cat_data in self._registry.get("categories", {}).values():
            for variant in cat_data.get("variants", []):
                if variant.get("id") == variant_id:
                    return variant
        return None

    def _scan_html_files(self) -> None:
        """Walk the components directory and analyze every HTML file."""
        if not self.components_dir.exists():
            logger.warning(f"[ResourceCatalog] Components dir not found: {self.components_dir}")
            return

        # Directories to skip (not real section types)
        skip_dirs = {"head", "nav", "v2"}

        for html_path in sorted(self.components_dir.rglob("*.html")):
            # Get relative path from components dir
            rel = html_path.relative_to(self.components_dir)
            parts = rel.parts  # e.g. ("hero", "hero-split-01.html")

            if len(parts) < 2:
                continue  # skip root-level files like head-template.html

            dir_name = parts[0]
            if dir_name in skip_dirs:
                continue

            # Derive variant_id from filename (strip .html)
            variant_id = html_path.stem  # e.g. "hero-split-01"
            section_type = _extract_section_type(dir_name)
            file_rel = str(rel).replace("\\", "/")  # normalize path separators

            # Read and analyze HTML
            try:
                html_content = html_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"[ResourceCatalog] Failed to read {html_path}: {e}")
                continue

            analysis = _analyze_html(html_content)

            # Merge with registry metadata if available
            registry_info = self._get_registry_variant(variant_id)

            self._components[variant_id] = {
                "variant_id": variant_id,
                "section_type": section_type,
                "file": file_rel,
                "name": registry_info.get("name", variant_id) if registry_info else variant_id,
                "description": registry_info.get("description", "") if registry_info else "",
                "tags": registry_info.get("tags", []) if registry_info else [],
                "registry_placeholders": registry_info.get("placeholders", []) if registry_info else [],
                # From HTML analysis
                "placeholders": analysis["placeholders"],
                "repeat_blocks": analysis["repeat_blocks"],
                "gsap_animations": analysis["gsap_animations"],
                "css_variables": analysis["css_variables"],
                "element_count": analysis["element_count"],
                "max_depth": analysis["max_depth"],
                "line_count": analysis["line_count"],
            }

    def _build_section_index(self) -> None:
        """Build section_type -> [variant_ids] index."""
        self._section_index.clear()
        for variant_id, meta in self._components.items():
            section = meta["section_type"]
            if section not in self._section_index:
                self._section_index[section] = []
            self._section_index[section].append(variant_id)
        # Sort each list for deterministic output
        for section in self._section_index:
            self._section_index[section].sort()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_full_inventory(self) -> Dict[str, Any]:
        """Return a summary of all components: counts per section, totals, coverage."""
        section_counts = {
            section: len(variants)
            for section, variants in sorted(self._section_index.items())
        }
        all_tags: Set[str] = set()
        all_animations: Set[str] = set()
        total_placeholders: Set[str] = set()

        for meta in self._components.values():
            all_tags.update(meta["tags"])
            all_animations.update(meta["gsap_animations"])
            total_placeholders.update(meta["placeholders"])

        return {
            "total_components": len(self._components),
            "total_section_types": len(self._section_index),
            "section_counts": section_counts,
            "all_tags": sorted(all_tags),
            "all_gsap_animations": sorted(all_animations),
            "unique_placeholders": len(total_placeholders),
            "sections": list(sorted(self._section_index.keys())),
        }

    def search_components(
        self,
        section_type: str,
        tags: Optional[List[str]] = None,
        mood: Optional[str] = None,
        min_complexity: Optional[int] = None,
        max_complexity: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Search components by section type and optional filters.

        Args:
            section_type: Required. e.g. "hero", "about", "services"
            tags: If provided, component must have at least one matching tag
            mood: Alias for a single tag search (e.g. "modern", "elegant")
            min_complexity: Minimum element_count
            max_complexity: Maximum element_count

        Returns:
            List of component metadata dicts matching the criteria
        """
        variant_ids = self._section_index.get(section_type, [])
        results = []

        # Combine mood into tags
        search_tags = set(tags or [])
        if mood:
            search_tags.add(mood)

        for vid in variant_ids:
            meta = self._components[vid]

            # Tag filter: component must have at least one matching tag
            if search_tags and not search_tags.intersection(meta["tags"]):
                continue

            # Complexity filters
            if min_complexity is not None and meta["element_count"] < min_complexity:
                continue
            if max_complexity is not None and meta["element_count"] > max_complexity:
                continue

            results.append(meta)

        return results

    def get_component_metadata(self, variant_id: str) -> Optional[Dict[str, Any]]:
        """Return full metadata for a single component by variant ID."""
        return self._components.get(variant_id)

    def get_alternatives(self, variant_id: str) -> List[Dict[str, Any]]:
        """Return other components of the same section type (excluding the given one)."""
        meta = self._components.get(variant_id)
        if not meta:
            return []

        section = meta["section_type"]
        return [
            self._components[vid]
            for vid in self._section_index.get(section, [])
            if vid != variant_id
        ]

    def get_section_coverage(self) -> Dict[str, Dict[str, Any]]:
        """Return per-section breakdown: variant count, variant IDs, whether required."""
        registry_categories = self._registry.get("categories", {})
        coverage = {}

        for section, variant_ids in sorted(self._section_index.items()):
            reg_cat = registry_categories.get(section, {})
            coverage[section] = {
                "count": len(variant_ids),
                "variants": variant_ids,
                "required": reg_cat.get("required", False),
                "label": reg_cat.get("label", section.title()),
            }

        return coverage

    def get_style_coverage(self, style_id: str) -> Dict[str, Any]:
        """Return what components a specific template style has available.

        Reads STYLE_VARIANT_MAP and STYLE_VARIANT_POOL from databinding_generator
        to check which sections are mapped for this style.
        """
        # Import lazily to avoid circular imports
        try:
            from app.services.databinding_generator import STYLE_VARIANT_MAP, STYLE_VARIANT_POOL
        except ImportError:
            STYLE_VARIANT_MAP = {}
            STYLE_VARIANT_POOL = {}

        # Primary map (deterministic)
        primary = STYLE_VARIANT_MAP.get(style_id, {})
        # Pool map (randomized alternatives)
        pool = STYLE_VARIANT_POOL.get(style_id, {})

        coverage: Dict[str, Any] = {
            "style_id": style_id,
            "found": bool(primary or pool),
            "sections": {},
        }

        # Merge sections from both maps
        all_sections = set(primary.keys()) | set(pool.keys())

        for section in sorted(all_sections):
            primary_variant = primary.get(section)
            pool_variants = pool.get(section, [])
            all_variants = pool_variants if pool_variants else ([primary_variant] if primary_variant else [])

            existing = [v for v in all_variants if v in self._components]
            missing = [v for v in all_variants if v not in self._components]

            coverage["sections"][section] = {
                "primary": primary_variant,
                "pool": pool_variants,
                "pool_size": len(pool_variants),
                "existing": existing,
                "missing": missing,
            }

        coverage["total_sections"] = len(all_sections)
        coverage["total_variants"] = sum(
            len(s["existing"]) for s in coverage["sections"].values()
        )

        return coverage

    def get_all_variant_ids(self) -> List[str]:
        """Return a sorted list of all known variant IDs."""
        return sorted(self._components.keys())

    def get_placeholders_for_variant(self, variant_id: str) -> List[str]:
        """Return the list of placeholders found in a component's HTML."""
        meta = self._components.get(variant_id)
        if not meta:
            return []
        return meta["placeholders"]

    def get_gsap_usage_report(self) -> Dict[str, Any]:
        """Return a report of GSAP animation usage across all components."""
        animation_usage: Dict[str, List[str]] = {}
        components_without_gsap: List[str] = []

        for variant_id, meta in sorted(self._components.items()):
            animations = meta["gsap_animations"]
            if not animations:
                components_without_gsap.append(variant_id)
            for anim in animations:
                if anim not in animation_usage:
                    animation_usage[anim] = []
                animation_usage[anim].append(variant_id)

        return {
            "total_unique_animations": len(animation_usage),
            "animation_usage": {
                anim: {"count": len(variants), "variants": variants}
                for anim, variants in sorted(animation_usage.items())
            },
            "components_without_gsap": components_without_gsap,
            "components_without_gsap_count": len(components_without_gsap),
        }

    def get_complexity_report(self) -> Dict[str, Any]:
        """Return component complexity statistics grouped by section."""
        section_stats: Dict[str, Dict[str, Any]] = {}

        for section, variant_ids in sorted(self._section_index.items()):
            counts = [self._components[v]["element_count"] for v in variant_ids]
            depths = [self._components[v]["max_depth"] for v in variant_ids]
            lines = [self._components[v]["line_count"] for v in variant_ids]

            section_stats[section] = {
                "count": len(variant_ids),
                "avg_elements": round(sum(counts) / len(counts), 1) if counts else 0,
                "max_elements": max(counts) if counts else 0,
                "avg_depth": round(sum(depths) / len(depths), 1) if depths else 0,
                "avg_lines": round(sum(lines) / len(lines), 1) if lines else 0,
            }

        return section_stats


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------

catalog = ResourceCatalog()
