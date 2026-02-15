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
import os
import random
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

# Reference HTML sites for quality injection
try:
    from app.services.reference_sites import get_reference_for_category
    _has_reference_sites = True
except Exception:
    _has_reference_sites = False

# URL analyzer for reference websites
try:
    from app.services.url_analyzer import analyze_reference_url, format_analysis_for_prompt
    _has_url_analyzer = True
except Exception:
    _has_url_analyzer = False

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[int, str, Optional[Dict[str, Any]]], None]]

# =========================================================
# VARIETY ENGINE: Personality, mood, and creative direction pools.
# Each generation randomly picks from these pools to ensure
# every site feels unique even for the same template style.
# =========================================================

# Creative personality archetypes that shape ALL copy tone
PERSONALITY_POOL = [
    {
        "name": "provocative",
        "directive": "You are PROVOCATIVE. Challenge assumptions. Use contrasts, paradoxes, and unexpected juxtapositions. 'Il Caos che Crea Ordine'. Make the reader stop and think.",
        "headline_style": "contrasting, paradoxical, thought-provoking",
    },
    {
        "name": "poetic",
        "directive": "You are POETIC. Write like a modern poet. Use metaphors drawn from nature, art, and human emotion. 'Dove il Vento Incontra la Pietra'. Rhythm matters — alternate short and flowing.",
        "headline_style": "lyrical, metaphorical, evocative",
    },
    {
        "name": "minimal",
        "directive": "You are MINIMALIST. Less is everything. Each word is surgical. No adjective without purpose. 'Meno. Meglio.' White space is your friend. Think Dieter Rams meets copywriting.",
        "headline_style": "ultra-short, punchy, stark",
    },
    {
        "name": "bold",
        "directive": "You are BOLD and LOUD. Capital energy. Confidence that borders on audacity. 'Noi Non Seguiamo Tendenze. Le Creiamo.' Every sentence should feel like a manifesto.",
        "headline_style": "declarative, confident, manifesto-like",
    },
    {
        "name": "storytelling",
        "directive": "You are a STORYTELLER. Every section is a chapter. Create narrative tension — hint at a journey, a transformation, a before/after. 'C era un Vuoto. Poi Siamo Arrivati Noi.' Hook the reader emotionally.",
        "headline_style": "narrative, hook-driven, emotional arc",
    },
    {
        "name": "data-driven",
        "directive": "You are DATA-DRIVEN. Lead with proof, numbers, evidence. '847 Progetti. Zero Compromessi.' Use specific numbers, percentages, timeframes. Credibility through precision.",
        "headline_style": "numbers-first, evidence-based, precise",
    },
    {
        "name": "emotional",
        "directive": "You are DEEPLY EMOTIONAL. Write from the heart. What does the customer FEEL? Fear of missing out? Joy of discovery? Relief? 'Finalmente, Qualcuno Che Capisce.' Touch nerves.",
        "headline_style": "empathetic, feelings-first, intimate",
    },
    {
        "name": "visionary",
        "directive": "You are a VISIONARY. Write from the future. Paint a picture of what could be. 'Il Futuro Non Aspetta. Noi Nemmeno.' Aspirational, forward-looking, transformative.",
        "headline_style": "future-oriented, aspirational, transformative",
    },
    {
        "name": "irreverent",
        "directive": "You are IRREVERENT. Break the mold. Use unexpected humor, informal tone, and anti-corporate language. 'Basta Siti Noiosi.' Be the brand that winks at the reader.",
        "headline_style": "witty, informal, rule-breaking",
    },
    {
        "name": "luxurious",
        "directive": "You are LUXURIOUS. Every word drips exclusivity. Understated elegance. 'Per Chi Non Si Accontenta.' Use words like esclusivo, raffinato, senza tempo, artigianale. Appeal to taste, not price.",
        "headline_style": "refined, exclusive, understated elegance",
    },
    {
        "name": "scientific",
        "directive": "You are SCIENTIFIC. Precision meets clarity. Explain complex things simply. 'La Scienza Dietro Ogni Dettaglio.' Use structured arguments, cause-effect chains, and evidence.",
        "headline_style": "analytical, precise, clarity-first",
    },
    {
        "name": "warm",
        "directive": "You are WARM and HUMAN. Write like a trusted friend giving honest advice. 'Ti Meriti di Meglio.' Conversational, genuine, zero corporate veneer. Use 'tu' form naturally.",
        "headline_style": "conversational, genuine, friendly",
    },
]

# Color mood presets — injected into theme prompt to push the AI toward diverse palettes
COLOR_MOOD_POOL = [
    {"mood": "Sunset Warmth", "hint": "Think golden hour: amber #F59E0B, terracotta #C2410C, warm cream #FFFBEB, deep mahogany #7C2D12. Warm, inviting, organic."},
    {"mood": "Ocean Depth", "hint": "Think deep sea: teal #0D9488, navy #0C4A6E, seafoam #CCFBF1, coral accent #FB7185. Cool, professional, trustworthy."},
    {"mood": "Forest Calm", "hint": "Think ancient forest: emerald #059669, sage #D1FAE5, bark brown #78350F, golden light #FDE68A. Natural, grounded, sustainable."},
    {"mood": "Electric Night", "hint": "Think neon city: electric purple #A855F7, hot pink #EC4899, dark navy #0F172A, cyan spark #22D3EE. Bold, modern, energetic."},
    {"mood": "Desert Minimal", "hint": "Think desert sand: sand #D4A574, terracotta #9A3412, bone white #FEF3C7, indigo sky #4338CA. Earthy, warm, Mediterranean."},
    {"mood": "Nordic Clean", "hint": "Think Scandinavian: slate blue #475569, ice white #F8FAFC, pine green #166534, blush #FECDD3. Clean, crisp, functional."},
    {"mood": "Art Deco Luxe", "hint": "Think 1920s glamour: gold #D4AF37, black #1C1917, cream #FFFDD0, emerald #047857. Opulent, dramatic, sophisticated."},
    {"mood": "Candy Pop", "hint": "Think playful: bubblegum #F472B6, lavender #C4B5FD, mint #A7F3D0, sunny yellow #FDE047. Fun, youthful, creative."},
    {"mood": "Monochrome Power", "hint": "Think high contrast: charcoal #1E293B, silver #CBD5E1, white #FFFFFF, one vivid accent (red #EF4444 OR orange #F97316). Powerful, dramatic, sophisticated."},
    {"mood": "Terracotta Earth", "hint": "Think Italian countryside: burnt sienna #A0522D, olive #808000, cream #FAF0E6, dusty rose #BC8F8F. Warm, artisanal, authentic."},
    {"mood": "Cyber Fresh", "hint": "Think tech startup: lime #84CC16, dark slate #1E1B4B, electric blue #3B82F6, white #F5F5F5. Fresh, innovative, dynamic."},
    {"mood": "Royal Velvet", "hint": "Think regal: deep burgundy #831843, royal purple #581C87, gold #B8860B, ivory #FFFFF0. Rich, prestigious, commanding."},
]

# Extended font pairings pool — more options to reduce repetition
FONT_PAIRING_POOL = [
    {"heading": "Playfair Display", "body": "Inter", "personality": "ELEGANT/LUXURY", "url_h": "Playfair+Display:wght@400;600;700;800", "url_b": "Inter:wght@400;500;600"},
    {"heading": "Space Grotesk", "body": "DM Sans", "personality": "MODERN TECH/SAAS", "url_h": "Space+Grotesk:wght@400;600;700", "url_b": "DM+Sans:wght@400;500;600"},
    {"heading": "Sora", "body": "Inter", "personality": "CLEAN STARTUP", "url_h": "Sora:wght@400;600;700;800", "url_b": "Inter:wght@400;500;600"},
    {"heading": "DM Serif Display", "body": "Plus Jakarta Sans", "personality": "EDITORIAL/BLOG", "url_h": "DM+Serif+Display:wght@400", "url_b": "Plus+Jakarta+Sans:wght@400;500;600;700"},
    {"heading": "Outfit", "body": "DM Sans", "personality": "GEOMETRIC MODERN", "url_h": "Outfit:wght@400;600;700;800", "url_b": "DM+Sans:wght@400;500;600"},
    {"heading": "Fraunces", "body": "Nunito Sans", "personality": "WARM ARTISAN", "url_h": "Fraunces:wght@400;600;700;800", "url_b": "Nunito+Sans:wght@400;500;600;700"},
    {"heading": "Epilogue", "body": "Source Sans 3", "personality": "PROFESSIONAL", "url_h": "Epilogue:wght@400;600;700;800", "url_b": "Source+Sans+3:wght@400;500;600"},
    {"heading": "Bricolage Grotesque", "body": "Inter", "personality": "PLAYFUL MODERN", "url_h": "Bricolage+Grotesque:wght@400;600;700;800", "url_b": "Inter:wght@400;500;600"},
    {"heading": "Instrument Serif", "body": "Instrument Sans", "personality": "REFINED EDITORIAL", "url_h": "Instrument+Serif:wght@400", "url_b": "Instrument+Sans:wght@400;500;600;700"},
    {"heading": "Libre Baskerville", "body": "Karla", "personality": "CLASSIC LITERARY", "url_h": "Libre+Baskerville:wght@400;700", "url_b": "Karla:wght@400;500;600;700"},
    {"heading": "Unbounded", "body": "Figtree", "personality": "FUTURISTIC BOLD", "url_h": "Unbounded:wght@400;600;700;800;900", "url_b": "Figtree:wght@400;500;600;700"},
    {"heading": "Cormorant Garamond", "body": "Lato", "personality": "TIMELESS LUXURY", "url_h": "Cormorant+Garamond:wght@400;600;700", "url_b": "Lato:wght@400;700"},
    {"heading": "Archivo Black", "body": "Work Sans", "personality": "IMPACT INDUSTRIAL", "url_h": "Archivo+Black", "url_b": "Work+Sans:wght@400;500;600"},
    {"heading": "Josefin Sans", "body": "Mulish", "personality": "SLEEK GEOMETRIC", "url_h": "Josefin+Sans:wght@400;600;700", "url_b": "Mulish:wght@400;500;600;700"},
    {"heading": "Bitter", "body": "Poppins", "personality": "WARM PROFESSIONAL", "url_h": "Bitter:wght@400;600;700;800", "url_b": "Poppins:wght@400;500;600"},
    {"heading": "Albert Sans", "body": "IBM Plex Sans", "personality": "SWISS CLEAN", "url_h": "Albert+Sans:wght@400;600;700;800", "url_b": "IBM+Plex+Sans:wght@400;500;600"},
]

# Fallback theme palettes — used when Kimi fails, each is distinct
FALLBACK_THEME_POOL = [
    {
        "primary_color": "#7C3AED", "secondary_color": "#1E3A5F", "accent_color": "#F59E0B",
        "bg_color": "#FAF7F2", "bg_alt_color": "#F0EDE6", "text_color": "#1A1A2E", "text_muted_color": "#6B7280",
        "font_heading": "Space Grotesk", "font_heading_url": "Space+Grotesk:wght@400;600;700;800",
        "font_body": "DM Sans", "font_body_url": "DM+Sans:wght@400;500;600",
    },
    {
        "primary_color": "#0D9488", "secondary_color": "#0C4A6E", "accent_color": "#FB7185",
        "bg_color": "#F0FDFA", "bg_alt_color": "#CCFBF1", "text_color": "#0F172A", "text_muted_color": "#64748B",
        "font_heading": "Sora", "font_heading_url": "Sora:wght@400;600;700;800",
        "font_body": "Inter", "font_body_url": "Inter:wght@400;500;600",
    },
    {
        "primary_color": "#DC2626", "secondary_color": "#1E293B", "accent_color": "#FBBF24",
        "bg_color": "#FFFBEB", "bg_alt_color": "#FEF3C7", "text_color": "#1C1917", "text_muted_color": "#78716C",
        "font_heading": "DM Serif Display", "font_heading_url": "DM+Serif+Display:wght@400",
        "font_body": "Plus Jakarta Sans", "font_body_url": "Plus+Jakarta+Sans:wght@400;500;600;700",
    },
    {
        "primary_color": "#059669", "secondary_color": "#78350F", "accent_color": "#F472B6",
        "bg_color": "#ECFDF5", "bg_alt_color": "#D1FAE5", "text_color": "#064E3B", "text_muted_color": "#6B7280",
        "font_heading": "Fraunces", "font_heading_url": "Fraunces:wght@400;600;700;800",
        "font_body": "Nunito Sans", "font_body_url": "Nunito+Sans:wght@400;500;600;700",
    },
    {
        "primary_color": "#7C2D12", "secondary_color": "#4338CA", "accent_color": "#22D3EE",
        "bg_color": "#FEF3C7", "bg_alt_color": "#FDE68A", "text_color": "#1C1917", "text_muted_color": "#92400E",
        "font_heading": "Playfair Display", "font_heading_url": "Playfair+Display:wght@400;600;700;800",
        "font_body": "Lato", "font_body_url": "Lato:wght@400;700",
    },
    {
        "primary_color": "#A855F7", "secondary_color": "#EC4899", "accent_color": "#22D3EE",
        "bg_color": "#0F172A", "bg_alt_color": "#1E293B", "text_color": "#F1F5F9", "text_muted_color": "#94A3B8",
        "font_heading": "Outfit", "font_heading_url": "Outfit:wght@400;600;700;800",
        "font_body": "DM Sans", "font_body_url": "DM+Sans:wght@400;500;600",
    },
    {
        "primary_color": "#B8860B", "secondary_color": "#1C1917", "accent_color": "#047857",
        "bg_color": "#FFFDD0", "bg_alt_color": "#FEF9C3", "text_color": "#1C1917", "text_muted_color": "#78716C",
        "font_heading": "Cormorant Garamond", "font_heading_url": "Cormorant+Garamond:wght@400;600;700",
        "font_body": "Lato", "font_body_url": "Lato:wght@400;700",
    },
    {
        "primary_color": "#831843", "secondary_color": "#581C87", "accent_color": "#FBBF24",
        "bg_color": "#FFFFF0", "bg_alt_color": "#FEF3C7", "text_color": "#1E1B4B", "text_muted_color": "#6B7280",
        "font_heading": "Libre Baskerville", "font_heading_url": "Libre+Baskerville:wght@400;700",
        "font_body": "Karla", "font_body_url": "Karla:wght@400;500;600;700",
    },
]


def _pick_variety_context() -> Dict[str, Any]:
    """Pick random personality, color mood, and font pairing for this generation."""
    return {
        "personality": random.choice(PERSONALITY_POOL),
        "color_mood": random.choice(COLOR_MOOD_POOL),
        "font_pairing": random.choice(FONT_PAIRING_POOL),
    }


# =========================================================
# HIGH-QUALITY UNSPLASH PHOTO POOLS (by business category)
# These replace ugly placehold.co grey boxes when no user photos
# or AI-generated images are available. Free to use via Unsplash Source.
# =========================================================
_UNSPLASH_PHOTOS: Dict[str, Dict[str, List[str]]] = {
    "restaurant": {
        "hero": [
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1581299894007-aaa50297cf16?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop",
        ],
    },
    "saas": {
        "hero": [
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1551434678-e076c223a692?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop",
        ],
    },
    "portfolio": {
        "hero": [
            "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1545665277-5937489d95eb?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1558655146-d09347e92766?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1572044162444-ad60f128bdea?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1626785774573-4b799315345d?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop",
        ],
    },
    "ecommerce": {
        "hero": [
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1556742111-a301076d9d18?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
        ],
    },
    "business": {
        "hero": [
            "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1497215842964-222b430dc094?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop",
        ],
    },
    "blog": {
        "hero": [
            "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1432821596592-e2c18b78144f?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1501504905252-473c47e087f8?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop",
        ],
    },
    "event": {
        "hero": [
            "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&h=800&fit=crop",
            "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=1200&h=800&fit=crop",
        ],
        "gallery": [
            "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?w=600&h=400&fit=crop",
            "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&h=400&fit=crop",
        ],
        "about": [
            "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=800&h=600&fit=crop",
        ],
        "team": [
            "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&h=300&fit=crop",
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300&h=300&fit=crop",
        ],
    },
}
# Fallback for unknown categories
_UNSPLASH_PHOTOS["default"] = _UNSPLASH_PHOTOS["business"]


def _get_stock_photos(category: str) -> Dict[str, List[str]]:
    """Get stock photo URLs for a business category. Picks from pool with shuffling."""
    # Detect category from template_style_id prefix
    for cat in _UNSPLASH_PHOTOS:
        if cat != "default" and category and category.startswith(cat):
            photos = _UNSPLASH_PHOTOS[cat]
            break
    else:
        photos = _UNSPLASH_PHOTOS["default"]
    # Return shuffled copies so each generation gets different photos
    return {k: random.sample(v, len(v)) for k, v in photos.items()}


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

# =========================================================
# Randomized variant pools for variety.
# Each style maps to a POOL of 2-3 compatible variants per section.
# At generation time, one variant is randomly chosen from the pool.
# STYLE_VARIANT_MAP above is kept as deterministic fallback.
# =========================================================
STYLE_VARIANT_POOL: Dict[str, Dict[str, List[str]]] = {
    # --- Restaurant ---
    "restaurant-elegant": {
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-typewriter-01"],
        "about": ["about-magazine-01", "about-image-showcase-01", "about-split-scroll-01"],
        "services": ["services-alternating-rows-01", "services-minimal-list-01", "services-icon-list-01"],
        "gallery": ["gallery-spotlight-01", "gallery-lightbox-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01"],
        "contact": ["contact-minimal-01", "contact-form-01", "contact-minimal-02"],
        "footer": ["footer-centered-01", "footer-minimal-02", "footer-sitemap-01"],
    },
    "restaurant-cozy": {
        "hero": ["hero-organic-01", "hero-typewriter-01", "hero-classic-01"],
        "about": ["about-split-scroll-01", "about-image-showcase-01", "about-magazine-01"],
        "services": ["services-icon-list-01", "services-minimal-list-01", "services-alternating-rows-01"],
        "gallery": ["gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01"],
        "testimonials": ["testimonials-card-stack-01", "testimonials-spotlight-01", "testimonials-carousel-01"],
        "contact": ["contact-card-01", "contact-minimal-01", "contact-form-01"],
        "footer": ["footer-multi-col-01", "footer-centered-01", "footer-minimal-02"],
    },
    "restaurant-modern": {
        "hero": ["hero-zen-01", "hero-parallax-01", "hero-glassmorphism-01"],
        "about": ["about-bento-01", "about-timeline-02", "about-split-cards-01"],
        "services": ["services-tabs-01", "services-hover-reveal-01", "services-bento-02"],
        "gallery": ["gallery-filmstrip-01", "gallery-masonry-01"],
        "testimonials": ["testimonials-marquee-01", "testimonials-masonry-01", "testimonials-card-stack-01"],
        "contact": ["contact-modern-form-01", "contact-split-map-01", "contact-card-01"],
        "footer": ["footer-minimal-02", "footer-gradient-01", "footer-multi-col-01"],
    },
    # --- SaaS / Landing Page ---
    "saas-gradient": {
        "hero": ["hero-gradient-03", "hero-animated-shapes-01", "hero-parallax-01"],
        "about": ["about-timeline-02", "about-bento-01", "about-split-cards-01"],
        "services": ["services-hover-reveal-01", "services-bento-02", "services-hover-expand-01"],
        "features": ["features-bento-grid-01", "features-hover-cards-01", "features-tabs-01"],
        "testimonials": ["testimonials-marquee-01", "testimonials-masonry-01", "testimonials-carousel-01"],
        "cta": ["cta-gradient-animated-01", "cta-gradient-banner-01", "cta-floating-card-01"],
        "contact": ["contact-modern-form-01", "contact-split-map-01", "contact-card-01"],
        "footer": ["footer-gradient-01", "footer-mega-01", "footer-multi-col-01"],
    },
    "saas-clean": {
        "hero": ["hero-centered-02", "hero-split-01", "hero-glassmorphism-01"],
        "about": ["about-alternating-01", "about-image-showcase-01", "about-timeline-02"],
        "services": ["services-cards-grid-01", "services-process-steps-01", "services-tabs-01"],
        "features": ["features-icons-grid-01", "features-alternating-01", "features-icon-showcase-01"],
        "testimonials": ["testimonials-grid-01", "testimonials-carousel-01", "testimonials-spotlight-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01"],
        "contact": ["contact-form-01", "contact-modern-form-01", "contact-minimal-01"],
        "footer": ["footer-sitemap-01", "footer-multi-col-01", "footer-centered-01"],
    },
    "saas-dark": {
        "hero": ["hero-dark-bold-01", "hero-neon-01", "hero-animated-shapes-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-01"],
        "services": ["services-bento-02", "services-hover-expand-01", "services-hover-reveal-01"],
        "features": ["features-hover-cards-01", "features-bento-grid-01", "features-tabs-01"],
        "testimonials": ["testimonials-masonry-01", "testimonials-marquee-01", "testimonials-card-stack-01"],
        "contact": ["contact-minimal-02", "contact-modern-form-01", "contact-card-01"],
        "footer": ["footer-mega-01", "footer-gradient-01", "footer-sitemap-01"],
    },
    # --- Portfolio ---
    "portfolio-gallery": {
        "hero": ["hero-editorial-01", "hero-zen-01", "hero-typewriter-01"],
        "about": ["about-image-showcase-01", "about-magazine-01", "about-split-scroll-01"],
        "gallery": ["gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01"],
        "services": ["services-minimal-list-01", "services-alternating-rows-01", "services-icon-list-01"],
        "testimonials": ["testimonials-grid-01", "testimonials-spotlight-01", "testimonials-carousel-01"],
        "contact": ["contact-minimal-01", "contact-minimal-02", "contact-form-01"],
        "footer": ["footer-minimal-02", "footer-centered-01"],
    },
    "portfolio-minimal": {
        "hero": ["hero-zen-01", "hero-typewriter-01", "hero-editorial-01"],
        "about": ["about-alternating-01", "about-split-scroll-01", "about-image-showcase-01"],
        "gallery": ["gallery-lightbox-01", "gallery-spotlight-01", "gallery-masonry-01"],
        "contact": ["contact-minimal-02", "contact-minimal-01", "contact-form-01"],
        "footer": ["footer-centered-01", "footer-minimal-02"],
    },
    "portfolio-creative": {
        "hero": ["hero-brutalist-01", "hero-animated-shapes-01", "hero-neon-01"],
        "about": ["about-bento-01", "about-split-cards-01", "about-timeline-02"],
        "gallery": ["gallery-spotlight-01", "gallery-filmstrip-01", "gallery-masonry-01"],
        "services": ["services-hover-expand-01", "services-hover-reveal-01", "services-bento-02"],
        "contact": ["contact-card-01", "contact-modern-form-01", "contact-split-map-01"],
        "footer": ["footer-gradient-01", "footer-mega-01", "footer-multi-col-01"],
    },
    # --- E-commerce / Shop ---
    "ecommerce-modern": {
        "hero": ["hero-split-01", "hero-parallax-01", "hero-glassmorphism-01"],
        "about": ["about-image-showcase-01", "about-bento-01", "about-alternating-01"],
        "services": ["services-cards-grid-01", "services-hover-reveal-01", "services-tabs-01"],
        "gallery": ["gallery-masonry-01", "gallery-filmstrip-01", "gallery-lightbox-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-grid-01", "testimonials-marquee-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01"],
        "footer": ["footer-multi-col-01", "footer-mega-01", "footer-sitemap-01"],
    },
    "ecommerce-luxury": {
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-video-bg-01"],
        "about": ["about-magazine-01", "about-image-showcase-01", "about-split-scroll-01"],
        "services": ["services-alternating-rows-01", "services-minimal-list-01", "services-icon-list-01"],
        "gallery": ["gallery-spotlight-01", "gallery-lightbox-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01"],
        "contact": ["contact-minimal-01", "contact-form-01", "contact-minimal-02"],
        "footer": ["footer-centered-01", "footer-minimal-02", "footer-sitemap-01"],
    },
    # --- Business ---
    "business-corporate": {
        "hero": ["hero-split-01", "hero-classic-01", "hero-video-bg-01"],
        "about": ["about-alternating-01", "about-image-showcase-01", "about-timeline-02"],
        "services": ["services-cards-grid-01", "services-process-steps-01", "services-tabs-01"],
        "features": ["features-comparison-01", "features-icons-grid-01", "features-alternating-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-grid-01", "testimonials-spotlight-01"],
        "contact": ["contact-form-01", "contact-split-map-01", "contact-modern-form-01"],
        "footer": ["footer-mega-01", "footer-sitemap-01", "footer-multi-col-01"],
    },
    "business-trust": {
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-split-01"],
        "about": ["about-timeline-01", "about-magazine-01", "about-image-showcase-01"],
        "services": ["services-process-steps-01", "services-alternating-rows-01", "services-cards-grid-01"],
        "team": ["team-grid-01", "team-carousel-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01"],
        "contact": ["contact-split-map-01", "contact-form-01", "contact-modern-form-01"],
        "footer": ["footer-sitemap-01", "footer-mega-01", "footer-multi-col-01"],
    },
    "business-fresh": {
        "hero": ["hero-gradient-03", "hero-animated-shapes-01", "hero-glassmorphism-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-02"],
        "services": ["services-hover-expand-01", "services-hover-reveal-01", "services-bento-02"],
        "features": ["features-alternating-01", "features-bento-grid-01", "features-hover-cards-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-marquee-01", "testimonials-masonry-01"],
        "cta": ["cta-split-image-01", "cta-gradient-animated-01", "cta-floating-card-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01"],
        "footer": ["footer-multi-col-01", "footer-gradient-01", "footer-mega-01"],
    },
    # --- Blog / Magazine ---
    "blog-editorial": {
        "hero": ["hero-editorial-01", "hero-typewriter-01", "hero-zen-01"],
        "about": ["about-alternating-01", "about-magazine-01", "about-split-scroll-01"],
        "services": ["services-minimal-list-01", "services-icon-list-01", "services-alternating-rows-01"],
        "gallery": ["gallery-lightbox-01", "gallery-spotlight-01", "gallery-masonry-01"],
        "contact": ["contact-card-01", "contact-minimal-01", "contact-form-01"],
        "footer": ["footer-sitemap-01", "footer-centered-01", "footer-multi-col-01"],
    },
    "blog-dark": {
        "hero": ["hero-neon-01", "hero-dark-bold-01", "hero-brutalist-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-01"],
        "services": ["services-hover-reveal-01", "services-bento-02", "services-hover-expand-01"],
        "gallery": ["gallery-filmstrip-01", "gallery-masonry-01"],
        "contact": ["contact-minimal-02", "contact-card-01", "contact-modern-form-01"],
        "footer": ["footer-gradient-01", "footer-mega-01", "footer-multi-col-01"],
    },
    # --- Evento / Community ---
    "event-vibrant": {
        "hero": ["hero-animated-shapes-01", "hero-gradient-03", "hero-parallax-01"],
        "about": ["about-bento-01", "about-timeline-02", "about-split-cards-01"],
        "services": ["services-tabs-01", "services-hover-expand-01", "services-bento-02"],
        "team": ["team-carousel-01", "team-grid-01"],
        "cta": ["cta-gradient-animated-01", "cta-gradient-banner-01", "cta-floating-card-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01"],
        "footer": ["footer-gradient-01", "footer-mega-01", "footer-multi-col-01"],
    },
    "event-minimal": {
        "hero": ["hero-centered-02", "hero-typewriter-01", "hero-zen-01"],
        "about": ["about-timeline-01", "about-alternating-01", "about-split-scroll-01"],
        "services": ["services-process-steps-01", "services-cards-grid-01", "services-icon-list-01"],
        "team": ["team-grid-01", "team-carousel-01"],
        "contact": ["contact-form-01", "contact-minimal-01", "contact-minimal-02"],
        "footer": ["footer-minimal-02", "footer-centered-01", "footer-sitemap-01"],
    },
}

# Randomized pools for default section types (faq, pricing, stats, etc.)
_DEFAULT_SECTION_VARIANT_POOLS: Dict[str, List[str]] = {
    "faq": ["faq-accordion-01", "faq-accordion-02", "faq-two-column-01", "faq-search-01"],
    "pricing": ["pricing-cards-01", "pricing-toggle-01", "pricing-toggle-02", "pricing-comparison-01", "pricing-minimal-01"],
    "stats": ["stats-counters-01"],
    "logos": ["logos-marquee-01"],
    "process": ["process-steps-01", "process-horizontal-01", "process-cards-01"],
    "timeline": ["timeline-vertical-01"],
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
        reference_url_context: str = "",
        variety_context: Optional[Dict[str, Any]] = None,
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

        # Inject reference URL analysis (colors and fonts from a real site)
        if reference_url_context:
            palette_hint += f"\n{reference_url_context}\nMatch these colors and fonts closely.\n"

        # --- VARIETY: inject random color mood and font suggestion ---
        variety_hint = ""
        if variety_context:
            color_mood = variety_context.get("color_mood", {})
            font_pair = variety_context.get("font_pairing", {})
            variety_hint = f"""
=== COLOR MOOD DIRECTION (follow this closely) ===
Design mood: "{color_mood.get('mood', 'Modern Bold')}"
{color_mood.get('hint', '')}
Adapt this mood to the business, but keep the color FEELING.

=== SUGGESTED FONT PAIRING (use this unless it clashes with the business) ===
Heading: "{font_pair.get('heading', 'Space Grotesk')}" ({font_pair.get('personality', 'MODERN')})
Body: "{font_pair.get('body', 'DM Sans')}"
font_heading_url: "{font_pair.get('url_h', 'Space+Grotesk:wght@400;600;700')}"
font_body_url: "{font_pair.get('url_b', 'DM+Sans:wght@400;500;600')}"
"""

        # Build the full font pairings list dynamically from the pool
        # Shuffle to prevent the AI from always picking the first option
        shuffled_fonts = random.sample(FONT_PAIRING_POOL, min(8, len(FONT_PAIRING_POOL)))
        font_list_str = "\n".join(
            f'{fp["personality"]}: "{fp["heading"]}" (heading) + "{fp["body"]}" (body)'
            for fp in shuffled_fonts
        )

        prompt = f"""You are a Dribbble/Awwwards-level UI designer. Generate a STUNNING, BOLD color palette and typography for a website.
Return ONLY valid JSON, no markdown, no explanation.

BUSINESS: {business_name} - {business_description[:500]}
{style_hint}
{palette_hint}
{variety_hint}
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

{font_list_str}

- NEVER use the same font for heading and body
- NEVER use Inter, Roboto, Open Sans, or Arial for headings — they lack personality
- Heading fonts must have VISUAL CHARACTER: serifs, distinctive letter shapes, or bold geometric forms
- Body fonts must be CLEAN and highly readable at 16px
- font_heading_url format: "FontName:wght@400;600;700;800" (replace spaces with +)
- font_body_url format: "FontName:wght@400;500;600"

=== UNIQUENESS DIRECTIVE (CRITICAL) ===
IMPORTANT: Generate a UNIQUE palette. Do NOT repeat common web palettes.
Use the business personality to pick unexpected but fitting color combinations.
Each generation must feel fresh and different from the previous ones.
Randomization seed: {random.randint(1000, 9999)}
Pick a font pairing you haven't used recently. Surprise the viewer.

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
                temperature=0.75, top_p=0.95, json_mode=True,
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
        reference_url_context: str = "",
        variety_context: Optional[Dict[str, Any]] = None,
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

        # Inject reference URL analysis (tone and content structure from a real site)
        if reference_url_context:
            knowledge_hint += f"\n{reference_url_context}\nMatch this site's tone and content structure.\n"

        # Inject reference HTML so AI can see the quality level expected
        reference_hint = ""
        if _has_reference_sites:
            try:
                category_label = ""
                if business_description:
                    # Extract category from first line of description (e.g., "Template: Restaurant - Stile: elegant")
                    first_line = business_description.split("\n")[0].lower()
                    for cat in ["restaurant", "ristorante", "saas", "tech", "portfolio", "creative", "business", "corporate", "ecommerce", "shop", "blog", "event"]:
                        if cat in first_line:
                            category_label = cat
                            break
                if not category_label:
                    category_label = "business"
                ref_html = get_reference_for_category(category_label)
                if ref_html:
                    # Truncate to keep token count reasonable
                    reference_hint = f"\n\n=== REFERENCE QUALITY LEVEL (your output must match this design sophistication) ===\nStudy this professional HTML carefully. Notice: gradient backgrounds, generous spacing (py-32), hover effects, decorative elements, specific compelling copy, emoji icons, shadow effects. YOUR generated content must achieve THIS level of design polish.\n{ref_html[:3000]}\n=== END REFERENCE ===\n"
            except Exception:
                pass

        prompt = f"""You are Italy's most awarded copywriter — think Oliviero Toscani meets Apple. You write text for websites that win design awards.{knowledge_hint}{reference_hint}
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

=== CREATIVE PERSONALITY (CRITICAL — this defines the ENTIRE tone of the site) ===
{variety_context["personality"]["directive"] if variety_context else random.choice(PERSONALITY_POOL)["directive"]}
Headline style: {variety_context["personality"]["headline_style"] if variety_context else "varied and surprising"}
EVERY piece of text — headlines, subtitles, descriptions, CTAs — must reflect this personality.
Do NOT write generic copy that ignores the personality. The personality is your creative brief.
Randomization seed: {random.randint(10000, 99999)}

Return this JSON (include only the sections listed above):
{{
  "meta": {{
    "title": "Page title (max 60 chars)",
    "description": "Meta description (max 155 chars)",
    "og_title": "OG title",
    "og_description": "OG description"
  }},
  "hero": {{
    "HERO_TITLE": "Headline impattante (max 8 parole, MIN 3 parole)",
    "HERO_SUBTITLE": "Sottotitolo evocativo (MIN 15 parole, 2-3 frasi che creano desiderio)",
    "HERO_CTA_TEXT": "Testo bottone CTA (3-5 parole, verbo d'azione)",
    "HERO_CTA_URL": "#contact",
    "HERO_IMAGE_URL": "https://placehold.co/800x600/{{primary_color_no_hash}}/white?text={business_name}",
    "HERO_IMAGE_ALT": "Descrizione immagine specifica"
  }},
  "about": {{
    "ABOUT_TITLE": "Titolo sezione (evocativo, NO 'Chi Siamo')",
    "ABOUT_SUBTITLE": "Sottotitolo (MIN 10 parole)",
    "ABOUT_TEXT": "MIN 40 parole: racconta la storia/missione con dettagli specifici, emozioni, visione futura",
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
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}},
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}},
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}}
    ]
  }},
  "features": {{
    "FEATURES_TITLE": "Titolo sezione",
    "FEATURES_SUBTITLE": "Sottotitolo",
    "FEATURES": [
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}},
      {{"FEATURE_ICON": "emoji unico", "FEATURE_TITLE": "Feature (2-4 parole)", "FEATURE_DESCRIPTION": "MIN 12 parole: cosa ottiene l'utente"}}
    ]
  }},
  "testimonials": {{
    "TESTIMONIALS_TITLE": "Titolo sezione",
    "TESTIMONIALS": [
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: storia specifica con dettagli, emozioni, risultati concreti", "TESTIMONIAL_AUTHOR": "Nome e Cognome realistico italiano", "TESTIMONIAL_ROLE": "Ruolo specifico (es: CEO di NomeDitta)", "TESTIMONIAL_INITIAL": "N"}},
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: esperienza unica, diversa dalla precedente", "TESTIMONIAL_AUTHOR": "Nome e Cognome", "TESTIMONIAL_ROLE": "Ruolo specifico", "TESTIMONIAL_INITIAL": "N"}},
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: racconto con before/after, numeri o dettagli specifici", "TESTIMONIAL_AUTHOR": "Nome e Cognome", "TESTIMONIAL_ROLE": "Ruolo specifico", "TESTIMONIAL_INITIAL": "N"}}
    ]
  }},
  "cta": {{
    "CTA_TITLE": "Headline CTA urgente e persuasiva (4-8 parole)",
    "CTA_SUBTITLE": "MIN 12 parole: motiva all'azione con beneficio chiaro",
    "CTA_BUTTON_TEXT": "Verbo d'azione + risultato (3-5 parole)",
    "CTA_BUTTON_URL": "#contact"
  }},
  "contact": {{
    "CONTACT_TITLE": "Titolo sezione (invitante, NO 'Contattaci')",
    "CONTACT_SUBTITLE": "MIN 10 parole: sottotitolo che invoglia a scrivere",
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
      {{"MEMBER_NAME": "Nome Cognome realistico", "MEMBER_ROLE": "Ruolo specifico (es: Direttore Creativo)", "MEMBER_IMAGE_URL": "https://placehold.co/300x300/eee/999?text=Team", "MEMBER_BIO": "MIN 15 parole: personalita, passioni, competenze uniche"}},
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo specifico", "MEMBER_IMAGE_URL": "https://placehold.co/300x300/eee/999?text=Team", "MEMBER_BIO": "MIN 15 parole: storia personale e approccio al lavoro"}},
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo specifico", "MEMBER_IMAGE_URL": "https://placehold.co/300x300/eee/999?text=Team", "MEMBER_BIO": "MIN 15 parole: background e contributo al team"}}
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

=== CRITICAL JSON STRUCTURE RULES (violating these = BROKEN website) ===
1. The "SERVICES" key MUST be an array [...] of objects, each with EXACTLY these keys: "SERVICE_ICON", "SERVICE_TITLE", "SERVICE_DESCRIPTION". NOT "ICON"/"TITLE"/"DESCRIPTION". NOT "service_icon". EXACTLY "SERVICE_ICON", "SERVICE_TITLE", "SERVICE_DESCRIPTION". Include at LEAST 3 items.
2. The "FEATURES" key MUST be an array [...] of objects, each with EXACTLY: "FEATURE_ICON", "FEATURE_TITLE", "FEATURE_DESCRIPTION". At LEAST 4 items.
3. The "TESTIMONIALS" key MUST be an array [...] of objects, each with EXACTLY: "TESTIMONIAL_TEXT", "TESTIMONIAL_AUTHOR", "TESTIMONIAL_ROLE", "TESTIMONIAL_INITIAL". At LEAST 3 items.
4. The "GALLERY_ITEMS" key MUST be an array [...] of objects, each with EXACTLY: "GALLERY_IMAGE_URL", "GALLERY_IMAGE_ALT", "GALLERY_CAPTION". At LEAST 4 items.
5. The "TEAM_MEMBERS" key MUST be an array of objects with EXACTLY: "MEMBER_NAME", "MEMBER_ROLE", "MEMBER_IMAGE_URL", "MEMBER_BIO". At LEAST 3 items.
6. EVERY array must contain REAL, SUBSTANTIAL content. NO empty strings. Each description must be at least 15 words.
7. DO NOT use short key names like "ICON", "TITLE", "DESCRIPTION" — always use the FULL prefixed key name as shown above.

=== MINIMUM WORD COUNTS (MANDATORY — short text = FAILURE) ===
- HERO_SUBTITLE: MIN 15 parole
- ABOUT_TEXT: MIN 40 parole (racconta una storia, non una frase)
- SERVICE_DESCRIPTION / FEATURE_DESCRIPTION: MIN 12 parole ciascuna
- TESTIMONIAL_TEXT: MIN 20 parole ciascuna (storia specifica, non "ottimo servizio")
- CTA_SUBTITLE: MIN 12 parole
- MEMBER_BIO: MIN 15 parole

FINAL CHECKLIST (every point is mandatory):
- ALL text MUST be in Italian
- Be WILDLY creative and hyper-specific to THIS business — if you replaced the business name, the text should NOT work for any other company
- Hero title: MAX 6 words, think Nike/Apple-level copywriting
- ZERO generic text anywhere. Read every line and ask: "Could this appear on a random corporate site?" If yes, REWRITE IT.
- Each service/feature icon: UNIQUE emoji, never repeated in the same section
- TESTIMONIAL_INITIAL = first letter of TESTIMONIAL_AUTHOR name
- Testimonials: real Italian names (Nome Cognome), specific details, emotional stories (NOT "Ottimo servizio" or "Molto professionali")
- Generate ONLY the sections listed in SECTIONS NEEDED
- Double-check: NO banned phrases from the list above appear ANYWHERE in your output
- VERIFY: every SERVICES/FEATURES/TESTIMONIALS/GALLERY_ITEMS/TEAM_MEMBERS array has 3+ items with FULL key names (SERVICE_ICON not ICON)
- COUNT WORDS: if any description has fewer words than the minimum, EXPAND it immediately
- Return ONLY the JSON object"""

        result = await self.kimi.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000, thinking=False, timeout=120.0,
            temperature=0.75, top_p=0.95, json_mode=True,
        )

        if result.get("success"):
            try:
                texts = self._extract_json(result["content"])
                result["parsed"] = texts
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[DataBinding] Texts JSON parse failed (attempt 1): {e}")
                logger.debug(f"[DataBinding] Raw response: {result['content'][:500]}...")
                # Retry with stricter prompt and lower temperature
                retry_result = await self.kimi.call(
                    messages=[{"role": "user", "content": prompt + "\n\nIMPORTANT: Your previous response had invalid JSON. Return ONLY valid JSON. No comments, no trailing commas, no explanation."}],
                    max_tokens=4000, thinking=False, timeout=120.0,
                    temperature=0.5, json_mode=True,
                )
                if retry_result.get("success"):
                    try:
                        texts = self._extract_json(retry_result["content"])
                        result["parsed"] = texts
                        result["tokens_input"] = result.get("tokens_input", 0) + retry_result.get("tokens_input", 0)
                        result["tokens_output"] = result.get("tokens_output", 0) + retry_result.get("tokens_output", 0)
                        logger.info("[DataBinding] Texts JSON parse succeeded on retry")
                    except (json.JSONDecodeError, ValueError) as e2:
                        logger.error(f"[DataBinding] Texts JSON parse failed (attempt 2): {e2}")
                        result["success"] = False
                        result["error"] = f"Failed to parse texts JSON after retry: {e2}"
                else:
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
        """Select component variants with randomization from curated pools.

        For each section, randomly picks from the STYLE_VARIANT_POOL if available.
        Falls back to the fixed STYLE_VARIANT_MAP, then to _DEFAULT_SECTION_VARIANTS.
        This ensures every generated site looks different even for the same template style.
        """
        pool_map = STYLE_VARIANT_POOL.get(template_style_id, {})
        fixed_map = STYLE_VARIANT_MAP.get(template_style_id, {})
        available = self.assembler.get_variant_ids()
        selections = {}

        for section in sections:
            # Priority 1: Randomized pool for this style + section
            pool = pool_map.get(section, [])
            if pool:
                selections[section] = random.choice(pool)
            # Priority 2: Fixed deterministic map (fallback)
            elif section in fixed_map:
                selections[section] = fixed_map[section]
            # Priority 3: Randomized pool for default section types (faq, pricing, etc.)
            elif section in _DEFAULT_SECTION_VARIANT_POOLS:
                selections[section] = random.choice(_DEFAULT_SECTION_VARIANT_POOLS[section])
            # Priority 4: Fixed default for known section types
            elif section in self._DEFAULT_SECTION_VARIANTS:
                selections[section] = self._DEFAULT_SECTION_VARIANTS[section]
            else:
                # Last resort: pick first available variant for unknown sections
                variants = available.get(section, [])
                if variants:
                    selections[section] = variants[0]
                else:
                    logger.warning(
                        f"[DataBinding] No variant available for section '{section}' "
                        f"in style '{template_style_id}'"
                    )

        logger.info(f"[DataBinding] Randomized selection for '{template_style_id}': {selections}")
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
            json_mode=True,
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

        # === ANALYZE REFERENCE URL (if provided) ===
        reference_url_context = ""
        if _has_url_analyzer:
            # Extract URL from business_description (format: "Siti di riferimento: https://...")
            url_match = re.search(r'Siti di riferimento:\s*(https?://\S+)', business_description)
            if url_match:
                ref_url = url_match.group(1).strip()
                try:
                    analysis = await analyze_reference_url(ref_url)
                    if analysis:
                        reference_url_context = format_analysis_for_prompt(analysis)
                        logger.info(f"[DataBinding] Analyzed reference URL: {ref_url}")
                except Exception as e:
                    logger.warning(f"[DataBinding] URL analysis failed: {e}")

        # === PICK VARIETY CONTEXT (random personality, color mood, font pairing) ===
        variety = _pick_variety_context()
        logger.info(
            f"[DataBinding] Variety: personality={variety['personality']['name']}, "
            f"color_mood={variety['color_mood']['mood']}, "
            f"font={variety['font_pairing']['heading']}/{variety['font_pairing']['body']}"
        )

        # === STEP 1+2 PARALLEL: Theme + Texts ===
        if on_progress:
            on_progress(1, "Analisi stile e generazione testi...", {
                "phase": "analyzing",
            })

        theme_task = self._generate_theme(
            business_name, business_description,
            style_preferences, reference_image_url,
            creative_context=creative_context,
            reference_url_context=reference_url_context,
            variety_context=variety,
        )
        texts_task = self._generate_texts(
            business_name, business_description,
            sections, contact_info,
            creative_context=creative_context,
            reference_url_context=reference_url_context,
            variety_context=variety,
        )
        theme_result, texts_result = await asyncio.gather(theme_task, texts_task)

        # Extract results
        theme = theme_result.get("parsed", self._fallback_theme(style_preferences))

        if not texts_result.get("success") or not texts_result.get("parsed"):
            logger.warning(f"[DataBinding] AI texts failed, using fallback: {texts_result.get('error', 'unknown')}")
            texts = self._fallback_texts(business_name, sections)
        else:
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

        # Inject stock photos as default (replace ugly placehold.co grey boxes)
        # Only if no AI images were generated — stock photos are the fallback
        if not should_generate_images:
            site_data = self._inject_stock_photos(site_data, template_style_id)

        # Inject user-uploaded photos (override stock/placeholder photos)
        if photo_urls:
            site_data = self._inject_user_photos(site_data, photo_urls)

        try:
            html_content = self.assembler.assemble(site_data)
            html_content = sanitize_output(html_content)
            # Post-process: remove empty sections (better no section than blank space)
            html_content = self._post_process_html(html_content)
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
            "model_used": self.kimi.model,
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

            # Skip sections where the AI returned no real content at all
            # (empty dict or only empty-string values). Keep hero, footer, contact always.
            if section not in ("hero", "footer", "contact", "cta"):
                if not self._section_has_content(section, section_texts):
                    logger.warning(
                        f"[DataBinding] Section '{section}' has no real content after normalization, skipping"
                    )
                    continue

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
                "LOGO_URL": logo_url or self._generate_text_logo(business_name, theme),
                "BUSINESS_PHONE": phone,
                "BUSINESS_EMAIL": email,
                "BUSINESS_ADDRESS": address,
                # Duplicate as CONTACT_* for templates that use that prefix
                "CONTACT_PHONE": phone,
                "CONTACT_EMAIL": email,
                "CONTACT_ADDRESS": address,
                "CURRENT_YEAR": str(__import__('datetime').datetime.now().year),
                "WEB3FORMS_KEY": os.getenv("WEB3FORMS_KEY", ""),
            },
        }

    def _section_has_content(self, section: str, data: Dict[str, Any]) -> bool:
        """Check if a section's data dict has any real content.

        Returns False if:
        - data is empty or not a dict
        - All string values are empty or only whitespace
        - List values (repeat arrays) are empty or contain only empty dicts
        """
        if not data or not isinstance(data, dict):
            return False

        # Sections that use REPEAT arrays: check if the array has items
        repeat_keys = {
            "services": "SERVICES",
            "features": "FEATURES",
            "testimonials": "TESTIMONIALS",
            "gallery": "GALLERY_ITEMS",
            "team": "TEAM_MEMBERS",
            "pricing": "PRICING_PLANS",
            "faq": "FAQ_ITEMS",
            "stats": "STATS_ITEMS",
            "logos": "LOGOS_ITEMS",
            "process": "PROCESS_STEPS",
            "timeline": "TIMELINE_ITEMS",
        }

        repeat_key = repeat_keys.get(section)
        if repeat_key:
            items = data.get(repeat_key, [])
            if not isinstance(items, list) or len(items) == 0:
                return False
            # Check that at least one item has a non-empty value
            for item in items:
                if isinstance(item, dict):
                    for v in item.values():
                        if isinstance(v, str) and v.strip():
                            return True
            return False

        # For non-repeat sections (about, etc.), check for any non-empty string values
        # Exclude the title/subtitle check - a section needs more than just a heading
        title_keys = {k for k in data.keys() if k.endswith("_TITLE") or k.endswith("_SUBTITLE")}
        has_non_title_content = False
        for key, value in data.items():
            if key in title_keys:
                continue
            if isinstance(value, str) and value.strip():
                has_non_title_content = True
                break
            if isinstance(value, list) and len(value) > 0:
                has_non_title_content = True
                break

        return has_non_title_content

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
            # Inject avatar URLs for each testimonial using UI Avatars API
            data = self._inject_testimonial_avatars(data)

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
            # This is needed for templates like about-magazine-01, about-bento-01
            # which use <!-- REPEAT:ABOUT_STATS --> blocks
            if "ABOUT_STATS" not in data:
                stats = []
                for i in range(1, 10):  # support up to 9 highlights
                    # Try standard format: ABOUT_HIGHLIGHT_NUM_1 + ABOUT_HIGHLIGHT_1
                    num_key = f"ABOUT_HIGHLIGHT_NUM_{i}"
                    label_key = f"ABOUT_HIGHLIGHT_{i}"
                    if num_key in data and label_key in data:
                        stats.append({
                            "STAT_NUMBER": str(data[num_key]),
                            "STAT_LABEL": str(data[label_key]),
                        })
                        continue
                    # Try alternative formats Kimi might use
                    for nk in [f"ABOUT_STAT_NUM_{i}", f"ABOUT_NUM_{i}", f"STAT_NUMBER_{i}", f"HIGHLIGHT_NUM_{i}"]:
                        if nk in data:
                            for lk in [f"ABOUT_STAT_{i}", f"ABOUT_LABEL_{i}", f"STAT_LABEL_{i}", f"HIGHLIGHT_{i}", label_key]:
                                if lk in data:
                                    stats.append({
                                        "STAT_NUMBER": str(data[nk]),
                                        "STAT_LABEL": str(data[lk]),
                                    })
                                    break
                            break
                if stats:
                    data["ABOUT_STATS"] = stats

                # Also check if Kimi returned ABOUT_STATS as an array directly
                # with different key names (e.g., ABOUT_HIGHLIGHTS, HIGHLIGHTS, etc.)
                if not stats:
                    for alt_key in ["ABOUT_HIGHLIGHTS", "HIGHLIGHTS", "ABOUT_NUMBERS", "about_stats"]:
                        val = data.get(alt_key)
                        if isinstance(val, list) and len(val) > 0:
                            normalized_stats = []
                            for item in val:
                                if isinstance(item, dict):
                                    num = item.get("STAT_NUMBER", item.get("NUMBER", item.get("NUM", item.get("number", ""))))
                                    label = item.get("STAT_LABEL", item.get("LABEL", item.get("label", "")))
                                    if num and label:
                                        normalized_stats.append({
                                            "STAT_NUMBER": str(num),
                                            "STAT_LABEL": str(label),
                                        })
                            if normalized_stats:
                                data["ABOUT_STATS"] = normalized_stats
                                logger.info(f"[DataBinding] Normalized {alt_key} -> ABOUT_STATS ({len(normalized_stats)} items)")
                                break

            # Fallback: if no stats at all, generate sensible defaults
            if "ABOUT_STATS" not in data or not data["ABOUT_STATS"]:
                data["ABOUT_STATS"] = [
                    {"STAT_NUMBER": "10", "STAT_LABEL": "Anni di Esperienza"},
                    {"STAT_NUMBER": "500", "STAT_LABEL": "Clienti Soddisfatti"},
                    {"STAT_NUMBER": "98", "STAT_LABEL": "% Soddisfazione"},
                ]
                # Also set the flat keys for templates that use them directly
                if "ABOUT_HIGHLIGHT_NUM_1" not in data:
                    data["ABOUT_HIGHLIGHT_NUM_1"] = "10"
                    data["ABOUT_HIGHLIGHT_1"] = "Anni di Esperienza"
                    data["ABOUT_HIGHLIGHT_NUM_2"] = "500"
                    data["ABOUT_HIGHLIGHT_2"] = "Clienti Soddisfatti"
                    data["ABOUT_HIGHLIGHT_NUM_3"] = "98"
                    data["ABOUT_HIGHLIGHT_3"] = "% Soddisfazione"

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

    # Synonym map: maps common AI key variations to canonical suffixes.
    # Used by _normalize_item_keys to catch any creative key naming Kimi uses.
    _KEY_SYNONYMS: Dict[str, str] = {
        # ICON synonyms
        "ICON": "ICON",
        "EMOJI": "ICON",
        "ICONA": "ICON",
        "SYMBOL": "ICON",
        "SIMBOLO": "ICON",
        "IMAGE": "ICON",  # fallback: if no IMAGE_URL field, treat as icon
        # TITLE synonyms
        "TITLE": "TITLE",
        "TITOLO": "TITLE",
        "NAME": "TITLE",
        "NOME": "TITLE",
        "HEADING": "TITLE",
        "LABEL": "TITLE",
        "TITL": "TITLE",
        # DESCRIPTION synonyms
        "DESCRIPTION": "DESCRIPTION",
        "DESCRIZIONE": "DESCRIPTION",
        "DESC": "DESCRIPTION",
        "TEXT": "DESCRIPTION",
        "TESTO": "DESCRIPTION",
        "BODY": "DESCRIPTION",
        "CONTENT": "DESCRIPTION",
        "DETAIL": "DESCRIPTION",
        "DETAILS": "DESCRIPTION",
        "SUMMARY": "DESCRIPTION",
        # CTA synonyms
        "CTA": "CTA",
        "CTA_TEXT": "CTA",
        "LINK": "CTA",
        "LINK_TEXT": "CTA",
        "BUTTON": "CTA",
        "BUTTON_TEXT": "CTA",
        # AUTHOR synonyms (for testimonials)
        "AUTHOR": "AUTHOR",
        "AUTORE": "AUTHOR",
        "WRITER": "AUTHOR",
        # ROLE synonyms (for testimonials)
        "ROLE": "ROLE",
        "RUOLO": "ROLE",
        "JOB": "ROLE",
        "POSITION": "ROLE",
        "JOB_TITLE": "ROLE",
        # INITIAL synonyms (for testimonials)
        "INITIAL": "INITIAL",
        "INIZIALE": "INITIAL",
        "AVATAR": "INITIAL",
        # IMAGE_URL synonyms
        "IMAGE_URL": "IMAGE_URL",
        "IMG_URL": "IMAGE_URL",
        "PHOTO": "IMAGE_URL",
        "FOTO": "IMAGE_URL",
        "PHOTO_URL": "IMAGE_URL",
        "IMAGE_SRC": "IMAGE_URL",
        # IMAGE_ALT synonyms
        "IMAGE_ALT": "IMAGE_ALT",
        "IMG_ALT": "IMAGE_ALT",
        "ALT": "IMAGE_ALT",
        "ALT_TEXT": "IMAGE_ALT",
        # CAPTION synonyms
        "CAPTION": "CAPTION",
        "DIDASCALIA": "CAPTION",
        # BIO synonyms
        "BIO": "BIO",
        "BIOGRAFIA": "BIO",
        "ABOUT": "BIO",
        # NUMBER/NUM synonyms (for stats)
        "NUMBER": "NUMBER",
        "NUM": "NUMBER",
        "NUMERO": "NUMBER",
        "VALUE": "NUMBER",
        "VALORE": "NUMBER",
        # SUFFIX synonyms (for stats)
        "SUFFIX": "SUFFIX",
        "SUFFISSO": "SUFFIX",
        "UNIT": "SUFFIX",
        # QUESTION/ANSWER synonyms (for FAQ)
        "QUESTION": "QUESTION",
        "DOMANDA": "QUESTION",
        "Q": "QUESTION",
        "ANSWER": "ANSWER",
        "RISPOSTA": "ANSWER",
        "A": "ANSWER",
        # YEAR synonyms (for timeline)
        "YEAR": "YEAR",
        "ANNO": "YEAR",
        "DATE": "YEAR",
        "DATA": "YEAR",
        "PERIOD": "YEAR",
        # HEADING synonym (for timeline)
        "HEADING": "HEADING",
        # STEP fields
        "STEP_NUMBER": "NUMBER",
        "STEP_TITLE": "TITLE",
        "STEP_DESCRIPTION": "DESCRIPTION",
    }

    def _normalize_item_keys(
        self,
        items: List[Dict[str, Any]],
        item_fields: List[str],
        flat_prefix: str,
    ) -> List[Dict[str, str]]:
        """Normalize item dict keys to match expected template placeholders.

        Handles common AI variations where Kimi returns short keys:
        - {"ICON": "x", "TITLE": "y"} -> {"SERVICE_ICON": "x", "SERVICE_TITLE": "y"}
        - {"icon": "x", "title": "y"} -> {"SERVICE_ICON": "x", "SERVICE_TITLE": "y"}
        - {"service_icon": "x"} -> {"SERVICE_ICON": "x"}  (already correct, just uppercased)
        - {"emoji": "x", "name": "y"} -> {"SERVICE_ICON": "x", "SERVICE_TITLE": "y"}
        - {"titolo": "x", "descrizione": "y"} -> {"SERVICE_TITLE": "x", "SERVICE_DESCRIPTION": "y"}

        Uses a synonym map to handle any creative key naming the AI might use.
        Also preserves any extra keys the item might have (e.g., SERVICE_IMAGE_URL).
        """
        if not items or not isinstance(items, list):
            return items

        prefix_upper = flat_prefix.upper()

        # Build a mapping: canonical_suffix -> full_field (e.g., "ICON" -> "SERVICE_ICON")
        suffix_map: Dict[str, str] = {}
        for field in item_fields:
            if field.startswith(prefix_upper + "_"):
                suffix = field[len(prefix_upper) + 1:]
                suffix_map[suffix.upper()] = field

        # Build a reverse synonym lookup: any synonym key -> canonical suffix -> full field
        # e.g., "EMOJI" -> "ICON" -> "SERVICE_ICON"
        synonym_to_field: Dict[str, str] = {}
        for synonym, canonical in self._KEY_SYNONYMS.items():
            if canonical in suffix_map:
                synonym_to_field[synonym.upper()] = suffix_map[canonical]

        # Log for debugging
        if items:
            sample_keys = list(items[0].keys()) if isinstance(items[0], dict) else []
            logger.info(
                f"[DataBinding] _normalize_item_keys: prefix={prefix_upper}, "
                f"expected_fields={item_fields}, "
                f"sample_item_keys={sample_keys}, "
                f"items_count={len(items)}"
            )

        normalized = []
        for item in items:
            if not isinstance(item, dict):
                continue
            new_item = {}
            for key, value in item.items():
                key_upper = key.upper().strip()
                str_value = str(value) if value is not None else ""

                # 1. Already has the full prefix (e.g., SERVICE_ICON) - keep as-is
                if key_upper.startswith(prefix_upper + "_"):
                    new_item[key_upper] = str_value
                    continue

                # 2. Strip any OTHER prefix the AI may have added (e.g., "SERVIZIO_TITOLO")
                #    Try removing everything before the last underscore segment
                #    But first check direct suffix match
                if key_upper in suffix_map:
                    new_item[suffix_map[key_upper]] = str_value
                    continue

                # 3. Synonym lookup (e.g., "emoji" -> SERVICE_ICON, "name" -> SERVICE_TITLE)
                if key_upper in synonym_to_field:
                    target_field = synonym_to_field[key_upper]
                    # Don't overwrite if we already have this field from a more specific match
                    if target_field not in new_item:
                        new_item[target_field] = str_value
                    continue

                # 4. Try stripping any prefix from the key and check suffix
                #    e.g., "SERVIZIO_TITOLO" -> strip "SERVIZIO_" -> "TITOLO" -> synonym -> TITLE -> SERVICE_TITLE
                if "_" in key_upper:
                    parts = key_upper.split("_")
                    # Try the last part as a synonym
                    last_part = parts[-1]
                    if last_part in synonym_to_field:
                        target_field = synonym_to_field[last_part]
                        if target_field not in new_item:
                            new_item[target_field] = str_value
                        continue
                    # Try last two parts joined (e.g., "IMAGE_URL")
                    if len(parts) >= 2:
                        last_two = "_".join(parts[-2:])
                        if last_two in synonym_to_field:
                            target_field = synonym_to_field[last_two]
                            if target_field not in new_item:
                                new_item[target_field] = str_value
                            continue

                # 5. Preserve unknown keys with prefix applied
                new_item[key_upper] = str_value

            # Ensure all expected fields exist (even if empty) to prevent template breakage
            for field in item_fields:
                if field not in new_item:
                    new_item[field] = ""

            normalized.append(new_item)

        # Log what we produced
        if normalized:
            sample = normalized[0]
            matched_fields = [f for f in item_fields if sample.get(f, "") != ""]
            logger.info(
                f"[DataBinding] _normalize_item_keys result: "
                f"matched_fields={matched_fields}/{len(item_fields)}, "
                f"sample_output_keys={list(sample.keys())}"
            )

        return normalized

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
        1. Correct key with valid array (SERVICES: [...]) -- normalize item keys
        2. Alternative key name (SERVICE_ITEMS, items, etc.) -- rename + normalize
        3. Flat numbered keys (SERVICE_1_TITLE, SERVICE_2_TITLE, etc.) -- collect into array
        4. Lowercase key versions -- case-insensitive lookup
        5. Single object instead of array -- wrap in array
        6. Any key containing a list of dicts -- heuristic discovery
        7. Empty/missing array -- use fallback items if provided
        """
        found_items = None
        found_source = None

        # 1. Check if canonical key already has a valid non-empty array
        existing = data.get(canonical_key)
        if isinstance(existing, list) and len(existing) > 0 and isinstance(existing[0], dict):
            found_items = existing
            found_source = canonical_key

        # 2. Check alternative key names (case-insensitive)
        if found_items is None:
            all_keys_lower = {k.lower(): k for k in data.keys()}
            for alt_key in alt_keys:
                # Direct key check
                if alt_key in data:
                    val = data[alt_key]
                    if isinstance(val, list) and len(val) > 0:
                        found_items = val
                        found_source = alt_key
                        break
                    elif isinstance(val, dict):
                        found_items = [val]
                        found_source = f"{alt_key} (single object)"
                        break
                # Case-insensitive check
                if alt_key.lower() in all_keys_lower:
                    real_key = all_keys_lower[alt_key.lower()]
                    val = data[real_key]
                    if isinstance(val, list) and len(val) > 0:
                        found_items = val
                        found_source = real_key
                        break

            # Also check canonical key with different casing
            if found_items is None and canonical_key.lower() in all_keys_lower:
                real_key = all_keys_lower[canonical_key.lower()]
                if real_key != canonical_key:
                    val = data[real_key]
                    if isinstance(val, list) and len(val) > 0:
                        found_items = val
                        found_source = f"{real_key} (case-insensitive)"

        # 3. Check for flat numbered keys (e.g., SERVICE_1_TITLE, SERVICE_2_TITLE, ...)
        if found_items is None:
            flat_items = self._collect_flat_numbered_items(data, flat_prefix, item_fields)
            if flat_items:
                found_items = flat_items
                found_source = f"flat {flat_prefix}_N_* keys"

        # 4. Heuristic: scan ALL keys for any list of dicts that looks like the right data
        if found_items is None:
            # Build suffix set for matching (e.g., {"icon", "title", "description"})
            suffix_set = set()
            for field in item_fields:
                if field.startswith(flat_prefix + "_"):
                    suffix_set.add(field[len(flat_prefix) + 1:].lower())
                suffix_set.add(field.lower())

            # Also add all synonym keys for broader matching
            for field in item_fields:
                if field.startswith(flat_prefix + "_"):
                    suffix = field[len(flat_prefix) + 1:].upper()
                    for syn, canonical in self._KEY_SYNONYMS.items():
                        if canonical == suffix:
                            suffix_set.add(syn.lower())

            best_match = None
            best_score = 0
            for key, val in data.items():
                if not isinstance(val, list) or len(val) == 0:
                    continue
                if not isinstance(val[0], dict):
                    continue
                # Score: how many item keys match expected suffixes or synonyms
                item_keys_lower = {k.lower() for k in val[0].keys()}
                score = len(item_keys_lower & suffix_set)
                if score > best_score:
                    best_score = score
                    best_match = (key, val)

            if best_match and best_score >= 1:
                found_items = best_match[1]
                found_source = f"heuristic match on key '{best_match[0]}' (score={best_score})"

        # 5. If we found items, normalize their keys and store under canonical key
        if found_items is not None and len(found_items) > 0:
            logger.info(
                f"[DataBinding] _normalize_repeat_array: found {len(found_items)} items "
                f"from source='{found_source}', sample_keys="
                f"{list(found_items[0].keys()) if isinstance(found_items[0], dict) else 'N/A'}"
            )
            normalized = self._normalize_item_keys(found_items, item_fields, flat_prefix)
            if normalized:
                # Validate: check if at least one item has non-empty required fields
                # For services: at least TITLE or DESCRIPTION should be non-empty
                has_content = False
                for item in normalized:
                    non_empty_fields = [f for f in item_fields if item.get(f, "").strip()]
                    if len(non_empty_fields) >= 2:  # At least 2 fields filled
                        has_content = True
                        break

                if has_content:
                    data[canonical_key] = normalized
                    logger.info(f"[DataBinding] Normalized {found_source} -> {canonical_key} ({len(normalized)} items, validated)")
                    return data
                else:
                    logger.warning(
                        f"[DataBinding] Normalized items from '{found_source}' have no real content "
                        f"(all fields empty after normalization). Falling through to fallback."
                    )

        # 6. If canonical key exists but is empty/invalid, or doesn't exist at all -> fallback
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

    # ----- Post-processing: remove empty sections -----

    def _post_process_html(self, html: str) -> str:
        """Scan assembled HTML for empty sections and remove them entirely.

        A section is considered 'empty' if it has a heading element but the
        container that should hold repeated content (cards, items, etc.) is
        effectively empty -- meaning the REPEAT block produced no output.

        This catches cases where:
        - REPEAT block was empty (data array missing or with wrong keys)
        - Section has only a title + subtitle but no actual content items
        - Unreplaced {{PLACEHOLDER}} strings remain in the HTML

        Better to show NO section than an empty section with a big blank space.
        """
        # Pre-cleanup: remove any leftover unreplaced {{PLACEHOLDER}} strings
        # that would appear as visible text to the user
        html = re.sub(r'\{\{[A-Z_]+\}\}', '', html)

        # Find all <section ...>...</section> blocks (including nested divs)
        # Use a balanced approach: find section tags and track nesting
        result_parts = []
        pos = 0
        section_pattern = re.compile(r'<section\b[^>]*>', re.IGNORECASE)

        while pos < len(html):
            match = section_pattern.search(html, pos)
            if not match:
                # No more sections - append rest of html
                result_parts.append(html[pos:])
                break

            # Append content before this section
            result_parts.append(html[pos:match.start()])

            # Find the matching </section> (handle nesting)
            section_start = match.start()
            depth = 1
            search_pos = match.end()
            while depth > 0 and search_pos < len(html):
                open_tag = html.find('<section', search_pos)
                close_tag = html.find('</section>', search_pos)

                if close_tag == -1:
                    # No closing tag found - broken HTML, keep everything
                    search_pos = len(html)
                    break

                if open_tag != -1 and open_tag < close_tag:
                    depth += 1
                    search_pos = open_tag + 8  # len('<section')
                else:
                    depth -= 1
                    if depth == 0:
                        section_end = close_tag + len('</section>')
                        break
                    search_pos = close_tag + len('</section>')
            else:
                section_end = len(html)

            section_html = html[section_start:section_end]

            # Check if this section is empty (has heading but no real content)
            if self._is_section_empty(section_html):
                # Extract section id for logging
                id_match = re.search(r'id=["\']([^"\']+)["\']', section_html)
                section_id = id_match.group(1) if id_match else "unknown"
                logger.info(f"[DataBinding] Post-process: removing empty section '{section_id}'")
                # Skip this section (don't add to result)
            else:
                result_parts.append(section_html)

            pos = section_end

        return "".join(result_parts)

    def _is_section_empty(self, section_html: str) -> bool:
        """Determine if a section is empty (has heading but no meaningful content).

        Returns True if the section should be removed.

        Strategy:
        1. Never remove hero, footer, contact, or CTA sections
        2. Check if the section has very little visible text (broken template)
        3. Check if key content containers (grid, stagger, space-y, columns, flex, etc.) are empty
           which means the REPEAT block rendered nothing
        4. Check for unreplaced placeholders that signal missing data
        """
        # Don't remove hero, footer, contact, or CTA sections
        section_lower = section_html.lower()
        if re.search(r'id=["\']hero["\']', section_html):
            return False
        if '<footer' in section_lower or re.search(r'id=["\']footer["\']', section_html):
            return False
        if re.search(r'id=["\']contact["\']', section_html):
            return False
        if re.search(r'id=["\']cta["\']', section_html):
            return False

        # Strip HTML tags to get visible text content
        text_only = re.sub(r'<style[^>]*>.*?</style>', '', section_html, flags=re.DOTALL)
        text_only = re.sub(r'<script[^>]*>.*?</script>', '', text_only, flags=re.DOTALL)
        text_only = re.sub(r'<[^>]+>', ' ', text_only)
        text_only = re.sub(r'\s+', ' ', text_only).strip()

        # If very little visible text (less than 30 chars), it's likely empty
        if len(text_only) < 30:
            return True

        # Check for unreplaced placeholders: if most visible text is just {{...}}, section is broken
        placeholder_count = len(re.findall(r'\{\{\w+\}\}', text_only))
        words_without_placeholders = re.sub(r'\{\{\w+\}\}', '', text_only).strip()
        if placeholder_count >= 3 and len(words_without_placeholders) < 50:
            logger.info(f"[PostProcess] Section has {placeholder_count} unreplaced placeholders, removing")
            return True

        # Check for empty content containers that SHOULD have repeated items
        # These patterns catch the case where a REPEAT block rendered "" (no items)

        # Pattern 1: Empty grid containers - <div class="grid ...">  \n  </div>
        empty_grid = re.compile(
            r'<div[^>]*class="[^"]*\bgrid\b[^"]*"[^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_grid.search(section_html):
            return True

        # Pattern 2: Empty stagger containers
        empty_stagger = re.compile(
            r'data-animate=["\']stagger["\'][^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_stagger.search(section_html):
            return True

        # Pattern 3: Empty space-y containers
        empty_space = re.compile(
            r'<div[^>]*class="[^"]*\bspace-y-\d+\b[^"]*"[^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_space.search(section_html):
            return True

        # Pattern 4: Empty svc-tab-panels (tabs template)
        empty_tabs = re.compile(
            r'<div[^>]*class="[^"]*svc-tab-panels[^"]*"[^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_tabs.search(section_html):
            return True

        # Pattern 5: Section with heading but the grid/stagger has no .stagger-item children
        if 'data-animate="stagger"' in section_html or "data-animate='stagger'" in section_html:
            stagger_items_count = section_html.count('stagger-item')
            if stagger_items_count == 0:
                return True

        # Pattern 6: Empty CSS columns containers (masonry layouts)
        empty_columns = re.compile(
            r'<div[^>]*class="[^"]*\bcolumns-\d+\b[^"]*"[^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_columns.search(section_html):
            return True
        # Also catch columns with sm:/md: prefixes
        empty_columns_responsive = re.compile(
            r'<div[^>]*class="[^"]*\b(?:sm:|md:|lg:)?columns-\d+\b[^"]*"[^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_columns_responsive.search(section_html):
            return True

        # Pattern 7: Empty flex containers that should hold items
        empty_flex = re.compile(
            r'<div[^>]*class="[^"]*\bflex\b[^"]*\bgap-\d+\b[^"]*"[^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_flex.search(section_html):
            return True

        # Pattern 8: Empty marquee/scroll containers
        empty_marquee = re.compile(
            r'<div[^>]*(?:data-animate=["\']marquee["\']|class="[^"]*marquee[^"]*")[^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_marquee.search(section_html):
            return True

        # Pattern 9: Empty overflow-x scroll containers (filmstrip, carousel)
        empty_scroll = re.compile(
            r'<div[^>]*class="[^"]*\boverflow-x-(?:auto|scroll)\b[^"]*"[^>]*>\s*</div>',
            re.DOTALL,
        )
        if empty_scroll.search(section_html):
            return True

        return False

    # ----- Fallback content generators -----

    def _fallback_services(self, business_name: str) -> List[Dict[str, str]]:
        """Generate fallback service items when AI returns empty/missing services."""
        return [
            {
                "SERVICE_ICON": "\U0001f3af",
                "SERVICE_TITLE": "Strategia su Misura",
                "SERVICE_DESCRIPTION": f"Analizziamo a fondo il tuo contesto per costruire un percorso che rifletta la vera identità di {business_name} e porti risultati misurabili nel tempo.",
            },
            {
                "SERVICE_ICON": "\U0001f680",
                "SERVICE_TITLE": "Esecuzione Fulminante",
                "SERVICE_DESCRIPTION": "Dalla visione al lancio in tempi record. Ogni fase del progetto segue un metodo collaudato che elimina gli sprechi e accelera i risultati concreti.",
            },
            {
                "SERVICE_ICON": "\U0001f4a1",
                "SERVICE_TITLE": "Evoluzione Continua",
                "SERVICE_DESCRIPTION": "Non ci fermiamo al primo traguardo. Monitoriamo, ottimizziamo e iteriamo per garantire che ogni aspetto cresca insieme al tuo business.",
            },
        ]

    def _fallback_features(self, business_name: str) -> List[Dict[str, str]]:
        """Generate fallback feature items when AI returns empty/missing features."""
        return [
            {
                "FEATURE_ICON": "\u2728",
                "FEATURE_TITLE": "Cura Artigianale",
                "FEATURE_DESCRIPTION": f"Ogni progetto di {business_name} riceve un'attenzione maniacale ai dettagli, perché la differenza si vede nei particolari che altri trascurano.",
            },
            {
                "FEATURE_ICON": "\u26a1",
                "FEATURE_TITLE": "Tempi Che Stupiscono",
                "FEATURE_DESCRIPTION": "Il nostro metodo strutturato ci permette di consegnare in metà del tempo medio del settore, senza sacrificare nemmeno un grammo di qualità.",
            },
            {
                "FEATURE_ICON": "\U0001f6e1\ufe0f",
                "FEATURE_TITLE": "Zero Sorprese",
                "FEATURE_DESCRIPTION": "Trasparenza totale su costi, tempi e risultati attesi. Report settimanali dettagliati e un canale diretto sempre aperto con il tuo referente.",
            },
            {
                "FEATURE_ICON": "\U0001f9e0",
                "FEATURE_TITLE": "Pensiero Laterale",
                "FEATURE_DESCRIPTION": "Portiamo al tavolo idee che non ti aspetti, combiniamo creatività e dati per trovare angoli unici che distinguono il tuo brand dalla massa.",
            },
            {
                "FEATURE_ICON": "\U0001f4ca",
                "FEATURE_TITLE": "Risultati Misurabili",
                "FEATURE_DESCRIPTION": "Ogni azione è tracciata, ogni risultato documentato. Dashboard personalizzata con metriche chiare che raccontano la crescita reale del tuo progetto.",
            },
            {
                "FEATURE_ICON": "\U0001f504",
                "FEATURE_TITLE": "Miglioramento Perpetuo",
                "FEATURE_DESCRIPTION": "Non esiste il 'buono abbastanza'. Analizziamo continuamente i dati per ottimizzare ogni aspetto e portarti sempre un passo oltre le aspettative.",
            },
        ]

    def _fallback_testimonials(self) -> List[Dict[str, str]]:
        """Generate fallback testimonial items with specific, believable stories."""
        return [
            {
                "TESTIMONIAL_TEXT": "In tre mesi hanno ribaltato completamente la nostra presenza online. Il traffico organico è salito del 340% e le richieste di preventivo sono triplicate. Non credevo fosse possibile in così poco tempo.",
                "TESTIMONIAL_AUTHOR": "Marco Ferretti",
                "TESTIMONIAL_ROLE": "Fondatore, Ferretti & Associati",
                "TESTIMONIAL_INITIAL": "M",
            },
            {
                "TESTIMONIAL_TEXT": "Dopo anni di tentativi con altre realtà, finalmente qualcuno che ascolta davvero. Hanno capito l'anima del nostro brand al primo incontro e l'hanno tradotta in un'esperienza digitale che i nostri clienti adorano.",
                "TESTIMONIAL_AUTHOR": "Elena Marchetti",
                "TESTIMONIAL_ROLE": "Direttrice Creativa, Studio Lume",
                "TESTIMONIAL_INITIAL": "E",
            },
            {
                "TESTIMONIAL_TEXT": "Il nostro e-commerce faceva 12 ordini al giorno. Dopo il restyling ne facciamo 47 in media, con uno scontrino medio più alto del 28%. I numeri parlano da soli, ma è la cura nei dettagli che mi ha convinto.",
                "TESTIMONIAL_AUTHOR": "Alessandro Conti",
                "TESTIMONIAL_ROLE": "CEO, Bottega Digitale",
                "TESTIMONIAL_INITIAL": "A",
            },
        ]

    def _fallback_gallery(self) -> List[Dict[str, str]]:
        """Generate fallback gallery items with Unsplash stock images."""
        # Use default/business gallery pool for high-quality fallback images
        gallery_photos = _UNSPLASH_PHOTOS.get("default", {}).get("gallery", [])
        captions = [
            "Creatività in ogni dettaglio",
            "Dove l'idea prende forma",
            "Precisione e visione",
            "L'arte del risultato",
            "Oltre le aspettative",
            "Il nostro tocco distintivo",
        ]
        items = []
        for i in range(6):
            url = gallery_photos[i % len(gallery_photos)] if gallery_photos else f"https://placehold.co/600x400/eee/999?text=Foto+{i+1}"
            items.append({
                "GALLERY_IMAGE_URL": url,
                "GALLERY_IMAGE_ALT": captions[i],
                "GALLERY_CAPTION": captions[i],
            })
        return items

    @staticmethod
    def _inject_testimonial_avatars(data: Dict[str, Any]) -> Dict[str, Any]:
        """Add TESTIMONIAL_AVATAR_URL to each testimonial using UI Avatars API.
        Generates consistent, professional-looking avatar images from author names.
        No API key required — https://ui-avatars.com is free and unlimited."""
        from urllib.parse import quote
        testimonials = data.get("TESTIMONIALS", [])
        if not isinstance(testimonials, list):
            return data

        # Color palette for avatar backgrounds (warm, professional tones)
        bg_colors = ["3b82f6", "8b5cf6", "ec4899", "f59e0b", "10b981", "6366f1", "ef4444", "14b8a6"]

        for i, item in enumerate(testimonials):
            if isinstance(item, dict) and "TESTIMONIAL_AVATAR_URL" not in item:
                name = item.get("TESTIMONIAL_AUTHOR", "User")
                bg = bg_colors[i % len(bg_colors)]
                encoded_name = quote(name)
                item["TESTIMONIAL_AVATAR_URL"] = (
                    f"https://ui-avatars.com/api/?name={encoded_name}"
                    f"&background={bg}&color=fff&size=80&bold=true&format=svg"
                )
        return data

    def _inject_stock_photos(self, site_data: Dict[str, Any], template_style_id: Optional[str] = None) -> Dict[str, Any]:
        """Replace placehold.co grey boxes with high-quality Unsplash stock photos.
        Only replaces URLs that still contain 'placehold.co'."""
        photos = _get_stock_photos(template_style_id or "default")

        hero_pool = photos.get("hero", [])
        gallery_pool = photos.get("gallery", [])
        about_pool = photos.get("about", [])
        team_pool = photos.get("team", [])

        for component in site_data.get("components", []):
            data = component.get("data", {})

            # Hero image
            if "HERO_IMAGE_URL" in data and "placehold.co" in str(data.get("HERO_IMAGE_URL", "")):
                if hero_pool:
                    data["HERO_IMAGE_URL"] = hero_pool[0]

            # About image
            if "ABOUT_IMAGE_URL" in data and "placehold.co" in str(data.get("ABOUT_IMAGE_URL", "")):
                if about_pool:
                    data["ABOUT_IMAGE_URL"] = about_pool[0]

            # Gallery images
            gallery_items = data.get("GALLERY_ITEMS", [])
            if isinstance(gallery_items, list):
                for i, item in enumerate(gallery_items):
                    if isinstance(item, dict) and "placehold.co" in str(item.get("GALLERY_IMAGE_URL", "")):
                        if gallery_pool:
                            item["GALLERY_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]

            # Team member images
            team_members = data.get("TEAM_MEMBERS", [])
            if isinstance(team_members, list):
                for i, member in enumerate(team_members):
                    if isinstance(member, dict) and "placehold.co" in str(member.get("MEMBER_IMAGE_URL", "")):
                        if team_pool:
                            member["MEMBER_IMAGE_URL"] = team_pool[i % len(team_pool)]

            # Logo partner images - use stylish SVG placeholders instead of grey boxes
            logos_items = data.get("LOGOS_ITEMS", [])
            if isinstance(logos_items, list):
                for i, logo in enumerate(logos_items):
                    if isinstance(logo, dict) and "placehold.co" in str(logo.get("LOGO_IMAGE_URL", "")):
                        name = logo.get("LOGO_NAME", f"Partner {i+1}")
                        # Use a clean text-based logo placeholder
                        logo["LOGO_IMAGE_URL"] = f"https://placehold.co/160x60/f8fafc/64748b?text={name.replace(' ', '+')}&font=raleway"

        logger.info(f"[DataBinding] Injected stock photos for category: {template_style_id or 'default'}")
        return site_data

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
        """Extracts JSON from AI response with repair for common LLM errors."""
        # Try JSON in code block
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', content, re.DOTALL)
        raw_json = json_match.group(1).strip() if json_match else None

        if not raw_json:
            # Try raw JSON (find first { to last })
            stripped = content.strip()
            start = stripped.find('{')
            end = stripped.rfind('}')
            if start != -1 and end != -1 and end > start:
                raw_json = stripped[start:end + 1]

        if not raw_json:
            raise ValueError(f"No JSON found in response: {content[:200]}...")

        # Try parsing as-is first
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            pass

        # Repair common LLM JSON errors and retry
        repaired = self._repair_json(raw_json)
        return json.loads(repaired)

    def _repair_json(self, raw: str) -> str:
        """Repair common JSON errors from LLM output."""
        s = raw
        # Remove trailing commas before } or ]
        s = re.sub(r',\s*([}\]])', r'\1', s)
        # Fix missing commas between "value"\n"key" patterns (missing comma between properties)
        s = re.sub(r'(")\s*\n(\s*")', r'\1,\n\2', s)
        # But the above may add double commas where one already existed — fix that
        s = re.sub(r',\s*,', ',', s)
        # Remove control characters (except \n \r \t)
        s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
        # Fix single quotes used instead of double quotes for keys
        # Only do this if the JSON has no double-quoted keys (heuristic)
        if s.count("'") > s.count('"'):
            s = s.replace("'", '"')
        # Remove JavaScript-style comments (// and /* */)
        s = re.sub(r'//[^\n]*', '', s)
        s = re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL)
        # Fix truncated JSON: ensure balanced braces/brackets
        open_braces = s.count('{') - s.count('}')
        open_brackets = s.count('[') - s.count(']')
        if open_braces > 0 or open_brackets > 0:
            # Truncated response — close open structures
            s = s.rstrip().rstrip(',')
            s += ']' * max(0, open_brackets)
            s += '}' * max(0, open_braces)
        return s

    def _fallback_texts(self, business_name: str, sections: List[str]) -> dict:
        """Generate minimal fallback texts when AI text generation fails twice."""
        texts = {
            "meta": {
                "title": business_name,
                "description": f"{business_name} - Sito ufficiale",
                "og_title": business_name,
                "og_description": f"{business_name} - Sito ufficiale",
            }
        }
        if "hero" in sections:
            texts["hero"] = {
                "HERO_TITLE": f"Il Futuro è {business_name}",
                "HERO_SUBTITLE": f"Dove la visione incontra l'eccellenza. {business_name} ridefinisce gli standard del settore con un approccio che mette al centro le persone e i risultati concreti.",
                "HERO_CTA_TEXT": "Inizia la Trasformazione",
                "HERO_CTA_URL": "#contact",
                "HERO_IMAGE_URL": f"https://placehold.co/800x600/3b82f6/white?text={business_name}",
                "HERO_IMAGE_ALT": f"L'esperienza {business_name}",
            }
        if "about" in sections:
            texts["about"] = {
                "ABOUT_TITLE": "La Nostra Filosofia",
                "ABOUT_SUBTITLE": f"Ogni traguardo di {business_name} nasce da un'idea semplice: fare le cose nel modo giusto",
                "ABOUT_TEXT": f"{business_name} nasce dalla convinzione che il mercato merita di meglio. Non ci accontentiamo della mediocrità e non inseguiamo le scorciatoie. Ogni progetto che affrontiamo diventa una sfida personale, un'opportunità per dimostrare che si può fare di più, meglio e con più cura. La nostra storia è fatta di notti insonni, intuizioni brillanti e la testardaggine di chi crede davvero in quello che fa.",
                "ABOUT_HIGHLIGHT_1": "Anni di esperienza sul campo",
                "ABOUT_HIGHLIGHT_2": "Progetti completati con successo",
                "ABOUT_HIGHLIGHT_3": "Tasso di soddisfazione clienti",
                "ABOUT_HIGHLIGHT_NUM_1": "12",
                "ABOUT_HIGHLIGHT_NUM_2": "847",
                "ABOUT_HIGHLIGHT_NUM_3": "99.2",
            }
        if "services" in sections:
            texts["services"] = {
                "SERVICES_TITLE": "Il Metodo Dietro la Magia",
                "SERVICES_SUBTITLE": f"Tre pilastri che rendono {business_name} il partner che stavi cercando",
                "SERVICES": self._fallback_services(business_name),
            }
        if "contact" in sections:
            texts["contact"] = {
                "CONTACT_TITLE": "Parliamo del Tuo Prossimo Passo",
                "CONTACT_SUBTITLE": "Ogni grande progetto inizia con una conversazione. Raccontaci la tua idea e trasformiamola insieme in qualcosa di straordinario.",
                "CONTACT_ADDRESS": "",
                "CONTACT_PHONE": "",
                "CONTACT_EMAIL": "",
            }
        if "footer" in sections:
            texts["footer"] = {
                "FOOTER_DESCRIPTION": f"{business_name} — Dove nascono le idee che cambiano le regole del gioco.",
            }
        if "cta" in sections:
            texts["cta"] = {
                "CTA_TITLE": "Il Momento è Adesso",
                "CTA_SUBTITLE": "Ogni giorno che passa è un'opportunità persa. Fai il primo passo verso risultati che superano le aspettative.",
                "CTA_BUTTON_TEXT": "Prenota una Consulenza Gratuita",
                "CTA_BUTTON_URL": "#contact",
            }
        if "features" in sections:
            texts["features"] = {
                "FEATURES_TITLE": "Cosa Ci Rende Diversi",
                "FEATURES_SUBTITLE": f"I dettagli che fanno la differenza tra un risultato ordinario e uno straordinario",
                "FEATURES": self._fallback_features(business_name),
            }
        if "testimonials" in sections:
            texts["testimonials"] = {
                "TESTIMONIALS_TITLE": "Storie di Chi Ha Scelto Noi",
                "TESTIMONIALS": self._fallback_testimonials(),
            }
        logger.warning(f"[DataBinding] Using fallback texts for {business_name} (sections: {sections})")
        return texts

    def _fallback_theme(self, style_preferences=None) -> Dict[str, str]:
        """Default theme if Kimi theme generation fails. Randomly picks from diverse palette pool."""
        theme = random.choice(FALLBACK_THEME_POOL).copy()
        if style_preferences and style_preferences.get("primary_color"):
            theme["primary_color"] = style_preferences["primary_color"]
        return theme

    @staticmethod
    def _generate_text_logo(business_name: str, theme: Dict[str, str]) -> str:
        """Generate a data URI SVG logo with business initials when no logo is provided."""
        # Extract initials (max 2 characters)
        words = business_name.strip().split()
        initials = "".join(w[0].upper() for w in words[:2]) if words else "?"
        primary = theme.get("primary_color", "#3b82f6")
        # SVG with rounded rect background and white text
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40" viewBox="0 0 120 40">'
            f'<rect width="120" height="40" rx="8" fill="{primary}"/>'
            f'<text x="60" y="26" font-family="system-ui,sans-serif" font-size="16" '
            f'font-weight="700" fill="white" text-anchor="middle">{initials}</text>'
            f'</svg>'
        )
        import base64
        encoded = base64.b64encode(svg.encode()).decode()
        return f"data:image/svg+xml;base64,{encoded}"

    def _default_selections(self, sections: List[str], available: Dict[str, List[str]]) -> Dict[str, str]:
        """Fallback: randomly pick a variant for each section from available options."""
        selections = {}
        for section in sections:
            variants = available.get(section, [])
            if variants:
                selections[section] = random.choice(variants)
        return selections


# Singleton
databinding_generator = DataBindingGenerator()
