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
  Step 1+2 (parallel): Kimi → JSON {colors, fonts, mood} + JSON {texts for all sections}
  Step 3+Images (parallel): Component variant selection + AI image generation (Flux/fal.ai)
  Step 4: Replace placeholder URLs with generated image URLs
  Step 5: TemplateAssembler → complete HTML
  Step 6: Quality Control
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

# AI Image generation (Flux/fal.ai) - graceful fallback if not available
try:
    from app.services.image_generator import generate_all_site_images, _has_api_key as _has_image_api_key
    _has_image_generation = True
except Exception:
    _has_image_generation = False

    def _has_image_api_key() -> bool:
        return False

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
        creative_context: str = "",
    ) -> Dict[str, Any]:
        """Kimi returns JSON with color palette and fonts."""
        style_hint = ""
        if style_preferences:
            if style_preferences.get("primary_color"):
                style_hint += f"Primary color requested: {style_preferences['primary_color']}. "
            if style_preferences.get("mood"):
                style_hint += f"Mood/style: {style_preferences['mood']}. "

        # Extract palette guidance from creative context (blueprints)
        palette_hint = ""
        if creative_context:
            # Extract just the palette/font recommendations (first ~500 chars of blueprint)
            palette_hint = f"\nPROFESSIONAL DESIGN REFERENCE:\n{creative_context[:500]}\n"

        prompt = f"""You are a Dribbble/Awwwards-level UI designer. Generate a STUNNING, BOLD color palette and typography for a website.
Return ONLY valid JSON, no markdown, no explanation.

BUSINESS: {business_name} - {business_description[:500]}
{style_hint}
{palette_hint}
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

=== COLOR RULES (CRITICAL) ===
- primary_color: SATURATED and VIBRANT. High chroma, fully alive. Never desaturated, never grayish. Think #E63946 not #8b9da5, think #7C3AED not #6677aa.
- secondary_color: COMPLEMENTARY to primary, not just a darker shade. If primary is warm, secondary can be cool (and vice versa). Must be visually distinct.
- accent_color: must POP against the palette. Use a CONTRASTING hue from primary (not analogous). Examples: deep blue primary + electric amber accent, forest green primary + coral accent, purple primary + lime accent. The accent is for CTAs and highlights — it must DEMAND attention.
- bg_color: NEVER plain #ffffff or #000000. Use rich tones: warm cream (#FAF7F2), deep navy (#0A1628), charcoal slate (#1A1D23), soft sage (#F0F4F1), warm blush (#FFF5F5), ivory (#FFFDF7). The background sets the entire mood.
- bg_alt_color: must be NOTICEABLY different from bg_color (at least 8-12% lightness shift). If bg is light, bg_alt should be a tinted pastel (e.g. soft lavender, light sand). If bg is dark, bg_alt should be 2-3 shades lighter. Sections must visually alternate.
- text_color: WCAG AA contrast against bg_color (minimum 4.5:1). For dark bg use near-white (#F1F5F9), for light bg use rich dark (#0F172A or #1A1A2E).
- text_muted_color: 40-50% opacity feel vs text_color. Must still be readable.
- BANNED dull palettes: no all-blue (#3b82f6 + #1e40af + #2563eb), no corporate gray, no monochromatic schemes. Every color should earn its place.

=== FONT PAIRING RULES (CRITICAL) ===
Pick ONE of these curated pairings based on the business personality:

ELEGANT/LUXURY: "Playfair Display" (heading) + "Inter" (body)
MODERN TECH/SAAS: "Space Grotesk" (heading) + "DM Sans" (body)
CLEAN STARTUP: "Sora" (heading) + "Inter" (body)
EDITORIAL/BLOG: "DM Serif Display" (heading) + "Plus Jakarta Sans" (body)
BOLD CREATIVE: "Cabinet Grotesk" (heading) + "Inter" (body)
GEOMETRIC MODERN: "Outfit" (heading) + "DM Sans" (body)
WARM ARTISAN: "Fraunces" (heading) + "Nunito Sans" (body)
PROFESSIONAL: "Epilogue" (heading) + "Source Sans 3" (body)

- NEVER use the same font for heading and body
- NEVER use Inter, Roboto, Open Sans, or Arial for headings — they lack personality
- Heading fonts must have VISUAL CHARACTER: serifs, distinctive letter shapes, or bold geometric forms
- Body fonts must be CLEAN and highly readable at 16px
- font_heading_url format: "FontName:wght@400;600;700;800" (replace spaces with +)
- font_body_url format: "FontName:wght@400;500;600"

Return ONLY the JSON object"""

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
            knowledge_hint = f"\n\nDESIGN KNOWLEDGE (follow these professional guidelines closely):\n{creative_context[:2500]}\n"

        prompt = f"""You are Italy's most awarded copywriter — think Oliviero Toscani meets Apple. You write text for websites that win design awards.{knowledge_hint}
Your copy must be SHARP, EVOCATIVE, and EMOTIONALLY MAGNETIC. Every word earns its place. Zero filler, zero corporate jargon.
Return ONLY valid JSON, no markdown.

BUSINESS: {business_name}
DESCRIPTION: {business_description[:800]}
SECTIONS NEEDED: {sections_str}
{contact_str}

=== ABSOLUTE BANNED PHRASES (using ANY of these = failure) ===
- "Benvenuti" / "Benvenuto" (in any form)
- "Siamo un'azienda" / "Siamo un team" / "Siamo leader"
- "I nostri servizi" / "Cosa offriamo" / "I nostri prodotti"
- "Qualita e professionalita" / "Eccellenza e innovazione"
- "Contattaci per maggiori informazioni"
- "Il nostro team di esperti"
- "Soluzioni su misura" / "Soluzioni personalizzate"
- "A 360 gradi" / "Chiavi in mano"
- "Da anni nel settore"
- "Non esitare a contattarci"
- Any text that could appear on ANY other business website. Be SPECIFIC to THIS business.

=== HEADLINE RULES ===
- Hero headline: MAX 6 words. Must be UNFORGETTABLE. Use metaphors, contrasts, provocations.
  GREAT EXAMPLES (adapt the style, don't copy):
  - Restaurant: "Il Futuro del Gusto" / "Dove il Tempo si Ferma" / "Sapori che Raccontano Storie"
  - SaaS: "Meno Caos. Piu' Risultati." / "La Velocita Cambia Tutto" / "Il Tuo Prossimo Livello"
  - Portfolio: "Creo Mondi Visivi" / "Design Senza Compromessi" / "Ogni Pixel Ha un Perche"
  - Business: "Costruiamo il Domani" / "Oltre le Aspettative" / "Dove Nasce il Cambiamento"
  TERRIBLE EXAMPLES (NEVER write like this):
  - "Benvenuti nel Nostro Sito" / "La Nostra Azienda" / "Servizi Professionali" / "Chi Siamo"
- Section headings: NEVER generic ("I Nostri Servizi"). Instead, be SPECIFIC and evocative ("Ogni Progetto, Una Rivoluzione" / "Il Metodo Dietro la Magia")

=== COPYWRITING CRAFT ===
- Subtitles: Poetic but clear, 1-2 sentences max. Create CURIOSITY and DESIRE. Make the reader NEED to scroll down.
- Service/feature descriptions: Lead with the BENEFIT, not the feature. What does the customer FEEL, GAIN, BECOME? Use sensory language. Each description must be UNIQUE in tone (don't repeat the same sentence structure).
- Testimonials: Sound like REAL humans — include specific details, emotions, a before/after story. "Mi hanno salvato 20 ore a settimana" not "Ottimo servizio, consigliato."
- Stats/numbers: Use IMPRESSIVE, SPECIFIC numbers (not round). "847" is more believable than "800". "99.2%" is more credible than "100%".
- Use POWER WORDS strategically: rivoluzionario, straordinario, autentico, artigianale, esclusivo, fulminante, impeccabile, visionario.
- Vary rhythm: alternate short punchy phrases with longer flowing descriptions. Create MUSIC in the text.
- CTA buttons: action verbs + urgency. "Inizia la Trasformazione" / "Scopri il Metodo" / "Prenota il Tuo Posto" — NOT "Contattaci" / "Scopri di Piu"

=== ICON RULES ===
- Each service/feature MUST have a UNIQUE, RELEVANT emoji icon
- NEVER repeat the same emoji twice in a section
- Choose MODERN, SPECIFIC emojis that match the content (not generic like checkmarks or stars)
- Examples: for speed use thunderbolt, for security use shield, for analytics use chart, for design use palette

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

FINAL CHECKLIST (every point is mandatory):
- ALL text MUST be in Italian
- Be WILDLY creative and hyper-specific to THIS business — if you replaced the business name, the text should NOT work for any other company
- Hero title: MAX 6 words, think Nike/Apple-level copywriting
- ZERO generic text anywhere. Read every line and ask: "Could this appear on a random corporate site?" If yes, REWRITE IT.
- Each service/feature icon: UNIQUE emoji, never repeated in the same section
- TESTIMONIAL_INITIAL = first letter of TESTIMONIAL_AUTHOR name
- Testimonials: real names, specific details, emotional stories (NOT "Ottimo servizio" or "Molto professionali")
- Generate ONLY the sections listed in SECTIONS NEEDED
- Double-check: NO banned phrases from the list above appear ANYWHERE in your output
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
    # Default variants for section types not in STYLE_VARIANT_MAP.
    # Used when a user requests sections like faq/pricing/stats that aren't
    # curated per-style but exist in the component registry.
    _DEFAULT_SECTION_VARIANTS: Dict[str, str] = {
        "faq": "faq-accordion-01",
        "pricing": "pricing-cards-01",
        "stats": "stats-counters-01",
        "logos": "logos-marquee-01",
        "process": "process-steps-01",
        "timeline": "timeline-vertical-01",
    }

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
            if section in variant_map:
                # Use curated variant for this style
                selections[section] = variant_map[section]
            elif section in self._DEFAULT_SECTION_VARIANTS:
                # Use known default for common section types not in the style map
                selections[section] = self._DEFAULT_SECTION_VARIANTS[section]
            else:
                # Fallback: pick first available variant for unknown sections
                variants = available.get(section, [])
                if variants:
                    selections[section] = variants[0]
                else:
                    logger.warning(
                        f"[DataBinding] No variant available for section '{section}' "
                        f"in style '{template_style_id}'"
                    )

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
            creative_context=creative_context,
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

        # === STEP 3 + IMAGES (parallel): Component Selection + Image Generation ===
        mood = ""
        if style_preferences:
            mood = style_preferences.get("mood", "modern")
        if not mood:
            mood = "modern"

        # Determine if we should generate AI images
        should_generate_images = (
            _has_image_generation
            and _has_image_api_key()
        )

        if should_generate_images:
            if on_progress:
                on_progress(3, "Selezione layout e generazione immagini AI...", {
                    "phase": "images_and_layout",
                })

            # Detect style mood from template_style_id for image prompts
            image_style_mood = mood
            if template_style_id:
                # Extract mood hint from style ID (e.g. "restaurant-elegant" -> "elegant")
                parts = template_style_id.split("-")
                if len(parts) >= 2:
                    image_style_mood = parts[-1]

            # Run component selection and image generation in parallel
            selection_coro = self._select_components(
                business_description, sections, mood,
                template_style_id=template_style_id,
            )
            images_coro = generate_all_site_images(
                business_name=business_name,
                business_description=business_description,
                sections=sections,
                style_mood=image_style_mood,
                color_palette=theme,
                user_photos=photo_urls,
                quality="fast",
            )
            selection_result, generated_images = await asyncio.gather(
                selection_coro, images_coro,
            )

            # Replace placeholder URLs in texts with generated images
            total_ai_images = sum(
                1 for urls in generated_images.values()
                for u in urls if "placehold.co" not in u
            )
            if total_ai_images > 0:
                texts = self._inject_ai_images(texts, generated_images)
                logger.info(f"[DataBinding] Injected {total_ai_images} AI-generated images")
            else:
                logger.info("[DataBinding] No AI images generated, keeping placeholders")
        else:
            # No image generation: just run component selection
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
            progress_msg = "Contenuti, layout e immagini pronti" if should_generate_images else "Contenuti e layout pronti"
            on_progress(4 if should_generate_images else 3, progress_msg, {
                "phase": "content_complete",
                "sections": sections,
                "hero_title": hero_texts.get("HERO_TITLE", ""),
                "hero_subtitle": hero_texts.get("HERO_SUBTITLE", ""),
                "hero_cta": hero_texts.get("HERO_CTA_TEXT", ""),
                "services_titles": [
                    s.get("SERVICE_TITLE", "") for s in services_texts.get("SERVICES", [])
                ] if isinstance(services_texts.get("SERVICES"), list) else [],
                "ai_images_generated": should_generate_images,
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
            on_progress(5, "Sito assemblato, controllo qualita'...", {
                "phase": "assembled",
            })

        # === Quality Control ===
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
                on_progress(6, status_msg, {
                    "phase": "complete",
                    "qc_score": qc_report.final_score,
                    "qc_passed": qc_report.passed,
                })
        except Exception as e:
            logger.warning(f"[DataBinding] QC pipeline failed (non-blocking): {e}")
            # QC failure is non-blocking: return the original HTML
            if on_progress:
                on_progress(6, "Il tuo sito e' pronto!", {
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
            "pipeline_steps": 6,
            "ai_images_generated": should_generate_images if _has_image_generation else False,
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
                logger.warning(f"[DataBinding] No variant selected for section '{section}', skipping")
                continue
            section_texts = texts.get(section, {})
            if isinstance(section_texts, dict):
                section_texts = self._normalize_section_data(section, section_texts, variant_id, business_name)
            components.append({
                "variant_id": variant_id,
                "data": section_texts,
            })

        # Build global data with both BUSINESS_* and CONTACT_* keys for compatibility
        phone = contact_info.get("phone", "") if contact_info else ""
        email = contact_info.get("email", "") if contact_info else ""
        address = contact_info.get("address", "") if contact_info else ""

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
                "BUSINESS_PHONE": phone,
                "BUSINESS_EMAIL": email,
                "BUSINESS_ADDRESS": address,
                # Duplicate as CONTACT_* for templates that use that prefix
                "CONTACT_PHONE": phone,
                "CONTACT_EMAIL": email,
                "CONTACT_ADDRESS": address,
                "CURRENT_YEAR": "2026",
            },
        }

    def _normalize_section_data(
        self, section: str, data: Dict[str, Any], variant_id: str, business_name: str,
    ) -> Dict[str, Any]:
        """Transform AI-generated flat data into the array/repeat format templates expect.

        Key transformations:
        - services: normalize SERVICES array from various AI output formats + fallback
        - features: normalize FEATURES array from various AI output formats + fallback
        - testimonials: normalize TESTIMONIALS array + fallback
        - gallery: normalize GALLERY_ITEMS array + fallback
        - team: normalize TEAM_MEMBERS array
        - about: ABOUT_HIGHLIGHT_NUM_1/2/3 + ABOUT_HIGHLIGHT_1/2/3 -> ABOUT_STATS array
        - about: ensure ABOUT_IMAGE_URL/ABOUT_IMAGE_ALT have fallback values
        - contact: copy CONTACT_* to BUSINESS_* and vice versa for template compatibility
        - pricing: convert comma-separated PLAN_FEATURES to array
        - faq/stats/logos/process/timeline: normalize repeat arrays
        """
        data = dict(data)  # shallow copy to avoid mutating original

        if section == "services":
            data = self._normalize_repeat_array(
                data,
                canonical_key="SERVICES",
                alt_keys=["SERVICE_ITEMS", "SERVICES_ITEMS", "SERVICE_LIST", "SERVICES_LIST", "items", "services"],
                item_fields=["SERVICE_ICON", "SERVICE_TITLE", "SERVICE_DESCRIPTION"],
                flat_prefix="SERVICE",
                fallback_items=self._fallback_services(business_name),
            )

        elif section == "features":
            data = self._normalize_repeat_array(
                data,
                canonical_key="FEATURES",
                alt_keys=["FEATURE_ITEMS", "FEATURES_ITEMS", "FEATURE_LIST", "FEATURES_LIST", "items", "features"],
                item_fields=["FEATURE_ICON", "FEATURE_TITLE", "FEATURE_DESCRIPTION"],
                flat_prefix="FEATURE",
                fallback_items=self._fallback_features(business_name),
            )

        elif section == "testimonials":
            data = self._normalize_repeat_array(
                data,
                canonical_key="TESTIMONIALS",
                alt_keys=["TESTIMONIAL_ITEMS", "TESTIMONIALS_ITEMS", "TESTIMONIAL_LIST", "items", "testimonials"],
                item_fields=["TESTIMONIAL_TEXT", "TESTIMONIAL_AUTHOR", "TESTIMONIAL_ROLE", "TESTIMONIAL_INITIAL"],
                flat_prefix="TESTIMONIAL",
                fallback_items=self._fallback_testimonials(),
            )

        elif section == "gallery":
            data = self._normalize_repeat_array(
                data,
                canonical_key="GALLERY_ITEMS",
                alt_keys=["GALLERY", "GALLERY_LIST", "GALLERY_IMAGES", "items", "gallery"],
                item_fields=["GALLERY_IMAGE_URL", "GALLERY_IMAGE_ALT", "GALLERY_CAPTION"],
                flat_prefix="GALLERY",
                fallback_items=self._fallback_gallery(),
            )

        elif section == "team":
            data = self._normalize_repeat_array(
                data,
                canonical_key="TEAM_MEMBERS",
                alt_keys=["TEAM", "TEAM_ITEMS", "TEAM_LIST", "MEMBERS", "items", "team"],
                item_fields=["MEMBER_NAME", "MEMBER_ROLE", "MEMBER_IMAGE_URL", "MEMBER_BIO"],
                flat_prefix="MEMBER",
                fallback_items=None,
            )

        elif section == "about":
            # Convert flat ABOUT_HIGHLIGHT_* keys to ABOUT_STATS repeat array
            if "ABOUT_STATS" not in data:
                stats = []
                for i in range(1, 10):  # support up to 9 highlights
                    num_key = f"ABOUT_HIGHLIGHT_NUM_{i}"
                    label_key = f"ABOUT_HIGHLIGHT_{i}"
                    if num_key in data and label_key in data:
                        stats.append({
                            "STAT_NUMBER": str(data[num_key]),
                            "STAT_LABEL": str(data[label_key]),
                        })
                if stats:
                    data["ABOUT_STATS"] = stats

            # Ensure ABOUT_IMAGE_URL has a fallback for templates that need it
            if "ABOUT_IMAGE_URL" not in data or not data["ABOUT_IMAGE_URL"]:
                primary = "3b82f6"
                data["ABOUT_IMAGE_URL"] = f"https://placehold.co/800x600/{primary}/white?text={business_name}"
            if "ABOUT_IMAGE_ALT" not in data or not data["ABOUT_IMAGE_ALT"]:
                data["ABOUT_IMAGE_ALT"] = f"Immagine {business_name}"

        elif section == "contact":
            # Ensure both CONTACT_* and BUSINESS_* prefixes are available
            contact_map = {
                "CONTACT_EMAIL": "BUSINESS_EMAIL",
                "CONTACT_PHONE": "BUSINESS_PHONE",
                "CONTACT_ADDRESS": "BUSINESS_ADDRESS",
            }
            for contact_key, business_key in contact_map.items():
                if contact_key in data and business_key not in data:
                    data[business_key] = data[contact_key]
                elif business_key in data and contact_key not in data:
                    data[contact_key] = data[business_key]

        elif section == "pricing":
            # Normalize the array first
            data = self._normalize_repeat_array(
                data,
                canonical_key="PRICING_PLANS",
                alt_keys=["PLANS", "PRICING", "PRICING_ITEMS", "items", "pricing"],
                item_fields=["PLAN_NAME", "PLAN_PRICE", "PLAN_PERIOD"],
                flat_prefix="PLAN",
                fallback_items=None,
            )
            # Convert comma-separated PLAN_FEATURES string into array for nested REPEAT
            plans = data.get("PRICING_PLANS", [])
            if isinstance(plans, list):
                for plan in plans:
                    if isinstance(plan, dict):
                        features_str = plan.get("PLAN_FEATURES", "")
                        if isinstance(features_str, str) and features_str:
                            plan["PLAN_FEATURES"] = [
                                {"FEATURE_TEXT": f.strip()}
                                for f in features_str.split(",")
                                if f.strip()
                            ]

        elif section == "faq":
            data = self._normalize_repeat_array(
                data,
                canonical_key="FAQ_ITEMS",
                alt_keys=["FAQ", "FAQS", "FAQ_LIST", "items", "faq"],
                item_fields=["FAQ_QUESTION", "FAQ_ANSWER"],
                flat_prefix="FAQ",
                fallback_items=None,
            )

        elif section == "stats":
            data = self._normalize_repeat_array(
                data,
                canonical_key="STATS_ITEMS",
                alt_keys=["STATS", "STATS_LIST", "items", "stats"],
                item_fields=["STAT_NUMBER", "STAT_SUFFIX", "STAT_LABEL"],
                flat_prefix="STAT",
                fallback_items=None,
            )

        elif section == "logos":
            data = self._normalize_repeat_array(
                data,
                canonical_key="LOGOS_ITEMS",
                alt_keys=["LOGOS", "LOGOS_LIST", "LOGO_ITEMS", "items", "logos"],
                item_fields=["LOGO_IMAGE_URL", "LOGO_ALT", "LOGO_NAME"],
                flat_prefix="LOGO",
                fallback_items=None,
            )

        elif section == "process":
            data = self._normalize_repeat_array(
                data,
                canonical_key="PROCESS_STEPS",
                alt_keys=["PROCESS", "PROCESS_ITEMS", "PROCESS_LIST", "STEPS", "items", "process"],
                item_fields=["STEP_NUMBER", "STEP_TITLE", "STEP_DESCRIPTION"],
                flat_prefix="STEP",
                fallback_items=None,
            )

        elif section == "timeline":
            data = self._normalize_repeat_array(
                data,
                canonical_key="TIMELINE_ITEMS",
                alt_keys=["TIMELINE", "TIMELINE_LIST", "TIMELINE_EVENTS", "items", "timeline"],
                item_fields=["TIMELINE_YEAR", "TIMELINE_HEADING", "TIMELINE_DESCRIPTION"],
                flat_prefix="TIMELINE",
                fallback_items=None,
            )

        return data

    def _normalize_repeat_array(
        self,
        data: Dict[str, Any],
        canonical_key: str,
        alt_keys: List[str],
        item_fields: List[str],
        flat_prefix: str,
        fallback_items: Optional[List[Dict[str, str]]],
    ) -> Dict[str, Any]:
        """Normalize a repeating array in the data dict.

        Handles these common AI output variations:
        1. Correct key with valid array (SERVICES: [...]) -- no-op
        2. Alternative key name (SERVICE_ITEMS, items, etc.) -- rename to canonical
        3. Flat numbered keys (SERVICE_1_TITLE, SERVICE_2_TITLE, etc.) -- collect into array
        4. Lowercase key versions -- case-insensitive lookup
        5. Single object instead of array -- wrap in array
        6. Empty/missing array -- use fallback items if provided
        """
        # 1. Check if canonical key already has a valid non-empty array
        existing = data.get(canonical_key)
        if isinstance(existing, list) and len(existing) > 0:
            # Validate items have the expected fields (at least one recognized field)
            if isinstance(existing[0], dict) and any(f in existing[0] for f in item_fields):
                return data

        # 2. Check alternative key names (case-insensitive)
        all_keys_lower = {k.lower(): k for k in data.keys()}
        for alt_key in alt_keys:
            # Direct key check
            if alt_key in data:
                val = data[alt_key]
                if isinstance(val, list) and len(val) > 0:
                    data[canonical_key] = val
                    logger.info(f"[DataBinding] Normalized {alt_key} -> {canonical_key} ({len(val)} items)")
                    return data
                elif isinstance(val, dict):
                    # Single object wrapped as array
                    data[canonical_key] = [val]
                    logger.info(f"[DataBinding] Normalized {alt_key} (single object) -> {canonical_key} array")
                    return data
            # Case-insensitive check
            if alt_key.lower() in all_keys_lower:
                real_key = all_keys_lower[alt_key.lower()]
                if real_key != alt_key:  # avoid re-checking the same key
                    val = data[real_key]
                    if isinstance(val, list) and len(val) > 0:
                        data[canonical_key] = val
                        logger.info(f"[DataBinding] Normalized {real_key} -> {canonical_key} ({len(val)} items)")
                        return data

        # Also check canonical key with different casing
        if canonical_key.lower() in all_keys_lower:
            real_key = all_keys_lower[canonical_key.lower()]
            if real_key != canonical_key:
                val = data[real_key]
                if isinstance(val, list) and len(val) > 0:
                    data[canonical_key] = val
                    logger.info(f"[DataBinding] Normalized {real_key} (case) -> {canonical_key} ({len(val)} items)")
                    return data

        # 3. Check for flat numbered keys (e.g., SERVICE_1_TITLE, SERVICE_2_TITLE, ...)
        flat_items = self._collect_flat_numbered_items(data, flat_prefix, item_fields)
        if flat_items:
            data[canonical_key] = flat_items
            logger.info(f"[DataBinding] Collected {len(flat_items)} flat {flat_prefix}_* items -> {canonical_key}")
            return data

        # 4. If canonical key exists but is empty/invalid, or doesn't exist at all
        if fallback_items:
            logger.warning(f"[DataBinding] {canonical_key} missing or empty, using {len(fallback_items)} fallback items")
            data[canonical_key] = fallback_items

        return data

    def _collect_flat_numbered_items(
        self,
        data: Dict[str, Any],
        prefix: str,
        item_fields: List[str],
    ) -> List[Dict[str, str]]:
        """Collect flat numbered keys into a list of dicts.

        Handles patterns like:
        - SERVICE_1_TITLE, SERVICE_1_DESCRIPTION, SERVICE_2_TITLE, ...
        - SERVICE_TITLE_1, SERVICE_DESCRIPTION_1, SERVICE_TITLE_2, ...
        """
        items: Dict[int, Dict[str, str]] = {}
        # Extract the field suffixes from item_fields
        # e.g., item_fields=["SERVICE_ICON", "SERVICE_TITLE", "SERVICE_DESCRIPTION"]
        # field_suffixes = {"ICON": "SERVICE_ICON", "TITLE": "SERVICE_TITLE", ...}
        field_map: Dict[str, str] = {}
        for field in item_fields:
            if field.startswith(prefix + "_"):
                suffix = field[len(prefix) + 1:]
                field_map[suffix] = field

        # Pattern 1: PREFIX_N_SUFFIX (e.g., SERVICE_1_TITLE)
        for key, value in data.items():
            for suffix, full_field in field_map.items():
                m = re.match(rf"{prefix}_(\d+)_{suffix}$", key, re.IGNORECASE)
                if m:
                    idx = int(m.group(1))
                    if idx not in items:
                        items[idx] = {}
                    items[idx][full_field] = str(value)

        # Pattern 2: PREFIX_SUFFIX_N (e.g., SERVICE_TITLE_1)
        if not items:
            for key, value in data.items():
                for suffix, full_field in field_map.items():
                    m = re.match(rf"{prefix}_{suffix}_(\d+)$", key, re.IGNORECASE)
                    if m:
                        idx = int(m.group(1))
                        if idx not in items:
                            items[idx] = {}
                        items[idx][full_field] = str(value)

        if items:
            return [items[k] for k in sorted(items.keys())]
        return []

    # ----- Fallback content generators -----

    def _fallback_services(self, business_name: str) -> List[Dict[str, str]]:
        """Generate fallback service items when AI returns empty/missing services."""
        return [
            {
                "SERVICE_ICON": "\U0001f3af",
                "SERVICE_TITLE": "Consulenza Personalizzata",
                "SERVICE_DESCRIPTION": f"Un approccio su misura per le tue esigenze. {business_name} ti guida passo dopo passo verso i tuoi obiettivi.",
            },
            {
                "SERVICE_ICON": "\U0001f680",
                "SERVICE_TITLE": "Soluzioni Innovative",
                "SERVICE_DESCRIPTION": "Tecnologie all'avanguardia e metodologie collaudate per risultati che superano le aspettative.",
            },
            {
                "SERVICE_ICON": "\U0001f91d",
                "SERVICE_TITLE": "Supporto Dedicato",
                "SERVICE_DESCRIPTION": "Un team di esperti sempre al tuo fianco. Assistenza continua e comunicazione trasparente.",
            },
        ]

    def _fallback_features(self, business_name: str) -> List[Dict[str, str]]:
        """Generate fallback feature items when AI returns empty/missing features."""
        return [
            {
                "FEATURE_ICON": "\u2728",
                "FEATURE_TITLE": "Qualita' Superiore",
                "FEATURE_DESCRIPTION": "Standard elevati in ogni dettaglio, dalla progettazione alla consegna finale.",
            },
            {
                "FEATURE_ICON": "\u26a1",
                "FEATURE_TITLE": "Velocita' ed Efficienza",
                "FEATURE_DESCRIPTION": "Processi ottimizzati per garantire tempi di consegna rapidi senza compromessi.",
            },
            {
                "FEATURE_ICON": "\U0001f6e1\ufe0f",
                "FEATURE_TITLE": "Affidabilita' Garantita",
                "FEATURE_DESCRIPTION": "La sicurezza di un partner che mantiene le promesse. Risultati concreti e misurabili.",
            },
            {
                "FEATURE_ICON": "\U0001f4a1",
                "FEATURE_TITLE": "Innovazione Continua",
                "FEATURE_DESCRIPTION": "Sempre aggiornati con le ultime tendenze e tecnologie del settore.",
            },
            {
                "FEATURE_ICON": "\U0001f310",
                "FEATURE_TITLE": "Approccio Globale",
                "FEATURE_DESCRIPTION": "Una visione internazionale con attenzione alle specificita' del mercato locale.",
            },
            {
                "FEATURE_ICON": "\U0001f4b0",
                "FEATURE_TITLE": "Rapporto Qualita'-Prezzo",
                "FEATURE_DESCRIPTION": "Investimenti intelligenti con un ritorno tangibile e misurabile nel tempo.",
            },
        ]

    def _fallback_testimonials(self) -> List[Dict[str, str]]:
        """Generate fallback testimonial items."""
        return [
            {
                "TESTIMONIAL_TEXT": "Un'esperienza straordinaria dall'inizio alla fine. Professionalita' e creativita' ai massimi livelli.",
                "TESTIMONIAL_AUTHOR": "Marco Rossi",
                "TESTIMONIAL_ROLE": "CEO, TechVenture",
                "TESTIMONIAL_INITIAL": "M",
            },
            {
                "TESTIMONIAL_TEXT": "Hanno trasformato la nostra visione in realta'. Il risultato ha superato ogni aspettativa.",
                "TESTIMONIAL_AUTHOR": "Laura Bianchi",
                "TESTIMONIAL_ROLE": "Direttrice Marketing",
                "TESTIMONIAL_INITIAL": "L",
            },
            {
                "TESTIMONIAL_TEXT": "Collaborazione impeccabile e risultati tangibili. Li consiglio senza esitazione.",
                "TESTIMONIAL_AUTHOR": "Andrea Verdi",
                "TESTIMONIAL_ROLE": "Imprenditore",
                "TESTIMONIAL_INITIAL": "A",
            },
        ]

    def _fallback_gallery(self) -> List[Dict[str, str]]:
        """Generate fallback gallery items with placeholder images."""
        items = []
        for i in range(1, 7):
            items.append({
                "GALLERY_IMAGE_URL": f"https://placehold.co/600x400/eee/999?text=Foto+{i}",
                "GALLERY_IMAGE_ALT": f"Immagine galleria {i}",
                "GALLERY_CAPTION": f"Progetto {i}",
            })
        return items

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

    def _inject_ai_images(
        self,
        texts: Dict[str, Any],
        generated_images: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Replace placehold.co URLs in texts dict with AI-generated image URLs.

        Only replaces URLs that contain 'placehold.co' so user-uploaded photos
        (injected later via _inject_user_photos) are not affected here.
        """
        def _is_placeholder(url: str) -> bool:
            return isinstance(url, str) and "placehold.co" in url

        def _get_image(section: str, index: int) -> Optional[str]:
            urls = generated_images.get(section, [])
            if index < len(urls):
                return urls[index]
            return None

        # Hero image
        hero = texts.get("hero", {})
        if isinstance(hero, dict) and _is_placeholder(hero.get("HERO_IMAGE_URL", "")):
            img = _get_image("hero", 0)
            if img:
                hero["HERO_IMAGE_URL"] = img

        # About image
        about = texts.get("about", {})
        if isinstance(about, dict) and _is_placeholder(about.get("ABOUT_IMAGE_URL", "")):
            img = _get_image("about", 0)
            if img:
                about["ABOUT_IMAGE_URL"] = img

        # Gallery images
        gallery = texts.get("gallery", {})
        if isinstance(gallery, dict):
            items = gallery.get("GALLERY_ITEMS", [])
            if isinstance(items, list):
                for i, item in enumerate(items):
                    if isinstance(item, dict) and _is_placeholder(item.get("GALLERY_IMAGE_URL", "")):
                        img = _get_image("gallery", i)
                        if img:
                            item["GALLERY_IMAGE_URL"] = img

        # Team member images
        team = texts.get("team", {})
        if isinstance(team, dict):
            members = team.get("TEAM_MEMBERS", [])
            if isinstance(members, list):
                for i, member in enumerate(members):
                    if isinstance(member, dict) and _is_placeholder(member.get("MEMBER_IMAGE_URL", "")):
                        img = _get_image("team", i)
                        if img:
                            member["MEMBER_IMAGE_URL"] = img

        # Services images (if present)
        services = texts.get("services", {})
        if isinstance(services, dict):
            svc_list = services.get("SERVICES", [])
            if isinstance(svc_list, list):
                for i, svc in enumerate(svc_list):
                    if isinstance(svc, dict) and _is_placeholder(svc.get("SERVICE_IMAGE_URL", "")):
                        img = _get_image("services", i)
                        if img:
                            svc["SERVICE_IMAGE_URL"] = img

        # Features image (if present)
        features = texts.get("features", {})
        if isinstance(features, dict) and _is_placeholder(features.get("FEATURES_IMAGE_URL", "")):
            img = _get_image("features", 0)
            if img:
                features["FEATURES_IMAGE_URL"] = img

        # CTA image (if present)
        cta = texts.get("cta", {})
        if isinstance(cta, dict) and _is_placeholder(cta.get("CTA_IMAGE_URL", "")):
            img = _get_image("cta", 0)
            if img:
                cta["CTA_IMAGE_URL"] = img

        # Contact image (if present)
        contact = texts.get("contact", {})
        if isinstance(contact, dict) and _is_placeholder(contact.get("CONTACT_IMAGE_URL", "")):
            img = _get_image("contact", 0)
            if img:
                contact["CONTACT_IMAGE_URL"] = img

        # Logos images
        logos = texts.get("logos", {})
        if isinstance(logos, dict):
            logo_items = logos.get("LOGOS_ITEMS", [])
            if isinstance(logo_items, list):
                for i, logo in enumerate(logo_items):
                    if isinstance(logo, dict) and _is_placeholder(logo.get("LOGO_IMAGE_URL", "")):
                        img = _get_image("logos", i)
                        if img:
                            logo["LOGO_IMAGE_URL"] = img

        return texts

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
        """Default theme if Kimi theme generation fails. Uses a vibrant palette, not boring defaults."""
        primary = "#7C3AED"  # Vibrant purple
        if style_preferences and style_preferences.get("primary_color"):
            primary = style_preferences["primary_color"]
        return {
            "primary_color": primary,
            "secondary_color": "#1E3A5F",
            "accent_color": "#F59E0B",
            "bg_color": "#FAF7F2",
            "bg_alt_color": "#F0EDE6",
            "text_color": "#1A1A2E",
            "text_muted_color": "#6B7280",
            "font_heading": "Space Grotesk",
            "font_heading_url": "Space+Grotesk:wght@400;600;700;800",
            "font_body": "DM Sans",
            "font_body_url": "DM+Sans:wght@400;500;600",
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
