"""
Data-Binding Generator - Kimi produces JSON data, templates produce HTML.

Replaces SwarmGenerator for initial site generation. Kimi only generates
structured JSON (colors, texts, component choices). Pre-built HTML templates
with placeholders are assembled by TemplateAssembler.

Benefits:
- Consistent quality (pre-tested templates)
- GSAP animations on every site
- Faster generation (~40-60s vs 2-3 min)
- Lower token costs (~30% less)
- Diversified designs (multiple template variants)

Pipeline:
  Step 1 (parallel): Kimi → JSON {colors, fonts, mood}
  Step 2 (parallel): Kimi → JSON {texts for all sections}
  Step 3: Kimi → JSON {component variant selection}
  Step 4: TemplateAssembler → complete HTML
"""

import asyncio
import json
import logging
import re
import time
from typing import Dict, Any, Optional, List, Callable

from app.services.kimi_client import kimi
from app.services.template_assembler import assembler as template_assembler
from app.services.sanitizer import sanitize_input, sanitize_output
from app.services.quality_control import qc_pipeline

# Design knowledge (ChromaDB) - graceful fallback if not available
try:
    from app.services.design_knowledge import get_creative_context, get_collection_stats
    _has_design_knowledge = True
except Exception:
    _has_design_knowledge = False

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[int, str, Optional[Dict[str, Any]]], None]]

# =========================================================
# Deterministic style → component variant mapping.
# Each frontend template style maps to curated component variants
# ensuring visually distinct sites for every template choice.
# =========================================================
STYLE_VARIANT_MAP: Dict[str, Dict[str, str]] = {
    # --- Restaurant ---
    "restaurant-elegant": {
        "hero": "hero-classic-01",
        "about": "about-magazine-01",
        "services": "services-alternating-rows-01",
        "gallery": "gallery-spotlight-01",
        "testimonials": "testimonials-spotlight-01",
        "contact": "contact-minimal-01",
        "footer": "footer-centered-01",
    },
    "restaurant-cozy": {
        "hero": "hero-organic-01",
        "about": "about-split-scroll-01",
        "services": "services-icon-list-01",
        "gallery": "gallery-masonry-01",
        "testimonials": "testimonials-card-stack-01",
        "contact": "contact-card-01",
        "footer": "footer-multi-col-01",
    },
    "restaurant-modern": {
        "hero": "hero-zen-01",
        "about": "about-bento-01",
        "services": "services-tabs-01",
        "gallery": "gallery-filmstrip-01",
        "testimonials": "testimonials-marquee-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-minimal-02",
    },
    # --- SaaS / Landing Page ---
    "saas-gradient": {
        "hero": "hero-gradient-03",
        "about": "about-timeline-02",
        "services": "services-hover-reveal-01",
        "features": "features-bento-grid-01",
        "testimonials": "testimonials-marquee-01",
        "cta": "cta-gradient-animated-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-gradient-01",
    },
    "saas-clean": {
        "hero": "hero-centered-02",
        "about": "about-alternating-01",
        "services": "services-cards-grid-01",
        "features": "features-icons-grid-01",
        "testimonials": "testimonials-grid-01",
        "cta": "cta-banner-01",
        "contact": "contact-form-01",
        "footer": "footer-sitemap-01",
    },
    "saas-dark": {
        "hero": "hero-dark-bold-01",
        "about": "about-split-cards-01",
        "services": "services-bento-02",
        "features": "features-hover-cards-01",
        "testimonials": "testimonials-masonry-01",
        "contact": "contact-minimal-02",
        "footer": "footer-mega-01",
    },
    # --- Portfolio ---
    "portfolio-gallery": {
        "hero": "hero-editorial-01",
        "about": "about-image-showcase-01",
        "gallery": "gallery-masonry-01",
        "services": "services-minimal-list-01",
        "testimonials": "testimonials-grid-01",
        "contact": "contact-minimal-01",
        "footer": "footer-minimal-02",
    },
    "portfolio-minimal": {
        "hero": "hero-zen-01",
        "about": "about-alternating-01",
        "gallery": "gallery-lightbox-01",
        "contact": "contact-minimal-02",
        "footer": "footer-centered-01",
    },
    "portfolio-creative": {
        "hero": "hero-brutalist-01",
        "about": "about-bento-01",
        "gallery": "gallery-spotlight-01",
        "services": "services-hover-expand-01",
        "contact": "contact-card-01",
        "footer": "footer-gradient-01",
    },
    # --- E-commerce / Shop ---
    "ecommerce-modern": {
        "hero": "hero-split-01",
        "about": "about-image-showcase-01",
        "services": "services-cards-grid-01",
        "gallery": "gallery-masonry-01",
        "testimonials": "testimonials-carousel-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-multi-col-01",
    },
    "ecommerce-luxury": {
        "hero": "hero-classic-01",
        "about": "about-magazine-01",
        "services": "services-alternating-rows-01",
        "gallery": "gallery-spotlight-01",
        "testimonials": "testimonials-spotlight-01",
        "contact": "contact-minimal-01",
        "footer": "footer-centered-01",
    },
    # --- Business ---
    "business-corporate": {
        "hero": "hero-split-01",
        "about": "about-alternating-01",
        "services": "services-cards-grid-01",
        "features": "features-comparison-01",
        "testimonials": "testimonials-carousel-01",
        "contact": "contact-form-01",
        "footer": "footer-mega-01",
    },
    "business-trust": {
        "hero": "hero-classic-01",
        "about": "about-timeline-01",
        "services": "services-process-steps-01",
        "team": "team-grid-01",
        "testimonials": "testimonials-spotlight-01",
        "contact": "contact-split-map-01",
        "footer": "footer-sitemap-01",
    },
    "business-fresh": {
        "hero": "hero-gradient-03",
        "about": "about-split-cards-01",
        "services": "services-hover-expand-01",
        "features": "features-alternating-01",
        "testimonials": "testimonials-carousel-01",
        "cta": "cta-split-image-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-multi-col-01",
    },
    # --- Blog / Magazine ---
    "blog-editorial": {
        "hero": "hero-editorial-01",
        "about": "about-alternating-01",
        "services": "services-minimal-list-01",
        "gallery": "gallery-lightbox-01",
        "contact": "contact-card-01",
        "footer": "footer-sitemap-01",
    },
    "blog-dark": {
        "hero": "hero-neon-01",
        "about": "about-split-cards-01",
        "services": "services-hover-reveal-01",
        "gallery": "gallery-filmstrip-01",
        "contact": "contact-minimal-02",
        "footer": "footer-gradient-01",
    },
    # --- Evento / Community ---
    "event-vibrant": {
        "hero": "hero-animated-shapes-01",
        "about": "about-bento-01",
        "services": "services-tabs-01",
        "team": "team-carousel-01",
        "cta": "cta-gradient-animated-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-gradient-01",
    },
    "event-minimal": {
        "hero": "hero-centered-02",
        "about": "about-timeline-01",
        "services": "services-process-steps-01",
        "team": "team-grid-01",
        "contact": "contact-form-01",
        "footer": "footer-minimal-02",
    },
}


class DataBindingGenerator:
    def __init__(self):
        self.kimi = kimi
        self.assembler = template_assembler

    # =========================================================
    # Step 1: Generate Theme JSON (colors, fonts)
    # =========================================================
    async def _generate_theme(
        self,
        business_name: str,
        business_description: str,
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Kimi returns JSON with color palette and fonts."""
        style_hint = ""
        if style_preferences:
            if style_preferences.get("primary_color"):
                style_hint += f"Primary color requested: {style_preferences['primary_color']}. "
            if style_preferences.get("mood"):
                style_hint += f"Mood/style: {style_preferences['mood']}. "

        prompt = f"""You are an award-winning UI designer. Generate a STUNNING color palette and typography for a website.
Return ONLY valid JSON, no markdown, no explanation.

BUSINESS: {business_name} - {business_description[:500]}
{style_hint}

Return this exact JSON structure:
{{
  "primary_color": "#hex",
  "secondary_color": "#hex",
  "accent_color": "#hex",
  "bg_color": "#hex",
  "bg_alt_color": "#hex",
  "text_color": "#hex",
  "text_muted_color": "#hex",
  "font_heading": "Google Font Name",
  "font_heading_url": "FontName:wght@400;600;700;800",
  "font_body": "Google Font Name",
  "font_body_url": "FontName:wght@400;500;600"
}}

DESIGN RULES:
- Create a BOLD, MEMORABLE palette - never boring defaults like plain blue/gray
- Use modern color trends: deep purples, warm ambers, rich teals, vibrant corals
- Primary should be saturated and striking, accent should create visual pop
- WCAG AA contrast between text and bg colors (minimum 4.5:1 ratio)
- bg_color: prefer rich tones (deep navy, warm cream, soft sage) over plain white/black
- bg_alt_color: subtle shift from bg_color for section alternation
- Font pairing: heading font should have CHARACTER (Playfair Display, Sora, Space Grotesk, Clash Display, Cabinet Grotesk, Outfit, DM Serif Display, Fraunces, Epilogue)
- Body font: clean and readable (Inter, DM Sans, Plus Jakarta Sans, Nunito Sans, Source Sans 3)
- NEVER use default Inter for headings - pick something with personality
- Return ONLY the JSON object"""

        if reference_image_url:
            result = await self.kimi.call_with_image(
                prompt=prompt, image_url=reference_image_url,
                max_tokens=500, thinking=False, timeout=60.0,
            )
        else:
            result = await self.kimi.call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500, thinking=False, timeout=60.0,
            )

        if result.get("success"):
            try:
                theme = self._extract_json(result["content"])
                result["parsed"] = theme
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[DataBinding] Theme JSON parse failed: {e}, using fallback")
                result["parsed"] = self._fallback_theme(style_preferences)
        else:
            result["parsed"] = self._fallback_theme(style_preferences)

        return result

    # =========================================================
    # Step 2: Generate Texts JSON (all section content)
    # =========================================================
    async def _generate_texts(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        contact_info: Optional[Dict[str, str]] = None,
        creative_context: str = "",
    ) -> Dict[str, Any]:
        """Kimi returns JSON with all text content for every section."""
        contact_str = ""
        if contact_info:
            contact_str = "CONTACT INFO: " + ", ".join(f"{k}: {v}" for k, v in contact_info.items())

        sections_str = ", ".join(sections)

        # Inject creative context from design knowledge base
        knowledge_hint = ""
        if creative_context:
            knowledge_hint = f"\n\nDESIGN KNOWLEDGE (use these insights for better copy):\n{creative_context[:1500]}\n"

        prompt = f"""You are a world-class Italian copywriter creating text for a stunning, award-winning website.{knowledge_hint}
Your text must be BOLD, EVOCATIVE, and EMOTIONALLY COMPELLING - never generic or corporate.
Return ONLY valid JSON, no markdown.

BUSINESS: {business_name}
DESCRIPTION: {business_description[:800]}
SECTIONS NEEDED: {sections_str}
{contact_str}

CREATIVE WRITING RULES:
- Hero headline: MAX 6 words, powerful and memorable. Use strong verbs, evoke emotion.
  GOOD: "Dove il Gusto Incontra l'Arte" / "Il Futuro Inizia Qui"
  BAD: "Benvenuti nel Nostro Sito" / "La Nostra Azienda"
- Subtitles: Poetic but clear, 1-2 sentences max. Create intrigue.
- Service descriptions: Benefit-focused, not feature-focused. What does the customer FEEL?
- Testimonials: Sound REAL and specific, not generic praise.
- Use power words: esclusivo, rivoluzionario, straordinario, autentico, artigianale
- Vary sentence rhythm: mix short punchy lines with longer flowing ones.
- Every text should make the reader FEEL something.

Return this JSON (include only the sections listed above):
{{
  "meta": {{
    "title": "Page title (max 60 chars)",
    "description": "Meta description (max 155 chars)",
    "og_title": "OG title",
    "og_description": "OG description"
  }},
  "hero": {{
    "HERO_TITLE": "Headline impattante (max 8 parole)",
    "HERO_SUBTITLE": "Sottotitolo (2-3 frasi)",
    "HERO_CTA_TEXT": "Testo bottone CTA",
    "HERO_CTA_URL": "#contact",
    "HERO_IMAGE_URL": "https://placehold.co/800x600/{{primary_color_no_hash}}/white?text={business_name}",
    "HERO_IMAGE_ALT": "Descrizione immagine"
  }},
  "about": {{
    "ABOUT_TITLE": "Titolo sezione",
    "ABOUT_SUBTITLE": "Sottotitolo",
    "ABOUT_TEXT": "2-4 frasi sulla storia/missione",
    "ABOUT_HIGHLIGHT_1": "Fatto chiave 1",
    "ABOUT_HIGHLIGHT_2": "Fatto chiave 2",
    "ABOUT_HIGHLIGHT_3": "Fatto chiave 3",
    "ABOUT_HIGHLIGHT_NUM_1": "25",
    "ABOUT_HIGHLIGHT_NUM_2": "500",
    "ABOUT_HIGHLIGHT_NUM_3": "98"
  }},
  "services": {{
    "SERVICES_TITLE": "Titolo sezione",
    "SERVICES_SUBTITLE": "Sottotitolo",
    "SERVICES": [
      {{"SERVICE_ICON": "emoji", "SERVICE_TITLE": "Nome servizio", "SERVICE_DESCRIPTION": "Descrizione breve"}},
      {{"SERVICE_ICON": "emoji", "SERVICE_TITLE": "Nome servizio", "SERVICE_DESCRIPTION": "Descrizione breve"}},
      {{"SERVICE_ICON": "emoji", "SERVICE_TITLE": "Nome servizio", "SERVICE_DESCRIPTION": "Descrizione breve"}}
    ]
  }},
  "features": {{
    "FEATURES_TITLE": "Titolo sezione",
    "FEATURES_SUBTITLE": "Sottotitolo",
    "FEATURES": [
      {{"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"}},
      {{"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"}},
      {{"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"}},
      {{"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"}},
      {{"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"}},
      {{"FEATURE_ICON": "emoji", "FEATURE_TITLE": "Feature", "FEATURE_DESCRIPTION": "Descrizione breve"}}
    ]
  }},
  "testimonials": {{
    "TESTIMONIALS_TITLE": "Titolo sezione",
    "TESTIMONIALS": [
      {{"TESTIMONIAL_TEXT": "Citazione", "TESTIMONIAL_AUTHOR": "Nome", "TESTIMONIAL_ROLE": "Ruolo", "TESTIMONIAL_INITIAL": "N"}},
      {{"TESTIMONIAL_TEXT": "Citazione", "TESTIMONIAL_AUTHOR": "Nome", "TESTIMONIAL_ROLE": "Ruolo", "TESTIMONIAL_INITIAL": "N"}},
      {{"TESTIMONIAL_TEXT": "Citazione", "TESTIMONIAL_AUTHOR": "Nome", "TESTIMONIAL_ROLE": "Ruolo", "TESTIMONIAL_INITIAL": "N"}}
    ]
  }},
  "cta": {{
    "CTA_TITLE": "Headline CTA",
    "CTA_SUBTITLE": "Testo supporto",
    "CTA_BUTTON_TEXT": "Testo bottone",
    "CTA_BUTTON_URL": "#contact"
  }},
  "contact": {{
    "CONTACT_TITLE": "Titolo sezione",
    "CONTACT_SUBTITLE": "Sottotitolo",
    "CONTACT_ADDRESS": "indirizzo o vuoto",
    "CONTACT_PHONE": "telefono o vuoto",
    "CONTACT_EMAIL": "email o vuoto"
  }},
  "gallery": {{
    "GALLERY_TITLE": "Titolo galleria",
    "GALLERY_SUBTITLE": "Sottotitolo",
    "GALLERY_ITEMS": [
      {{"GALLERY_IMAGE_URL": "https://placehold.co/600x400/eee/999?text=Foto+1", "GALLERY_IMAGE_ALT": "descrizione", "GALLERY_CAPTION": "Didascalia"}},
      {{"GALLERY_IMAGE_URL": "https://placehold.co/600x400/eee/999?text=Foto+2", "GALLERY_IMAGE_ALT": "descrizione", "GALLERY_CAPTION": "Didascalia"}},
      {{"GALLERY_IMAGE_URL": "https://placehold.co/600x400/eee/999?text=Foto+3", "GALLERY_IMAGE_ALT": "descrizione", "GALLERY_CAPTION": "Didascalia"}},
      {{"GALLERY_IMAGE_URL": "https://placehold.co/600x400/eee/999?text=Foto+4", "GALLERY_IMAGE_ALT": "descrizione", "GALLERY_CAPTION": "Didascalia"}},
      {{"GALLERY_IMAGE_URL": "https://placehold.co/600x400/eee/999?text=Foto+5", "GALLERY_IMAGE_ALT": "descrizione", "GALLERY_CAPTION": "Didascalia"}},
      {{"GALLERY_IMAGE_URL": "https://placehold.co/600x400/eee/999?text=Foto+6", "GALLERY_IMAGE_ALT": "descrizione", "GALLERY_CAPTION": "Didascalia"}}
    ]
  }},
  "team": {{
    "TEAM_TITLE": "Titolo sezione team",
    "TEAM_SUBTITLE": "Sottotitolo",
    "TEAM_MEMBERS": [
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo", "MEMBER_IMAGE_URL": "https://placehold.co/300x300/eee/999?text=Team", "MEMBER_BIO": "Breve bio (1-2 frasi)"}},
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo", "MEMBER_IMAGE_URL": "https://placehold.co/300x300/eee/999?text=Team", "MEMBER_BIO": "Breve bio"}},
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo", "MEMBER_IMAGE_URL": "https://placehold.co/300x300/eee/999?text=Team", "MEMBER_BIO": "Breve bio"}}
    ]
  }},
  "pricing": {{
    "PRICING_TITLE": "Titolo sezione prezzi",
    "PRICING_SUBTITLE": "Sottotitolo",
    "PRICING_PLANS": [
      {{"PLAN_NAME": "Base", "PLAN_PRICE": "29", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Ideale per iniziare", "PLAN_FEATURES": "Feature 1, Feature 2, Feature 3", "PLAN_CTA_TEXT": "Inizia Ora", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "false"}},
      {{"PLAN_NAME": "Pro", "PLAN_PRICE": "59", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Il più popolare", "PLAN_FEATURES": "Tutto Base + Feature 4, Feature 5, Feature 6", "PLAN_CTA_TEXT": "Scegli Pro", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "true"}},
      {{"PLAN_NAME": "Enterprise", "PLAN_PRICE": "99", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Per grandi aziende", "PLAN_FEATURES": "Tutto Pro + Feature 7, Feature 8, Supporto dedicato", "PLAN_CTA_TEXT": "Contattaci", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "false"}}
    ]
  }},
  "faq": {{
    "FAQ_TITLE": "Domande Frequenti",
    "FAQ_SUBTITLE": "Sottotitolo",
    "FAQ_ITEMS": [
      {{"FAQ_QUESTION": "Domanda 1?", "FAQ_ANSWER": "Risposta dettagliata (2-3 frasi)"}},
      {{"FAQ_QUESTION": "Domanda 2?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 3?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 4?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 5?", "FAQ_ANSWER": "Risposta dettagliata"}}
    ]
  }},
  "stats": {{
    "STATS_TITLE": "I Nostri Numeri",
    "STATS_SUBTITLE": "Sottotitolo",
    "STATS_ITEMS": [
      {{"STAT_NUMBER": "150", "STAT_SUFFIX": "+", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "98", "STAT_SUFFIX": "%", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "10", "STAT_SUFFIX": "K", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "24", "STAT_SUFFIX": "/7", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}}
    ]
  }},
  "logos": {{
    "LOGOS_TITLE": "I Nostri Partner",
    "LOGOS_ITEMS": [
      {{"LOGO_IMAGE_URL": "https://placehold.co/160x60/eee/999?text=Partner+1", "LOGO_ALT": "Partner 1", "LOGO_NAME": "Partner 1"}},
      {{"LOGO_IMAGE_URL": "https://placehold.co/160x60/eee/999?text=Partner+2", "LOGO_ALT": "Partner 2", "LOGO_NAME": "Partner 2"}},
      {{"LOGO_IMAGE_URL": "https://placehold.co/160x60/eee/999?text=Partner+3", "LOGO_ALT": "Partner 3", "LOGO_NAME": "Partner 3"}},
      {{"LOGO_IMAGE_URL": "https://placehold.co/160x60/eee/999?text=Partner+4", "LOGO_ALT": "Partner 4", "LOGO_NAME": "Partner 4"}}
    ]
  }},
  "process": {{
    "PROCESS_TITLE": "Come Funziona",
    "PROCESS_SUBTITLE": "Sottotitolo",
    "PROCESS_STEPS": [
      {{"STEP_NUMBER": "1", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}},
      {{"STEP_NUMBER": "2", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}},
      {{"STEP_NUMBER": "3", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}}
    ]
  }},
  "timeline": {{
    "TIMELINE_TITLE": "La Nostra Storia",
    "TIMELINE_SUBTITLE": "Sottotitolo",
    "TIMELINE_ITEMS": [
      {{"TIMELINE_YEAR": "2020", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}},
      {{"TIMELINE_YEAR": "2022", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}},
      {{"TIMELINE_YEAR": "2024", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}}
    ]
  }},
  "footer": {{
    "FOOTER_DESCRIPTION": "Breve descrizione per footer (1 frase)"
  }}
}}

IMPORTANT:
- ALL text MUST be in Italian
- Be WILDLY creative and hyper-specific to this business (ZERO generic text)
- Hero title: MAX 6 words, powerful and memorable (think Nike, Apple-level copy)
- Subtitles: evocative, create curiosity and desire
- Service/feature descriptions: benefit-focused, emotional, specific
- Use relevant emojis for service/feature icons (modern, not cliche)
- TESTIMONIAL_INITIAL = first letter of author name
- Testimonials must sound like REAL people with specific details
- Generate ONLY the sections listed in SECTIONS NEEDED
- Avoid these BANNED generic phrases: "benvenuti", "siamo un'azienda", "offriamo servizi", "il nostro team", "qualita e professionalita"
- Return ONLY the JSON object"""

        result = await self.kimi.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000, thinking=False, timeout=120.0,
        )

        if result.get("success"):
            try:
                texts = self._extract_json(result["content"])
                result["parsed"] = texts
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"[DataBinding] Texts JSON parse failed: {e}")
                result["success"] = False
                result["error"] = f"Failed to parse texts JSON: {e}"

        return result

    # =========================================================
    # Step 3: Select Components
    # =========================================================
    def _select_components_deterministic(
        self,
        template_style_id: str,
        sections: List[str],
    ) -> Dict[str, str]:
        """Use curated STYLE_VARIANT_MAP for deterministic component selection."""
        variant_map = STYLE_VARIANT_MAP.get(template_style_id, {})
        available = self.assembler.get_variant_ids()
        selections = {}

        for section in sections:
            # Use curated variant if available for this style
            if section in variant_map:
                selections[section] = variant_map[section]
            else:
                # Fallback: pick first available variant for sections not in the map
                variants = available.get(section, [])
                if variants:
                    selections[section] = variants[0]

        logger.info(f"[DataBinding] Deterministic selection for '{template_style_id}': {selections}")
        return selections

    async def _select_components(
        self,
        business_description: str,
        sections: List[str],
        style_mood: str,
        template_style_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Select component variants. Uses deterministic map if template_style_id is provided,
        otherwise falls back to Kimi AI selection."""

        # If we have a template_style_id with a mapping, use deterministic selection
        if template_style_id and template_style_id in STYLE_VARIANT_MAP:
            selections = self._select_components_deterministic(template_style_id, sections)
            return {"success": True, "parsed": selections}

        # Fallback: AI-based selection (for custom-free or unknown styles)
        available = self.assembler.get_variant_ids()
        relevant = {k: v for k, v in available.items() if k in sections}

        prompt = f"""Select the best website component variant for each section. Return ONLY valid JSON.

BUSINESS TYPE: {business_description[:300]}
STYLE/MOOD: {style_mood}
SECTIONS NEEDED: {', '.join(sections)}

AVAILABLE VARIANTS:
{json.dumps(relevant, indent=2)}

Return a JSON object mapping each section to the best variant ID:
{{
  "hero": "variant-id",
  "about": "variant-id",
  ...
}}

Choose variants whose style matches the business type and mood.
For footer, prefer "footer-multi-col-01" for sites with 4+ sections, "footer-minimal-02" for simpler sites.
Return ONLY the JSON object."""

        result = await self.kimi.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600, thinking=False, timeout=45.0,
        )

        if result.get("success"):
            try:
                selections = self._extract_json(result["content"])
                result["parsed"] = selections
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[DataBinding] Selection JSON parse failed: {e}, using defaults")
                result["parsed"] = self._default_selections(sections, available)
        else:
            result["parsed"] = self._default_selections(sections, available)

        return result

    # =========================================================
    # Main generate() method - same interface as SwarmGenerator
    # =========================================================
    async def generate(
        self,
        business_name: str,
        business_description: str,
        sections: List[str] = None,
        style_preferences: Optional[Dict[str, Any]] = None,
        reference_image_url: Optional[str] = None,
        reference_analysis: Optional[str] = None,
        logo_url: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None,
        on_progress: ProgressCallback = None,
        photo_urls: Optional[List[str]] = None,
        template_style_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a website using the data-binding pipeline.
        Returns same format as SwarmGenerator.generate() for compatibility.
        """
        if sections is None:
            sections = ["hero", "about", "services", "contact", "footer"]

        try:
            return await asyncio.wait_for(
                self._generate_pipeline(
                    business_name=business_name,
                    business_description=business_description,
                    sections=sections,
                    style_preferences=style_preferences,
                    reference_image_url=reference_image_url,
                    logo_url=logo_url,
                    contact_info=contact_info,
                    on_progress=on_progress,
                    photo_urls=photo_urls,
                    template_style_id=template_style_id,
                ),
                timeout=180.0,
            )
        except asyncio.TimeoutError:
            logger.error("[DataBinding] Pipeline timeout (180s)")
            return {"success": False, "error": "Timeout: generazione ha impiegato troppo tempo."}

    async def _generate_pipeline(
        self,
        business_name: str,
        business_description: str,
        sections: List[str],
        style_preferences: Optional[Dict[str, Any]],
        reference_image_url: Optional[str],
        logo_url: Optional[str],
        contact_info: Optional[Dict[str, str]],
        on_progress: ProgressCallback,
        photo_urls: Optional[List[str]] = None,
        template_style_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        total_tokens_in = 0
        total_tokens_out = 0

        # Sanitize input
        business_name, business_description, sections = sanitize_input(
            business_name, business_description, sections
        )

        # === QUERY DESIGN KNOWLEDGE (local, instant) ===
        creative_context = ""
        if _has_design_knowledge:
            try:
                stats = get_collection_stats()
                if stats.get("total_patterns", 0) > 0:
                    category_label = template_style_id.split("-")[0] if template_style_id else "modern"
                    creative_context = get_creative_context(
                        style_id=template_style_id or "custom-free",
                        category_label=category_label,
                        sections=sections,
                    )
                    if creative_context:
                        logger.info(f"[DataBinding] Creative context: {len(creative_context)} chars from ChromaDB")
            except Exception as e:
                logger.warning(f"[DataBinding] Design knowledge query failed: {e}")

        # === STEP 1+2 PARALLEL: Theme + Texts ===
        if on_progress:
            on_progress(1, "Analisi stile e generazione testi...", {
                "phase": "analyzing",
            })

        theme_task = self._generate_theme(
            business_name, business_description,
            style_preferences, reference_image_url,
        )
        texts_task = self._generate_texts(
            business_name, business_description,
            sections, contact_info,
            creative_context=creative_context,
        )
        theme_result, texts_result = await asyncio.gather(theme_task, texts_task)

        # Extract results
        theme = theme_result.get("parsed", self._fallback_theme(style_preferences))

        if not texts_result.get("success") or not texts_result.get("parsed"):
            return {
                "success": False,
                "error": texts_result.get("error", "Impossibile generare i testi del sito"),
            }
        texts = texts_result["parsed"]

        # Accumulate tokens
        for r in [theme_result, texts_result]:
            if r.get("success"):
                total_tokens_in += r.get("tokens_input", 0)
                total_tokens_out += r.get("tokens_output", 0)

        # Send preview: colors + fonts found
        if on_progress:
            on_progress(2, "Palette e stile identificati", {
                "phase": "theme_complete",
                "colors": {
                    "primary": theme.get("primary_color", "#3b82f6"),
                    "secondary": theme.get("secondary_color", "#1e40af"),
                    "accent": theme.get("accent_color", "#f59e0b"),
                    "bg": theme.get("bg_color", "#ffffff"),
                    "text": theme.get("text_color", "#0f172a"),
                },
                "font_heading": theme.get("font_heading", "Inter"),
                "font_body": theme.get("font_body", "Inter"),
            })

        # === STEP 3: Component Selection ===
        mood = ""
        if style_preferences:
            mood = style_preferences.get("mood", "modern")
        if not mood:
            mood = "modern"

        selection_result = await self._select_components(
            business_description, sections, mood,
            template_style_id=template_style_id,
        )
        selections = selection_result.get("parsed", self._default_selections(
            sections, self.assembler.get_variant_ids()
        ))

        if selection_result.get("success"):
            total_tokens_in += selection_result.get("tokens_input", 0)
            total_tokens_out += selection_result.get("tokens_output", 0)

        # Send preview: layout + texts
        hero_texts = texts.get("hero", {})
        services_texts = texts.get("services", {})
        if on_progress:
            on_progress(3, "Contenuti e layout pronti", {
                "phase": "content_complete",
                "sections": sections,
                "hero_title": hero_texts.get("HERO_TITLE", ""),
                "hero_subtitle": hero_texts.get("HERO_SUBTITLE", ""),
                "hero_cta": hero_texts.get("HERO_CTA_TEXT", ""),
                "services_titles": [
                    s.get("SERVICE_TITLE", "") for s in services_texts.get("SERVICES", [])
                ] if isinstance(services_texts.get("SERVICES"), list) else [],
            })

        site_data = self._build_site_data(
            theme=theme,
            texts=texts,
            selections=selections,
            business_name=business_name,
            logo_url=logo_url,
            contact_info=contact_info,
            sections=sections,
        )

        # Inject user-uploaded photos (replace placehold.co URLs)
        if photo_urls:
            site_data = self._inject_user_photos(site_data, photo_urls)

        try:
            html_content = self.assembler.assemble(site_data)
            html_content = sanitize_output(html_content)
        except Exception as e:
            logger.exception("[DataBinding] Assembly failed")
            return {"success": False, "error": f"Errore assemblaggio: {str(e)}"}

        if on_progress:
            on_progress(4, "Sito assemblato, controllo qualita'...", {
                "phase": "assembled",
            })

        # === STEP 5: Quality Control ===
        qc_report_data = None
        try:
            qc_report = await qc_pipeline.run_full_qc(
                html=html_content,
                theme_config=theme,
                requested_sections=sections,
                style_id=template_style_id or "custom-free",
                on_progress=on_progress,
            )
            qc_report_data = qc_report.to_dict()

            # Use fixed HTML if QC applied fixes
            if qc_report.html_after and qc_report.html_after != qc_report.html_before:
                html_content = qc_report.html_after
                logger.info(
                    f"[DataBinding] QC applied fixes: score {qc_report.overall_score} -> {qc_report.final_score}"
                )

            if on_progress:
                status_msg = "Sito approvato!" if qc_report.passed else "Sito pronto (revisione consigliata)"
                on_progress(5, status_msg, {
                    "phase": "complete",
                    "qc_score": qc_report.final_score,
                    "qc_passed": qc_report.passed,
                })
        except Exception as e:
            logger.warning(f"[DataBinding] QC pipeline failed (non-blocking): {e}")
            # QC failure is non-blocking: return the original HTML
            if on_progress:
                on_progress(5, "Il tuo sito e' pronto!", {
                    "phase": "complete",
                })

        generation_time = int((time.time() - start_time) * 1000)
        cost = self.kimi.calculate_cost(total_tokens_in, total_tokens_out)

        logger.info(
            f"[DataBinding] Done in {generation_time}ms, "
            f"tokens: {total_tokens_in}in/{total_tokens_out}out, ${cost:.4f}"
        )

        return {
            "success": True,
            "html_content": html_content,
            "model_used": "kimi-k2.5-databinding",
            "tokens_input": total_tokens_in,
            "tokens_output": total_tokens_out,
            "cost_usd": cost,
            "generation_time_ms": generation_time,
            "pipeline_steps": 5,
            "site_data": site_data,
            "qc_report": qc_report_data,
        }

    # =========================================================
    # Refine - delegates to SwarmGenerator
    # =========================================================
    async def refine(
        self,
        current_html: str,
        modification_request: str,
        section_to_modify: Optional[str] = None,
    ) -> Dict[str, Any]:
        """For chat refinements, delegate to SwarmGenerator (works on raw HTML)."""
        from app.services.swarm_generator import swarm
        return await swarm.refine(current_html, modification_request, section_to_modify)

    # =========================================================
    # Helpers
    # =========================================================
    def _build_site_data(
        self, theme, texts, selections, business_name, logo_url, contact_info, sections,
    ) -> Dict[str, Any]:
        """Builds the site_data dict consumed by TemplateAssembler.assemble()."""
        components = []
        for section in sections:
            variant_id = selections.get(section)
            if not variant_id:
                continue
            section_texts = texts.get(section, {})
            components.append({
                "variant_id": variant_id,
                "data": section_texts,
            })

        return {
            "theme": theme,
            "meta": texts.get("meta", {
                "title": business_name,
                "description": f"Sito web di {business_name}",
                "og_title": business_name,
                "og_description": f"Sito web di {business_name}",
            }),
            "components": components,
            "global": {
                "BUSINESS_NAME": business_name,
                "LOGO_URL": logo_url or "",
                "BUSINESS_PHONE": contact_info.get("phone", "") if contact_info else "",
                "BUSINESS_EMAIL": contact_info.get("email", "") if contact_info else "",
                "BUSINESS_ADDRESS": contact_info.get("address", "") if contact_info else "",
                "CURRENT_YEAR": "2026",
            },
        }

    def _inject_user_photos(self, site_data: Dict[str, Any], photo_urls: List[str]) -> Dict[str, Any]:
        """Replace placehold.co URLs with user-uploaded photos in site_data."""
        if not photo_urls:
            return site_data

        photo_index = 0

        def get_next_photo():
            nonlocal photo_index
            if not photo_urls:
                return None
            photo = photo_urls[photo_index % len(photo_urls)]
            photo_index += 1
            return photo

        for component in site_data.get("components", []):
            data = component.get("data", {})

            # Replace hero image
            if "HERO_IMAGE_URL" in data:
                photo = get_next_photo()
                if photo:
                    data["HERO_IMAGE_URL"] = photo

            # Replace gallery images
            gallery_items = data.get("GALLERY_ITEMS", [])
            if isinstance(gallery_items, list):
                for item in gallery_items:
                    if isinstance(item, dict) and "GALLERY_IMAGE_URL" in item:
                        photo = get_next_photo()
                        if photo:
                            item["GALLERY_IMAGE_URL"] = photo

            # Replace about image if present
            if "ABOUT_IMAGE_URL" in data:
                photo = get_next_photo()
                if photo:
                    data["ABOUT_IMAGE_URL"] = photo

            # Replace team member images
            team_members = data.get("TEAM_MEMBERS", [])
            if isinstance(team_members, list):
                for member in team_members:
                    if isinstance(member, dict) and "MEMBER_IMAGE_URL" in member:
                        photo = get_next_photo()
                        if photo:
                            member["MEMBER_IMAGE_URL"] = photo

        return site_data

    def _extract_json(self, content: str) -> dict:
        """Extracts JSON from Kimi response (handles markdown code blocks)."""
        # Try JSON in code block
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1).strip())
        # Try raw JSON (find first { to last })
        content = content.strip()
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1 and end > start:
            return json.loads(content[start:end + 1])
        raise ValueError(f"No JSON found in response: {content[:200]}...")

    def _fallback_theme(self, style_preferences=None) -> Dict[str, str]:
        """Default theme if Kimi theme generation fails."""
        primary = "#3b82f6"
        if style_preferences and style_preferences.get("primary_color"):
            primary = style_preferences["primary_color"]
        return {
            "primary_color": primary,
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
        }

    def _default_selections(self, sections: List[str], available: Dict[str, List[str]]) -> Dict[str, str]:
        """Fallback: pick first variant for each section."""
        selections = {}
        for section in sections:
            variants = available.get(section, [])
            if variants:
                selections[section] = variants[0]
        return selections


# Singleton
databinding_generator = DataBindingGenerator()
