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


def _hex_to_rgb(hex_color: str) -> str:
    """Convert '#3b82f6' to '59,130,246' for use in rgba()."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        return "99,102,241"  # fallback: indigo
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r},{g},{b}"
    except ValueError:
        return "99,102,241"


# Section labels for navigation (Italian)
_SECTION_NAV_LABELS = {
    "hero": None,  # hero is the top of the page, no nav link needed
    "about": "Chi Siamo",
    "services": "Servizi",
    "features": "Funzionalità",
    "gallery": "Galleria",
    "testimonials": "Testimonianze",
    "team": "Team",
    "pricing": "Prezzi",
    "faq": "FAQ",
    "blog": "Blog",
    "contact": "Contatti",
    "cta": None,  # CTA doesn't need a nav link
    "footer": None,
    "stats": "Numeri",
    "process": "Processo",
}


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

        Auto-injects INDEX (1-based) and INDEX_PADDED (zero-padded, e.g. "01")
        into each item so templates like services-tabs-01 and services-minimal-list-01
        can reference {{INDEX}} and {{INDEX_PADDED}}.

        Includes case-insensitive key lookup as a safety net for data normalization.
        """
        pattern = r'<!-- REPEAT:(\w+) -->(.*?)<!-- /REPEAT:\1 -->'

        # Build a case-insensitive lookup map for the data keys
        key_lookup = {k.upper(): k for k in data.keys() if isinstance(data[k], list)}

        def expand_block(match):
            key = match.group(1)
            inner_template = match.group(2)

            # Try exact key first, then case-insensitive lookup
            items = data.get(key)
            if items is None:
                real_key = key_lookup.get(key.upper())
                if real_key:
                    items = data[real_key]
                    logger.info(f"[Assembler] REPEAT:{key} resolved via case-insensitive lookup to '{real_key}'")

            if not isinstance(items, list) or not items:
                available_lists = {k: len(v) for k, v in data.items() if isinstance(v, list)}
                logger.warning(
                    f"[Assembler] REPEAT:{key} has no items (key missing or empty array). "
                    f"Available list keys in data: {available_lists}. "
                    f"All data keys: {list(data.keys())}"
                )
                return ""

            fragments = []
            for idx, item in enumerate(items):
                if isinstance(item, dict):
                    # Inject index placeholders for templates that need them
                    item_with_index = {
                        **item,
                        "INDEX": str(idx + 1),
                        "INDEX_PADDED": f"{idx + 1:02d}",
                        "INDEX_ZERO": str(idx),
                    }
                    # Recursively expand nested repeats within this item
                    fragment = self._expand_repeats(inner_template, item_with_index)
                    fragment = self._replace_placeholders(fragment, item_with_index)
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

        # Inject RGB color variants for rgba() usage in templates
        primary_hex = head_data.get("PRIMARY_COLOR", "#3b82f6")
        bg_hex = head_data.get("BG_COLOR", "#ffffff")
        head_data["PRIMARY_COLOR_RGB"] = _hex_to_rgb(primary_hex)
        head_data["BG_COLOR_RGB"] = _hex_to_rgb(bg_hex)

        # Map layout design tokens from theme choices to CSS values
        radius_map = {
            "sharp": ("2px", "4px", "8px"),
            "soft": ("6px", "12px", "20px"),
            "round": ("12px", "24px", "32px"),
            "pill": ("8px", "16px", "9999px"),
        }
        spacing_map = {
            "compact": ("clamp(2rem, 6vw, 4rem)", "72rem"),
            "normal": ("clamp(3rem, 10vw, 7rem)", "80rem"),
            "generous": ("clamp(5rem, 14vw, 10rem)", "72rem"),
        }
        radius_style = head_data.get("BORDER_RADIUS_STYLE", "soft")
        r_sm, r_md, r_lg = radius_map.get(radius_style, radius_map["soft"])
        head_data["RADIUS_SM"] = r_sm
        head_data["RADIUS_MD"] = r_md
        head_data["RADIUS_LG"] = r_lg

        spacing = head_data.get("SPACING_DENSITY", "normal")
        sp_section, sp_max = spacing_map.get(spacing, spacing_map["normal"])
        head_data["SPACE_SECTION"] = sp_section
        head_data["MAX_WIDTH"] = sp_max

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

            # For footer sections, strip nav links to non-existent sections
            if variant_id and variant_id.startswith("footer"):
                section_html = self._clean_footer_nav(section_html, site_data)

            sections_html.append(section_html)

        # 3. Build navigation bar from section IDs
        nav_style = site_data.get("nav_style", "nav-classic-01")
        nav_html = self._build_nav(site_data, nav_style=nav_style)

        # 4. Generate Schema.org JSON-LD
        schema_ld = self._build_schema_ld(site_data)

        # 5. Build Web3Forms contact handler script
        form_handler = self._build_form_handler(site_data)

        # 6. Assemble complete page
        body_content = "\n\n".join(sections_html)
        gsap_script_tag = f"<script>\n{self.gsap_script}\n</script>"

        complete_html = f"""{head_html}
<body class="bg-[var(--color-bg)] text-[var(--color-text)] font-body antialiased">

{nav_html}

{body_content}

{schema_ld}
{form_handler}
{gsap_script_tag}
</body>
</html>"""

        return complete_html

    def _build_nav(self, site_data: Dict[str, Any], nav_style: str = "nav-classic-01") -> str:
        """Generate a sticky navigation bar with anchor links to each section.

        Tries to load a template from components/nav/{nav_style}.html.
        Falls back to inline generation if the file doesn't exist.
        """
        global_data = site_data.get("global", {})
        business_name = global_data.get("BUSINESS_NAME", "")
        logo_url = global_data.get("LOGO_URL", "")

        # Collect section IDs from components
        nav_links = []
        for component in site_data.get("components", []):
            variant_id = component.get("variant_id", "")
            # Extract section type from variant_id (e.g. "hero-split-01" -> "hero")
            section_type = variant_id.rsplit("-", 2)[0] if "-" in variant_id else variant_id
            # Normalize: strip trailing digits and hyphens to get base type
            for sec_key, label in _SECTION_NAV_LABELS.items():
                if section_type.startswith(sec_key) and label:
                    if not any(l[0] == sec_key for l in nav_links):
                        nav_links.append((sec_key, label))
                    break

        if not nav_links:
            return ""

        # --- Try loading a nav template file ---
        nav_template_path = self.components_dir / "nav" / f"{nav_style}.html"
        try:
            with open(nav_template_path, "r", encoding="utf-8") as f:
                nav_template = f.read()
            return self._render_nav_template(
                nav_template, nav_links, business_name, logo_url,
            )
        except FileNotFoundError:
            logger.warning(f"[Assembler] Nav template '{nav_style}' not found, using inline fallback")

        # --- Fallback: inline generation (original code) ---
        links_html = "\n".join(
            f'        <a href="#{sid}" class="text-sm font-medium text-[var(--color-text)]/70 '
            f'hover:text-[var(--color-primary)] transition-colors duration-200">{label}</a>'
            for sid, label in nav_links
        )

        return f"""<!-- Auto-generated sticky navigation -->
<nav data-scroll-nav class="fixed top-0 left-0 right-0 z-50 transition-all duration-300" style="background: rgba(var(--color-bg-rgb, 255,255,255), 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid rgba(var(--color-primary-rgb, 99,102,241), 0.08);" data-animate="fade-down">
  <div class="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
    <a href="#hero" class="flex items-center gap-2 shrink-0">
      <img src="{logo_url}" alt="" class="h-7 w-auto object-contain">
      <span class="font-bold font-heading text-sm text-[var(--color-text)]">{business_name}</span>
    </a>
    <div class="hidden md:flex items-center gap-6">
{links_html}
    </div>
    <button onclick="this.nextElementSibling.classList.toggle('hidden')" class="md:hidden p-2 rounded-lg hover:bg-[var(--color-bg-alt)] transition-colors" aria-label="Menu">
      <svg class="w-5 h-5 text-[var(--color-text)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
    <div class="hidden absolute top-16 left-0 right-0 md:hidden p-4 space-y-3" style="background: rgba(var(--color-bg-rgb, 255,255,255), 0.95); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(var(--color-primary-rgb, 99,102,241), 0.08);">
{links_html.replace('text-sm', 'text-base block py-1')}
    </div>
  </div>
</nav>
<!-- Spacer for fixed nav -->
<div class="h-16"></div>"""

    def _render_nav_template(
        self,
        template: str,
        nav_links: List[tuple],
        business_name: str,
        logo_url: str,
    ) -> str:
        """Replace placeholders in a nav template file with generated link HTML."""
        link_class = (
            'text-sm font-medium text-[var(--color-text)]/70 '
            'hover:text-[var(--color-primary)] transition-colors duration-200'
        )
        mobile_class = (
            'block w-full text-center text-base font-medium py-2 rounded-lg '
            'text-[var(--color-text)]/80 hover:text-[var(--color-primary)] '
            'hover:bg-[var(--color-bg-alt)] transition-colors duration-200'
        )
        overlay_class = (
            'nav-overlay-link block text-3xl md:text-4xl font-heading font-bold '
            'text-[var(--color-text)] hover:text-[var(--color-primary)] transition-colors duration-300'
        )

        all_links = "\n".join(
            f'      <a href="#{sid}" class="{link_class}">{label}</a>'
            for sid, label in nav_links
        )
        all_mobile = "\n".join(
            f'      <a href="#{sid}" class="{mobile_class}">{label}</a>'
            for sid, label in nav_links
        )
        all_overlay = "\n".join(
            f'    <a href="#{sid}" class="{overlay_class}">{label}</a>'
            for sid, label in nav_links
        )

        # Split links for centered nav: left half / right half
        mid = len(nav_links) // 2
        left_links = nav_links[:mid] if mid > 0 else nav_links[:1]
        right_links = nav_links[mid:] if mid > 0 else nav_links[1:]

        left_html = "\n".join(
            f'      <a href="#{sid}" class="{link_class}">{label}</a>'
            for sid, label in left_links
        )
        right_html = "\n".join(
            f'      <a href="#{sid}" class="{link_class}">{label}</a>'
            for sid, label in right_links
        )

        result = template
        result = result.replace("{{LOGO_URL}}", logo_url or "")
        result = result.replace("{{BUSINESS_NAME}}", business_name or "")
        result = result.replace("{{NAV_LINKS_LEFT}}", left_html)
        result = result.replace("{{NAV_LINKS_RIGHT}}", right_html)
        result = result.replace("{{NAV_LINKS_OVERLAY}}", all_overlay)
        result = result.replace("{{NAV_LINKS_MOBILE}}", all_mobile)
        result = result.replace("{{NAV_LINKS}}", all_links)
        return result

    def _build_schema_ld(self, site_data: Dict[str, Any]) -> str:
        """Generate Schema.org JSON-LD structured data for SEO."""
        import json as _json
        global_data = site_data.get("global", {})
        meta = site_data.get("meta", {})

        business_name = global_data.get("BUSINESS_NAME", "")
        if not business_name:
            return ""

        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business_name,
            "description": meta.get("description", meta.get("og_description", "")),
        }

        phone = global_data.get("BUSINESS_PHONE", "")
        if phone:
            schema["telephone"] = phone

        email = global_data.get("BUSINESS_EMAIL", "")
        if email:
            schema["email"] = email

        address = global_data.get("BUSINESS_ADDRESS", "")
        if address:
            schema["address"] = {
                "@type": "PostalAddress",
                "streetAddress": address,
            }

        logo_url = global_data.get("LOGO_URL", "")
        if logo_url and not logo_url.startswith("data:"):
            schema["logo"] = logo_url

        schema_json = _json.dumps(schema, ensure_ascii=False, indent=2)
        return f'<script type="application/ld+json">\n{schema_json}\n</script>'

    def _build_form_handler(self, site_data: Dict[str, Any]) -> str:
        """Generate a Web3Forms-compatible form handler script.

        If a WEB3FORMS_KEY is set in global data, forms submit via API.
        Otherwise, forms show the inline success state (demo mode).
        The script also sends a copy to the business email via mailto: fallback.
        """
        global_data = site_data.get("global", {})
        business_email = global_data.get("BUSINESS_EMAIL", "")
        web3forms_key = global_data.get("WEB3FORMS_KEY", "")

        return f"""<script>
(function() {{
  // Web3Forms contact form handler
  var W3F_KEY = '{web3forms_key}';
  var BIZ_EMAIL = '{business_email}';

  document.querySelectorAll('#contact form').forEach(function(form) {{
    form.addEventListener('submit', function(e) {{
      e.preventDefault();
      var fd = new FormData(form);
      var data = {{}};
      form.querySelectorAll('input,textarea').forEach(function(el) {{
        if (el.name) data[el.name] = el.value;
        else if (el.type === 'email') data['email'] = el.value;
        else if (el.type === 'text' && !data['name']) data['name'] = el.value;
        else if (el.tagName === 'TEXTAREA') data['message'] = el.value;
      }});

      // Show success state immediately
      var successHTML = '<div class="text-center py-12">'
        + '<div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" style="background: var(--color-primary);">'
        + '<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>'
        + '</div><h3 class="text-xl font-bold font-heading" style="color: var(--color-text);">Messaggio inviato!</h3>'
        + '<p class="mt-2 font-body" style="color: var(--color-text-muted);">Grazie, ti risponderemo al pi\\u00f9 presto.</p></div>';
      form.innerHTML = successHTML;

      // If Web3Forms key is configured, send via API
      if (W3F_KEY) {{
        fetch('https://api.web3forms.com/submit', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ access_key: W3F_KEY, ...data, to: BIZ_EMAIL }})
        }}).catch(function() {{}});
      }}
    }});
  }});
}})();
</script>"""

    @staticmethod
    def _clean_footer_nav(footer_html: str, site_data: Dict[str, Any]) -> str:
        """Remove footer nav links that point to sections not present in this site."""
        import re

        # Collect active section IDs from components
        active_sections = set()
        for comp in site_data.get("components", []):
            vid = comp.get("variant_id", "")
            for sec_key in _SECTION_NAV_LABELS:
                if vid.startswith(sec_key):
                    active_sections.add(sec_key)
                    break

        # Remove <a href="#section">...</a> links where section is not active
        # Matches anchor tags with href="#something" pattern
        def _strip_dead_link(match):
            href_section = match.group(1)
            if href_section in active_sections or href_section == "hero":
                return match.group(0)  # keep it
            return ""  # remove the entire link

        footer_html = re.sub(
            r'<a\s+href="#(\w+)"[^>]*>[^<]*</a>\s*',
            _strip_dead_link,
            footer_html,
        )
        return footer_html


# Singleton instance
assembler = TemplateAssembler()
