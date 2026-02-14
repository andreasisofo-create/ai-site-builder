"""
Template Assembler - Reads HTML component templates and assembles complete pages.

Designed to be portable: works in FastAPI backend AND can be pasted into an n8n Code Node.
No framework imports (no FastAPI, no SQLAlchemy).

Usage:
    assembler = TemplateAssembler()
    html = assembler.assemble(site_data)
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TemplateAssembler:
    def __init__(self, components_dir: Optional[str] = None):
        if components_dir is None:
            components_dir = str(Path(__file__).parent.parent / "components")
        self.components_dir = Path(components_dir)
        self._registry: Optional[Dict] = None
        self._gsap_script: Optional[str] = None

    @property
    def registry(self) -> Dict:
        """Lazy-load and cache components.json."""
        if self._registry is None:
            registry_path = self.components_dir / "components.json"
            with open(registry_path, "r", encoding="utf-8") as f:
                self._registry = json.load(f)
        return self._registry

    @property
    def gsap_script(self) -> str:
        """Lazy-load and cache gsap-universal.js."""
        if self._gsap_script is None:
            js_path = self.components_dir / "gsap-universal.js"
            with open(js_path, "r", encoding="utf-8") as f:
                self._gsap_script = f.read()
        return self._gsap_script

    def get_variant_ids(self) -> Dict[str, List[str]]:
        """Returns {category: [variant_id, ...]} for all categories."""
        result = {}
        for cat_name, cat_data in self.registry["categories"].items():
            result[cat_name] = [v["id"] for v in cat_data["variants"]]
        return result

    def _read_template(self, file_path: str) -> str:
        """Reads an HTML template file."""
        full_path = self.components_dir / file_path
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def _replace_placeholders(self, template: str, data: Dict[str, Any]) -> str:
        """Replaces {{PLACEHOLDER}} with values from data dict."""
        def replacer(match):
            key = match.group(1)
            value = data.get(key, "")
            if value is None:
                value = ""
            return str(value)
        return re.sub(r'\{\{(\w+)\}\}', replacer, template)

    def _expand_repeats(self, template: str, data: Dict[str, Any]) -> str:
        """Expands <!-- REPEAT:KEY -->...<!-- /REPEAT:KEY --> blocks.

        Supports nested repeats: outer repeats are expanded first, then inner
        repeats within each item are expanded recursively using item data.
        """
        pattern = r'<!-- REPEAT:(\w+) -->(.*?)<!-- /REPEAT:\1 -->'

        def expand_block(match):
            key = match.group(1)
            inner_template = match.group(2)
            items = data.get(key, [])
            if not isinstance(items, list) or not items:
                return ""
            fragments = []
            for item in items:
                if isinstance(item, dict):
                    # Recursively expand nested repeats within this item
                    fragment = self._expand_repeats(inner_template, item)
                    fragment = self._replace_placeholders(fragment, item)
                else:
                    fragment = inner_template
                fragments.append(fragment)
            return "\n".join(fragments)

        return re.sub(pattern, expand_block, template, flags=re.DOTALL)

    def _find_variant_file(self, variant_id: str) -> Optional[str]:
        """Finds the file path for a variant ID."""
        for cat_data in self.registry["categories"].values():
            for variant in cat_data["variants"]:
                if variant["id"] == variant_id:
                    return variant["file"]
        return None

    def assemble(self, site_data: Dict[str, Any]) -> str:
        """
        Assembles a complete HTML page from site_data.

        site_data structure:
        {
            "theme": {
                "primary_color": "#3b82f6",
                "secondary_color": "#1e40af",
                "accent_color": "#f59e0b",
                "bg_color": "#ffffff",
                "bg_alt_color": "#f8fafc",
                "text_color": "#0f172a",
                "text_muted_color": "#64748b",
                "font_heading": "Inter",
                "font_heading_url": "Inter:wght@400;600;700;800",
                "font_body": "Inter",
                "font_body_url": "Inter:wght@400;500;600",
            },
            "meta": {
                "title": "...",
                "description": "...",
                "og_title": "...",
                "og_description": "...",
            },
            "components": [
                {"variant_id": "hero-split-01", "data": {"HERO_TITLE": "...", ...}},
                ...
            ],
            "global": {
                "BUSINESS_NAME": "...",
                "BUSINESS_PHONE": "...",
                "BUSINESS_EMAIL": "...",
                "BUSINESS_ADDRESS": "...",
                "LOGO_URL": "...",
                "CURRENT_YEAR": "2026",
            }
        }
        """
        # 1. Build head from template
        head_template = self._read_template("head/head-template.html")

        # Merge theme + meta + global into a single dict for head replacement
        head_data = {}
        theme = site_data.get("theme", {})
        for key, value in theme.items():
            head_data[key.upper()] = value

        meta = site_data.get("meta", {})
        for key, value in meta.items():
            upper_key = key.upper()
            # title/description need META_ prefix to match {{META_TITLE}}, {{META_DESCRIPTION}}
            if upper_key in ("TITLE", "DESCRIPTION"):
                upper_key = f"META_{upper_key}"
            head_data[upper_key] = value

        global_data = site_data.get("global", {})
        for key, value in global_data.items():
            head_data[key] = value  # global keys are already UPPER

        head_html = self._replace_placeholders(head_template, head_data)

        # 2. Build body sections
        sections_html = []
        for component in site_data.get("components", []):
            variant_id = component.get("variant_id")
            component_data = component.get("data", {})

            # Merge global data (lower priority) with component data (higher priority)
            merged_data = {**global_data, **component_data}

            file_path = self._find_variant_file(variant_id)
            if not file_path:
                logger.warning(f"Variant '{variant_id}' not found in registry, skipping")
                continue

            try:
                template = self._read_template(file_path)
            except FileNotFoundError:
                logger.warning(f"Template file '{file_path}' not found, skipping")
                continue

            # First expand repeats, then replace remaining placeholders
            section_html = self._expand_repeats(template, merged_data)
            section_html = self._replace_placeholders(section_html, merged_data)
            sections_html.append(section_html)

        # 3. Assemble complete page
        body_content = "\n\n".join(sections_html)
        gsap_script_tag = f"<script>\n{self.gsap_script}\n</script>"

        complete_html = f"""{head_html}
<body class="bg-[var(--color-bg)] text-[var(--color-text)] font-body antialiased">

{body_content}

{gsap_script_tag}
</body>
</html>"""

        return complete_html


# Singleton instance
assembler = TemplateAssembler()
