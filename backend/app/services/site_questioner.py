"""
Site Questioner - Interactive questioning system for missing user info.

After the AI planner creates a site plan, this service analyzes what
information is missing and generates targeted questions for the user.
Users can answer questions or skip them (AI generates the content instead).

Question types:
  - text: free text input
  - image_upload: photo/image upload
  - choice: pick from options
  - toggle: yes/no toggle (can unlock follow-up text input)

All user-facing strings are in Italian.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Category alias map: Italian / alternate names -> canonical English category
# ---------------------------------------------------------------------------
CATEGORY_ALIASES: Dict[str, str] = {
    "ristorante": "restaurant",
    "tech": "saas",
    "corporate": "business",
    "studio_professionale": "business",
    "shop": "ecommerce",
    "creative": "portfolio",
    "bellezza": "portfolio",
    "fitness": "business",
    "salute": "business",
    "artigiani": "business",
    "agenzia": "saas",
    "evento": "event",
}

# Canonical category list (used for validation)
VALID_CATEGORIES = {"restaurant", "saas", "portfolio", "business", "ecommerce", "event", "blog"}


class SiteQuestioner:
    """Generates interactive questions based on site plan and user data."""

    # ------------------------------------------------------------------
    # Category-specific question templates
    # ------------------------------------------------------------------
    CATEGORY_QUESTIONS: Dict[str, List[Dict]] = {
        "restaurant": [
            {
                "id": "restaurant_gallery_photos",
                "section": "gallery",
                "field": "photos",
                "question_it": "Hai foto dei tuoi piatti da inserire nella galleria?",
                "type": "image_upload",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 1,
            },
            {
                "id": "restaurant_hours",
                "section": "contact",
                "field": "hours",
                "question_it": "Quali sono i tuoi orari di apertura?",
                "type": "text",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 1,
            },
            {
                "id": "restaurant_menu",
                "section": "menu",
                "field": "menu_items",
                "question_it": "Vuoi inserire il menu con i piatti e i prezzi?",
                "type": "toggle",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
            {
                "id": "restaurant_address",
                "section": "contact",
                "field": "address",
                "question_it": "Hai l'indirizzo del locale?",
                "type": "text",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 1,
            },
        ],
        "saas": [
            {
                "id": "saas_screenshots",
                "section": "hero",
                "field": "photos",
                "question_it": "Hai screenshot del tuo prodotto?",
                "type": "image_upload",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 1,
            },
            {
                "id": "saas_pricing",
                "section": "pricing",
                "field": "pricing_plans",
                "question_it": "Quali sono i piani tariffari? (nome, prezzo, caratteristiche)",
                "type": "text",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
            {
                "id": "saas_client_logos",
                "section": "clients",
                "field": "logos",
                "question_it": "Hai loghi di aziende clienti?",
                "type": "image_upload",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
        ],
        "portfolio": [
            {
                "id": "portfolio_project_images",
                "section": "gallery",
                "field": "photos",
                "question_it": "Hai immagini dei tuoi progetti da mostrare?",
                "type": "image_upload",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 1,
            },
            {
                "id": "portfolio_bio",
                "section": "about",
                "field": "text",
                "question_it": "Vuoi aggiungere una breve bio personale?",
                "type": "text",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
        ],
        "business": [
            {
                "id": "business_team_photos",
                "section": "team",
                "field": "photos",
                "question_it": "Hai foto del team?",
                "type": "image_upload",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
            {
                "id": "business_services_detail",
                "section": "services",
                "field": "services_text",
                "question_it": "Vuoi specificare i servizi offerti in dettaglio?",
                "type": "text",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
        ],
        "ecommerce": [
            {
                "id": "ecommerce_product_photos",
                "section": "products",
                "field": "photos",
                "question_it": "Hai foto dei prodotti?",
                "type": "image_upload",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 1,
            },
            {
                "id": "ecommerce_prices",
                "section": "products",
                "field": "prices_text",
                "question_it": "Vuoi inserire i prezzi dei prodotti?",
                "type": "text",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
        ],
        "event": [
            {
                "id": "event_date",
                "section": "hero",
                "field": "event_date",
                "question_it": "Qual \u00e8 la data dell'evento?",
                "type": "text",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 1,
            },
            {
                "id": "event_speaker_photos",
                "section": "speakers",
                "field": "photos",
                "question_it": "Hai foto dei relatori/artisti?",
                "type": "image_upload",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
            {
                "id": "event_schedule",
                "section": "schedule",
                "field": "schedule_text",
                "question_it": "Vuoi inserire il programma dell'evento?",
                "type": "text",
                "options": None,
                "default_action": "generate_ai",
                "required": False,
                "priority": 2,
            },
        ],
    }

    # ------------------------------------------------------------------
    # Common questions applicable to all categories
    # ------------------------------------------------------------------
    COMMON_QUESTIONS: List[Dict] = [
        {
            "id": "common_phone",
            "section": "contact",
            "field": "phone",
            "question_it": "Hai un numero di telefono da mostrare?",
            "type": "text",
            "options": None,
            "default_action": "generate_ai",
            "required": False,
            "priority": 2,
            "_condition": "needs_phone",
        },
        {
            "id": "common_email",
            "section": "contact",
            "field": "email",
            "question_it": "Hai un indirizzo email per i contatti?",
            "type": "text",
            "options": None,
            "default_action": "generate_ai",
            "required": False,
            "priority": 2,
            "_condition": "needs_email",
        },
        {
            "id": "common_social",
            "section": "contact",
            "field": "social_links",
            "question_it": "Vuoi inserire link ai social media?",
            "type": "text",
            "options": None,
            "default_action": "generate_ai",
            "required": False,
            "priority": 3,
            "_condition": None,
        },
        {
            "id": "common_testimonials",
            "section": "testimonials",
            "field": "testimonials_text",
            "question_it": "Hai testimonianze dei clienti?",
            "type": "text",
            "options": None,
            "default_action": "generate_ai",
            "required": False,
            "priority": 2,
            "_condition": "needs_testimonials",
        },
        # ── Photo & Video common questions ──
        {
            "id": "common_hero_photo",
            "section": "hero",
            "field": "photos",
            "question_it": "Vuoi caricare una foto/immagine per l'intestazione del sito?",
            "type": "image_upload",
            "options": None,
            "default_action": "generate_ai",
            "required": False,
            "priority": 1,
            "_condition": "needs_hero_photo",
        },
        {
            "id": "common_about_photo",
            "section": "about",
            "field": "photos",
            "question_it": "Hai una foto del tuo team, ufficio o attivita da inserire nella sezione 'Chi siamo'?",
            "type": "image_upload",
            "options": None,
            "default_action": "generate_ai",
            "required": False,
            "priority": 1,
            "_condition": "needs_about_photo",
        },
        {
            "id": "common_gallery_photos",
            "section": "gallery",
            "field": "photos",
            "question_it": "Vuoi caricare foto per la galleria? (Puoi caricare piu immagini)",
            "type": "image_upload",
            "options": None,
            "default_action": "generate_ai",
            "required": False,
            "priority": 1,
            "_condition": "needs_gallery",
        },
        {
            "id": "common_video",
            "section": "hero",
            "field": "video_url",
            "question_it": "Hai un video di presentazione? (URL YouTube o Vimeo)",
            "type": "text",
            "options": None,
            "default_action": "skip",
            "required": False,
            "priority": 2,
            "_condition": None,
        },
    ]

    # ------------------------------------------------------------------
    # Section ordering for deterministic sort (lower = earlier)
    # ------------------------------------------------------------------
    SECTION_ORDER: Dict[str, int] = {
        "hero": 0,
        "about": 1,
        "services": 2,
        "menu": 3,
        "products": 3,
        "pricing": 3,
        "gallery": 4,
        "team": 5,
        "speakers": 5,
        "schedule": 6,
        "testimonials": 7,
        "clients": 8,
        "contact": 9,
    }

    # ------------------------------------------------------------------
    # Photo choice labels (Italian) for interactive photo selection
    # ------------------------------------------------------------------
    PHOTO_CHOICE_LABELS: Dict[str, str] = {
        "hero": "Sezione Hero (immagine principale)",
        "about": "Chi Siamo",
        "gallery": "Gallery / Portfolio",
        "team": "Il Nostro Team",
        "services": "Servizi",
        "blog": "Blog",
        "contact": "Contatti",
        "products": "Prodotti",
        "menu": "Menu",
        "testimonials": "Testimonianze",
        "features": "Funzionalita'",
        "speakers": "Relatori",
    }

    @classmethod
    def get_photo_choice_labels(cls) -> Dict[str, str]:
        """Return section_type -> Italian label mapping for photo choice UI."""
        return dict(cls.PHOTO_CHOICE_LABELS)

    @classmethod
    def get_photo_choice_label(cls, section_type: str) -> str:
        """Return the Italian label for a given section type."""
        return cls.PHOTO_CHOICE_LABELS.get(
            section_type, section_type.replace("_", " ").title()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_completeness(
        self,
        site_plan: Dict[str, Any],
        user_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Analyze what info is missing and generate questions.

        Args:
            site_plan: The SitePlan dict from SitePlanner with keys:
                - sections: list of section types
                - components: dict of section -> variant_id
                - category: business category
                - missing_info: list of missing info types
            user_data: What the user already provided:
                - business_name: str
                - business_description: str
                - contact_info: dict with phone, email, address
                - photo_urls: list of uploaded photos
                - logo_url: str

        Returns:
            List of Question dicts, sorted by priority (1=highest)
            then by section order.
        """
        site_plan = site_plan or {}
        user_data = user_data or {}

        category = self._normalize_category(site_plan.get("category", ""))
        sections = site_plan.get("sections", [])

        logger.info(
            "Analyzing completeness for category=%s, sections=%s",
            category,
            sections,
        )

        questions: List[Dict[str, Any]] = []

        # 1. Category-specific questions
        questions.extend(
            self._get_category_questions(category, sections, user_data)
        )

        # 2. Common questions (phone, email, social, testimonials)
        questions.extend(
            self._get_common_questions(sections, user_data)
        )

        # 3. Sort: priority ASC, then section order ASC
        questions.sort(
            key=lambda q: (
                q.get("priority", 99),
                self.SECTION_ORDER.get(q.get("section", ""), 99),
            )
        )

        logger.info(
            "Generated %d questions (priorities: %s)",
            len(questions),
            [q["priority"] for q in questions],
        )

        return questions

    def apply_answers(
        self,
        site_plan: Dict[str, Any],
        answers: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply user answers to the site plan.

        Answered questions get stored in ``site_plan["user_content"]``
        keyed by section name. Unanswered / skipped questions are left
        for the AI generation pipeline to handle.

        Args:
            site_plan: Current site plan dict.
            answers: Dict mapping question IDs to answer values.
                e.g. {"restaurant_hours": "9-18",
                       "restaurant_gallery_photos": ["data:image/..."]}

        Returns:
            Updated site plan with ``user_content`` field populated.
        """
        if not answers:
            logger.info("No answers provided, returning site plan unchanged")
            return site_plan

        user_content: Dict[str, Dict[str, Any]] = site_plan.get("user_content", {})

        # Build a lookup of question_id -> question template
        question_lookup = self._build_question_lookup(
            self._normalize_category(site_plan.get("category", ""))
        )

        applied_count = 0

        for question_id, value in answers.items():
            # Skip empty / None answers
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            if isinstance(value, list) and len(value) == 0:
                continue

            template = question_lookup.get(question_id)
            if template is None:
                logger.warning(
                    "Unknown question_id '%s' in answers, skipping", question_id
                )
                continue

            section = template["section"]
            field = template["field"]

            if section not in user_content:
                user_content[section] = {}

            # Map field names to the user_content structure
            if field == "photos" or field == "logos":
                user_content[section]["photos"] = (
                    value if isinstance(value, list) else [value]
                )
            elif field == "menu_items":
                # Toggle + text: value can be True/False or a string with menu content
                if isinstance(value, bool):
                    user_content[section]["include_menu"] = value
                else:
                    user_content[section]["menu_text"] = value
                    user_content[section]["include_menu"] = True
            elif field == "text":
                user_content[section]["custom_text"] = value
            elif field in ("hours", "address", "phone", "email", "social_links"):
                user_content[section][field] = value
            elif field == "event_date":
                user_content[section]["event_date"] = value
            elif field in ("pricing_plans", "prices_text", "services_text",
                           "schedule_text", "testimonials_text"):
                user_content[section][field] = value
            else:
                # Generic fallback
                user_content[section][field] = value

            applied_count += 1
            logger.debug(
                "Applied answer: question=%s -> section=%s, field=%s",
                question_id, section, field,
            )

        site_plan["user_content"] = user_content

        logger.info(
            "Applied %d/%d answers to site plan (sections with content: %s)",
            applied_count,
            len(answers),
            list(user_content.keys()),
        )

        return site_plan

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize_category(self, category: str) -> str:
        """Resolve aliases and normalize category to canonical English name."""
        if not category:
            return ""
        cat = category.strip().lower()
        resolved = CATEGORY_ALIASES.get(cat, cat)
        if resolved not in VALID_CATEGORIES:
            logger.warning(
                "Category '%s' (resolved: '%s') not in known categories, "
                "will only generate common questions",
                category,
                resolved,
            )
        return resolved

    def _has_info(self, user_data: Dict[str, Any], field: str) -> bool:
        """Check if user already provided this info.

        Looks in top-level user_data fields and nested contact_info.
        """
        # Direct top-level check
        val = user_data.get(field)
        if val:
            if isinstance(val, str) and val.strip():
                return True
            if isinstance(val, list) and len(val) > 0:
                return True

        # Check inside contact_info dict
        contact_info = user_data.get("contact_info", {})
        if isinstance(contact_info, dict):
            val = contact_info.get(field)
            if val and isinstance(val, str) and val.strip():
                return True

        # Check photo_urls for image fields
        if field == "photos":
            photo_urls = user_data.get("photo_urls", [])
            if isinstance(photo_urls, list) and len(photo_urls) > 0:
                return True

        return False

    def _section_present(self, sections: List[str], target: str) -> bool:
        """Check if a section (or related section) is in the plan.

        Uses loose matching: 'contatti' matches 'contact',
        'galleria' matches 'gallery', etc.
        """
        section_aliases: Dict[str, List[str]] = {
            "contact": ["contact", "contatti", "contatto", "footer"],
            "gallery": ["gallery", "galleria", "portfolio", "progetti"],
            "testimonials": ["testimonials", "testimonianze", "reviews", "recensioni"],
            "hero": ["hero", "header", "banner"],
            "about": ["about", "chi_siamo", "chi-siamo", "about_us"],
            "services": ["services", "servizi"],
            "menu": ["menu", "piatti"],
            "products": ["products", "prodotti"],
            "pricing": ["pricing", "prezzi", "piani"],
            "team": ["team", "squadra"],
            "speakers": ["speakers", "relatori", "artisti"],
            "schedule": ["schedule", "programma", "agenda"],
            "clients": ["clients", "clienti", "partner"],
        }

        aliases = section_aliases.get(target, [target])
        normalized = [s.strip().lower() for s in sections]
        return any(alias in normalized for alias in aliases)

    def _get_category_questions(
        self,
        category: str,
        sections: List[str],
        user_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Get category-specific questions filtered by what's already provided."""
        templates = self.CATEGORY_QUESTIONS.get(category, [])
        if not templates:
            logger.debug("No category-specific questions for '%s'", category)
            return []

        questions: List[Dict[str, Any]] = []

        for tmpl in templates:
            # Skip if the relevant section is not in the plan
            # (exception: contact section is almost always present)
            section = tmpl["section"]
            if section != "contact" and not self._section_present(sections, section):
                logger.debug(
                    "Skipping question '%s': section '%s' not in plan",
                    tmpl["id"],
                    section,
                )
                continue

            # Skip if user already provided this info
            if self._has_info(user_data, tmpl["field"]):
                logger.debug(
                    "Skipping question '%s': user already provided '%s'",
                    tmpl["id"],
                    tmpl["field"],
                )
                continue

            # Build a clean question dict (without internal keys)
            questions.append({
                "id": tmpl["id"],
                "section": tmpl["section"],
                "field": tmpl["field"],
                "question_it": tmpl["question_it"],
                "type": tmpl["type"],
                "options": tmpl.get("options"),
                "default_action": tmpl["default_action"],
                "required": tmpl["required"],
                "priority": tmpl["priority"],
            })

        return questions

    def _get_common_questions(
        self,
        sections: List[str],
        user_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Get common questions applicable to this site."""
        questions: List[Dict[str, Any]] = []

        for tmpl in self.COMMON_QUESTIONS:
            condition = tmpl.get("_condition")

            # Evaluate conditions
            if condition == "needs_phone":
                # Only ask if contact section exists and no phone provided
                if not self._section_present(sections, "contact"):
                    continue
                if self._has_info(user_data, "phone"):
                    continue

            elif condition == "needs_email":
                # Only ask if contact section exists and no email provided
                if not self._section_present(sections, "contact"):
                    continue
                if self._has_info(user_data, "email"):
                    continue

            elif condition == "needs_testimonials":
                # Only ask if testimonials section is in the plan
                if not self._section_present(sections, "testimonials"):
                    continue

            elif condition == "needs_hero_photo":
                # Only ask if hero section exists and no photos uploaded
                if not self._section_present(sections, "hero"):
                    continue
                if user_data.get("photo_urls"):
                    continue

            elif condition == "needs_about_photo":
                # Only ask if about section exists
                if not self._section_present(sections, "about"):
                    continue
                if user_data.get("photo_urls") and len(user_data["photo_urls"]) >= 2:
                    continue

            elif condition == "needs_gallery":
                # Only ask if gallery section exists
                if not self._section_present(sections, "gallery"):
                    continue

            # Social links: always ask (no condition), but skip if already provided
            if tmpl["field"] == "social_links" and self._has_info(user_data, "social_links"):
                continue

            # Build clean question dict
            questions.append({
                "id": tmpl["id"],
                "section": tmpl["section"],
                "field": tmpl["field"],
                "question_it": tmpl["question_it"],
                "type": tmpl["type"],
                "options": tmpl.get("options"),
                "default_action": tmpl["default_action"],
                "required": tmpl["required"],
                "priority": tmpl["priority"],
            })

        return questions

    def _build_question_lookup(self, category: str) -> Dict[str, Dict]:
        """Build a flat lookup of question_id -> question template.

        Merges category-specific and common questions.
        """
        lookup: Dict[str, Dict] = {}

        # Category-specific
        for tmpl in self.CATEGORY_QUESTIONS.get(category, []):
            lookup[tmpl["id"]] = tmpl

        # Common
        for tmpl in self.COMMON_QUESTIONS:
            lookup[tmpl["id"]] = tmpl

        return lookup


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------
site_questioner = SiteQuestioner()
