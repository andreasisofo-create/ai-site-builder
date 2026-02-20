"""
Site Planner - Intelligent site architecture planner for the generation pipeline.

Analyzes user input (business name, description, category, style) and produces
a SitePlan dict that guides every downstream step: theme generation, text
generation, and component selection.

Integrates with:
  - SiteQualityGuide:  category-specific rules, must-have/recommended sections
  - ResourceCatalog:   component inventory, search, section coverage
  - UsageTracker:      anti-repetition priority scoring for components

Usage:
    from app.services.site_planner import site_planner
    plan = await site_planner.create_plan(
        business_name="Ristorante Da Mario",
        business_description="Trattoria tradizionale romana dal 1965",
        category="restaurant",
        sections=["hero", "about", "services", "gallery", "contact", "footer"],
        style_id="restaurant-elegant",
        primary_color="#D4AF37",
    )

Called from databinding_generator._generate_pipeline() BEFORE Theme+Texts step.
The resulting plan is injected into _generate_theme() and _generate_texts() as
context, and can override _select_components_deterministic() choices.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.services.resource_catalog import catalog
from app.services.site_quality_guide import quality_guide
from app.services.usage_tracker import usage_tracker

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Owner Rules — custom requirements beyond expert guide
# ---------------------------------------------------------------------------
_OWNER_RULES_PATH = Path(__file__).parent / "owner_rules.json"

def _load_owner_rules() -> Dict[str, Any]:
    """Load owner rules from JSON file. Returns empty dict on failure."""
    try:
        if _OWNER_RULES_PATH.exists():
            with open(_OWNER_RULES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning("Failed to load owner_rules.json: %s", e)
    return {}

OWNER_RULES = _load_owner_rules()

# ---------------------------------------------------------------------------
# Category alias map (user speaks Italian, style IDs use English)
# ---------------------------------------------------------------------------
_CATEGORY_ALIASES: Dict[str, str] = {
    "ristorante": "restaurant",
    "tech": "saas",
    "corporate": "business",
    "shop": "ecommerce",
    "negozio": "ecommerce",
    "creative": "portfolio",
    "creativo": "portfolio",
    "evento": "event",
    "eventi": "event",
    "blog": "blog",
    "azienda": "business",
    "impresa": "business",
}

_VALID_CATEGORIES = frozenset({
    "restaurant", "saas", "portfolio", "ecommerce",
    "business", "blog", "event", "custom",
})

# Recommended section ordering (matches quality guide SECTION_ORDER_RULES)
_SECTION_ORDER: List[str] = [
    "nav", "hero", "logos", "social-proof", "about", "services", "features",
    "gallery", "stats", "team", "process", "timeline", "testimonials",
    "pricing", "comparison", "faq", "schedule", "blog", "awards",
    "listings", "donations", "app-download", "booking", "cta", "contact", "footer",
]

# Animation strategy presets
_ANIMATION_STRATEGIES: Dict[str, str] = {
    "minimal": "Animazioni sottili e discrete: solo fade-up e text-split. Nessun effetto 3D o particellare.",
    "moderate": "Animazioni bilanciate: fade-up per i contenuti, text-split per i titoli, magnetic per i CTA, scale-in per le card.",
    "bold": "Animazioni audaci e d'impatto: parallax, blur-slide, rotate-3d, stagger per le griglie, morph-bg per gli sfondi.",
}

# Per-category animation defaults
_CATEGORY_ANIMATION_DEFAULT: Dict[str, str] = {
    "restaurant": "moderate",
    "saas": "bold",
    "portfolio": "bold",
    "ecommerce": "moderate",
    "business": "moderate",
    "blog": "minimal",
    "event": "bold",
    "custom": "moderate",
}

# Missing info detection: what data each section type typically needs
_SECTION_DATA_NEEDS: Dict[str, List[str]] = {
    "hero": ["headline", "subtitle", "hero_image"],
    "about": ["company_story", "team_photo"],
    "services": ["service_list"],
    "gallery": ["gallery_photos"],
    "testimonials": ["customer_reviews"],
    "contact": ["email", "phone", "address"],
    "team": ["team_members"],
    "pricing": ["pricing_plans"],
    "faq": ["faq_items"],
    "stats": ["company_stats"],
    "blog": ["blog_articles"],
    "schedule": ["event_schedule"],
    "booking": ["booking_availability"],
    "logos": ["partner_logos"],
}

# Per-category extra data requirements (beyond section-based needs)
_CATEGORY_EXTRA_NEEDS: Dict[str, List[str]] = {
    "restaurant": ["menu_items", "business_hours", "reservation_system"],
    "saas": ["product_screenshot", "pricing_plans", "feature_list"],
    "portfolio": ["project_images", "project_descriptions"],
    "ecommerce": ["product_catalog", "shipping_info", "return_policy"],
    "business": ["client_logos", "case_studies"],
    "blog": ["author_bio", "article_archive"],
    "event": ["event_date", "event_location", "speaker_list", "ticket_prices"],
    "custom": [],
}


def _normalize_category(category: str) -> str:
    """Normalize category string, resolving Italian aliases."""
    category = category.lower().strip()
    category = _CATEGORY_ALIASES.get(category, category)
    if category not in _VALID_CATEGORIES:
        category = "custom"
    return category


def _get_category_from_style_id(style_id: str) -> str:
    """Extract category from style ID (e.g. 'restaurant-elegant' -> 'restaurant')."""
    if not style_id:
        return "custom"
    prefix = style_id.split("-")[0].lower()
    return prefix if prefix in _VALID_CATEGORIES else "custom"


def _sort_sections(sections: List[str]) -> List[str]:
    """Sort sections according to the recommended visual flow order.

    Sections not in the ordering list are placed before the CTA/contact/footer
    tail so they don't end up awkwardly at the very end.
    """
    order_index = {s: i for i, s in enumerate(_SECTION_ORDER)}
    # Unknown sections get a high-but-not-tail index (before cta/contact/footer)
    tail_start = order_index.get("cta", 900) - 1

    def sort_key(section: str) -> int:
        return order_index.get(section, tail_start)

    return sorted(sections, key=sort_key)


# ---------------------------------------------------------------------------
# SitePlanner
# ---------------------------------------------------------------------------

class SitePlanner:
    """Creates a comprehensive SitePlan dict that drives the generation pipeline.

    The plan includes resolved sections, selected components, animation strategy,
    missing info detection, quality scoring, and a planning prompt for AI injection.
    """

    async def create_plan(
        self,
        business_name: str,
        business_description: str,
        category: str,
        sections: list[str],
        style_id: str | None = None,
        primary_color: str | None = None,
        logo_url: str | None = None,
        contact_info: dict | None = None,
    ) -> dict:
        """Create a complete site plan.

        This is the main entry point, called from databinding_generator before
        the Theme+Texts AI generation step.

        Args:
            business_name: Name of the business (e.g. "Ristorante Da Mario").
            business_description: Free-text description of the business.
            category: Business category (restaurant, saas, etc.) or Italian alias.
            sections: User-chosen section list (e.g. ["hero", "about", "services"]).
            style_id: Template style ID (e.g. "restaurant-elegant"). Optional.
            primary_color: User-selected primary brand color hex. Optional.
            logo_url: URL to the business logo. Optional.
            contact_info: Dict with keys like email, phone, address. Optional.

        Returns:
            SitePlan dict with keys: sections, components, color_palette,
            font_pairing, animation_strategy, missing_info, quality_score,
            quality_issues, category, style_id, planning_prompt.
        """
        logger.info(
            "[SitePlanner] Creating plan for '%s' (category=%s, style=%s, %d sections)",
            business_name, category, style_id, len(sections),
        )

        # 1. Normalize category (handle Italian aliases)
        resolved_category = _normalize_category(category)

        # If style_id given, derive category from it (style_id is more specific)
        if style_id:
            style_category = _get_category_from_style_id(style_id)
            if style_category != "custom":
                resolved_category = style_category

        logger.info(
            "[SitePlanner] Resolved category: '%s' (input was '%s')",
            resolved_category, category,
        )

        # 2. Resolve sections: ensure must-haves, add recommended, sort
        resolved_sections = self._resolve_sections(sections, resolved_category)
        logger.info(
            "[SitePlanner] Resolved sections (%d): %s",
            len(resolved_sections), resolved_sections,
        )

        # 3. Select component variants for each section (with priority scoring)
        selected_components = self._select_components(
            resolved_sections, style_id, resolved_category,
        )
        logger.info(
            "[SitePlanner] Selected components: %s",
            selected_components,
        )

        # 4. Determine animation strategy based on category
        animation_strategy = _CATEGORY_ANIMATION_DEFAULT.get(
            resolved_category, "moderate",
        )

        # 5. Build color palette hint (basic structure for AI to enhance)
        color_palette = self._build_color_palette_hint(
            primary_color, resolved_category,
        )

        # 6. Determine font pairing hint based on category rules
        font_pairing = self._get_font_pairing_hint(resolved_category)

        # 7. Identify missing info the user hasn't provided
        missing_info = self._identify_missing_info(
            resolved_sections,
            resolved_category,
            business_description,
            contact_info,
        )
        if missing_info:
            logger.info(
                "[SitePlanner] Informazioni mancanti: %s", missing_info,
            )

        # 8. Build the plan dict
        plan: Dict[str, Any] = {
            "sections": resolved_sections,
            "components": selected_components,
            "color_palette": color_palette,
            "font_pairing": font_pairing,
            "animation_strategy": animation_strategy,
            "missing_info": missing_info,
            "quality_score": 0.0,
            "quality_issues": [],
            "category": resolved_category,
            "style_id": style_id or "",
            "planning_prompt": "",
            "business_name": business_name,
            "business_description": business_description,
        }

        # 9. Quality evaluation
        quality_score, quality_issues = quality_guide.evaluate_plan({
            "category": resolved_category,
            "sections": resolved_sections,
        })
        plan["quality_score"] = quality_score
        plan["quality_issues"] = quality_issues
        logger.info(
            "[SitePlanner] Punteggio qualita: %.1f/100 (%d problemi rilevati)",
            quality_score, len(quality_issues),
        )

        # 10. Build planning prompt for AI injection
        plan["planning_prompt"] = self._build_planning_context(plan)

        # 11. Check for duplicate layout
        layout_hash = usage_tracker.compute_layout_hash(selected_components)
        if usage_tracker.is_duplicate_layout(layout_hash):
            logger.warning(
                "[SitePlanner] Layout duplicato rilevato (hash=%s). "
                "Il generatore potrebbe ri-selezionare i componenti.",
                layout_hash[:12],
            )
            plan["layout_duplicate"] = True
        else:
            plan["layout_duplicate"] = False

        logger.info(
            "[SitePlanner] Piano completato per '%s': %d sezioni, qualita %.1f/100",
            business_name, len(resolved_sections), quality_score,
        )
        return plan

    # ------------------------------------------------------------------
    # Section resolution
    # ------------------------------------------------------------------

    def _resolve_sections(
        self,
        user_sections: list[str],
        category: str,
    ) -> list[str]:
        """Ensure must-have sections are present and add recommended ones.

        Steps:
          1. Start with user's chosen sections (lowercased, deduplicated).
          2. Add must-have sections for the category that are missing.
          3. Add recommended sections that are missing (but mark them as
             suggestions -- they enrich the site without overwhelming).
          4. Sort all sections into the canonical visual flow order.

        Returns:
            Ordered list of section type strings.
        """
        # Normalize and deduplicate, preserving first occurrence
        seen = set()
        normalized: List[str] = []
        for s in user_sections:
            s_lower = s.lower().strip()
            if s_lower and s_lower not in seen:
                seen.add(s_lower)
                normalized.append(s_lower)

        # Must-have sections for this category
        must_have = quality_guide.get_must_have_sections(category)
        for section in must_have:
            if section not in seen:
                normalized.append(section)
                seen.add(section)
                logger.info(
                    "[SitePlanner] Aggiunta sezione obbligatoria '%s' per categoria '%s'",
                    section, category,
                )

        # Recommended sections: add only if user has fewer than 8 sections
        # to avoid overwhelming the page
        if len(normalized) < 8:
            recommended = quality_guide.get_recommended_sections(category)
            for section in recommended:
                if section not in seen and len(normalized) < 10:
                    normalized.append(section)
                    seen.add(section)
                    logger.info(
                        "[SitePlanner] Aggiunta sezione consigliata '%s' per categoria '%s'",
                        section, category,
                    )

        # Always ensure nav and footer are present
        if "nav" not in seen:
            normalized.insert(0, "nav")
            seen.add("nav")
        if "footer" not in seen:
            normalized.append("footer")
            seen.add("footer")

        # Sort into canonical flow order
        return _sort_sections(normalized)

    # ------------------------------------------------------------------
    # Component selection
    # ------------------------------------------------------------------

    def _select_components(
        self,
        sections: list[str],
        style_id: str | None,
        category: str,
    ) -> dict[str, str]:
        """Select the best component variant for each section.

        Selection priority:
          1. STYLE_VARIANT_POOL candidates for this style_id, scored by
             usage_tracker.score_candidates() (less-used = higher priority).
          2. STYLE_VARIANT_MAP deterministic fallback for this style_id.
          3. All available components in the catalog for this section type,
             scored by usage_tracker.
          4. First available variant as absolute fallback.

        Returns:
            Dict mapping section type -> variant_id.
        """
        # Lazy import to avoid circular dependency
        try:
            from app.services.databinding_generator import (
                STYLE_VARIANT_MAP,
                STYLE_VARIANT_POOL,
            )
        except ImportError:
            logger.warning(
                "[SitePlanner] Impossibile importare STYLE_VARIANT_MAP/POOL. "
                "Selezione componenti basata solo sul catalogo."
            )
            STYLE_VARIANT_MAP = {}
            STYLE_VARIANT_POOL = {}

        pool_map = STYLE_VARIANT_POOL.get(style_id, {}) if style_id else {}
        fixed_map = STYLE_VARIANT_MAP.get(style_id, {}) if style_id else {}

        selections: Dict[str, str] = {}

        for section in sections:
            selected = self._select_single_component(
                section, category, pool_map, fixed_map,
            )
            if selected:
                selections[section] = selected
            else:
                logger.warning(
                    "[SitePlanner] Nessun componente trovato per sezione '%s' "
                    "(style=%s, categoria=%s)",
                    section, style_id, category,
                )

        return selections

    def _select_single_component(
        self,
        section: str,
        category: str,
        pool_map: dict[str, list[str]],
        fixed_map: dict[str, str],
    ) -> str | None:
        """Select the best component variant for a single section.

        Uses priority scoring from UsageTracker to prefer less-used components.
        """
        # Priority 1: Pool candidates from style mapping
        pool_candidates = pool_map.get(section, [])
        if pool_candidates:
            scored = usage_tracker.score_candidates(
                pool_candidates, category,
            )
            if scored:
                best_id, best_score = scored[0]
                logger.debug(
                    "[SitePlanner] Sezione '%s': selezionato '%s' (punteggio=%.2f) "
                    "da pool di %d candidati",
                    section, best_id, best_score, len(scored),
                )
                return best_id

        # Priority 2: Fixed map deterministic fallback
        if section in fixed_map:
            return fixed_map[section]

        # Priority 3: All catalog components for this section type
        catalog_results = catalog.search_components(section)
        if catalog_results:
            candidate_ids = [c["variant_id"] for c in catalog_results]
            scored = usage_tracker.score_candidates(candidate_ids, category)
            if scored:
                best_id, best_score = scored[0]
                logger.debug(
                    "[SitePlanner] Sezione '%s': selezionato '%s' (punteggio=%.2f) "
                    "dal catalogo (%d varianti disponibili)",
                    section, best_id, best_score, len(scored),
                )
                return best_id

        # Priority 4: Absolute fallback -- first available from catalog
        if catalog_results:
            return catalog_results[0]["variant_id"]

        return None

    # ------------------------------------------------------------------
    # Missing info detection
    # ------------------------------------------------------------------

    def _identify_missing_info(
        self,
        sections: list[str],
        category: str,
        business_description: str,
        contact_info: dict | None,
    ) -> list[str]:
        """Identify what information the user hasn't provided but we need.

        Checks both section-specific data needs and category-specific extras.
        Uses simple heuristics on the business description to determine
        what's already implicitly provided.
        """
        missing: List[str] = []
        description_lower = business_description.lower() if business_description else ""
        contact = contact_info or {}

        # Check section-specific data needs
        for section in sections:
            needs = _SECTION_DATA_NEEDS.get(section, [])
            for need in needs:
                if self._is_info_missing(
                    need, description_lower, contact,
                ):
                    if need not in missing:
                        missing.append(need)

        # Check category-specific extra needs
        category_needs = _CATEGORY_EXTRA_NEEDS.get(category, [])
        for need in category_needs:
            if self._is_info_missing(need, description_lower, contact):
                if need not in missing:
                    missing.append(need)

        # Owner rules: enforce mandatory photo/video checks
        owner_photos = OWNER_RULES.get("mandatory_checks", {}).get("photos", {})
        if owner_photos.get("severity") == "critical":
            for section in owner_photos.get("sections_requiring_photos", []):
                photo_need = f"{section}_photo" if section != "gallery" else "gallery_photos"
                if section in sections and photo_need not in missing:
                    # Always flag photos as needed — let the questioner ask
                    missing.append(photo_need)

        if OWNER_RULES.get("mandatory_checks", {}).get("video", {}).get("ask_always"):
            if "presentation_video" not in missing:
                missing.append("presentation_video")

        return missing

    def _is_info_missing(
        self,
        need: str,
        description_lower: str,
        contact: dict,
    ) -> bool:
        """Heuristic check: is this piece of info missing from user input?

        Returns True if the info is likely NOT provided by the user.
        """
        # Contact-related needs: check contact_info dict
        if need == "email":
            return not contact.get("email")
        if need == "phone":
            return not contact.get("phone") and not contact.get("telefono")
        if need == "address":
            return not contact.get("address") and not contact.get("indirizzo")

        # Keyword-based detection in description
        keyword_map: Dict[str, List[str]] = {
            "menu_items": ["menu", "piatti", "cucina", "specialita", "ricette"],
            "business_hours": ["orari", "aperto", "chiuso", "ore", "orario"],
            "reservation_system": ["prenotazione", "prenota", "reservation"],
            "gallery_photos": ["foto", "immagini", "gallery", "galleria"],
            "customer_reviews": ["recensioni", "feedback", "opinioni", "testimonianze"],
            "team_members": ["team", "squadra", "staff", "personale", "chef"],
            "pricing_plans": ["prezzi", "prezzo", "costo", "piano", "abbonamento"],
            "company_stats": ["anni", "clienti", "progetti", "numeri"],
            "product_screenshot": ["screenshot", "demo", "prodotto", "app"],
            "feature_list": ["funzionalita", "caratteristiche", "features"],
            "project_images": ["portfolio", "progetti", "lavori", "opere"],
            "project_descriptions": ["progetto", "case study", "lavoro"],
            "product_catalog": ["catalogo", "prodotti", "articoli", "collezione"],
            "shipping_info": ["spedizione", "consegna", "shipping"],
            "return_policy": ["reso", "rimborso", "garanzia", "restituzione"],
            "client_logos": ["clienti", "partner", "collaborazioni", "brand"],
            "case_studies": ["case study", "risultati", "progetto"],
            "event_date": ["data", "quando", "giorno", "date"],
            "event_location": ["luogo", "dove", "location", "sede"],
            "speaker_list": ["speaker", "relatori", "artisti", "ospiti"],
            "ticket_prices": ["biglietto", "ticket", "ingresso", "prezzo"],
            "faq_items": ["domande", "faq", "risposte"],
            "blog_articles": ["articoli", "post", "blog", "contenuti"],
            "event_schedule": ["programma", "agenda", "scaletta", "schedule"],
            "author_bio": ["autore", "chi sono", "bio", "about me"],
            "article_archive": ["archivio", "articoli", "pubblicazioni"],
            "service_list": ["servizi", "cosa facciamo", "offriamo", "soluzioni"],
            "partner_logos": ["partner", "collaborazioni", "clienti"],
            "booking_availability": ["prenotazione", "disponibilita", "booking"],
        }

        # Info considered "present" if keywords appear in description
        keywords = keyword_map.get(need, [])
        if keywords:
            for kw in keywords:
                if kw in description_lower:
                    return False  # User mentioned it, not missing
            return True  # Keywords not found, info is likely missing

        # Generic needs (headline, subtitle, hero_image) -- always let AI handle
        if need in ("headline", "subtitle", "hero_image", "company_story", "team_photo"):
            return False  # AI generates these, not truly "missing"

        return True  # Unknown need: assume missing

    # ------------------------------------------------------------------
    # Color palette hint
    # ------------------------------------------------------------------

    def _build_color_palette_hint(
        self,
        primary_color: str | None,
        category: str,
    ) -> dict[str, str]:
        """Build a basic color palette hint for the AI.

        If the user provided a primary color, build around it.
        Otherwise, return empty dict and let the AI decide freely.
        The actual palette generation (harmony system) happens in the
        databinding_generator, so this is just a hint.
        """
        if primary_color:
            return {
                "primary": primary_color,
                "secondary": "",
                "accent": "",
            }
        return {}

    # ------------------------------------------------------------------
    # Font pairing hint
    # ------------------------------------------------------------------

    def _get_font_pairing_hint(self, category: str) -> dict[str, str]:
        """Return a suggested font pairing based on category.

        These are hints -- the AI theme generation may override them.
        Selected from the quality guide's font_style recommendations.
        """
        _CATEGORY_FONT_HINTS: Dict[str, Dict[str, str]] = {
            "restaurant": {"heading": "Playfair Display", "body": "DM Sans"},
            "saas": {"heading": "Space Grotesk", "body": "Inter"},
            "portfolio": {"heading": "Space Grotesk", "body": "Inter"},
            "ecommerce": {"heading": "Plus Jakarta Sans", "body": "Inter"},
            "business": {"heading": "Plus Jakarta Sans", "body": "Inter"},
            "blog": {"heading": "Playfair Display", "body": "Source Serif 4"},
            "event": {"heading": "Space Grotesk", "body": "DM Sans"},
            "custom": {"heading": "Sora", "body": "Inter"},
        }
        return _CATEGORY_FONT_HINTS.get(category, {"heading": "Sora", "body": "Inter"})

    # ------------------------------------------------------------------
    # Planning context builder (for AI prompt injection)
    # ------------------------------------------------------------------

    def _build_planning_context(self, plan: dict) -> str:
        """Build a context string from the plan for AI prompt injection.

        This string is appended to the AI generation prompts so Gemini
        knows about the architectural decisions we've already made.
        """
        category = plan.get("category", "custom")
        sections = plan.get("sections", [])

        # Get the quality guide's full planning prompt
        guide_prompt = quality_guide.get_planning_prompt(category, sections)

        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("SITE PLANNER - Piano Architetturale del Sito")
        lines.append("=" * 60)

        # Business context
        biz_name = plan.get("business_name", "")
        biz_desc = plan.get("business_description", "")
        if biz_name:
            lines.append(f"\nAttivita: {biz_name}")
        if biz_desc:
            lines.append(f"Descrizione: {biz_desc}")
        lines.append(f"Categoria: {category}")
        style_id = plan.get("style_id", "")
        if style_id:
            lines.append(f"Stile template: {style_id}")

        # Sections decided
        lines.append(f"\n### Sezioni pianificate ({len(sections)}):")
        for i, section in enumerate(sections, 1):
            component = plan.get("components", {}).get(section, "da assegnare")
            lines.append(f"  {i}. {section} -> {component}")

        # Animation strategy
        anim_strategy = plan.get("animation_strategy", "moderate")
        anim_description = _ANIMATION_STRATEGIES.get(anim_strategy, "")
        lines.append(f"\n### Strategia animazioni: {anim_strategy}")
        if anim_description:
            lines.append(f"  {anim_description}")

        # Color palette hint
        palette = plan.get("color_palette", {})
        if palette.get("primary"):
            lines.append(f"\n### Colore primario scelto dall'utente: {palette['primary']}")
            lines.append("  Genera una palette armonica attorno a questo colore.")

        # Font pairing hint
        fonts = plan.get("font_pairing", {})
        if fonts:
            lines.append(f"\n### Font suggeriti: heading={fonts.get('heading', '?')}, body={fonts.get('body', '?')}")
            lines.append("  Puoi variare ma mantieni lo stesso livello di personalita.")

        # Missing info
        missing = plan.get("missing_info", [])
        if missing:
            lines.append(f"\n### Informazioni mancanti ({len(missing)}):")
            lines.append("  L'utente NON ha fornito questi dati. Genera contenuti plausibili e realistici.")
            for item in missing:
                lines.append(f"  - {item}")

        # Owner rules (custom notes)
        custom_notes = OWNER_RULES.get("custom_notes", [])
        if custom_notes:
            lines.append("\n### Regole obbligatorie del proprietario:")
            for note in custom_notes:
                lines.append(f"  - {note}")

        # Owner rules: photo/video requirements
        photo_rule = OWNER_RULES.get("mandatory_checks", {}).get("photos", {}).get("rule", "")
        video_rule = OWNER_RULES.get("mandatory_checks", {}).get("video", {}).get("rule", "")
        if photo_rule or video_rule:
            lines.append("\n### Requisiti foto/video:")
            if photo_rule:
                lines.append(f"  FOTO: {photo_rule}")
            if video_rule:
                lines.append(f"  VIDEO: {video_rule}")

        # Quality score
        score = plan.get("quality_score", 0)
        issues = plan.get("quality_issues", [])
        lines.append(f"\n### Punteggio qualita attuale: {score:.0f}/100")
        if issues:
            critical = [i for i in issues if i.get("severity") == "critical"]
            high = [i for i in issues if i.get("severity") == "high"]
            if critical:
                lines.append("  Problemi CRITICI da risolvere:")
                for issue in critical:
                    lines.append(f"    - [{issue.get('section', '?')}] {issue.get('message', '')}")
            if high:
                lines.append("  Problemi IMPORTANTI:")
                for issue in high:
                    lines.append(f"    - [{issue.get('section', '?')}] {issue.get('message', '')}")

        lines.append("\n" + "=" * 60)

        # Append the full quality guide prompt
        lines.append("")
        lines.append(guide_prompt)

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------

site_planner = SitePlanner()
