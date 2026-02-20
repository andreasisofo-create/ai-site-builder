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

from app.core.config import settings
from app.services.kimi_client import kimi, kimi_refine, kimi_text
from app.services.template_assembler import assembler as template_assembler
from app.services.sanitizer import sanitize_input, sanitize_output
from app.services.quality_control import qc_pipeline
from app.services.generation_tracker import (
    get_recently_used,
    pick_avoiding_recent,
    pick_variant_avoiding_recent,
    record_generation,
    build_diversity_prompt_block,
    cleanup_old_records,
)

# AI Image generation (Flux/fal.ai) - graceful fallback if not available
try:
    from app.services.image_generator import generate_all_site_images, _has_api_key as _has_image_api_key, _svg_placeholder
    _has_image_generation = True
except Exception:
    _has_image_generation = False

    def _has_image_api_key() -> bool:
        return False

    def _svg_placeholder(width: int, height: int, label: str = "", bg_color: str = "#1a1a2e", text_color: str = "#94a3b8") -> str:
        import urllib.parse
        label_escaped = label.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            f'<rect fill="{bg_color}" width="{width}" height="{height}"/>'
            f'<text x="50%" y="50%" fill="{text_color}" font-family="system-ui,sans-serif" font-size="18" text-anchor="middle" dy=".3em">{label_escaped}</text>'
            f'</svg>'
        )
        return f"data:image/svg+xml,{urllib.parse.quote(svg)}"

# Design knowledge (SQLite FTS5) - graceful fallback if not available
try:
    from app.services.design_knowledge import get_creative_context, get_collection_stats
    _has_design_knowledge = True
except Exception:
    _has_design_knowledge = False

# Diversity agent (Qwen3/Groq) - graceful fallback if not available
try:
    from app.services.diversity_agent import get_diversity_suggestions, _generate_local_diversity
    _has_diversity_agent = True
except Exception:
    _has_diversity_agent = False

# Reference HTML sites for quality injection
try:
    from app.services.reference_sites import get_reference_for_category
    _has_reference_sites = True
except Exception:
    _has_reference_sites = False

# Color palette generator (Adobe Color-style harmony)
try:
    from app.services.color_palette import generate_palette as _generate_harmony_palette
    _has_palette_gen = True
except Exception:
    _has_palette_gen = False

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
        "border_radius_style": "soft", "shadow_style": "soft", "spacing_density": "normal",
    },
    {
        "primary_color": "#0D9488", "secondary_color": "#0C4A6E", "accent_color": "#FB7185",
        "bg_color": "#F0FDFA", "bg_alt_color": "#CCFBF1", "text_color": "#0F172A", "text_muted_color": "#64748B",
        "font_heading": "Sora", "font_heading_url": "Sora:wght@400;600;700;800",
        "font_body": "Inter", "font_body_url": "Inter:wght@400;500;600",
        "border_radius_style": "pill", "shadow_style": "soft", "spacing_density": "normal",
    },
    {
        "primary_color": "#DC2626", "secondary_color": "#1E293B", "accent_color": "#FBBF24",
        "bg_color": "#FFFBEB", "bg_alt_color": "#FEF3C7", "text_color": "#1C1917", "text_muted_color": "#78716C",
        "font_heading": "DM Serif Display", "font_heading_url": "DM+Serif+Display:wght@400",
        "font_body": "Plus Jakarta Sans", "font_body_url": "Plus+Jakarta+Sans:wght@400;500;600;700",
        "border_radius_style": "sharp", "shadow_style": "none", "spacing_density": "compact",
    },
    {
        "primary_color": "#059669", "secondary_color": "#78350F", "accent_color": "#F472B6",
        "bg_color": "#ECFDF5", "bg_alt_color": "#D1FAE5", "text_color": "#064E3B", "text_muted_color": "#6B7280",
        "font_heading": "Fraunces", "font_heading_url": "Fraunces:wght@400;600;700;800",
        "font_body": "Nunito Sans", "font_body_url": "Nunito+Sans:wght@400;500;600;700",
        "border_radius_style": "round", "shadow_style": "soft", "spacing_density": "generous",
    },
    {
        "primary_color": "#7C2D12", "secondary_color": "#4338CA", "accent_color": "#22D3EE",
        "bg_color": "#FEF3C7", "bg_alt_color": "#FDE68A", "text_color": "#1C1917", "text_muted_color": "#92400E",
        "font_heading": "Playfair Display", "font_heading_url": "Playfair+Display:wght@400;600;700;800",
        "font_body": "Lato", "font_body_url": "Lato:wght@400;700",
        "border_radius_style": "soft", "shadow_style": "dramatic", "spacing_density": "generous",
    },
    {
        "primary_color": "#A855F7", "secondary_color": "#EC4899", "accent_color": "#22D3EE",
        "bg_color": "#0F172A", "bg_alt_color": "#1E293B", "text_color": "#F1F5F9", "text_muted_color": "#CBD5E1",
        "font_heading": "Outfit", "font_heading_url": "Outfit:wght@400;600;700;800",
        "font_body": "DM Sans", "font_body_url": "DM+Sans:wght@400;500;600",
        "border_radius_style": "pill", "shadow_style": "dramatic", "spacing_density": "normal",
    },
    {
        "primary_color": "#B8860B", "secondary_color": "#1C1917", "accent_color": "#047857",
        "bg_color": "#FFFDD0", "bg_alt_color": "#FEF9C3", "text_color": "#1C1917", "text_muted_color": "#78716C",
        "font_heading": "Cormorant Garamond", "font_heading_url": "Cormorant+Garamond:wght@400;600;700",
        "font_body": "Lato", "font_body_url": "Lato:wght@400;700",
        "border_radius_style": "soft", "shadow_style": "soft", "spacing_density": "generous",
    },
    {
        "primary_color": "#831843", "secondary_color": "#581C87", "accent_color": "#FBBF24",
        "bg_color": "#FFFFF0", "bg_alt_color": "#FEF3C7", "text_color": "#1E1B4B", "text_muted_color": "#6B7280",
        "font_heading": "Libre Baskerville", "font_heading_url": "Libre+Baskerville:wght@400;700",
        "font_body": "Karla", "font_body_url": "Karla:wght@400;500;600;700",
        "border_radius_style": "round", "shadow_style": "none", "spacing_density": "normal",
    },
]


def _pick_variety_context(category: str = "") -> Dict[str, Any]:
    """Pick blended personality, color mood, and font pairing for this generation.

    Uses generation_tracker to avoid recently used combinations.
    Instead of a single personality, picks two and blends them (70/30 ratio)
    to produce more original and less robotic output.
    """
    recently_used = get_recently_used(category=category, limit=15)

    # Pick personality with anti-repetition
    primary = pick_avoiding_recent(
        PERSONALITY_POOL,
        recently_used.get("personalities", set()),
        key_fn=lambda p: p["name"],
    )
    remaining = [p for p in PERSONALITY_POOL if p["name"] != primary["name"]]
    secondary = random.choice(remaining) if remaining else primary
    blended = {
        "name": f"{primary['name']}+{secondary['name']}",
        "directive": (
            f"You have a BLENDED personality: 70% {primary['name'].upper()} and 30% {secondary['name'].upper()}.\n"
            f"PRIMARY VOICE (dominant): {primary['directive']}\n"
            f"SECONDARY VOICE (accent): {secondary['directive']}\n"
            f"Blend them: the primary voice leads, the secondary adds unexpected nuance. "
            f"This mix must feel NATURAL, not schizophrenic."
        ),
        "headline_style": f"primarily {primary['headline_style']}, with touches of {secondary['headline_style']}",
    }

    # Pick color mood avoiding recent ones
    color_mood = pick_avoiding_recent(
        COLOR_MOOD_POOL,
        recently_used.get("color_moods", set()),
        key_fn=lambda m: m["mood"],
    )

    # Pick font pairing avoiding recent headings
    font_pairing = pick_avoiding_recent(
        FONT_PAIRING_POOL,
        recently_used.get("font_headings", set()),
        key_fn=lambda f: f["heading"],
    )

    return {
        "personality": blended,
        "color_mood": color_mood,
        "font_pairing": font_pairing,
        "_recently_used": recently_used,  # Pass through for downstream use
    }


# =========================================================
# CATEGORY TONE PROFILES
# Injected into _generate_texts() prompt so the AI adapts
# its voice to the business sector, not just the personality.
# =========================================================
CATEGORY_TONES: Dict[str, str] = {
    "restaurant": (
        "TONO: Sensoriale, intimo, poetico. Evoca profumi, consistenze, luci soffuse. "
        "Scrivi come se il lettore potesse assaggiare le parole. Usa sinestesie "
        "(\"un sapore che suona come jazz\"). Il cibo e' memoria, identita', rituale."
    ),
    "saas": (
        "TONO: Affilato, sicuro, orientato ai risultati. Numeri specifici, "
        "contrasti prima/dopo, promesse misurabili. Niente buzzword vuote: "
        "ogni frase deve rispondere a 'perche' dovrei scegliere voi?'. "
        "Pensa a Stripe, Linear, Vercel — copy che taglia."
    ),
    "portfolio": (
        "TONO: Autoriale, visionario, leggermente enigmatico. "
        "Ogni progetto e' una storia, non una voce di catalogo. "
        "Parla del PERCHE', non del cosa. Il designer/artista ha una filosofia, "
        "non solo competenze. Ispira curiosita'."
    ),
    "ecommerce": (
        "TONO: Desiderio, identita', trasformazione. Non vendi prodotti, "
        "vendi chi il cliente DIVENTA. Linguaggio aspirazionale ma autentico. "
        "Dettagli sensoriali sui materiali, la fattura, l'esperienza di unboxing. "
        "Urgenza sottile, mai aggressiva."
    ),
    "business": (
        "TONO: Autorevole, visionario, concreto. Bilancia fiducia e ambizione. "
        "Numeri che dimostrano, non che vantano. Parla del futuro del cliente, "
        "non del passato dell'azienda. Ogni frase costruisce credibilita' "
        "attraverso specificita', non attraverso aggettivi."
    ),
    "blog": (
        "TONO: Intellettuale, curioso, provocatorio. Ogni titolo e' una domanda "
        "che il lettore non sapeva di avere. Crea tensione tra il conosciuto e "
        "l'inaspettato. Il blog non informa — sfida, reinterpreta, illumina."
    ),
    "event": (
        "TONO: Elettrico, urgente, esperienziale. Il lettore deve sentire "
        "l'energia PRIMA di arrivare. FOMO strategico: non 'partecipa', "
        "ma 'non puoi permetterti di perdere questo'. Date, numeri, "
        "countdown. Ogni parola accelera il battito."
    ),
    "custom": (
        "TONO: Adatta il tono al tipo di attivita' descritto. "
        "Se non e' chiaro, usa un mix di autorevolezza e calore. "
        "Copy che potrebbe vincere un Awwwards: specifico, ritmato, memorabile."
    ),
}

# =========================================================
# STYLE_TONE_MAP: Per-style copywriting directives.
# While CATEGORY_TONES sets the broad sector voice (restaurant,
# saas, etc.), this map overrides/refines the tone for each
# specific template sub-style. "restaurant-elegant" should read
# COMPLETELY different from "restaurant-cozy".
# Injected into BOTH _generate_texts() and _generate_theme()
# so that fonts, colors, AND copy all speak the same language.
# =========================================================
STYLE_TONE_MAP: Dict[str, Dict[str, str]] = {
    "restaurant-elegant": {
        "voice": (
            "VOCE: Formale, raffinata, sussurrata. Come un maitre d'hotel che ti accoglie per nome. "
            "Frasi lunghe ed eleganti, vocabolario ricercato (degustazione, mise en place, terroir). "
            "Mai esclamazioni, mai punti esclamativi. Il lusso non grida."
        ),
        "headlines": "Titoli evocativi e poetici. Metafore sensoriali. MAX 5 parole. Es: 'Dove il Gusto Diventa Arte'.",
        "theme_hint": (
            "Palette calda e profonda: bordeaux, oro antico, crema avorio. Font serif classico (Playfair, Cormorant). "
            "shadow_style: soft. spacing_density: generous. border_radius_style: soft."
        ),
    },
    "restaurant-cozy": {
        "voice": (
            "VOCE: Calda, familiare, come una nonna che ti invita a sederti. Tono colloquiale ma mai sciatto. "
            "Frasi brevi e affettuose. Parole che sanno di casa: 'fatto a mano', 'ricetta della nonna', "
            "'come una volta'. Accogliente, mai formale."
        ),
        "headlines": "Titoli che sorridono. Tono amichevole, quasi intimo. Es: 'A Casa Nostra, Si Mangia Col Cuore'.",
        "theme_hint": (
            "Colori caldi e terrosi: terracotta, arancio tenue, verde salvia, beige. Font morbido e arrotondato "
            "(Nunito, Quicksand heading). shadow_style: soft. spacing_density: normal. border_radius_style: round."
        ),
    },
    "restaurant-modern": {
        "voice": (
            "VOCE: Tagliente, contemporanea, magazine-style. Come Bon Appetit o Eater. "
            "Frasi corte e d'impatto. Giustapposizioni: 'Tradizione. Rivista.' — 'Fuoco. Tecnica. Ossessione.' "
            "Zero nostalgia, tutta innovazione. Food come design."
        ),
        "headlines": "Titoli brutali e minimali. Una parola. Un concetto. Es: 'Fuoco Vivo' o 'Crudo. Puro. Nostro.'.",
        "theme_hint": (
            "Palette ad alto contrasto: nero/bianco con un accento vivace (rosso fuoco, lime). Font sans-serif "
            "geometrico bold (Space Grotesk, Archivo). shadow_style: none. spacing_density: compact. "
            "border_radius_style: sharp."
        ),
    },
    "saas-gradient": {
        "voice": (
            "VOCE: Energica, futuristica, tech-ottimista. Come la landing page di Vercel o Linear. "
            "Promesse audaci con numeri specifici. Linguaggio da startup che sta cambiando il mondo. "
            "Verbi d'azione forti: 'accelera', 'scala', 'automatizza', 'domina'."
        ),
        "headlines": "Titoli brevi e potenti con numeri o verbi d'azione. Es: '10x Piu' Veloce' o 'Il Futuro e' Adesso'.",
        "theme_hint": (
            "Palette scura con gradienti vibranti: deep purple→electric blue, dark bg con glow neon. "
            "Font geometrico moderno (Sora, Inter heading bold). shadow_style: dramatic. "
            "spacing_density: normal. border_radius_style: soft."
        ),
    },
    "saas-clean": {
        "voice": (
            "VOCE: Chiara, diretta, senza fronzoli. Come Notion o Stripe. Ogni parola ha uno scopo. "
            "Niente metafore eccessive — chiarezza sopra tutto. Il prodotto parla da solo. "
            "Benefici misurabili, frasi che un CEO condividerebbe su LinkedIn."
        ),
        "headlines": "Titoli funzionali ma eleganti. Chiarezza > creativita'. Es: 'Tutto in Un Solo Strumento'.",
        "theme_hint": (
            "Palette luminosa e pulita: bianco/grigio chiaro con un primary vibrante (blue, indigo). "
            "Font sans-serif pulito (Inter, Plus Jakarta Sans). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: soft."
        ),
    },
    "saas-dark": {
        "voice": (
            "VOCE: Tecnica, affilata, da developer-tool. Come GitHub, Raycast, o Warp terminal. "
            "Gergo tech accettato. Poche parole, massima densita' informativa. "
            "Copy che sembra codice: preciso, senza sprechi. Mai 'soluzione innovativa' — "
            "piuttosto 'build, ship, iterate'."
        ),
        "headlines": "Titoli ultra-minimali, quasi comandi. Es: 'Ship Faster.' o 'Zero Config. Full Power.'.",
        "theme_hint": (
            "Palette dark-mode: charcoal/navy profondo, accento neon (cyan, green, amber). "
            "Font monospace o geometric (JetBrains Mono heading, Space Grotesk). shadow_style: none. "
            "spacing_density: compact. border_radius_style: sharp."
        ),
    },
    "portfolio-gallery": {
        "voice": (
            "VOCE: Visiva, minimale, ogni parola e' didascalia. Come un catalogo d'arte o Behance. "
            "I progetti parlano — il testo accompagna, non domina. Frasi poetiche e frammentarie. "
            "Il designer non spiega, mostra. 'Esplora il progetto' non 'Guarda i nostri lavori'."
        ),
        "headlines": "Titoli evocativi e astratti. Es: 'Forme che Parlano' o 'Spazio. Luce. Intenzione.'.",
        "theme_hint": (
            "Palette neutra con un accento deciso: bianco/nero + un colore signature (rosso, electric blue). "
            "Font display con carattere (Instrument Serif, Space Grotesk). shadow_style: none. "
            "spacing_density: generous. border_radius_style: sharp."
        ),
    },
    "portfolio-minimal": {
        "voice": (
            "VOCE: Ultra-ridotta, zen-like. Come il portfolio di un designer svizzero. "
            "Ogni parola e' pesata come in un haiku. Nessun aggettivo superfluo. "
            "Il vuoto parla piu' del pieno. Bio in terza persona, distaccata e autorevole."
        ),
        "headlines": "Titoli di una o due parole. Es: 'Design.' o 'Meno, Meglio.'.",
        "theme_hint": (
            "Palette monocromatica: bianco purissimo o nero profondo, quasi nessun colore. "
            "Font sans-serif raffinato con molto tracking (Epilogue, Albert Sans). shadow_style: none. "
            "spacing_density: generous. border_radius_style: sharp."
        ),
    },
    "portfolio-creative": {
        "voice": (
            "VOCE: Esplosiva, giocosa, anti-convenzionale. Come un manifesto artistico. "
            "Rompi le regole della punteggiatura. Mix di lingue accettato. Emotivo e viscerale. "
            "Il creativo non e' un fornitore — e' un visionario che trasforma brand."
        ),
        "headlines": "Titoli provocatori, anche irriverenti. Es: 'Facciamo Cose Belle (Sul Serio)' o 'Caos Calcolato'.",
        "theme_hint": (
            "Palette audace e inaspettata: accostamenti non convenzionali (lime+magenta, coral+indigo). "
            "Font display grassissimo (Unbounded, Archivo Black). shadow_style: dramatic. "
            "spacing_density: normal. border_radius_style: round."
        ),
    },
    "ecommerce-modern": {
        "voice": (
            "VOCE: Aspirazionale ma accessibile. Come Glossier o Everlane. "
            "Il prodotto diventa lifestyle. Linguaggio sensoriale sui materiali e l'esperienza. "
            "Urgenza morbida: 'Edizione limitata' non 'COMPRA ORA'. "
            "Ogni descrizione e' una micro-storia."
        ),
        "headlines": "Titoli che creano desiderio. Es: 'Progettato per Chi Non si Accontenta'.",
        "theme_hint": (
            "Palette lifestyle: toni neutri caldi (blush, sand, sage) con primary deciso. "
            "Font moderno elegante (DM Sans, Plus Jakarta Sans). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: soft."
        ),
    },
    "ecommerce-luxury": {
        "voice": (
            "VOCE: Esclusiva, sussurrata, da maison. Come Hermes o Bottega Veneta. "
            "Mai vendere — invitare. Mai 'economico' — 'accessibile'. Mai 'prodotto' — 'creazione'. "
            "Frasi brevi, peso specifico altissimo. L'understatement e' il vero lusso."
        ),
        "headlines": "Titoli che non spiegano, evocano. Es: 'L'Arte del Dettaglio' o 'Senza Tempo'.",
        "theme_hint": (
            "Palette lusso: nero/champagne/oro, fondi scuri con tipografia chiara. "
            "Font serif sofisticato (Playfair Display, DM Serif Display). shadow_style: dramatic. "
            "spacing_density: generous. border_radius_style: soft."
        ),
    },
    "business-corporate": {
        "voice": (
            "VOCE: Autorevole, strutturata, da report annuale di alto livello. Come McKinsey o Deloitte. "
            "Dati concreti, case study impliciti, linguaggio che ispira fiducia istituzionale. "
            "Mai informale. Il 'noi' aziendale e' forte e coeso."
        ),
        "headlines": "Titoli che comunicano solidita' e visione. Es: 'Costruiamo il Futuro delle Imprese'.",
        "theme_hint": (
            "Palette professionale: navy, grigio-blu, bianco. Accento corporate (teal o gold). "
            "Font serif autorevole per heading (DM Serif Display), sans-serif per body. "
            "shadow_style: soft. spacing_density: normal. border_radius_style: soft."
        ),
    },
    "business-trust": {
        "voice": (
            "VOCE: Empatica, rassicurante, concreta. Come un consulente che ti prende per mano. "
            "Meno 'noi siamo bravi' e piu' 'tu otterrai questo'. Focus su risultati tangibili. "
            "Testimonial e numeri costruiscono credibilita' naturale."
        ),
        "headlines": "Titoli orientati al risultato del cliente. Es: 'Il Tuo Successo e' la Nostra Misura'.",
        "theme_hint": (
            "Palette calda e affidabile: blu medio, verde, terra di Siena. Sfondo caldo (cream/ivory). "
            "Font amichevole ma professionale (Source Serif, Lora heading). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: round."
        ),
    },
    "business-fresh": {
        "voice": (
            "VOCE: Giovane, energica, startup-vibes. Come Mailchimp o Slack. "
            "Tono conversazionale, quasi amichevole. Emoji strategici OK. "
            "Humor sottile accettato. Parole corte, frasi che rimbalzano. "
            "Il business e' serio, il tono no."
        ),
        "headlines": "Titoli giocosi e diretti. Es: 'Basta Fogli Excel. Davvero.' o 'Lavora Meglio, Non di Piu''.",
        "theme_hint": (
            "Palette vivace e pop: primary brillante (viola, coral, teal), sfondo chiaro e fresco. "
            "Font sans-serif rotondo e friendly (Nunito, Outfit). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: round."
        ),
    },
    "blog-editorial": {
        "voice": (
            "VOCE: Intellettuale, narrativa, da rivista letteraria. Come The Atlantic o Il Post. "
            "Frasi lunghe e ben costruite. Citazioni, domande retoriche, aperture in medias res. "
            "Il blog non informa — crea pensiero. Ogni articolo e' un mini-saggio."
        ),
        "headlines": "Titoli che pongono domande o provocano. Es: 'Perche' Nessuno Parla di Questo?' o 'La Fine di un'Era'.",
        "theme_hint": (
            "Palette editoriale: fondi carta (ivory, linen), testo scuro ricco, accento minimo. "
            "Font serif da rivista (Instrument Serif, Lora heading). shadow_style: none. "
            "spacing_density: generous. border_radius_style: sharp."
        ),
    },
    "blog-dark": {
        "voice": (
            "VOCE: Intima, notturna, da blog tech/culture. Come The Verge o Wired dark mode. "
            "Tono informato e opinionated. Mix di analisi tecnica e storytelling. "
            "Linguaggio contemporaneo, riferimenti culturali, frasi nette e taglienti."
        ),
        "headlines": "Titoli d'impatto, stile news/tech. Es: 'L'Algoritmo Che Cambia Tutto' o 'Deep Dive: Oltre il Codice'.",
        "theme_hint": (
            "Palette dark: background scuro (charcoal, navy), testo chiaro, accento neon vivace. "
            "Font moderno e leggibile (Space Grotesk, Sora). shadow_style: soft. "
            "spacing_density: normal. border_radius_style: soft."
        ),
    },
    "event-vibrant": {
        "voice": (
            "VOCE: Elettrica, urgente, da festival poster. Come Primavera Sound o Web Summit. "
            "FOMO puro. Countdown implicito. Numeri ovunque (speaker, ore, partecipanti). "
            "Frasi brevissime. Imperativi. 'Non Mancare.' 'Ci Vediamo Li'.' "
            "L'energia deve uscire dallo schermo."
        ),
        "headlines": "Titoli da poster: grandi, audaci, 3 parole max. Es: 'L'Evento dell'Anno' o 'Preparati.'.",
        "theme_hint": (
            "Palette esplosiva: gradienti neon, accostamenti elettrici (magenta+cyan, arancio+viola). "
            "Font display gigantesco (Unbounded, Space Grotesk 900). shadow_style: dramatic. "
            "spacing_density: compact. border_radius_style: round."
        ),
    },
    "event-minimal": {
        "voice": (
            "VOCE: Elegante, curata, da invito esclusivo. Come un vernissage o un TED Talk. "
            "Poche parole, massima eleganza. L'evento parla di qualita', non di quantita'. "
            "Dettagli pratici (data, luogo, orario) presentati con grazia tipografica."
        ),
        "headlines": "Titoli raffinati e puliti. Es: 'Un Incontro di Menti' o '12 Aprile. Milano. Sii Presente.'.",
        "theme_hint": (
            "Palette sofisticata: bianco/nero con un accento metallico (oro, argento). "
            "Font serif elegante (Cormorant, Instrument Serif). shadow_style: none. "
            "spacing_density: generous. border_radius_style: sharp."
        ),
    },
}


def _get_style_tone(template_style_id: Optional[str]) -> str:
    """Build style-specific tone directive for prompt injection.

    Returns a formatted block with voice, headline, and visual
    directives for the specific sub-style (e.g., 'restaurant-elegant'
    vs 'restaurant-cozy'). Returns empty string if no match.
    """
    if not template_style_id:
        return ""
    tone = STYLE_TONE_MAP.get(template_style_id)
    if not tone:
        return ""
    lines = [
        f"=== IDENTITA' STILISTICA: {template_style_id.upper()} (SEGUI QUESTE DIRETTIVE ALLA LETTERA) ===",
        tone["voice"],
        f"HEADLINE STYLE: {tone['headlines']}",
        "=== FINE IDENTITA' STILISTICA ===",
    ]
    return "\n".join(lines)


def _get_style_theme_hint(template_style_id: Optional[str]) -> str:
    """Return theme-specific directives (colors, fonts, layout tokens) for the style."""
    if not template_style_id:
        return ""
    tone = STYLE_TONE_MAP.get(template_style_id)
    if not tone or "theme_hint" not in tone:
        return ""
    return (
        f"\n=== STYLE IDENTITY: {template_style_id.upper()} (adapt palette to match) ===\n"
        f"{tone['theme_hint']}\n"
        f"=== END STYLE IDENTITY ===\n"
    )


# =========================================================
# FEW-SHOT EXAMPLES: Award-winning Italian copy per category.
# Injected into _generate_texts() so the AI sees CONCRETE
# examples of the quality level expected. 2 examples each.
# =========================================================
FEW_SHOT_EXAMPLES: Dict[str, List[Dict[str, Any]]] = {
    "restaurant": [
        {
            "hero_title": "Dove il Tempo si Ferma a Tavola",
            "hero_subtitle": (
                "Ogni piatto nasce da un dialogo silenzioso tra la terra e le mani "
                "dello chef. Non serviamo cena — creiamo il ricordo che racconterai domani. "
                "Stagionalita' radicale, zero compromessi."
            ),
            "service_title": "Il Rituale del Fuoco",
            "service_description": (
                "Cotture lente su brace di quercia centenaria. 14 ore di pazienza per "
                "trasformare un taglio umile in qualcosa che non dimenticherai. La fiamma "
                "non ha fretta, e nemmeno noi."
            ),
            "testimonial": (
                "Ho chiuso gli occhi al primo boccone e ho rivisto la cucina di mia nonna "
                "a Matera. Non succedeva da vent'anni. Mia moglie dice che ho pianto — "
                "io dico che era il pepe. Ci torniamo ogni anniversario, ormai e' tradizione."
            ),
        },
        {
            "hero_title": "Sapori Che Raccontano Storie",
            "hero_subtitle": (
                "Trentadue ingredienti locali, sette fornitori che conosciamo per nome, "
                "un menu che cambia quando cambia il vento. Cucina d'autore che sa di casa, "
                "non di pretesa."
            ),
            "service_title": "L'Orto Segreto",
            "service_description": (
                "A 400 metri dal ristorante, il nostro orto biodinamico detta il menu. "
                "Quello che raccogliamo la mattina, lo serviamo la sera. Nessun intermediario "
                "tra la radice e il tuo piatto."
            ),
            "testimonial": (
                "Siamo arrivati per caso, sotto la pioggia, senza prenotazione. Tre ore dopo "
                "stavamo brindando col sommelier come vecchi amici. Il risotto allo zafferano "
                "dell'orto? Ancora ci penso, a distanza di sei mesi."
            ),
        },
    ],
    "saas": [
        {
            "hero_title": "Meno Caos. Piu' Risultati.",
            "hero_subtitle": (
                "Il tuo team perde 23 ore a settimana in task ripetitivi. "
                "Noi le restituiamo. Automazione intelligente che si adatta al tuo flusso, "
                "non il contrario. Setup in 4 minuti, ROI dal primo giorno."
            ),
            "service_title": "Automazione Predittiva",
            "service_description": (
                "L'AI analizza 10.000 pattern nel tuo workflow e anticipa i colli di bottiglia "
                "prima che esistano. Non reagire ai problemi — previenili. "
                "I nostri clienti riducono i ritardi del 67% nel primo trimestre."
            ),
            "testimonial": (
                "Prima gestivamo 200 ticket al giorno con 8 persone. Ora ne gestiamo 340 "
                "con 5. Non e' magia — e' che finalmente il software lavora PER noi, "
                "non CONTRO di noi. Il team e' tornato a fare il lavoro che conta."
            ),
        },
        {
            "hero_title": "847 Progetti. Zero Compromessi.",
            "hero_subtitle": (
                "Ogni feature nasce da un problema reale, non da una slide. "
                "Dashboard che parla la tua lingua, integrazioni che funzionano al primo click, "
                "supporto che risponde in 90 secondi. Provalo gratis, poi decidi."
            ),
            "service_title": "Dashboard Viva",
            "service_description": (
                "Dimentica i report statici di fine mese. La nostra dashboard si aggiorna "
                "in tempo reale, evidenzia anomalie con alert intelligenti e suggerisce "
                "azioni correttive. I tuoi dati, finalmente, parlano chiaro."
            ),
            "testimonial": (
                "Ho convinto il CEO con un solo screenshot della dashboard. In 30 secondi "
                "ha visto quello che prima richiedeva 3 riunioni e un foglio Excel da incubo. "
                "Budget approvato in giornata — mai successo prima."
            ),
        },
    ],
    "portfolio": [
        {
            "hero_title": "Ogni Pixel Ha un Perche'",
            "hero_subtitle": (
                "Non creo siti web. Creo sistemi visivi che trasformano visitatori distratti "
                "in clienti convinti. 12 anni di ossessione per il dettaglio, "
                "47 brand reinventati, zero template riciclati."
            ),
            "service_title": "Brand Identity Radicale",
            "service_description": (
                "Parto da chi sei veramente, non da chi vorresti sembrare. Interviste, "
                "analisi competitiva, moodboard che sfidano — e poi il logo arriva come "
                "una conseguenza naturale, non come una decorazione."
            ),
            "testimonial": (
                "Gli ho detto 'voglio qualcosa di diverso' aspettandomi il solito moodboard "
                "su Pinterest. Mi ha presentato un manifesto di 12 pagine sulla mia azienda "
                "che nemmeno io avrei saputo scrivere. Il rebranding ha aumentato "
                "le conversioni del 180%."
            ),
        },
        {
            "hero_title": "Design Senza Compromessi",
            "hero_subtitle": (
                "Tre regole: funziona, emoziona, dura. Il bello senza sostanza e' decorazione. "
                "La sostanza senza bellezza e' un foglio Excel. "
                "Io cerco il punto esatto dove si incontrano."
            ),
            "service_title": "UX Che Respira",
            "service_description": (
                "Ogni interfaccia che disegno viene testata con utenti reali prima di "
                "vedere la luce. Prototipi interattivi, A/B test, heatmap. "
                "Il design bello che nessuno usa e' solo arte — io faccio strumenti."
            ),
            "testimonial": (
                "Il nostro e-commerce aveva un tasso di abbandono carrello del 78%. "
                "Dopo il redesign, e' sceso al 31%. Non ha cambiato i colori — ha ripensato "
                "l'intero percorso dell'utente. Numeri che parlano."
            ),
        },
    ],
    "ecommerce": [
        {
            "hero_title": "Non Compri un Oggetto. Scegli Chi Vuoi Essere.",
            "hero_subtitle": (
                "Ogni pezzo della collezione nasce da 200 ore di artigianato e una domanda: "
                "'Lo terrai per sempre?'. Materiali che invecchiano con grazia, "
                "design che non segue le stagioni ma le anticipa."
            ),
            "service_title": "Pelle Che Racconta",
            "service_description": (
                "Conceria toscana, concia vegetale, 18 mesi di stagionatura. "
                "Ogni borsa porta i segni del suo viaggio — graffi, patina, carattere. "
                "Non la sostituirai. La erediterai."
            ),
            "testimonial": (
                "Ho aperto la scatola e ho sentito l'odore del cuoio prima ancora di vederla. "
                "La uso ogni giorno da 14 mesi e la pelle ha preso un colore ambrato "
                "che non esisteva all'inizio. E' diventata piu' bella con il tempo, come "
                "dovrebbero essere tutte le cose."
            ),
        },
        {
            "hero_title": "Il Lusso e' nella Scelta Consapevole",
            "hero_subtitle": (
                "Zero fast fashion, zero sovrapproduzione. Edizioni limitate da 50 pezzi, "
                "tessuti certificati, filiera trasparente dal filo al bottone. "
                "Quando scegli qualita', il pianeta ringrazia."
            ),
            "service_title": "Spedizione Rituale",
            "service_description": (
                "Packaging in carta riciclata con sigillo in ceralacca, biglietto scritto "
                "a mano, sacchetto in cotone organico. L'esperienza inizia "
                "dall'apertura della scatola, non dall'indossare il capo."
            ),
            "testimonial": (
                "Mia figlia mi ha chiesto perche' quella maglietta costava 'cosi' tanto'. "
                "Le ho fatto toccare il tessuto, leggere l'etichetta, sentire la differenza. "
                "Ora e' lei che non vuole piu' comprare fast fashion. "
                "Investimento migliore della mia vita."
            ),
        },
    ],
    "business": [
        {
            "hero_title": "Costruiamo il Domani. Oggi.",
            "hero_subtitle": (
                "In 15 anni abbiamo accompagnato 340 aziende dalla visione all'esecuzione. "
                "Non vendiamo consulenza — costruiamo ponti tra dove sei "
                "e dove il mercato ti aspetta. Risultati misurabili, non presentazioni."
            ),
            "service_title": "Strategia Operativa",
            "service_description": (
                "Basta piani strategici che finiscono in un cassetto. Il nostro metodo "
                "traduce la visione in sprint da 90 giorni con KPI chiari, owner definiti "
                "e review settimanali. La strategia funziona solo se cammina."
            ),
            "testimonial": (
                "Avevamo provato 3 societa' di consulenza in 5 anni. Slide bellissime, "
                "risultati zero. Questi sono entrati in azienda il lunedi' e il venerdi' "
                "avevamo gia' il primo processo ottimizzato. Il fatturato e' cresciuto "
                "del 34% in 8 mesi. Niente magia — metodo."
            ),
        },
        {
            "hero_title": "Dove Nasce il Cambiamento",
            "hero_subtitle": (
                "Il mercato non aspetta chi esita. Analisi predittiva, "
                "trasformazione digitale e un team che ha detto 'no' a 200 clienti "
                "per dire 'si' a quelli giusti. La tua crescita e' la nostra reputazione."
            ),
            "service_title": "Digital Acceleration",
            "service_description": (
                "Audit completo in 72 ore, roadmap personalizzata in 2 settimane, "
                "primi risultati in 30 giorni. Non digitalizziamo processi rotti — "
                "li ripensiamo da zero e poi li automatizziamo."
            ),
            "testimonial": (
                "Il nostro settore era fermo agli anni '90. Processi cartacei, Excel ovunque, "
                "decisioni a intuito. In 6 mesi ci hanno portato nel 2024. "
                "I dipendenti che resistevano al cambiamento ora sono i piu' entusiasti. "
                "Questo vale piu' di qualsiasi ROI."
            ),
        },
    ],
    "blog": [
        {
            "hero_title": "Le Idee Che Cambiano le Regole",
            "hero_subtitle": (
                "Non un altro blog di settore. Un laboratorio di pensiero dove "
                "le certezze vengono smontate, le tendenze anticipate e le domande "
                "scomode trovano risposte scomode. Leggi solo se vuoi cambiare idea."
            ),
            "service_title": "Deep Dive Settimanale",
            "service_description": (
                "Ogni giovedi', un'analisi di 2.000 parole che spacca un tema in due. "
                "Dati originali, interviste esclusive, zero riciclo di comunicati stampa. "
                "Il tipo di articolo che salvi nei preferiti e condividi con il team."
            ),
            "testimonial": (
                "Ho smesso di leggere newsletter due anni fa. Questa e' l'unica che apro "
                "il giovedi' mattina prima del caffe'. L'articolo sulla disruption del retail "
                "l'ho fatto leggere a tutto il board. Ha cambiato la nostra strategia Q3."
            ),
        },
        {
            "hero_title": "Pensiero Critico, Zero Filtri",
            "hero_subtitle": (
                "47.000 lettori che preferiscono la verita' scomoda alla rassicurazione facile. "
                "Analisi controcorrente, dati che contraddicono i titoli, "
                "prospettive che nessun altro osa pubblicare."
            ),
            "service_title": "Il Contrarian Report",
            "service_description": (
                "Una volta al mese prendiamo la narrativa dominante del settore "
                "e la mettiamo alla prova dei fatti. Con dati, fonti, e il coraggio "
                "di dire quello che tutti pensano ma nessuno scrive."
            ),
            "testimonial": (
                "L'analisi sul fallimento delle startup 'purpose-driven' mi ha fatto "
                "ripensare l'intero pitch deck. Scomodo? Si'. Necessario? Assolutamente. "
                "E' il blog che leggo per non restare nella bolla."
            ),
        },
    ],
    "event": [
        {
            "hero_title": "Non Partecipare. Vivi.",
            "hero_subtitle": (
                "12 ore che comprimeranno 12 mesi di ispirazione. "
                "Speaker che hanno cambiato industrie, workshop dove le idee diventano "
                "prototipi e 800 persone che condividono la stessa urgenza di fare."
            ),
            "service_title": "Masterclass Immersiva",
            "service_description": (
                "Niente slide da 50 pagine. 90 minuti di pratica pura con chi ha costruito "
                "aziende da zero. Gruppi da massimo 15 persone, "
                "un progetto reale da portare a casa. Impari facendo, non ascoltando."
            ),
            "testimonial": (
                "Sono andata per networking e sono tornata con un co-founder, "
                "tre clienti e un'idea che ha raccolto 200k in seed round. "
                "L'anno prima ho saltato l'evento. Non faro' mai piu' quell'errore."
            ),
        },
        {
            "hero_title": "Il Momento e' Adesso",
            "hero_subtitle": (
                "350 posti. 2.400 richieste. Una sola edizione all'anno. "
                "Non e' esclusivita' — e' la promessa che ogni persona in sala "
                "ha qualcosa da insegnarti. La lista d'attesa apre tra 48 ore."
            ),
            "service_title": "After Dark Sessions",
            "service_description": (
                "Quando le luci del palco si spengono, il vero evento inizia. "
                "Conversazioni informali con gli speaker, musica live, cena condivisa. "
                "Le connessioni migliori nascono dopo le 22."
            ),
            "testimonial": (
                "Al terzo cocktail ho trovato il coraggio di parlare con lo speaker "
                "che seguivo da anni. Mi ha dato un feedback sul mio progetto che valeva "
                "piu' di qualsiasi corso. Quell'incontro ha cambiato la traiettoria "
                "della mia carriera."
            ),
        },
    ],
    "custom": [
        {
            "hero_title": "Dove Tutto Prende Forma",
            "hero_subtitle": (
                "Non siamo per tutti — e va bene cosi'. Per chi cerca l'eccezionale "
                "nel quotidiano, per chi rifiuta il 'buono abbastanza', "
                "per chi sa che la differenza sta nei dettagli che nessuno nota. Tranne te."
            ),
            "service_title": "L'Approccio Sartoriale",
            "service_description": (
                "Niente soluzioni preconfezionate, niente template mentali. "
                "Ascoltiamo per tre volte il tempo che parliamo. Poi costruiamo "
                "qualcosa che non esisteva prima — su misura, come un abito "
                "che calza solo a te."
            ),
            "testimonial": (
                "Ho cercato per mesi qualcuno che capisse la mia visione senza che dovessi "
                "spiegarla tre volte. Alla prima call hanno completato le mie frasi. "
                "Il risultato? Esattamente quello che avevo in testa, "
                "ma meglio di come lo immaginavo."
            ),
        },
        {
            "hero_title": "L'Eccellenza Non e' un Caso",
            "hero_subtitle": (
                "Ogni dettaglio e' una decisione. Ogni decisione e' una dichiarazione. "
                "Lavoriamo con chi capisce che il valore si costruisce, "
                "non si dichiara. I risultati parlano — noi li facciamo gridare."
            ),
            "service_title": "Consulenza Strategica",
            "service_description": (
                "Due ore che valgono sei mesi di tentativi. Analizziamo il tuo mercato, "
                "smontiamo le assunzioni sbagliate, ricostruiamo la strategia "
                "su fondamenta solide. Niente teoria — solo azioni concrete con deadline."
            ),
            "testimonial": (
                "Ero scettico — l'ennesimo consulente, pensavo. Poi hanno trovato in 48 ore "
                "un problema che il mio team ignorava da 2 anni. Il fix ha aumentato "
                "la retention del 40%. A volte serve uno sguardo esterno per vedere "
                "l'ovvio."
            ),
        },
    ],
}


def _get_category_from_style_id(template_style_id: Optional[str]) -> str:
    """Extract business category from template_style_id (e.g., 'restaurant-elegant' -> 'restaurant')."""
    if template_style_id:
        category = template_style_id.split("-")[0].lower()
        if category in FEW_SHOT_EXAMPLES:
            return category
    return "custom"


def _build_few_shot_block(category: str) -> str:
    """Build the few-shot examples block for injection into the text generation prompt."""
    examples = FEW_SHOT_EXAMPLES.get(category, FEW_SHOT_EXAMPLES["custom"])
    tone = CATEGORY_TONES.get(category, CATEGORY_TONES["custom"])

    lines = []
    lines.append(f"=== TONE DI SETTORE ({category.upper()}) ===")
    lines.append(tone)
    lines.append("")
    lines.append("=== ESEMPI DI COPY ECCELLENTE (studia lo STILE, non copiare il contenuto) ===")
    lines.append("Questi esempi mostrano il LIVELLO QUALITATIVO atteso. Adatta lo stile a QUESTA azienda specifica.\n")

    for i, ex in enumerate(examples, 1):
        lines.append(f"--- Esempio {i} ---")
        lines.append(f"Hero Title: \"{ex['hero_title']}\"")
        lines.append(f"Hero Subtitle: \"{ex['hero_subtitle']}\"")
        lines.append(f"Service Title: \"{ex['service_title']}\"")
        lines.append(f"Service Description: \"{ex['service_description']}\"")
        lines.append(f"Testimonial: \"{ex['testimonial']}\"")
        lines.append("")

    lines.append("IMPORTANTE: NON copiare questi esempi. Usa lo stesso LIVELLO di qualita', specificita' e impatto emotivo per creare contenuti ORIGINALI per QUESTA azienda.")
    lines.append("=== FINE ESEMPI ===")

    return "\n".join(lines)


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
        "nav": "nav-classic-01",
        "hero": "hero-classic-01",
        "about": "about-magazine-01",
        "services": "services-alternating-rows-01",
        "gallery": "gallery-spotlight-01",
        "testimonials": "testimonials-spotlight-01",
        "contact": "contact-minimal-01",
        "footer": "footer-centered-01",
    },
    "restaurant-cozy": {
        "nav": "nav-classic-01",
        "hero": "hero-organic-01",
        "about": "about-split-scroll-01",
        "services": "services-icon-list-01",
        "gallery": "gallery-masonry-01",
        "testimonials": "testimonials-card-stack-01",
        "contact": "contact-card-01",
        "footer": "footer-multi-col-01",
    },
    "restaurant-modern": {
        "nav": "nav-minimal-01",
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
        "nav": "nav-minimal-01",
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
        "nav": "nav-classic-01",
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
        "nav": "nav-minimal-01",
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
        "nav": "nav-centered-01",
        "hero": "hero-editorial-01",
        "about": "about-image-showcase-01",
        "gallery": "gallery-masonry-01",
        "services": "services-minimal-list-01",
        "testimonials": "testimonials-grid-01",
        "contact": "contact-minimal-01",
        "footer": "footer-minimal-02",
    },
    "portfolio-minimal": {
        "nav": "nav-minimal-01",
        "hero": "hero-zen-01",
        "about": "about-alternating-01",
        "gallery": "gallery-lightbox-01",
        "contact": "contact-minimal-02",
        "footer": "footer-centered-01",
    },
    "portfolio-creative": {
        "nav": "nav-minimal-01",
        "hero": "hero-brutalist-01",
        "about": "about-bento-01",
        "gallery": "gallery-spotlight-01",
        "services": "services-hover-expand-01",
        "contact": "contact-card-01",
        "footer": "footer-gradient-01",
    },
    # --- E-commerce / Shop ---
    "ecommerce-modern": {
        "nav": "nav-classic-01",
        "hero": "hero-split-01",
        "about": "about-image-showcase-01",
        "services": "services-cards-grid-01",
        "gallery": "gallery-masonry-01",
        "testimonials": "testimonials-carousel-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-multi-col-01",
    },
    "ecommerce-luxury": {
        "nav": "nav-centered-01",
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
        "nav": "nav-classic-01",
        "hero": "hero-split-01",
        "about": "about-alternating-01",
        "services": "services-cards-grid-01",
        "features": "features-comparison-01",
        "testimonials": "testimonials-carousel-01",
        "contact": "contact-form-01",
        "footer": "footer-mega-01",
    },
    "business-trust": {
        "nav": "nav-classic-01",
        "hero": "hero-classic-01",
        "about": "about-timeline-01",
        "services": "services-process-steps-01",
        "team": "team-grid-01",
        "testimonials": "testimonials-spotlight-01",
        "contact": "contact-split-map-01",
        "footer": "footer-sitemap-01",
    },
    "business-fresh": {
        "nav": "nav-centered-01",
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
        "nav": "nav-centered-01",
        "hero": "hero-editorial-01",
        "about": "about-alternating-01",
        "services": "services-minimal-list-01",
        "gallery": "gallery-lightbox-01",
        "blog": "blog-editorial-grid-01",
        "contact": "contact-card-01",
        "footer": "footer-content-grid-01",
    },
    "blog-dark": {
        "nav": "nav-minimal-01",
        "hero": "hero-neon-01",
        "about": "about-split-cards-01",
        "services": "services-hover-reveal-01",
        "gallery": "gallery-filmstrip-01",
        "blog": "blog-cards-grid-01",
        "contact": "contact-minimal-02",
        "footer": "footer-gradient-01",
    },
    # --- Evento / Community ---
    "event-vibrant": {
        "nav": "nav-minimal-01",
        "hero": "hero-animated-shapes-01",
        "about": "about-bento-01",
        "services": "services-tabs-01",
        "team": "team-carousel-01",
        "schedule": "schedule-tabbed-multi-01",
        "cta": "cta-gradient-animated-01",
        "contact": "contact-modern-form-01",
        "footer": "footer-gradient-01",
    },
    "event-minimal": {
        "nav": "nav-centered-01",
        "hero": "hero-centered-02",
        "about": "about-timeline-01",
        "services": "services-process-steps-01",
        "team": "team-grid-01",
        "schedule": "schedule-tabbed-multi-01",
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
        "nav": ["nav-classic-01", "nav-centered-01", "nav-topbar-01", "nav-transparent-01"],
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-typewriter-01", "hero-parallax-01", "hero-video-bg-01", "hero-zen-01", "hero-counter-01", "hero-avatar-stack-01"],
        "about": ["about-magazine-01", "about-image-showcase-01", "about-split-scroll-01", "about-alternating-01", "about-timeline-01", "about-progress-bars-01"],
        "services": ["services-alternating-rows-01", "services-minimal-list-01", "services-icon-list-01", "services-cards-grid-01", "services-process-steps-01", "services-timeline-01", "services-numbered-zigzag-01"],
        "gallery": ["gallery-spotlight-01", "gallery-lightbox-01", "gallery-masonry-01", "gallery-filmstrip-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-minimal-01", "testimonials-video-01"],
        "contact": ["contact-minimal-01", "contact-form-01", "contact-minimal-02", "contact-card-01", "contact-split-map-01", "contact-two-col-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-newsletter-01", "cta-bold-text-01"],
        "footer": ["footer-centered-01", "footer-minimal-02", "footer-stacked-01", "footer-sitemap-01", "footer-multi-col-01"],
        "booking": ["booking-form-01"],
        "social-proof": ["social-bar-01"],
    },
    "restaurant-cozy": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-split-cta-01", "nav-topbar-01"],
        "hero": ["hero-organic-01", "hero-typewriter-01", "hero-classic-01", "hero-parallax-01", "hero-split-01", "hero-centered-02", "hero-avatar-stack-01"],
        "about": ["about-split-scroll-01", "about-image-showcase-01", "about-magazine-01", "about-alternating-01", "about-timeline-01", "about-progress-bars-01"],
        "services": ["services-icon-list-01", "services-minimal-list-01", "services-alternating-rows-01", "services-cards-grid-01", "services-process-steps-01", "services-timeline-01", "services-numbered-zigzag-01"],
        "gallery": ["gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01", "gallery-filmstrip-01"],
        "testimonials": ["testimonials-card-stack-01", "testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-masonry-01", "testimonials-minimal-01", "testimonials-video-01"],
        "contact": ["contact-card-01", "contact-minimal-01", "contact-form-01", "contact-split-map-01", "contact-modern-form-01", "contact-two-col-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-02", "cta-newsletter-01"],
        "footer": ["footer-multi-col-01", "footer-centered-01", "footer-stacked-01", "footer-sitemap-01", "footer-minimal-02"],
        "booking": ["booking-form-01"],
        "social-proof": ["social-bar-01"],
    },
    "restaurant-modern": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-transparent-01", "nav-pill-01"],
        "hero": ["hero-zen-01", "hero-parallax-01", "hero-glassmorphism-01", "hero-split-01", "hero-linear-01", "hero-video-bg-01", "hero-marquee-01"],
        "about": ["about-bento-01", "about-timeline-02", "about-split-cards-01", "about-image-showcase-01", "about-magazine-01", "about-split-scroll-01"],
        "services": ["services-tabs-01", "services-hover-reveal-01", "services-bento-02", "services-hover-expand-01", "services-minimal-list-01", "services-pricing-cards-01", "services-image-reveal-01"],
        "gallery": ["gallery-filmstrip-01", "gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01"],
        "testimonials": ["testimonials-marquee-01", "testimonials-masonry-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-spotlight-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "contact": ["contact-modern-form-01", "contact-split-map-01", "contact-card-01", "contact-minimal-02", "contact-form-01", "contact-cards-grid-01"],
        "cta": ["cta-gradient-banner-01", "cta-floating-card-01", "cta-split-image-01", "cta-countdown-01", "cta-bold-text-01"],
        "footer": ["footer-minimal-02", "footer-gradient-01", "footer-cta-band-01", "footer-asymmetric-01", "footer-social-01"],
        "booking": ["booking-form-01"],
        "social-proof": ["social-bar-01"],
    },
    # --- SaaS / Landing Page ---
    "saas-gradient": {
        "nav": ["nav-minimal-01", "nav-classic-01", "nav-pill-01", "nav-split-cta-01", "nav-transparent-01"],
        "hero": ["hero-linear-01", "hero-gradient-03", "hero-animated-shapes-01", "hero-parallax-01", "hero-rotating-01", "hero-glassmorphism-01", "hero-floating-cards-01", "hero-aurora-01", "hero-calculator-01"],
        "about": ["about-timeline-02", "about-bento-01", "about-split-cards-01", "about-image-showcase-01", "about-alternating-01", "about-progress-bars-01"],
        "services": ["services-hover-reveal-01", "services-bento-02", "services-hover-expand-01", "services-tabs-01", "services-cards-grid-01", "services-pricing-cards-01", "services-interactive-tabs-01", "services-numbered-zigzag-01"],
        "features": ["features-bento-01", "features-bento-grid-01", "features-hover-cards-01", "features-tabs-01", "features-icon-showcase-01", "features-showcase-01", "features-elevated-01"],
        "testimonials": ["testimonials-marquee-01", "testimonials-masonry-01", "testimonials-carousel-01", "testimonials-card-stack-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "cta": ["cta-gradient-animated-01", "cta-gradient-banner-01", "cta-floating-card-01", "cta-floating-card-02", "cta-split-image-01", "cta-countdown-01", "cta-bold-text-01"],
        "contact": ["contact-modern-form-01", "contact-split-map-01", "contact-card-01", "contact-form-01", "contact-minimal-02", "contact-cards-grid-01"],
        "footer": ["footer-gradient-01", "footer-mega-01", "footer-cta-band-01", "footer-multi-col-01", "footer-sitemap-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "app-download": ["app-download-01"],
    },
    "saas-clean": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-split-cta-01", "nav-pill-01", "nav-topbar-01"],
        "hero": ["hero-centered-02", "hero-split-01", "hero-linear-01", "hero-classic-01", "hero-gradient-03", "hero-counter-01", "hero-aurora-01", "hero-calculator-01", "hero-avatar-stack-01"],
        "about": ["about-alternating-01", "about-image-showcase-01", "about-timeline-02", "about-split-cards-01", "about-bento-01", "about-progress-bars-01"],
        "services": ["services-cards-grid-01", "services-process-steps-01", "services-tabs-01", "services-icon-list-01", "services-alternating-rows-01", "services-pricing-cards-01", "services-interactive-tabs-01", "services-numbered-zigzag-01"],
        "features": ["features-icons-grid-01", "features-bento-01", "features-alternating-01", "features-icon-showcase-01", "features-comparison-01", "features-showcase-01", "features-elevated-01"],
        "testimonials": ["testimonials-grid-01", "testimonials-carousel-01", "testimonials-spotlight-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-rating-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-floating-card-02", "cta-gradient-banner-01", "cta-newsletter-01"],
        "contact": ["contact-form-01", "contact-modern-form-01", "contact-minimal-01", "contact-split-map-01", "contact-card-01", "contact-two-col-01"],
        "footer": ["footer-sitemap-01", "footer-multi-col-01", "footer-cta-band-01", "footer-centered-01", "footer-mega-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
    },
    "saas-dark": {
        "nav": ["nav-minimal-01", "nav-classic-01", "nav-pill-01", "nav-transparent-01", "nav-split-cta-01"],
        "hero": ["hero-linear-01", "hero-dark-bold-01", "hero-neon-01", "hero-animated-shapes-01", "hero-rotating-01", "hero-gradient-03", "hero-floating-cards-01", "hero-spotlight-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-01", "about-timeline-02", "about-magazine-01"],
        "services": ["services-bento-02", "services-hover-expand-01", "services-hover-reveal-01", "services-tabs-01", "services-minimal-list-01", "services-pricing-cards-01", "services-hover-cards-01", "services-image-reveal-01"],
        "features": ["features-bento-01", "features-hover-cards-01", "features-bento-grid-01", "features-tabs-01", "features-comparison-01", "features-elevated-01"],
        "testimonials": ["testimonials-masonry-01", "testimonials-marquee-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "cta": ["cta-gradient-animated-01", "cta-gradient-banner-01", "cta-floating-card-01", "cta-countdown-01", "cta-bold-text-01"],
        "contact": ["contact-minimal-02", "contact-modern-form-01", "contact-card-01", "contact-form-01", "contact-split-map-01", "contact-cards-grid-01"],
        "footer": ["footer-mega-01", "footer-gradient-01", "footer-cta-band-01", "footer-asymmetric-01", "footer-social-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "app-download": ["app-download-01"],
    },
    # --- Portfolio ---
    "portfolio-gallery": {
        "nav": ["nav-centered-01", "nav-minimal-01", "nav-sidebar-01", "nav-transparent-01"],
        "hero": ["hero-editorial-01", "hero-zen-01", "hero-typewriter-01", "hero-parallax-01", "hero-video-bg-01", "hero-marquee-01"],
        "about": ["about-image-showcase-01", "about-magazine-01", "about-split-scroll-01", "about-alternating-01", "about-timeline-02"],
        "gallery": ["gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01", "gallery-filmstrip-01"],
        "services": ["services-minimal-list-01", "services-alternating-rows-01", "services-icon-list-01", "services-cards-grid-01", "services-hover-reveal-01"],
        "testimonials": ["testimonials-grid-01", "testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-masonry-01", "testimonials-card-stack-01", "testimonials-minimal-01", "testimonials-video-01"],
        "contact": ["contact-minimal-01", "contact-minimal-02", "contact-form-01", "contact-card-01", "contact-modern-form-01", "contact-two-col-01"],
        "footer": ["footer-minimal-02", "footer-social-01", "footer-asymmetric-01", "footer-centered-01", "footer-stacked-01"],
        "awards": ["awards-timeline-01"],
    },
    "portfolio-minimal": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-transparent-01", "nav-sidebar-01"],
        "hero": ["hero-zen-01", "hero-typewriter-01", "hero-editorial-01", "hero-centered-02", "hero-classic-01", "hero-spotlight-01"],
        "about": ["about-alternating-01", "about-split-scroll-01", "about-image-showcase-01", "about-magazine-01", "about-timeline-01"],
        "gallery": ["gallery-lightbox-01", "gallery-spotlight-01", "gallery-masonry-01", "gallery-filmstrip-01"],
        "services": ["services-minimal-list-01", "services-icon-list-01", "services-alternating-rows-01", "services-timeline-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-grid-01", "testimonials-carousel-01", "testimonials-minimal-01", "testimonials-video-01"],
        "contact": ["contact-minimal-02", "contact-minimal-01", "contact-form-01", "contact-card-01", "contact-modern-form-01"],
        "footer": ["footer-centered-01", "footer-social-01", "footer-minimal-02", "footer-stacked-01", "footer-asymmetric-01"],
        "awards": ["awards-timeline-01"],
    },
    "portfolio-creative": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-sidebar-01", "nav-transparent-01", "nav-pill-01"],
        "hero": ["hero-linear-01", "hero-brutalist-01", "hero-animated-shapes-01", "hero-neon-01", "hero-physics-01", "hero-rotating-01", "hero-marquee-01", "hero-aurora-01"],
        "about": ["about-bento-01", "about-split-cards-01", "about-timeline-02", "about-image-showcase-01", "about-magazine-01"],
        "gallery": ["gallery-spotlight-01", "gallery-filmstrip-01", "gallery-masonry-01", "gallery-lightbox-01"],
        "services": ["services-hover-expand-01", "services-hover-reveal-01", "services-bento-02", "services-tabs-01", "services-cards-grid-01", "services-hover-cards-01", "services-image-reveal-01"],
        "features": ["features-showcase-01", "features-bento-01", "features-hover-cards-01", "features-bento-grid-01", "features-elevated-01"],
        "testimonials": ["testimonials-masonry-01", "testimonials-marquee-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "contact": ["contact-card-01", "contact-modern-form-01", "contact-split-map-01", "contact-minimal-02", "contact-form-01"],
        "cta": ["cta-gradient-animated-01", "cta-floating-card-01", "cta-split-image-01", "cta-countdown-01", "cta-bold-text-01"],
        "footer": ["footer-gradient-01", "footer-asymmetric-01", "footer-social-01", "footer-cta-band-01", "footer-mega-01"],
        "awards": ["awards-timeline-01"],
    },
    # --- E-commerce / Shop ---
    "ecommerce-modern": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-split-cta-01", "nav-topbar-01", "nav-pill-01"],
        "hero": ["hero-split-01", "hero-parallax-01", "hero-glassmorphism-01", "hero-classic-01", "hero-gradient-03", "hero-centered-02", "hero-counter-01", "hero-search-01"],
        "about": ["about-image-showcase-01", "about-bento-01", "about-alternating-01", "about-split-cards-01", "about-magazine-01"],
        "services": ["services-cards-grid-01", "services-hover-reveal-01", "services-tabs-01", "services-hover-expand-01", "services-icon-list-01", "services-pricing-cards-01", "services-interactive-tabs-01"],
        "features": ["features-icons-grid-01", "features-bento-01", "features-comparison-01", "features-hover-cards-01", "features-alternating-01", "features-showcase-01", "features-elevated-01"],
        "gallery": ["gallery-masonry-01", "gallery-filmstrip-01", "gallery-lightbox-01", "gallery-spotlight-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-grid-01", "testimonials-marquee-01", "testimonials-masonry-01", "testimonials-spotlight-01", "testimonials-rating-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-gradient-banner-01", "cta-countdown-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01", "contact-form-01", "contact-minimal-01", "contact-cards-grid-01"],
        "footer": ["footer-multi-col-01", "footer-mega-01", "footer-cta-band-01", "footer-sitemap-01", "footer-stacked-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "listings": ["listings-cards-01", "listings-filterable-01"],
    },
    "ecommerce-luxury": {
        "nav": ["nav-centered-01", "nav-classic-01", "nav-topbar-01", "nav-transparent-01"],
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-video-bg-01", "hero-parallax-01", "hero-zen-01", "hero-typewriter-01", "hero-counter-01", "hero-spotlight-01"],
        "about": ["about-magazine-01", "about-image-showcase-01", "about-split-scroll-01", "about-alternating-01", "about-timeline-01", "about-progress-bars-01"],
        "services": ["services-alternating-rows-01", "services-minimal-list-01", "services-icon-list-01", "services-cards-grid-01", "services-process-steps-01", "services-timeline-01", "services-numbered-zigzag-01"],
        "features": ["features-icon-showcase-01", "features-alternating-01", "features-comparison-01", "features-icons-grid-01", "features-showcase-01"],
        "gallery": ["gallery-spotlight-01", "gallery-lightbox-01", "gallery-masonry-01", "gallery-filmstrip-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-minimal-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-newsletter-01", "cta-bold-text-01"],
        "contact": ["contact-minimal-01", "contact-form-01", "contact-minimal-02", "contact-card-01", "contact-split-map-01", "contact-two-col-01"],
        "footer": ["footer-centered-01", "footer-stacked-01", "footer-sitemap-01", "footer-multi-col-01", "footer-minimal-02"],
        "awards": ["awards-timeline-01"],
        "social-proof": ["social-bar-01"],
    },
    # --- Business ---
    "business-corporate": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-topbar-01", "nav-split-cta-01"],
        "hero": ["hero-split-01", "hero-classic-01", "hero-video-bg-01", "hero-centered-02", "hero-parallax-01", "hero-counter-01", "hero-calculator-01", "hero-avatar-stack-01"],
        "about": ["about-alternating-01", "about-image-showcase-01", "about-timeline-02", "about-timeline-01", "about-magazine-01", "about-progress-bars-01"],
        "services": ["services-cards-grid-01", "services-process-steps-01", "services-tabs-01", "services-alternating-rows-01", "services-icon-list-01", "services-timeline-01", "services-hover-cards-01", "services-numbered-zigzag-01"],
        "features": ["features-comparison-01", "features-icons-grid-01", "features-alternating-01", "features-icon-showcase-01", "features-bento-01", "features-showcase-01", "features-elevated-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-grid-01", "testimonials-spotlight-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-rating-01", "testimonials-video-01"],
        "team": ["team-grid-01", "team-carousel-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-gradient-banner-01", "cta-newsletter-01"],
        "contact": ["contact-form-01", "contact-split-map-01", "contact-modern-form-01", "contact-card-01", "contact-minimal-01", "contact-cards-grid-01"],
        "footer": ["footer-mega-01", "footer-sitemap-01", "footer-cta-band-01", "footer-multi-col-01", "footer-stacked-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "awards": ["awards-timeline-01"],
        "booking": ["booking-form-01"],
    },
    "business-trust": {
        "nav": ["nav-classic-01", "nav-centered-01", "nav-topbar-01", "nav-split-cta-01"],
        "hero": ["hero-classic-01", "hero-editorial-01", "hero-split-01", "hero-centered-02", "hero-video-bg-01", "hero-counter-01", "hero-avatar-stack-01"],
        "about": ["about-timeline-01", "about-magazine-01", "about-image-showcase-01", "about-alternating-01", "about-split-scroll-01", "about-progress-bars-01"],
        "services": ["services-process-steps-01", "services-alternating-rows-01", "services-cards-grid-01", "services-icon-list-01", "services-tabs-01", "services-timeline-01", "services-numbered-zigzag-01"],
        "features": ["features-icons-grid-01", "features-comparison-01", "features-alternating-01", "features-icon-showcase-01", "features-showcase-01", "features-elevated-01"],
        "team": ["team-grid-01", "team-carousel-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-rating-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-02", "cta-newsletter-01"],
        "contact": ["contact-split-map-01", "contact-form-01", "contact-modern-form-01", "contact-card-01", "contact-minimal-01", "contact-two-col-01"],
        "footer": ["footer-sitemap-01", "footer-mega-01", "footer-stacked-01", "footer-multi-col-01", "footer-centered-01"],
        "social-proof": ["social-bar-01"],
        "awards": ["awards-timeline-01"],
        "booking": ["booking-form-01"],
    },
    "business-fresh": {
        "nav": ["nav-centered-01", "nav-minimal-01", "nav-pill-01", "nav-split-cta-01", "nav-transparent-01"],
        "hero": ["hero-linear-01", "hero-gradient-03", "hero-animated-shapes-01", "hero-rotating-01", "hero-glassmorphism-01", "hero-floating-cards-01", "hero-calculator-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-02", "about-image-showcase-01", "about-alternating-01", "about-progress-bars-01"],
        "services": ["services-hover-expand-01", "services-hover-reveal-01", "services-bento-02", "services-tabs-01", "services-cards-grid-01", "services-pricing-cards-01", "services-interactive-tabs-01", "services-image-reveal-01"],
        "features": ["features-bento-01", "features-alternating-01", "features-bento-grid-01", "features-hover-cards-01", "features-icon-showcase-01", "features-elevated-01"],
        "testimonials": ["testimonials-carousel-01", "testimonials-marquee-01", "testimonials-masonry-01", "testimonials-card-stack-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "cta": ["cta-split-image-01", "cta-gradient-animated-01", "cta-floating-card-01", "cta-gradient-banner-01", "cta-floating-card-02", "cta-countdown-01", "cta-bold-text-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01", "contact-form-01", "contact-minimal-02", "contact-cards-grid-01"],
        "footer": ["footer-multi-col-01", "footer-gradient-01", "footer-cta-band-01", "footer-social-01", "footer-mega-01"],
        "comparison": ["comparison-table-01"],
        "social-proof": ["social-bar-01"],
        "app-download": ["app-download-01"],
    },
    # --- Blog / Magazine ---
    "blog-editorial": {
        "nav": ["nav-centered-01", "nav-classic-01", "nav-transparent-01", "nav-topbar-01"],
        "hero": ["hero-editorial-01", "hero-typewriter-01", "hero-zen-01", "hero-classic-01", "hero-split-01", "hero-marquee-01"],
        "about": ["about-alternating-01", "about-magazine-01", "about-split-scroll-01", "about-image-showcase-01", "about-timeline-01"],
        "services": ["services-minimal-list-01", "services-icon-list-01", "services-alternating-rows-01", "services-cards-grid-01", "services-process-steps-01", "services-timeline-01"],
        "features": ["features-showcase-01", "features-alternating-01", "features-icon-showcase-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-grid-01", "testimonials-carousel-01", "testimonials-card-stack-01", "testimonials-masonry-01", "testimonials-minimal-01", "testimonials-video-01"],
        "gallery": ["gallery-lightbox-01", "gallery-spotlight-01", "gallery-masonry-01", "gallery-filmstrip-01"],
        "cta": ["cta-newsletter-01", "cta-banner-01", "cta-split-image-01"],
        "contact": ["contact-card-01", "contact-minimal-01", "contact-form-01", "contact-minimal-02", "contact-modern-form-01", "contact-two-col-01"],
        "footer": ["footer-sitemap-01", "footer-centered-01", "footer-asymmetric-01", "footer-stacked-01", "footer-multi-col-01", "footer-content-grid-01"],
        "blog": ["blog-editorial-grid-01", "blog-minimal-01"],
    },
    "blog-dark": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-pill-01", "nav-transparent-01"],
        "hero": ["hero-neon-01", "hero-dark-bold-01", "hero-brutalist-01", "hero-linear-01", "hero-animated-shapes-01", "hero-floating-cards-01", "hero-spotlight-01"],
        "about": ["about-split-cards-01", "about-bento-01", "about-timeline-01", "about-timeline-02", "about-magazine-01"],
        "services": ["services-hover-reveal-01", "services-bento-02", "services-hover-expand-01", "services-tabs-01", "services-minimal-list-01", "services-image-reveal-01"],
        "testimonials": ["testimonials-masonry-01", "testimonials-marquee-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "gallery": ["gallery-filmstrip-01", "gallery-masonry-01", "gallery-spotlight-01", "gallery-lightbox-01"],
        "contact": ["contact-minimal-02", "contact-card-01", "contact-modern-form-01", "contact-form-01", "contact-split-map-01", "contact-cards-grid-01"],
        "cta": ["cta-gradient-animated-01", "cta-floating-card-01", "cta-gradient-banner-01", "cta-countdown-01", "cta-bold-text-01"],
        "footer": ["footer-gradient-01", "footer-mega-01", "footer-social-01", "footer-asymmetric-01", "footer-cta-band-01", "footer-content-grid-01"],
        "blog": ["blog-cards-grid-01", "blog-editorial-grid-01", "blog-minimal-01"],
    },
    # --- Evento / Community ---
    "event-vibrant": {
        "nav": ["nav-minimal-01", "nav-centered-01", "nav-pill-01", "nav-transparent-01", "nav-split-cta-01"],
        "hero": ["hero-animated-shapes-01", "hero-gradient-03", "hero-parallax-01", "hero-physics-01", "hero-rotating-01", "hero-neon-01", "hero-marquee-01", "hero-aurora-01", "hero-countdown-01"],
        "about": ["about-bento-01", "about-timeline-02", "about-split-cards-01", "about-image-showcase-01", "about-alternating-01"],
        "services": ["services-tabs-01", "services-hover-expand-01", "services-bento-02", "services-hover-reveal-01", "services-cards-grid-01", "services-hover-cards-01"],
        "features": ["features-bento-grid-01", "features-hover-cards-01", "features-tabs-01", "features-bento-01", "features-elevated-01"],
        "team": ["team-carousel-01", "team-grid-01"],
        "testimonials": ["testimonials-marquee-01", "testimonials-masonry-01", "testimonials-card-stack-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-quote-wall-01", "testimonials-video-01"],
        "cta": ["cta-gradient-animated-01", "cta-gradient-banner-01", "cta-floating-card-01", "cta-floating-card-02", "cta-split-image-01", "cta-countdown-01", "cta-bold-text-01"],
        "contact": ["contact-modern-form-01", "contact-card-01", "contact-split-map-01", "contact-form-01", "contact-minimal-02", "contact-cards-grid-01"],
        "footer": ["footer-gradient-01", "footer-cta-band-01", "footer-social-01", "footer-mega-01", "footer-asymmetric-01"],
        "schedule": ["schedule-tabbed-multi-01"],
        "social-proof": ["social-bar-01"],
        "booking": ["booking-form-01"],
    },
    "event-minimal": {
        "nav": ["nav-centered-01", "nav-classic-01", "nav-transparent-01", "nav-minimal-01"],
        "hero": ["hero-centered-02", "hero-typewriter-01", "hero-zen-01", "hero-editorial-01", "hero-classic-01", "hero-counter-01", "hero-aurora-01", "hero-countdown-01"],
        "about": ["about-timeline-01", "about-alternating-01", "about-split-scroll-01", "about-image-showcase-01", "about-magazine-01"],
        "services": ["services-process-steps-01", "services-cards-grid-01", "services-icon-list-01", "services-minimal-list-01", "services-alternating-rows-01", "services-timeline-01"],
        "team": ["team-grid-01", "team-carousel-01"],
        "testimonials": ["testimonials-spotlight-01", "testimonials-carousel-01", "testimonials-grid-01", "testimonials-card-stack-01", "testimonials-minimal-01", "testimonials-video-01"],
        "cta": ["cta-banner-01", "cta-split-image-01", "cta-floating-card-01", "cta-newsletter-01"],
        "contact": ["contact-form-01", "contact-minimal-01", "contact-minimal-02", "contact-card-01", "contact-split-map-01", "contact-two-col-01"],
        "footer": ["footer-minimal-02", "footer-stacked-01", "footer-centered-01", "footer-sitemap-01", "footer-social-01"],
        "schedule": ["schedule-tabbed-multi-01"],
        "booking": ["booking-form-01"],
    },
}

# Randomized pools for default section types (faq, pricing, stats, etc.)
_DEFAULT_SECTION_VARIANT_POOLS: Dict[str, List[str]] = {
    "faq": ["faq-accordion-01", "faq-accordion-02", "faq-two-column-01", "faq-search-01"],
    "pricing": ["pricing-cards-01", "pricing-toggle-01", "pricing-toggle-02", "pricing-comparison-01", "pricing-minimal-01", "pricing-dark-parallax-01"],
    "stats": ["stats-counters-01", "stats-wave-01"],
    "logos": ["logos-marquee-01"],
    "process": ["process-steps-01", "process-horizontal-01", "process-cards-01"],
    "timeline": ["timeline-vertical-01"],
    "blog": ["blog-editorial-grid-01", "blog-cards-grid-01", "blog-minimal-01"],
    "awards": ["awards-timeline-01"],
    "listings": ["listings-cards-01", "listings-filterable-01"],
    "donations": ["donations-progress-01", "donations-form-01"],
    "comparison": ["comparison-table-01"],
    "booking": ["booking-form-01"],
    "app-download": ["app-download-01"],
    "social-proof": ["social-bar-01"],
    "schedule": ["schedule-tabbed-multi-01"],
}

# =========================================================
# STYLE CSS PROFILES: Per-style visual overrides
# Each profile creates a distinct spatial/visual rhythm so
# sites don't all share the same Tailwind defaults.
# =========================================================
STYLE_CSS_PROFILES: Dict[str, Dict[str, str]] = {
    "restaurant-elegant": {
        "space_section": "7rem",
        "max_width": "75rem",
        "radius": "1rem",
        "shadow": "0 25px 60px -12px rgba(0,0,0,0.12)",
        "h1_scale": "clamp(3rem, 6vw + 1rem, 6rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 0.5rem, 4rem)",
        "animation_speed": "1.2",
        "letter_spacing": "-0.03em",
    },
    "restaurant-cozy": {
        "space_section": "6rem",
        "max_width": "72rem",
        "radius": "1.25rem",
        "shadow": "0 10px 30px -5px rgba(0,0,0,0.1)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 4.5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.2rem)",
        "animation_speed": "1.0",
        "letter_spacing": "-0.02em",
    },
    "restaurant-modern": {
        "space_section": "5rem",
        "max_width": "76rem",
        "radius": "0.5rem",
        "shadow": "0 4px 20px rgba(0,0,0,0.08)",
        "h1_scale": "clamp(2.8rem, 6vw + 0.5rem, 5.5rem)",
        "h2_scale": "clamp(1.8rem, 3vw + 0.5rem, 3rem)",
        "animation_speed": "0.8",
        "letter_spacing": "-0.04em",
    },
    "saas-gradient": {
        "space_section": "5.5rem",
        "max_width": "76rem",
        "radius": "0.75rem",
        "shadow": "0 8px 32px rgba(0,0,0,0.12)",
        "h1_scale": "clamp(2.8rem, 5.5vw + 1rem, 5.5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.5rem)",
        "animation_speed": "0.7",
        "letter_spacing": "-0.03em",
    },
    "saas-clean": {
        "space_section": "5rem",
        "max_width": "72rem",
        "radius": "0.5rem",
        "shadow": "0 2px 12px rgba(0,0,0,0.06)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 4.5rem)",
        "h2_scale": "clamp(1.8rem, 2.5vw + 0.5rem, 3rem)",
        "animation_speed": "0.6",
        "letter_spacing": "-0.02em",
    },
    "saas-dark": {
        "space_section": "5rem",
        "max_width": "74rem",
        "radius": "0.75rem",
        "shadow": "0 4px 24px rgba(0,0,0,0.3)",
        "h1_scale": "clamp(2.5rem, 5vw + 1rem, 5.5rem)",
        "h2_scale": "clamp(1.8rem, 3vw + 0.5rem, 3rem)",
        "animation_speed": "0.7",
        "letter_spacing": "0em",
    },
    "portfolio-gallery": {
        "space_section": "7rem",
        "max_width": "80rem",
        "radius": "0.25rem",
        "shadow": "none",
        "h1_scale": "clamp(3.5rem, 7vw + 1rem, 7rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 0.5rem, 4rem)",
        "animation_speed": "1.3",
        "letter_spacing": "-0.04em",
    },
    "portfolio-minimal": {
        "space_section": "8rem",
        "max_width": "68rem",
        "radius": "0",
        "shadow": "none",
        "h1_scale": "clamp(2.5rem, 4vw + 1rem, 4.5rem)",
        "h2_scale": "clamp(1.8rem, 3vw + 0.5rem, 3rem)",
        "animation_speed": "1.5",
        "letter_spacing": "-0.02em",
    },
    "portfolio-creative": {
        "space_section": "6rem",
        "max_width": "80rem",
        "radius": "1.5rem",
        "shadow": "0 12px 40px rgba(0,0,0,0.15)",
        "h1_scale": "clamp(3.5rem, 8vw + 1rem, 8rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 1rem, 4.5rem)",
        "animation_speed": "0.9",
        "letter_spacing": "-0.05em",
    },
    "ecommerce-modern": {
        "space_section": "5.5rem",
        "max_width": "76rem",
        "radius": "0.75rem",
        "shadow": "0 8px 24px rgba(0,0,0,0.08)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 5rem)",
        "h2_scale": "clamp(1.8rem, 3vw + 0.5rem, 3rem)",
        "animation_speed": "0.8",
        "letter_spacing": "-0.02em",
    },
    "ecommerce-luxury": {
        "space_section": "7rem",
        "max_width": "74rem",
        "radius": "1rem",
        "shadow": "0 20px 50px -10px rgba(0,0,0,0.15)",
        "h1_scale": "clamp(3rem, 6vw + 1rem, 6rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 0.5rem, 4rem)",
        "animation_speed": "1.2",
        "letter_spacing": "-0.03em",
    },
    "business-corporate": {
        "space_section": "6rem",
        "max_width": "76rem",
        "radius": "0.5rem",
        "shadow": "0 4px 16px rgba(0,0,0,0.08)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.2rem)",
        "animation_speed": "1.0",
        "letter_spacing": "-0.02em",
    },
    "business-trust": {
        "space_section": "6rem",
        "max_width": "74rem",
        "radius": "0.75rem",
        "shadow": "0 6px 20px rgba(0,0,0,0.08)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 4.5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.2rem)",
        "animation_speed": "1.0",
        "letter_spacing": "-0.02em",
    },
    "business-fresh": {
        "space_section": "5.5rem",
        "max_width": "76rem",
        "radius": "1rem",
        "shadow": "0 8px 28px rgba(0,0,0,0.1)",
        "h1_scale": "clamp(2.8rem, 5.5vw + 1rem, 5.5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.5rem)",
        "animation_speed": "0.8",
        "letter_spacing": "-0.03em",
    },
    "blog-editorial": {
        "space_section": "7.5rem",
        "max_width": "70rem",
        "radius": "0",
        "shadow": "none",
        "h1_scale": "clamp(3rem, 6vw + 1rem, 6.5rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 0.5rem, 4rem)",
        "animation_speed": "1.3",
        "letter_spacing": "-0.04em",
    },
    "blog-dark": {
        "space_section": "6rem",
        "max_width": "72rem",
        "radius": "0.5rem",
        "shadow": "0 4px 20px rgba(0,0,0,0.25)",
        "h1_scale": "clamp(2.5rem, 5vw + 0.5rem, 5rem)",
        "h2_scale": "clamp(2rem, 3vw + 0.5rem, 3.2rem)",
        "animation_speed": "1.0",
        "letter_spacing": "-0.02em",
    },
    "event-vibrant": {
        "space_section": "4.5rem",
        "max_width": "80rem",
        "radius": "1.5rem",
        "shadow": "0 12px 36px rgba(0,0,0,0.15)",
        "h1_scale": "clamp(3.5rem, 8vw + 1rem, 9rem)",
        "h2_scale": "clamp(2.2rem, 4vw + 1rem, 4.5rem)",
        "animation_speed": "0.5",
        "letter_spacing": "-0.05em",
    },
    "event-minimal": {
        "space_section": "7rem",
        "max_width": "72rem",
        "radius": "0.25rem",
        "shadow": "none",
        "h1_scale": "clamp(3rem, 6vw + 1rem, 6rem)",
        "h2_scale": "clamp(2rem, 3.5vw + 0.5rem, 3.5rem)",
        "animation_speed": "1.2",
        "letter_spacing": "-0.03em",
    },
}



# =========================================================
# SECTION BACKGROUND ACCENTS: Break the monotonous bg/bg-alt alternation
# by injecting special backgrounds on specific sections per style.
# Uses CSS targeting section IDs (#testimonials, #cta, etc.) to add
# gradients, patterns, or inverted color schemes.
# =========================================================
SECTION_BG_ACCENTS: Dict[str, str] = {
    "restaurant-elegant": """
    /* Testimonials: warm gradient overlay */
    #testimonials { background: linear-gradient(135deg, var(--color-bg-alt), rgba(var(--color-primary-rgb), 0.06)) !important; }
    /* CTA: inverted dark section */
    #cta { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #cta h2, #cta p, #cta span { color: var(--color-bg) !important; }
    #cta [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    """,
    "restaurant-cozy": """
    /* About: subtle warm pattern */
    #about { background: radial-gradient(circle at 20% 80%, rgba(var(--color-primary-rgb), 0.04), transparent 50%), var(--color-bg-alt) !important; }
    /* Testimonials: warm tint */
    #testimonials { background: linear-gradient(180deg, var(--color-bg), rgba(var(--color-secondary-rgb), 0.05)) !important; }
    """,
    "restaurant-modern": """
    /* Testimonials: full dark inversion */
    #testimonials { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #testimonials h2, #testimonials p, #testimonials span, #testimonials blockquote { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text-muted)"] { color: rgba(var(--color-bg-rgb), 0.6) !important; }
    """,
    "saas-gradient": """
    /* Features: gradient mesh */
    #features { background: linear-gradient(135deg, var(--color-bg), rgba(var(--color-primary-rgb), 0.08) 40%, rgba(var(--color-secondary-rgb), 0.06)) !important; }
    /* CTA: vibrant gradient */
    #cta { background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)) !important; color: #fff !important; }
    #cta h2, #cta p, #cta span { color: #fff !important; }
    """,
    "saas-clean": """
    /* Testimonials: subtle dot pattern */
    #testimonials { background: radial-gradient(circle, rgba(var(--color-primary-rgb), 0.08) 1px, transparent 1px), var(--color-bg-alt) !important; background-size: 24px 24px !important; }
    """,
    "saas-dark": """
    /* Features: glow gradient */
    #features { background: radial-gradient(ellipse at 50% 0%, rgba(var(--color-primary-rgb), 0.12), transparent 70%), var(--color-bg) !important; }
    /* CTA: accent glow */
    #cta { background: radial-gradient(ellipse at 50% 100%, rgba(var(--color-accent-rgb), 0.15), transparent 60%), var(--color-bg-alt) !important; }
    """,
    "portfolio-gallery": """
    /* About: clean white break */
    #about { background: #fff !important; }
    """,
    "portfolio-minimal": """
    /* Testimonials: single thin top border as accent */
    #testimonials { border-top: 1px solid rgba(var(--color-primary-rgb), 0.15); }
    """,
    "portfolio-creative": """
    /* Services: diagonal gradient */
    #services { background: linear-gradient(160deg, var(--color-bg), rgba(var(--color-primary-rgb), 0.1) 30%, rgba(var(--color-accent-rgb), 0.08) 70%, var(--color-bg-alt)) !important; }
    /* Testimonials: inverted */
    #testimonials { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #testimonials h2, #testimonials p, #testimonials span, #testimonials blockquote { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    """,
    "ecommerce-modern": """
    /* Testimonials: soft radial spotlight */
    #testimonials { background: radial-gradient(ellipse at 50% 50%, rgba(var(--color-primary-rgb), 0.06), transparent 70%), var(--color-bg) !important; }
    /* CTA: accent band */
    #cta { background: linear-gradient(90deg, var(--color-primary), var(--color-secondary)) !important; color: #fff !important; }
    #cta h2, #cta p, #cta span { color: #fff !important; }
    """,
    "ecommerce-luxury": """
    /* Testimonials: dark luxurious section */
    #testimonials { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #testimonials h2, #testimonials p, #testimonials span, #testimonials blockquote { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    #testimonials [style*="color: var(--color-text-muted)"] { color: rgba(var(--color-bg-rgb), 0.5) !important; }
    /* CTA: gold-tinted */
    #cta { background: linear-gradient(135deg, var(--color-bg-alt), rgba(var(--color-primary-rgb), 0.08)) !important; }
    """,
    "business-corporate": """
    /* Stats/features: corporate dark band */
    #stats, #features { background: var(--color-text) !important; color: var(--color-bg) !important; }
    #stats h2, #stats p, #stats span, #features h2, #features p, #features span { color: var(--color-bg) !important; }
    #stats [style*="color: var(--color-text)"], #features [style*="color: var(--color-text)"] { color: var(--color-bg) !important; }
    """,
    "business-trust": """
    /* Testimonials: warm trust gradient */
    #testimonials { background: linear-gradient(180deg, rgba(var(--color-primary-rgb), 0.04), var(--color-bg-alt)) !important; }
    """,
    "business-fresh": """
    /* Features: playful gradient mesh */
    #features { background: linear-gradient(135deg, rgba(var(--color-primary-rgb), 0.06), transparent 40%, rgba(var(--color-secondary-rgb), 0.06)) !important; }
    /* CTA: vibrant gradient */
    #cta { background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important; color: #fff !important; }
    #cta h2, #cta p, #cta span { color: #fff !important; }
    """,
    "blog-editorial": """
    /* Pull-quote accent on testimonials */
    #testimonials { border-top: 3px solid var(--color-primary); border-bottom: 3px solid var(--color-primary); }
    """,
    "blog-dark": """
    /* About: glow from below */
    #about { background: radial-gradient(ellipse at 50% 100%, rgba(var(--color-primary-rgb), 0.1), transparent 60%), var(--color-bg) !important; }
    """,
    "event-vibrant": """
    /* CTA: explosive gradient */
    #cta { background: linear-gradient(135deg, var(--color-primary), var(--color-secondary), var(--color-accent)) !important; color: #fff !important; }
    #cta h2, #cta p, #cta span { color: #fff !important; }
    /* Testimonials: dark with glow */
    #testimonials { background: radial-gradient(ellipse at 30% 50%, rgba(var(--color-primary-rgb), 0.15), transparent 50%), var(--color-text) !important; color: var(--color-bg) !important; }
    #testimonials h2, #testimonials p, #testimonials span, #testimonials blockquote { color: var(--color-bg) !important; }
    """,
    "event-minimal": """
    /* Subtle section dividers */
    #about, #services, #contact { border-top: 1px solid rgba(var(--color-text-rgb), 0.08); }
    """,
}


# =========================================================
# ANIMATION RANDOMIZER: Replace hardcoded data-animate values
# with randomly-chosen alternatives from equivalent pools.
# This ensures each generation gets a unique animation fingerprint.
# =========================================================
_ANIMATION_POOLS = {
    # Heading animations (replacements for text-split)
    "heading": ["text-split", "text-reveal", "typewriter", "blur-in", "clip-reveal"],
    # Subtitle/paragraph entrance
    "subtitle": ["blur-slide", "fade-up", "fade-left", "slide-up", "fade-right", "reveal-up"],
    # CTA button entrance
    "cta": ["bounce-in", "scale-in", "magnetic", "blur-in", "fade-up"],
    # Card/item entrance
    "card": ["fade-up", "scale-in", "blur-in", "fade-left", "fade-right", "zoom-out"],
    # Section entrance (generic)
    "section": ["fade-up", "fade-left", "fade-right", "reveal-up", "reveal-left", "blur-in", "scale-in"],
    # Image entrance
    "image": ["scale-in", "blur-in", "fade-up", "clip-reveal", "zoom-out"],
}

# Stagger animation variants
_STAGGER_VARIANTS = ["stagger", "stagger-scale"]

# Ease function variants
_EASE_VARIANTS = [
    "power2.out", "power3.out", "power4.out",
    "back.out(1.2)", "expo.out", "circ.out",
    "elastic.out(0.5,0.3)",
]


def _randomize_animations(html: str) -> str:
    """Randomize GSAP data-animate attributes for per-site animation uniqueness.

    Replaces specific animation values with alternatives from equivalent pools.
    Also varies data-delay and data-duration slightly.
    """
    import re as _re

    # Replace heading animations (h1, h2 with text-split)
    def _vary_heading_anim(m):
        prefix = m.group(1)
        anim = random.choice(_ANIMATION_POOLS["heading"])
        # Keep data-split-type only for text-split/text-reveal
        suffix = m.group(0)[len(m.group(1)) + len('data-animate="text-split"'):]
        if anim not in ("text-split", "text-reveal") and 'data-split-type' in suffix:
            suffix = _re.sub(r'\s*data-split-type="[^"]*"', '', suffix)
        return f'{prefix}data-animate="{anim}"{suffix}'

    html = _re.sub(
        r'(<h[12][^>]*?)data-animate="text-split"([^>]*)',
        _vary_heading_anim,
        html,
    )

    # Replace subtitle animations (p, span with blur-slide)
    def _vary_subtitle(m):
        anim = random.choice(_ANIMATION_POOLS["subtitle"])
        return f'{m.group(1)}data-animate="{anim}"{m.group(2)}'

    html = _re.sub(
        r'(<(?:p|span)[^>]*?)data-animate="blur-slide"([^>]*)',
        _vary_subtitle,
        html,
    )

    # Replace CTA animations (a, button with bounce-in)
    def _vary_cta(m):
        anim = random.choice(_ANIMATION_POOLS["cta"])
        return f'{m.group(1)}data-animate="{anim}"{m.group(2)}'

    html = _re.sub(
        r'(<(?:a|button)[^>]*?)data-animate="bounce-in"([^>]*)',
        _vary_cta,
        html,
    )

    # Replace generic fade-up with varied section entrances (on divs/sections)
    def _vary_section_entrance(m):
        # Only vary ~60% of the time to keep some consistency
        if random.random() < 0.6:
            anim = random.choice(_ANIMATION_POOLS["section"])
            return f'{m.group(1)}data-animate="{anim}"{m.group(2)}'
        return m.group(0)

    html = _re.sub(
        r'(<(?:div|section|article)[^>]*?)data-animate="fade-up"([^>]*)',
        _vary_section_entrance,
        html,
    )

    # Vary image animations
    def _vary_image(m):
        anim = random.choice(_ANIMATION_POOLS["image"])
        return f'{m.group(1)}data-animate="{anim}"{m.group(2)}'

    html = _re.sub(
        r'(<img[^>]*?)data-animate="scale-in"([^>]*)',
        _vary_image,
        html,
    )

    # Vary data-delay values slightly (add +-0.1s jitter)
    def _vary_delay(m):
        try:
            val = float(m.group(1))
            jittered = max(0, val + random.uniform(-0.1, 0.15))
            return f'data-delay="{jittered:.1f}"'
        except ValueError:
            return m.group(0)

    html = _re.sub(r'data-delay="([\d.]+)"', _vary_delay, html)

    # Vary data-duration values slightly (add +-0.2s jitter)
    def _vary_duration(m):
        try:
            val = float(m.group(1))
            jittered = max(0.3, val + random.uniform(-0.2, 0.3))
            return f'data-duration="{jittered:.1f}"'
        except ValueError:
            return m.group(0)

    html = _re.sub(r'data-duration="([\d.]+)"', _vary_duration, html)

    # Randomly vary ease functions (~30% of the time)
    def _vary_ease(m):
        if random.random() < 0.3:
            ease = random.choice(_EASE_VARIANTS)
            return f'data-ease="{ease}"'
        return m.group(0)

    html = _re.sub(r'data-ease="[^"]*"', _vary_ease, html)

    return html


def _jitter_rem(base_rem: str, delta_range: float = 0.8) -> str:
    """Add random jitter to a rem value string. '6rem' -> '5.4rem' to '6.8rem'."""
    try:
        val = float(base_rem.replace("rem", ""))
        jittered = val + random.uniform(-delta_range, delta_range)
        return f"{max(2.0, jittered):.1f}rem"
    except (ValueError, AttributeError):
        return base_rem


def _jitter_clamp(clamp_str: str, factor_range: tuple = (0.92, 1.12)) -> str:
    """Slightly scale a clamp() font-size by wrapping with calc()."""
    factor = random.uniform(*factor_range)
    if factor < 0.97 or factor > 1.03:
        return f"calc({clamp_str} * {factor:.2f})"
    return clamp_str


def _jitter_shadow(shadow: str, intensity: float = None) -> str:
    """Vary shadow intensity. Multiplies blur/spread values."""
    if shadow == "none":
        return shadow
    if intensity is None:
        intensity = random.uniform(0.6, 1.5)
    # Simple approach: adjust the opacity in rgba
    import re as _re
    def _scale_opacity(m):
        val = float(m.group(1))
        new_val = min(0.5, max(0.02, val * intensity))
        return f"{new_val:.2f})"
    return _re.sub(r'([\d.]+)\)', _scale_opacity, shadow)


def _build_per_style_css(style_id: str) -> str:
    """Build CSS overrides for a specific template style.

    Combines spatial overrides (from STYLE_CSS_PROFILES) with section
    background accents (from SECTION_BG_ACCENTS) plus per-generation
    random micro-variations to ensure every site looks unique.
    """
    profile = STYLE_CSS_PROFILES.get(style_id)
    if not profile:
        return ""

    s = f"body.style-{style_id}"
    # Apply micro-jitter to each CSS property for per-site uniqueness
    space = _jitter_rem(profile["space_section"], delta_range=0.8)
    mw = _jitter_rem(profile["max_width"], delta_range=2.0)
    rad = _jitter_rem(profile["radius"], delta_range=0.2) if profile["radius"] != "0" else "0"
    shd = _jitter_shadow(profile["shadow"])
    h1 = _jitter_clamp(profile["h1_scale"])
    h2 = _jitter_clamp(profile["h2_scale"])
    ls = profile["letter_spacing"]
    base_speed = float(profile["animation_speed"])
    aspeed = str(round(base_speed + random.uniform(-0.15, 0.15), 2))

    # Section background accents (gradients, patterns, inversions)
    bg_accents = SECTION_BG_ACCENTS.get(style_id, "")
    # Scope accents to the style body class
    if bg_accents:
        scoped_accents = bg_accents.replace("#testimonials", f"{s} #testimonials")
        scoped_accents = scoped_accents.replace("#cta", f"{s} #cta")
        scoped_accents = scoped_accents.replace("#features", f"{s} #features")
        scoped_accents = scoped_accents.replace("#services", f"{s} #services")
        scoped_accents = scoped_accents.replace("#about", f"{s} #about")
        scoped_accents = scoped_accents.replace("#stats", f"{s} #stats")
        scoped_accents = scoped_accents.replace("#contact", f"{s} #contact")
    else:
        scoped_accents = ""

    return f"""
    /* Style profile: {style_id} */
    {s} section {{ padding-top: {space}; padding-bottom: {space}; }}
    {s} section > div {{ max-width: {mw}; }}
    {s} h1, {s} .h1 {{ font-size: {h1}; letter-spacing: {ls}; }}
    {s} h2, {s} .h2 {{ font-size: {h2}; }}
    {s} [class*="rounded-2xl"], {s} [class*="rounded-3xl"],
    {s} [class*="rounded-xl"] {{ border-radius: {rad}; }}
    {s} [class*="shadow-xl"], {s} [class*="shadow-2xl"],
    {s} [class*="shadow-lg"] {{ box-shadow: {shd}; }}
    {s} {{ --animation-speed: {aspeed}; }}
    {scoped_accents}
    """


# =========================================================
# BLUEPRINTS: Optimal section ordering per business category.
# Each blueprint defines the narrative flow that converts best
# for that business type. Sections not in the blueprint are
# kept but placed before the footer. Hero always first, footer last.
# =========================================================
BLUEPRINTS: Dict[str, List[str]] = {
    "restaurant": [
        "hero", "about", "gallery", "services", "testimonials",
        "team", "faq", "contact",
    ],
    "saas": [
        "hero", "features", "about", "services", "testimonials",
        "pricing", "cta", "faq", "contact",
    ],
    "portfolio": [
        "hero", "gallery", "about", "services", "testimonials",
        "contact",
    ],
    "ecommerce": [
        "hero", "services", "gallery", "about", "testimonials",
        "pricing", "cta", "faq", "contact",
    ],
    "business": [
        "hero", "about", "services", "features", "team",
        "testimonials", "cta", "contact",
    ],
    "blog": [
        "hero", "about", "services", "gallery", "contact",
    ],
    "event": [
        "hero", "about", "services", "team", "gallery",
        "cta", "faq", "contact",
    ],
    "custom": [
        "hero", "about", "services", "gallery", "testimonials",
        "contact",
    ],
}

# =========================================================
# HARMONY GROUPS: Visual families for cross-section cohesion.
# When generating a site, one harmony group is selected and
# component variants are preferentially chosen from it.
# =========================================================
HARMONY_GROUPS: Dict[str, List[str]] = {
    "bento": [
        "bento", "masonry", "hover-expand", "grid", "split-cards",
    ],
    "editorial": [
        "alternating", "magazine", "spotlight", "editorial", "image-showcase",
        "split-scroll",
    ],
    "interactive": [
        "hover-expand", "hover-reveal", "tabs", "hover-cards", "card-stack",
    ],
    "classic": [
        "classic", "centered", "grid", "cards", "carousel", "form",
        "process-steps", "icon-list", "icons-grid",
    ],
    "dark-bold": [
        "dark-bold", "neon", "brutalist", "gradient", "animated-shapes",
    ],
    "organic": [
        "organic", "zen", "scroll", "minimal", "typewriter", "parallax",
    ],
}

# =========================================================
# SECTION SCHEMAS: JSON template for each section type.
# _generate_texts() assembles only the schemas for the
# sections the user actually requested, cutting prompt size
# by 40-60% and reducing noise for the LLM.
# =========================================================
_SECTION_SCHEMAS: Dict[str, str] = {
    "hero": '''"hero": {{
    "HERO_TITLE": "Headline impattante (max 8 parole, MIN 3 parole)",
    "HERO_SUBTITLE": "Sottotitolo evocativo (MIN 15 parole, 2-3 frasi che creano desiderio)",
    "HERO_CTA_TEXT": "Testo bottone CTA (3-5 parole, verbo d'azione)",
    "HERO_CTA_URL": "#contact",
    "HERO_IMAGE_URL": "",
    "HERO_IMAGE_ALT": "Descrizione immagine specifica per il business",
    "HERO_ROTATING_TEXTS": "3-4 frasi alternative per il titolo hero, separate da | (es: Frase Uno|Frase Due|Frase Tre)"
  }}''',
    "about": '''"about": {{
    "ABOUT_TITLE": "Titolo sezione (evocativo, NO 'Chi Siamo')",
    "ABOUT_SUBTITLE": "Sottotitolo (MIN 10 parole)",
    "ABOUT_TEXT": "MIN 40 parole: racconta la storia/missione con dettagli specifici, emozioni, visione futura",
    "ABOUT_HIGHLIGHT_1": "Fatto chiave 1",
    "ABOUT_HIGHLIGHT_2": "Fatto chiave 2",
    "ABOUT_HIGHLIGHT_3": "Fatto chiave 3",
    "ABOUT_HIGHLIGHT_NUM_1": "25",
    "ABOUT_HIGHLIGHT_NUM_2": "500",
    "ABOUT_HIGHLIGHT_NUM_3": "98"
  }}''',
    "services": '''"services": {{
    "SERVICES_TITLE": "Titolo sezione",
    "SERVICES_SUBTITLE": "Sottotitolo",
    "SERVICES": [
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}},
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}},
      {{"SERVICE_ICON": "emoji unico", "SERVICE_TITLE": "Nome servizio (2-4 parole)", "SERVICE_DESCRIPTION": "MIN 15 parole: beneficio concreto per il cliente"}}
    ]
  }}''',
    "features": '''"features": {{
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
  }}''',
    "testimonials": '''"testimonials": {{
    "TESTIMONIALS_TITLE": "Titolo sezione",
    "TESTIMONIALS": [
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: storia specifica con dettagli, emozioni, risultati concreti", "TESTIMONIAL_AUTHOR": "Nome e Cognome realistico italiano", "TESTIMONIAL_ROLE": "Ruolo specifico (es: CEO di NomeDitta)", "TESTIMONIAL_INITIAL": "N"}},
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: esperienza unica, diversa dalla precedente", "TESTIMONIAL_AUTHOR": "Nome e Cognome", "TESTIMONIAL_ROLE": "Ruolo specifico", "TESTIMONIAL_INITIAL": "N"}},
      {{"TESTIMONIAL_TEXT": "MIN 20 parole: racconto con before/after, numeri o dettagli specifici", "TESTIMONIAL_AUTHOR": "Nome e Cognome", "TESTIMONIAL_ROLE": "Ruolo specifico", "TESTIMONIAL_INITIAL": "N"}}
    ]
  }}''',
    "cta": '''"cta": {{
    "CTA_TITLE": "Headline CTA urgente e persuasiva (4-8 parole)",
    "CTA_SUBTITLE": "MIN 12 parole: motiva all'azione con beneficio chiaro",
    "CTA_BUTTON_TEXT": "Verbo d'azione + risultato (3-5 parole)",
    "CTA_BUTTON_URL": "#contact"
  }}''',
    "contact": '''"contact": {{
    "CONTACT_TITLE": "Titolo sezione (invitante, NO 'Contattaci')",
    "CONTACT_SUBTITLE": "MIN 10 parole: sottotitolo che invoglia a scrivere",
    "CONTACT_ADDRESS": "indirizzo o vuoto",
    "CONTACT_PHONE": "telefono o vuoto",
    "CONTACT_EMAIL": "email o vuoto"
  }}''',
    "gallery": '''"gallery": {{
    "GALLERY_TITLE": "Titolo galleria",
    "GALLERY_SUBTITLE": "Sottotitolo",
    "GALLERY_ITEMS": [
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}},
      {{"GALLERY_IMAGE_URL": "", "GALLERY_IMAGE_ALT": "descrizione specifica", "GALLERY_CAPTION": "Didascalia evocativa"}}
    ]
  }}''',
    "team": '''"team": {{
    "TEAM_TITLE": "Titolo sezione team",
    "TEAM_SUBTITLE": "Sottotitolo",
    "TEAM_MEMBERS": [
      {{"MEMBER_NAME": "Nome Cognome realistico", "MEMBER_ROLE": "Ruolo specifico (es: Direttore Creativo)", "MEMBER_IMAGE_URL": "", "MEMBER_BIO": "MIN 15 parole: personalita, passioni, competenze uniche"}},
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo specifico", "MEMBER_IMAGE_URL": "", "MEMBER_BIO": "MIN 15 parole: storia personale e approccio al lavoro"}},
      {{"MEMBER_NAME": "Nome Cognome", "MEMBER_ROLE": "Ruolo specifico", "MEMBER_IMAGE_URL": "", "MEMBER_BIO": "MIN 15 parole: background e contributo al team"}}
    ]
  }}''',
    "pricing": '''"pricing": {{
    "PRICING_TITLE": "Titolo sezione prezzi",
    "PRICING_SUBTITLE": "Sottotitolo",
    "PRICING_PLANS": [
      {{"PLAN_NAME": "Base", "PLAN_PRICE": "29", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Ideale per iniziare", "PLAN_FEATURES": "Feature 1, Feature 2, Feature 3", "PLAN_CTA_TEXT": "Inizia Ora", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "false"}},
      {{"PLAN_NAME": "Pro", "PLAN_PRICE": "59", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Il piu popolare", "PLAN_FEATURES": "Tutto Base + Feature 4, Feature 5, Feature 6", "PLAN_CTA_TEXT": "Scegli Pro", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "true"}},
      {{"PLAN_NAME": "Enterprise", "PLAN_PRICE": "99", "PLAN_PERIOD": "/mese", "PLAN_DESCRIPTION": "Per grandi aziende", "PLAN_FEATURES": "Tutto Pro + Feature 7, Feature 8, Supporto dedicato", "PLAN_CTA_TEXT": "Contattaci", "PLAN_CTA_URL": "#contact", "PLAN_FEATURED": "false"}}
    ]
  }}''',
    "faq": '''"faq": {{
    "FAQ_TITLE": "Domande Frequenti",
    "FAQ_SUBTITLE": "Sottotitolo",
    "FAQ_ITEMS": [
      {{"FAQ_QUESTION": "Domanda 1?", "FAQ_ANSWER": "Risposta dettagliata (2-3 frasi)"}},
      {{"FAQ_QUESTION": "Domanda 2?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 3?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 4?", "FAQ_ANSWER": "Risposta dettagliata"}},
      {{"FAQ_QUESTION": "Domanda 5?", "FAQ_ANSWER": "Risposta dettagliata"}}
    ]
  }}''',
    "stats": '''"stats": {{
    "STATS_TITLE": "I Nostri Numeri",
    "STATS_SUBTITLE": "Sottotitolo",
    "STATS_ITEMS": [
      {{"STAT_NUMBER": "150", "STAT_SUFFIX": "+", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "98", "STAT_SUFFIX": "%", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "10", "STAT_SUFFIX": "K", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}},
      {{"STAT_NUMBER": "24", "STAT_SUFFIX": "/7", "STAT_LABEL": "Etichetta", "STAT_ICON": "emoji"}}
    ]
  }}''',
    "logos": '''"logos": {{
    "LOGOS_TITLE": "I Nostri Partner",
    "LOGOS_ITEMS": [
      {{"LOGO_IMAGE_URL": "", "LOGO_ALT": "Partner 1", "LOGO_NAME": "Partner 1"}},
      {{"LOGO_IMAGE_URL": "", "LOGO_ALT": "Partner 2", "LOGO_NAME": "Partner 2"}},
      {{"LOGO_IMAGE_URL": "", "LOGO_ALT": "Partner 3", "LOGO_NAME": "Partner 3"}},
      {{"LOGO_IMAGE_URL": "", "LOGO_ALT": "Partner 4", "LOGO_NAME": "Partner 4"}}
    ]
  }}''',
    "process": '''"process": {{
    "PROCESS_TITLE": "Come Funziona",
    "PROCESS_SUBTITLE": "Sottotitolo",
    "PROCESS_STEPS": [
      {{"STEP_NUMBER": "1", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}},
      {{"STEP_NUMBER": "2", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}},
      {{"STEP_NUMBER": "3", "STEP_TITLE": "Titolo step", "STEP_DESCRIPTION": "Descrizione breve", "STEP_ICON": "emoji"}}
    ]
  }}''',
    "timeline": '''"timeline": {{
    "TIMELINE_TITLE": "La Nostra Storia",
    "TIMELINE_SUBTITLE": "Sottotitolo",
    "TIMELINE_ITEMS": [
      {{"TIMELINE_YEAR": "2020", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}},
      {{"TIMELINE_YEAR": "2022", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}},
      {{"TIMELINE_YEAR": "2024", "TIMELINE_HEADING": "Titolo", "TIMELINE_DESCRIPTION": "Descrizione evento", "TIMELINE_ICON": "emoji"}}
    ]
  }}''',
    "footer": '''"footer": {{
    "FOOTER_DESCRIPTION": "Breve descrizione per footer (1 frase)"
  }}''',
    "blog": '''"blog": {{
    "BLOG_TITLE": "Titolo sezione blog",
    "BLOG_SUBTITLE": "Sottotitolo",
    "BLOG_POSTS": [
      {{"POST_TITLE": "Titolo articolo (5-10 parole)", "POST_EXCERPT": "MIN 15 parole: anteprima accattivante dell'articolo", "POST_CATEGORY": "Categoria (1-2 parole)", "POST_DATE": "15 Gen 2025", "POST_AUTHOR": "Nome Cognome", "POST_IMAGE_URL": "", "POST_IMAGE_ALT": "descrizione immagine"}},
      {{"POST_TITLE": "Titolo articolo diverso", "POST_EXCERPT": "MIN 15 parole: anteprima diversa dal precedente", "POST_CATEGORY": "Categoria", "POST_DATE": "8 Gen 2025", "POST_AUTHOR": "Nome Cognome", "POST_IMAGE_URL": "", "POST_IMAGE_ALT": "descrizione immagine"}},
      {{"POST_TITLE": "Terzo titolo articolo", "POST_EXCERPT": "MIN 15 parole: anteprima unica", "POST_CATEGORY": "Categoria", "POST_DATE": "2 Gen 2025", "POST_AUTHOR": "Nome Cognome", "POST_IMAGE_URL": "", "POST_IMAGE_ALT": "descrizione immagine"}}
    ]
  }}''',
    "awards": '''"awards": {{
    "AWARDS_TITLE": "Titolo sezione premi/riconoscimenti",
    "AWARDS_SUBTITLE": "Sottotitolo",
    "AWARDS_IMAGE_1": "",
    "AWARDS_IMAGE_2": "",
    "AWARDS_IMAGE_3": "",
    "AWARDS": [
      {{"AWARD_YEAR": "2024", "AWARD_TITLE": "Nome premio", "AWARD_DESCRIPTION": "Breve descrizione del riconoscimento"}},
      {{"AWARD_YEAR": "2023", "AWARD_TITLE": "Nome premio", "AWARD_DESCRIPTION": "Breve descrizione"}},
      {{"AWARD_YEAR": "2022", "AWARD_TITLE": "Nome premio", "AWARD_DESCRIPTION": "Breve descrizione"}}
    ]
  }}''',
    "listings": '''"listings": {{
    "LISTINGS_TITLE": "Titolo sezione catalogo",
    "LISTINGS_SUBTITLE": "Sottotitolo",
    "LISTING_ITEMS": [
      {{"LISTING_TITLE": "Titolo elemento", "LISTING_DESCRIPTION": "MIN 10 parole: descrizione", "LISTING_PRICE": "€99", "LISTING_IMAGE_URL": "", "LISTING_IMAGE_ALT": "descrizione", "LISTING_SPEC_1": "Specifica 1", "LISTING_SPEC_2": "Specifica 2", "LISTING_SPEC_3": "Specifica 3"}},
      {{"LISTING_TITLE": "Titolo elemento", "LISTING_DESCRIPTION": "MIN 10 parole: descrizione", "LISTING_PRICE": "€149", "LISTING_IMAGE_URL": "", "LISTING_IMAGE_ALT": "descrizione", "LISTING_SPEC_1": "Specifica 1", "LISTING_SPEC_2": "Specifica 2", "LISTING_SPEC_3": "Specifica 3"}},
      {{"LISTING_TITLE": "Titolo elemento", "LISTING_DESCRIPTION": "MIN 10 parole: descrizione", "LISTING_PRICE": "€199", "LISTING_IMAGE_URL": "", "LISTING_IMAGE_ALT": "descrizione", "LISTING_SPEC_1": "Specifica 1", "LISTING_SPEC_2": "Specifica 2", "LISTING_SPEC_3": "Specifica 3"}}
    ]
  }}''',
    "donations": '''"donations": {{
    "DONATIONS_TITLE": "Titolo sezione donazioni",
    "DONATIONS_SUBTITLE": "Sottotitolo",
    "DONATION_ITEMS": [
      {{"DONATION_TITLE": "Nome campagna", "DONATION_DESCRIPTION": "MIN 10 parole: descrizione causa", "DONATION_RAISED": "€12.500", "DONATION_GOAL": "€25.000", "DONATION_PROGRESS": "50", "DONATION_IMAGE_URL": "", "DONATION_IMAGE_ALT": "descrizione"}},
      {{"DONATION_TITLE": "Nome campagna", "DONATION_DESCRIPTION": "MIN 10 parole: descrizione", "DONATION_RAISED": "€8.200", "DONATION_GOAL": "€15.000", "DONATION_PROGRESS": "55", "DONATION_IMAGE_URL": "", "DONATION_IMAGE_ALT": "descrizione"}}
    ]
  }}''',
    "comparison": '''"comparison": {{
    "COMPARISON_TITLE": "Perche Scegliere Noi",
    "COMPARISON_SUBTITLE": "Sottotitolo confronto",
    "COMPARISON_BRAND_NAME": "Il Nostro Brand",
    "COMPARISON_ITEMS": [
      {{"COMPARISON_FEATURE": "Feature 1", "COMPARISON_US": "true", "COMPARISON_OTHERS": "false"}},
      {{"COMPARISON_FEATURE": "Feature 2", "COMPARISON_US": "true", "COMPARISON_OTHERS": "false"}},
      {{"COMPARISON_FEATURE": "Feature 3", "COMPARISON_US": "true", "COMPARISON_OTHERS": "true"}},
      {{"COMPARISON_FEATURE": "Feature 4", "COMPARISON_US": "true", "COMPARISON_OTHERS": "false"}},
      {{"COMPARISON_FEATURE": "Feature 5", "COMPARISON_US": "true", "COMPARISON_OTHERS": "false"}}
    ],
    "COMPARISON_CTA_TEXT": "Inizia Ora",
    "COMPARISON_CTA_URL": "#contact"
  }}''',
    "booking": '''"booking": {{
    "BOOKING_TITLE": "Prenota un Appuntamento",
    "BOOKING_SUBTITLE": "Sottotitolo",
    "BOOKING_DESCRIPTION": "MIN 15 parole: descrizione del servizio di prenotazione",
    "BOOKING_PHONE": "telefono o vuoto",
    "BOOKING_EMAIL": "email o vuoto",
    "BOOKING_HOURS": "Lun-Ven: 9:00-18:00",
    "BOOKING_SERVICE_LABEL": "Seleziona Servizio",
    "BOOKING_NOTES_LABEL": "Note Aggiuntive",
    "BOOKING_BUTTON_TEXT": "Prenota Ora"
  }}''',
    "app-download": '''"app-download": {{
    "APP_TITLE": "Scarica la Nostra App",
    "APP_SUBTITLE": "MIN 10 parole: sottotitolo che invoglia al download",
    "APP_FEATURES": [
      {{"APP_FEATURE_TEXT": "Feature 1 dell'app"}},
      {{"APP_FEATURE_TEXT": "Feature 2 dell'app"}},
      {{"APP_FEATURE_TEXT": "Feature 3 dell'app"}}
    ],
    "APP_IMAGE_URL": "",
    "APP_STORE_URL": "#",
    "APP_PLAY_URL": "#"
  }}''',
    "social-proof": '''"social-proof": {{
    "SOCIAL_TITLE": "I Nostri Numeri Parlano",
    "SOCIAL_ITEMS": [
      {{"SOCIAL_ICON": "emoji", "SOCIAL_COUNT": "10K", "SOCIAL_LABEL": "Followers"}},
      {{"SOCIAL_ICON": "emoji", "SOCIAL_COUNT": "500", "SOCIAL_LABEL": "Progetti"}},
      {{"SOCIAL_ICON": "emoji", "SOCIAL_COUNT": "98%", "SOCIAL_LABEL": "Soddisfazione"}},
      {{"SOCIAL_ICON": "emoji", "SOCIAL_COUNT": "24/7", "SOCIAL_LABEL": "Supporto"}}
    ]
  }}''',
    "schedule": '''"schedule": {{
    "SCHEDULE_TITLE": "Programma",
    "SCHEDULE_SUBTITLE": "Sottotitolo",
    "SCHEDULE_ITEMS": [
      {{"SCHEDULE_TIME": "09:00", "SCHEDULE_TITLE": "Titolo sessione", "SCHEDULE_SPEAKER": "Nome Speaker", "SCHEDULE_DESCRIPTION": "Breve descrizione"}},
      {{"SCHEDULE_TIME": "10:30", "SCHEDULE_TITLE": "Titolo sessione", "SCHEDULE_SPEAKER": "Nome Speaker", "SCHEDULE_DESCRIPTION": "Breve descrizione"}},
      {{"SCHEDULE_TIME": "14:00", "SCHEDULE_TITLE": "Titolo sessione", "SCHEDULE_SPEAKER": "Nome Speaker", "SCHEDULE_DESCRIPTION": "Breve descrizione"}}
    ]
  }}''',
}

# Map array keys for dynamic structure-rule generation
_SECTION_ARRAY_RULES: Dict[str, str] = {
    "services": 'The "SERVICES" key MUST be an array of objects with EXACTLY: "SERVICE_ICON", "SERVICE_TITLE", "SERVICE_DESCRIPTION". At LEAST 3 items.',
    "features": 'The "FEATURES" key MUST be an array of objects with EXACTLY: "FEATURE_ICON", "FEATURE_TITLE", "FEATURE_DESCRIPTION". At LEAST 4 items.',
    "testimonials": 'The "TESTIMONIALS" key MUST be an array of objects with EXACTLY: "TESTIMONIAL_TEXT", "TESTIMONIAL_AUTHOR", "TESTIMONIAL_ROLE", "TESTIMONIAL_INITIAL". At LEAST 3 items.',
    "gallery": 'The "GALLERY_ITEMS" key MUST be an array of objects with EXACTLY: "GALLERY_IMAGE_URL", "GALLERY_IMAGE_ALT", "GALLERY_CAPTION". At LEAST 4 items.',
    "team": 'The "TEAM_MEMBERS" key MUST be an array of objects with EXACTLY: "MEMBER_NAME", "MEMBER_ROLE", "MEMBER_IMAGE_URL", "MEMBER_BIO". At LEAST 3 items.',
    "blog": 'The "BLOG_POSTS" key MUST be an array of objects with EXACTLY: "POST_TITLE", "POST_EXCERPT", "POST_CATEGORY", "POST_DATE", "POST_AUTHOR", "POST_IMAGE_URL", "POST_IMAGE_ALT". At LEAST 3 items.',
    "awards": 'The "AWARDS" key MUST be an array of objects with EXACTLY: "AWARD_YEAR", "AWARD_TITLE", "AWARD_DESCRIPTION". At LEAST 3 items.',
    "listings": 'The "LISTING_ITEMS" key MUST be an array of objects with EXACTLY: "LISTING_TITLE", "LISTING_DESCRIPTION", "LISTING_PRICE", "LISTING_IMAGE_URL", "LISTING_IMAGE_ALT", "LISTING_SPEC_1", "LISTING_SPEC_2", "LISTING_SPEC_3". At LEAST 3 items.',
    "donations": 'The "DONATION_ITEMS" key MUST be an array of objects with EXACTLY: "DONATION_TITLE", "DONATION_DESCRIPTION", "DONATION_RAISED", "DONATION_GOAL", "DONATION_PROGRESS", "DONATION_IMAGE_URL", "DONATION_IMAGE_ALT". At LEAST 2 items.',
    "comparison": 'The "COMPARISON_ITEMS" key MUST be an array of objects with EXACTLY: "COMPARISON_FEATURE", "COMPARISON_US", "COMPARISON_OTHERS". At LEAST 4 items.',
    "social-proof": 'The "SOCIAL_ITEMS" key MUST be an array of objects with EXACTLY: "SOCIAL_ICON", "SOCIAL_COUNT", "SOCIAL_LABEL". At LEAST 3 items.',
    "schedule": 'The "SCHEDULE_ITEMS" key MUST be an array of objects with EXACTLY: "SCHEDULE_TIME", "SCHEDULE_TITLE", "SCHEDULE_SPEAKER", "SCHEDULE_DESCRIPTION". At LEAST 3 items.',
    "app-download": 'The "APP_FEATURES" key MUST be an array of objects with EXACTLY: "APP_FEATURE_TEXT". At LEAST 3 items.',
}

# =========================================================
# CATEGORY-SPECIFIC FALLBACK TEXTS
# When AI text generation fails, use these instead of generic text.
# Each category has tailored copy that matches the business type.
# =========================================================
_CATEGORY_FALLBACK_TEXTS: Dict[str, Dict[str, dict]] = {
    "restaurant": {
        "hero": {
            "HERO_TITLE": "Dove il Gusto Incontra l'Arte",
            "HERO_SUBTITLE": "Ogni piatto racconta una storia di passione, tradizione e ingredienti scelti con cura maniacale. Un viaggio sensoriale che inizia dal primo sguardo al menu.",
            "HERO_CTA_TEXT": "Prenota il Tuo Tavolo",
            "HERO_CTA_URL": "#contact",
            "HERO_IMAGE_URL": "",
            "HERO_IMAGE_ALT": "L'esperienza culinaria nel nostro ristorante",
        },
        "about": {
            "ABOUT_TITLE": "La Nostra Filosofia in Cucina",
            "ABOUT_SUBTITLE": "Ogni ingrediente ha una provenienza, ogni ricetta una storia che merita di essere raccontata",
            "ABOUT_TEXT": "Nasciamo dalla convinzione che mangiare non sia solo nutrirsi, ma vivere un'esperienza. La nostra cucina parte dalla terra: collaboriamo con produttori locali selezionati, seguiamo la stagionalita e trasformiamo materie prime eccezionali in piatti che emozionano. Ogni ricetta e il risultato di ricerca, sperimentazione e amore per il dettaglio.",
            "ABOUT_HIGHLIGHT_1": "Fornitori locali selezionati",
            "ABOUT_HIGHLIGHT_2": "Coperti serviti ogni anno",
            "ABOUT_HIGHLIGHT_3": "Valutazione media clienti",
            "ABOUT_HIGHLIGHT_NUM_1": "18",
            "ABOUT_HIGHLIGHT_NUM_2": "12400",
            "ABOUT_HIGHLIGHT_NUM_3": "4.9",
        },
        "services": {
            "SERVICES_TITLE": "I Nostri Piatti Signature",
            "SERVICES_SUBTITLE": "Tre esperienze culinarie che definiscono la nostra identita gastronomica",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f372", "SERVICE_TITLE": "Menu Degustazione", "SERVICE_DESCRIPTION": "Un percorso di 7 portate che attraversa sapori e territori. Ogni piatto dialoga con il successivo in un crescendo di gusto che sorprende il palato."},
                {"SERVICE_ICON": "\U0001f37e", "SERVICE_TITLE": "Cantina Curata", "SERVICE_DESCRIPTION": "Oltre 180 etichette selezionate personalmente dal nostro sommelier. Abbinamenti pensati per esaltare ogni singola portata del vostro menu."},
                {"SERVICE_ICON": "\U0001f382", "SERVICE_TITLE": "Eventi Privati", "SERVICE_DESCRIPTION": "La nostra sala riservata accoglie fino a 40 ospiti per cene aziendali, celebrazioni e serate esclusive con menu personalizzati dallo chef."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Riserva il Tuo Momento Speciale",
            "CONTACT_SUBTITLE": "Che sia una cena romantica, un pranzo di lavoro o una serata tra amici, siamo pronti ad accoglierti con il calore che meriti.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "La Tavola Ti Aspetta",
            "CTA_SUBTITLE": "I posti migliori vanno via in fretta, soprattutto il venerdi e sabato sera. Prenota ora e assicurati un'esperienza indimenticabile.",
            "CTA_BUTTON_TEXT": "Prenota Ora", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Dove ogni pasto diventa un ricordo che vale la pena conservare."},
    },
    "saas": {
        "hero": {
            "HERO_TITLE": "Il Futuro e Adesso",
            "HERO_SUBTITLE": "La piattaforma che trasforma il caos operativo in flussi intelligenti. Automatizza, analizza, scala - mentre tu ti concentri su cio che conta davvero.",
            "HERO_CTA_TEXT": "Prova Gratis 14 Giorni",
            "HERO_CTA_URL": "#contact", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "Dashboard della piattaforma",
        },
        "about": {
            "ABOUT_TITLE": "Costruito per Chi Vuole di Piu",
            "ABOUT_SUBTITLE": "Non un altro tool. Una rivoluzione nel modo in cui lavori ogni giorno",
            "ABOUT_TEXT": "Siamo nati dalla frustrazione di chi usa 15 strumenti diversi per fare il lavoro di uno. La nostra piattaforma unifica, semplifica e potenzia ogni flusso operativo. Dietro ogni funzionalita c'e un team ossessionato dall'esperienza utente e dalla performance. Zero compromessi sulla velocita, zero compromessi sulla sicurezza.",
            "ABOUT_HIGHLIGHT_1": "Aziende attive sulla piattaforma",
            "ABOUT_HIGHLIGHT_2": "Uptime garantito",
            "ABOUT_HIGHLIGHT_3": "Ore risparmiate al mese per utente",
            "ABOUT_HIGHLIGHT_NUM_1": "2400", "ABOUT_HIGHLIGHT_NUM_2": "99.97", "ABOUT_HIGHLIGHT_NUM_3": "23",
        },
        "services": {
            "SERVICES_TITLE": "Funzionalita che Cambiano le Regole",
            "SERVICES_SUBTITLE": "Ogni feature e progettata per eliminare un problema reale, non per riempire una checklist",
            "SERVICES": [
                {"SERVICE_ICON": "\u26a1", "SERVICE_TITLE": "Automazione Intelligente", "SERVICE_DESCRIPTION": "Crea flussi di lavoro complessi in pochi click. Il nostro motore AI impara dai tuoi pattern e suggerisce ottimizzazioni che ti fanno risparmiare ore ogni settimana."},
                {"SERVICE_ICON": "\U0001f4ca", "SERVICE_TITLE": "Analytics in Tempo Reale", "SERVICE_DESCRIPTION": "Dashboard personalizzabili con metriche che contano. Visualizza trend, anomalie e opportunita prima che diventino problemi o che la concorrenza le colga."},
                {"SERVICE_ICON": "\U0001f6e1\ufe0f", "SERVICE_TITLE": "Sicurezza Enterprise", "SERVICE_DESCRIPTION": "Crittografia end-to-end, SSO, audit log completo e conformita GDPR integrata. La tua sicurezza non e un'opzione, e la nostra ossessione."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Parliamo del Tuo Prossimo Livello",
            "CONTACT_SUBTITLE": "Demo personalizzata in 15 minuti. Ti mostriamo esattamente come la piattaforma risolve i tuoi problemi specifici.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "Smetti di Perdere Tempo",
            "CTA_SUBTITLE": "Ogni giorno senza automazione e un giorno di produttivita sprecata. Inizia ora, i risultati arrivano dalla prima settimana.",
            "CTA_BUTTON_TEXT": "Inizia la Prova Gratuita", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "La piattaforma che fa lavorare la tecnologia per te, non il contrario."},
    },
    "portfolio": {
        "hero": {
            "HERO_TITLE": "Creo Mondi Visivi",
            "HERO_SUBTITLE": "Designer, pensatore, risolutore di problemi. Trasformo idee astratte in esperienze digitali che le persone ricordano e con cui vogliono interagire.",
            "HERO_CTA_TEXT": "Esplora i Progetti",
            "HERO_CTA_URL": "#gallery", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "Portfolio dei migliori progetti creativi",
        },
        "about": {
            "ABOUT_TITLE": "Il Metodo Dietro la Creativita",
            "ABOUT_SUBTITLE": "Ogni progetto inizia con una domanda: come posso superare le aspettative?",
            "ABOUT_TEXT": "Con oltre un decennio di esperienza nel design digitale, ho sviluppato un approccio che unisce ricerca, intuizione e ossessione per il dettaglio. Non creo semplicemente interfacce - costruisco esperienze che risolvono problemi reali e generano risultati misurabili. Ogni pixel ha uno scopo, ogni interazione racconta una storia.",
            "ABOUT_HIGHLIGHT_1": "Progetti completati", "ABOUT_HIGHLIGHT_2": "Premi e riconoscimenti",
            "ABOUT_HIGHLIGHT_3": "Clienti in tutto il mondo",
            "ABOUT_HIGHLIGHT_NUM_1": "127", "ABOUT_HIGHLIGHT_NUM_2": "14", "ABOUT_HIGHLIGHT_NUM_3": "38",
        },
        "services": {
            "SERVICES_TITLE": "Competenze al Tuo Servizio",
            "SERVICES_SUBTITLE": "Dalla strategia al pixel finale, ogni fase del progetto riceve la stessa cura maniacale",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f3a8", "SERVICE_TITLE": "Brand Identity", "SERVICE_DESCRIPTION": "Logo, palette, tipografia e sistema visivo completo. Costruisco identita che si distinguono nel rumore e restano impresse nella memoria."},
                {"SERVICE_ICON": "\U0001f4f1", "SERVICE_TITLE": "UI/UX Design", "SERVICE_DESCRIPTION": "Interfacce intuitive che guidano l'utente verso l'obiettivo. Ricerca, wireframe, prototipazione e test - ogni decisione e supportata dai dati."},
                {"SERVICE_ICON": "\U0001f680", "SERVICE_TITLE": "Design Strategico", "SERVICE_DESCRIPTION": "Non solo estetica: analizzo il mercato, studio i competitor e progetto soluzioni che generano conversioni reali e crescita misurabile."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Costruiamo Qualcosa di Grande",
            "CONTACT_SUBTITLE": "Hai un progetto ambizioso? Parliamone davanti a un caffe virtuale. Le migliori collaborazioni iniziano con una conversazione sincera.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "Il Tuo Progetto Merita il Meglio",
            "CTA_SUBTITLE": "Accetto solo 3 nuovi progetti al mese per garantire a ciascuno l'attenzione che merita. Verifica la mia disponibilita.",
            "CTA_BUTTON_TEXT": "Richiedi una Consulenza", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Design che risolve problemi e crea connessioni autentiche."},
    },
    "ecommerce": {
        "hero": {
            "HERO_TITLE": "Stile Che Parla di Te",
            "HERO_SUBTITLE": "Prodotti selezionati con cura per chi non si accontenta del banale. Qualita artigianale, design contemporaneo, spedizione fulminante.",
            "HERO_CTA_TEXT": "Scopri la Collezione",
            "HERO_CTA_URL": "#services", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "La nostra collezione esclusiva",
        },
        "services": {
            "SERVICES_TITLE": "Perche Scegliere Noi",
            "SERVICES_SUBTITLE": "Tre promesse che manteniamo ogni singolo giorno",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f48e", "SERVICE_TITLE": "Qualita Certificata", "SERVICE_DESCRIPTION": "Ogni prodotto passa 3 controlli qualita prima di raggiungere le tue mani. Materiali premium, lavorazione impeccabile, durabilita garantita nel tempo."},
                {"SERVICE_ICON": "\U0001f69a", "SERVICE_TITLE": "Spedizione Express", "SERVICE_DESCRIPTION": "Ordini prima delle 14? Spedito lo stesso giorno. Tracciamento in tempo reale e consegna in 24-48 ore in tutta Italia, gratis sopra i 59 euro."},
                {"SERVICE_ICON": "\U0001f504", "SERVICE_TITLE": "Reso Senza Pensieri", "SERVICE_DESCRIPTION": "30 giorni per cambiare idea. Reso gratuito, rimborso immediato, zero domande. La tua soddisfazione e la nostra unica priorita."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Siamo Qui Per Te",
            "CONTACT_SUBTITLE": "Dubbi sulla taglia, domande sui materiali o bisogno di un consiglio personalizzato? Il nostro team risponde in meno di 2 ore.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "Non Lasciarti Sfuggire Questo",
            "CTA_SUBTITLE": "Nuovi arrivi ogni settimana. Iscriviti alla newsletter e ricevi il 15% di sconto sul primo ordine.",
            "CTA_BUTTON_TEXT": "Ottieni il 15% di Sconto", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Prodotti che raccontano chi sei, consegnati a casa tua con cura."},
    },
    "business": {
        "hero": {
            "HERO_TITLE": "Costruiamo il Domani",
            "HERO_SUBTITLE": "Partner strategici per aziende che non si accontentano dello status quo. Trasformiamo sfide complesse in opportunita concrete di crescita misurabile.",
            "HERO_CTA_TEXT": "Richiedi una Consulenza",
            "HERO_CTA_URL": "#contact", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "Il nostro approccio strategico al business",
        },
        "about": {
            "ABOUT_TITLE": "Il Nostro Approccio Strategico",
            "ABOUT_SUBTITLE": "Non vendiamo servizi. Costruiamo partnership che generano risultati duraturi",
            "ABOUT_TEXT": "Nasciamo dalla convinzione che il mercato merita di meglio. Non ci accontentiamo della mediocrita e non inseguiamo le scorciatoie. Ogni progetto diventa una sfida personale, un'opportunita per dimostrare che si puo fare di piu, meglio e con piu cura. La nostra storia e fatta di intuizioni brillanti e la testardaggine di chi crede davvero in quello che fa.",
            "ABOUT_HIGHLIGHT_1": "Anni di esperienza sul campo",
            "ABOUT_HIGHLIGHT_2": "Progetti completati con successo",
            "ABOUT_HIGHLIGHT_3": "Tasso di soddisfazione clienti",
            "ABOUT_HIGHLIGHT_NUM_1": "15", "ABOUT_HIGHLIGHT_NUM_2": "847", "ABOUT_HIGHLIGHT_NUM_3": "99.2",
        },
        "services": {
            "SERVICES_TITLE": "Il Metodo Dietro i Risultati",
            "SERVICES_SUBTITLE": "Tre pilastri che trasformano la complessita in vantaggio competitivo",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f3af", "SERVICE_TITLE": "Strategia su Misura", "SERVICE_DESCRIPTION": "Analizziamo a fondo il tuo contesto per costruire un percorso che rifletta la vera identita del tuo business e porti risultati misurabili nel tempo."},
                {"SERVICE_ICON": "\U0001f680", "SERVICE_TITLE": "Esecuzione Fulminante", "SERVICE_DESCRIPTION": "Dalla visione al lancio in tempi record. Ogni fase del progetto segue un metodo collaudato che elimina gli sprechi e accelera i risultati concreti."},
                {"SERVICE_ICON": "\U0001f4a1", "SERVICE_TITLE": "Evoluzione Continua", "SERVICE_DESCRIPTION": "Non ci fermiamo al primo traguardo. Monitoriamo, ottimizziamo e iteriamo per garantire che ogni aspetto cresca insieme al tuo business."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Parliamo del Tuo Prossimo Passo",
            "CONTACT_SUBTITLE": "Ogni grande progetto inizia con una conversazione. Raccontaci la tua idea e trasformiamola insieme in qualcosa di straordinario.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "Il Momento e Adesso",
            "CTA_SUBTITLE": "Ogni giorno che passa e un'opportunita persa. Fai il primo passo verso risultati che superano le aspettative.",
            "CTA_BUTTON_TEXT": "Prenota una Consulenza Gratuita", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Dove nascono le idee che cambiano le regole del gioco."},
    },
    "blog": {
        "hero": {
            "HERO_TITLE": "Parole Che Lasciano il Segno",
            "HERO_SUBTITLE": "Storie, riflessioni e approfondimenti per chi vuole andare oltre la superficie. Contenuti che informano, ispirano e provocano il pensiero critico.",
            "HERO_CTA_TEXT": "Leggi l'Ultimo Articolo",
            "HERO_CTA_URL": "#services", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "Il nostro blog editoriale",
        },
        "services": {
            "SERVICES_TITLE": "Le Nostre Rubriche",
            "SERVICES_SUBTITLE": "Contenuti curati per menti curiose che cercano sostanza, non rumore",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f4dd", "SERVICE_TITLE": "Analisi di Fondo", "SERVICE_DESCRIPTION": "Approfondimenti che vanno oltre il titolo. Ricerche originali, dati verificati e prospettive che non trovi altrove. Ogni articolo e un viaggio."},
                {"SERVICE_ICON": "\U0001f4a1", "SERVICE_TITLE": "Idee e Tendenze", "SERVICE_DESCRIPTION": "Cosa sta cambiando nel nostro settore e perche dovrebbe importarti. Anticipiamo i trend con analisi lucide e consigli pratici immediati."},
                {"SERVICE_ICON": "\U0001f399\ufe0f", "SERVICE_TITLE": "Interviste Esclusive", "SERVICE_DESCRIPTION": "Conversazioni con chi sta plasmando il futuro. Storie vere, lezioni apprese e visioni che ampliano gli orizzonti di ogni lettore."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Unisciti alla Conversazione",
            "CONTACT_SUBTITLE": "Hai un'idea per un articolo, una storia da raccontare o semplicemente vuoi dire la tua? La nostra community cresce grazie a voci come la tua.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "footer": {"FOOTER_DESCRIPTION": "Storie che contano, scritte per chi vuole capire davvero."},
    },
    "event": {
        "hero": {
            "HERO_TITLE": "Vivi l'Esperienza dal Vivo",
            "HERO_SUBTITLE": "Gli eventi che creano connessioni autentiche, ispirano nuove idee e lasciano ricordi che durano. Non semplici incontri, ma momenti che cambiano prospettive.",
            "HERO_CTA_TEXT": "Riserva il Tuo Posto",
            "HERO_CTA_URL": "#contact", "HERO_IMAGE_URL": "", "HERO_IMAGE_ALT": "L'atmosfera dei nostri eventi esclusivi",
        },
        "services": {
            "SERVICES_TITLE": "Cosa Ti Aspetta",
            "SERVICES_SUBTITLE": "Un programma progettato per massimizzare ogni minuto della tua esperienza",
            "SERVICES": [
                {"SERVICE_ICON": "\U0001f3a4", "SERVICE_TITLE": "Speaker d'Eccezione", "SERVICE_DESCRIPTION": "Relatori selezionati tra i migliori del settore. Non le solite presentazioni, ma conversazioni che provocano idee e cambiano il modo di pensare."},
                {"SERVICE_ICON": "\U0001f91d", "SERVICE_TITLE": "Networking Mirato", "SERVICE_DESCRIPTION": "Sessioni strutturate per connettere le persone giuste. Il nostro sistema di matching ti mette in contatto con chi puo davvero fare la differenza."},
                {"SERVICE_ICON": "\U0001f3c6", "SERVICE_TITLE": "Esperienza Premium", "SERVICE_DESCRIPTION": "Dall'accoglienza al follow-up, ogni dettaglio e curato per offrirti un'esperienza che supera qualsiasi aspettativa. Location esclusiva, catering d'autore."},
            ],
        },
        "contact": {
            "CONTACT_TITLE": "Non Perdere Questa Occasione",
            "CONTACT_SUBTITLE": "I posti sono limitati e ogni edizione registra il tutto esaurito. Assicurati il tuo ingresso prima che sia troppo tardi.",
            "CONTACT_ADDRESS": "", "CONTACT_PHONE": "", "CONTACT_EMAIL": "",
        },
        "cta": {
            "CTA_TITLE": "I Posti Stanno Finendo",
            "CTA_SUBTITLE": "Le ultime tre edizioni hanno registrato il sold out in meno di una settimana. Non aspettare l'ultimo momento.",
            "CTA_BUTTON_TEXT": "Acquista il Tuo Biglietto", "CTA_BUTTON_URL": "#contact",
        },
        "footer": {"FOOTER_DESCRIPTION": "Eventi che creano connessioni e ispirano il cambiamento."},
    },
}


def _detect_category(template_style_id: Optional[str] = None, business_description: str = "") -> str:
    """Detect business category from template_style_id or business_description."""
    if template_style_id:
        prefix = template_style_id.split("-")[0]
        if prefix in _CATEGORY_FALLBACK_TEXTS:
            return prefix
    # Scan description for category hints
    desc_lower = business_description.lower() if business_description else ""
    category_keywords = {
        "restaurant": ["ristorante", "restaurant", "cucina", "chef", "menu", "trattoria", "pizzeria"],
        "saas": ["saas", "software", "piattaforma", "app", "startup", "tech", "dashboard"],
        "portfolio": ["portfolio", "designer", "creativo", "freelance", "fotografo", "artista"],
        "ecommerce": ["ecommerce", "e-commerce", "shop", "negozio", "vendita", "prodotti"],
        "blog": ["blog", "magazine", "editoriale", "articoli", "giornale"],
        "event": ["evento", "event", "conferenza", "workshop", "festival", "meetup"],
    }
    for cat, keywords in category_keywords.items():
        if any(kw in desc_lower for kw in keywords):
            return cat
    return "business"


def _parse_reference_analysis(analysis_text: str) -> Dict[str, Any]:
    """
    Parse structured reference image analysis into a dict with exact hex colors.
    Expects KEY: value format from the structured prompt. Falls back to regex
    extraction of any hex codes found in the text.
    """
    result = {}

    # Map structured field names to dict keys
    field_map = {
        "PRIMARY_COLOR": "primary_color",
        "SECONDARY_COLOR": "secondary_color",
        "ACCENT_COLOR": "accent_color",
        "BG_COLOR": "bg_color",
        "BG_ALT_COLOR": "bg_alt_color",
        "TEXT_COLOR": "text_color",
        "TEXT_MUTED_COLOR": "text_muted_color",
        "IS_DARK_THEME": "is_dark",
        "TYPOGRAPHY_STYLE": "typography_style",
        "FONT_WEIGHT": "font_weight",
        "LAYOUT_STYLE": "layout_style",
        "MOOD": "mood",
        "DESIGN_NOTES": "design_notes",
    }

    for line in analysis_text.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        # Split on first colon
        key_part, _, value_part = line.partition(":")
        key_part = key_part.strip().upper().replace(" ", "_")
        value_part = value_part.strip()

        if key_part in field_map:
            dict_key = field_map[key_part]
            if dict_key == "is_dark":
                result[dict_key] = value_part.lower().startswith("true")
            else:
                # For color fields, extract just the hex code
                hex_match = re.search(r'#[0-9A-Fa-f]{6}', value_part)
                if hex_match and dict_key.endswith("_color"):
                    result[dict_key] = hex_match.group(0)
                else:
                    # For non-color fields, take the first word/phrase
                    result[dict_key] = value_part.split("(")[0].strip().strip("[]")

    # Fallback: if structured parsing got fewer than 3 color fields, try brute-force hex extraction
    color_keys = [k for k in result if k.endswith("_color")]
    if len(color_keys) < 3:
        all_hexes = re.findall(r'#[0-9A-Fa-f]{6}', analysis_text)
        # Deduplicate while preserving order
        seen = set()
        unique_hexes = []
        for h in all_hexes:
            if h.lower() not in seen:
                seen.add(h.lower())
                unique_hexes.append(h)
        # Assign to standard fields in order of appearance
        fallback_keys = ["primary_color", "secondary_color", "accent_color",
                         "bg_color", "bg_alt_color", "text_color", "text_muted_color"]
        for i, hex_val in enumerate(unique_hexes):
            if i < len(fallback_keys) and fallback_keys[i] not in result:
                result[fallback_keys[i]] = hex_val

    # Detect dark theme from bg_color if not explicitly set
    if "is_dark" not in result and "bg_color" in result:
        try:
            bg = result["bg_color"].lstrip("#")
            r, g, b = int(bg[:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            result["is_dark"] = luminance < 0.5
        except (ValueError, IndexError):
            pass

    return result


# =========================================================
# Pending Photo Choices Registry
# Stores asyncio.Events and user choices for the interactive
# photo selection flow during generation.
# Key: site_id (int), Value: dict with event, choices, site_data
# =========================================================
_pending_photo_choices: Dict[int, Dict[str, Any]] = {}

PHOTO_CHOICE_TIMEOUT = 300  # 5 minutes


class DataBindingGenerator:
    def __init__(self):
        self.kimi = kimi
        self.kimi_text = kimi_text
        self.assembler = template_assembler

    # =========================================================
    # Blueprint Ordering
    # =========================================================
    @staticmethod
    def _apply_blueprint_ordering(
        sections: List[str], template_style_id: Optional[str]
    ) -> List[str]:
        """Reorder sections according to the category blueprint.

        Rules:
        - Hero always first, footer always last (hard constraint).
        - Sections in the blueprint are ordered by their blueprint position.
        - Sections NOT in the blueprint are kept and placed just before footer.
        - Never adds or removes sections.
        """
        if not template_style_id or not sections:
            return sections

        category = template_style_id.split("-")[0] if "-" in template_style_id else template_style_id
        blueprint = BLUEPRINTS.get(category)
        if not blueprint:
            return sections

        # Separate fixed anchors
        has_hero = "hero" in sections
        has_footer = "footer" in sections
        middle = [s for s in sections if s not in ("hero", "footer", "nav")]

        # Split into blueprint-ordered and extras
        in_blueprint = [s for s in blueprint if s in middle]
        extras = [s for s in middle if s not in blueprint]

        ordered = []
        if has_hero:
            ordered.append("hero")
        ordered.extend(in_blueprint)
        ordered.extend(extras)
        if has_footer:
            ordered.append("footer")

        logger.info(
            f"[Blueprint] {category}: {sections} -> {ordered}"
        )
        return ordered

    # =========================================================
    # Harmony Group Selection
    # =========================================================
    @staticmethod
    def _pick_harmony_group(
        template_style_id: Optional[str],
        pool_map: Dict[str, List[str]],
    ) -> Optional[List[str]]:
        """Select a visual harmony group based on overlap with the style pool.

        Returns the chosen group's keyword list, or None if no pool is available.
        The selection is random but weighted — groups with more matching variants
        in the pool have a higher probability.
        """
        if not pool_map:
            return None

        # Collect all variant IDs from the pool
        all_variants = []
        for variants in pool_map.values():
            all_variants.extend(variants)

        # Calculate overlap score for each harmony group
        scores: Dict[str, int] = {}
        for group_name, keywords in HARMONY_GROUPS.items():
            overlap = sum(
                1 for v in all_variants
                if any(kw in v.lower() for kw in keywords)
            )
            if overlap > 0:
                scores[group_name] = overlap

        if not scores:
            return None

        # Weighted random selection
        groups = list(scores.keys())
        weights = [scores[g] for g in groups]
        chosen = random.choices(groups, weights=weights, k=1)[0]

        logger.info(
            f"[Harmony] Scores: {scores}, chosen: {chosen}"
        )
        return HARMONY_GROUPS[chosen]

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
        reference_analysis: Optional[str] = None,
        parsed_reference: Optional[Dict[str, Any]] = None,
        photo_urls: Optional[List[str]] = None,
        template_style_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Kimi returns JSON with color palette and fonts.

        When parsed_reference contains hex colors (from image analysis), the
        generation is constrained: lower temperature, no variety injection,
        exact color codes in the prompt, and post-generation validation.
        """
        # Determine if we have a strong reference to follow
        has_reference = bool(reference_analysis) or bool(reference_image_url)
        # Exact parsed colors from reference image (structured hex codes)
        has_exact_colors = bool(parsed_reference and parsed_reference.get("primary_color"))

        style_hint = ""
        harmony_palette_hint = ""
        if style_preferences:
            # When reference has exact colors, skip template color hints (they conflict)
            if style_preferences.get("primary_color") and not has_exact_colors:
                style_hint += f"Primary color requested: {style_preferences['primary_color']}. "
                # Generate full harmony palette as strong color guidance
                if _has_palette_gen:
                    try:
                        category_label = template_style_id.split("-")[0] if template_style_id else "business"
                        palette = _generate_harmony_palette(
                            base_hex=style_preferences["primary_color"],
                            scheme=style_preferences.get("color_scheme", "auto"),
                            category=category_label,
                        )
                        harmony_palette_hint = f"""
=== HARMONY PALETTE (generated from user's chosen color — use as strong guidance) ===
primary_color: {palette['primary_color']}
secondary_color: {palette['secondary_color']}
accent_color: {palette['accent_color']}
bg_color: {palette['bg_color']}
bg_alt_color: {palette['bg_alt_color']}
text_color: {palette['text_color']}
text_muted_color: {palette['text_muted_color']}
Use these colors as your starting point. You may adjust slightly for the business personality but keep the harmony intact.
=== END HARMONY PALETTE ===
"""
                    except Exception as e:
                        logger.warning(f"[DataBinding] Harmony palette generation failed: {e}")
            if style_preferences.get("secondary_color") and not has_exact_colors:
                style_hint += f"Secondary color requested: {style_preferences['secondary_color']}. "
            if style_preferences.get("mood"):
                style_hint += f"Mood/style: {style_preferences['mood']}. "

        # === MANDATORY EXACT COLORS (highest priority - from parsed reference) ===
        exact_colors_block = ""
        if has_exact_colors:
            ref = parsed_reference
            dark_hint = ""
            if ref.get("is_dark") is True:
                dark_hint = "\nThe reference has a DARK background. bg_color MUST be dark (#000-#222 range). text_color MUST be light (#DDD-#FFF range)."
            elif ref.get("is_dark") is False:
                dark_hint = "\nThe reference has a LIGHT background. bg_color MUST be light (#EEE-#FFF range). text_color MUST be dark (#000-#333 range)."
            exact_colors_block = f"""
=== MANDATORY REFERENCE COLORS (DO NOT CHANGE) ===
Use EXACTLY these colors from the reference:
primary_color: {ref.get('primary_color')}
secondary_color: {ref.get('secondary_color', ref.get('primary_color'))}
accent_color: {ref.get('accent_color', ref.get('primary_color'))}
bg_color: {ref.get('bg_color', '#0F172A' if ref.get('is_dark') else '#FAF7F2')}
text_color: {ref.get('text_color', '#F1F5F9' if ref.get('is_dark') else '#1A1A2E')}
{dark_hint}

These are NON-NEGOTIABLE. Return them exactly as provided.
Only generate: bg_alt_color, text_muted_color (derived from above), fonts, border_radius, shadow, spacing.
=== END MANDATORY COLORS ===
"""

        # === REFERENCE ANALYSIS OVERRIDE (used when we have text analysis but no parsed colors) ===
        reference_override = ""
        if reference_analysis and not has_exact_colors:
            reference_override = f"""
=== MANDATORY REFERENCE OVERRIDE (HIGHEST PRIORITY — OVERRIDE ALL OTHER DIRECTIVES) ===
The user provided a reference website screenshot. You MUST match its visual style.
Here is the analysis of that reference:

{reference_analysis}

STRICT RULES:
1. Extract the EXACT hex colors mentioned above and use them as your primary, secondary, accent colors.
2. If the reference is DARK (dark background), your bg_color MUST be dark. If it's LIGHT, bg_color MUST be light.
3. Match the MOOD exactly: if the reference is brutalist/bold, your palette must be brutalist/bold. If elegant, be elegant. Do NOT soften or "corporate-ify" the style.
4. The typography style must match: if the reference uses bold geometric sans-serifs, pick similar fonts. If it uses elegant serifs, pick serifs.
5. Do NOT override these colors with random variety or creative context — the reference is the user's EXPLICIT design intent.
=== END MANDATORY REFERENCE ===
"""

        # Extract palette guidance from creative context (blueprints)
        # SKIP entirely when exact reference colors are provided
        palette_hint = ""
        if creative_context and not has_reference and not has_exact_colors:
            palette_hint = f"\nPROFESSIONAL DESIGN REFERENCE:\n{creative_context[:500]}\n"

        # Inject reference URL analysis (colors and fonts from a real site)
        # SKIP when exact colors are already parsed from image
        if reference_url_context and not has_exact_colors:
            palette_hint += f"\n{reference_url_context}\nMatch these colors and fonts closely.\n"

        # --- VARIETY: inject random color mood and font suggestion ---
        # SKIP entirely when reference or exact colors are provided
        variety_hint = ""
        if variety_context and not has_reference and not has_exact_colors:
            color_mood = variety_context.get("color_mood", {})
            font_pair = variety_context.get("font_pairing", {})
            # Only inject color mood if it has actual content (disabled when user specified colors)
            color_mood_block = ""
            if color_mood.get("mood"):
                color_mood_block = f"""
=== COLOR MOOD DIRECTION (follow this closely) ===
Design mood: "{color_mood.get('mood', 'Modern Bold')}"
{color_mood.get('hint', '')}
Adapt this mood to the business, but keep the color FEELING.
"""
            variety_hint = f"""{color_mood_block}
=== SUGGESTED FONT PAIRING (use this unless it clashes with the business) ===
Heading: "{font_pair.get('heading', 'Space Grotesk')}" ({font_pair.get('personality', 'MODERN')})
Body: "{font_pair.get('body', 'DM Sans')}"
font_heading_url: "{font_pair.get('url_h', 'Space+Grotesk:wght@400;600;700')}"
font_body_url: "{font_pair.get('url_b', 'DM+Sans:wght@400;500;600')}"
"""

        # --- FONT HINT for reference: match typography style ---
        reference_font_hint = ""
        if has_exact_colors:
            typo = parsed_reference.get("typography_style", "")
            fw = parsed_reference.get("font_weight", "")
            if typo == "brutalist" or fw == "bold":
                reference_font_hint = """
=== FONT OVERRIDE FOR REFERENCE ===
The reference uses BOLD/GEOMETRIC typography. Use one of these pairings:
- "Space Grotesk" (heading, wght 700-800) + "DM Sans" (body)
- "Archivo Black" (heading) + "Work Sans" (body)
- "Oswald" (heading, wght 700) + "Source Sans 3" (body)
- "Unbounded" (heading, wght 800-900) + "Figtree" (body)
The heading font MUST have weight 800-900 for maximum impact.
=== END FONT OVERRIDE ===
"""
            elif typo in ("elegant", "serif", "classic"):
                reference_font_hint = """
=== FONT OVERRIDE FOR REFERENCE ===
The reference uses ELEGANT/SERIF typography. Use one of these pairings:
- "Playfair Display" (heading) + "Inter" (body)
- "DM Serif Display" (heading) + "Plus Jakarta Sans" (body)
- "Cormorant Garamond" (heading) + "Lato" (body)
- "Instrument Serif" (heading) + "Instrument Sans" (body)
=== END FONT OVERRIDE ===
"""
            elif typo == "minimal":
                reference_font_hint = """
=== FONT OVERRIDE FOR REFERENCE ===
The reference uses MINIMAL/CLEAN typography. Use one of these pairings:
- "Sora" (heading) + "Inter" (body)
- "Albert Sans" (heading) + "IBM Plex Sans" (body)
- "Epilogue" (heading) + "Source Sans 3" (body)
=== END FONT OVERRIDE ===
"""

        # Build the full font pairings list dynamically from the pool
        # Skip random font pool when exact reference colors specify a typography override
        if has_exact_colors and reference_font_hint:
            font_list_str = "(See FONT OVERRIDE section above for reference-matched pairings)"
        else:
            shuffled_fonts = random.sample(FONT_PAIRING_POOL, min(8, len(FONT_PAIRING_POOL)))
            font_list_str = "\n".join(
                f'{fp["personality"]}: "{fp["heading"]}" (heading) + "{fp["body"]}" (body)'
                for fp in shuffled_fonts
            )

        # Photo context for theme: hint that real photos will be used
        theme_photo_hint = ""
        if photo_urls and len(photo_urls) > 0 and not has_exact_colors:
            theme_photo_hint = f"\nThe user has uploaded {len(photo_urls)} real photo(s) of their business. Choose colors that complement real-world photography: warm tones for food/hospitality, cool tones for tech, earthy tones for nature businesses. Avoid overly saturated backgrounds that clash with photos.\n"

        # Style-specific theme direction (colors, fonts, layout tokens for sub-style)
        style_theme_hint = _get_style_theme_hint(template_style_id) if not has_exact_colors else ""

        # --- DIVERSITY: inject creative seed and anti-repetition hints ---
        diversity_block = ""
        if not has_exact_colors and not has_reference:
            category = _get_category_from_style_id(template_style_id)
            recently_used = (variety_context or {}).get("_recently_used")
            diversity_block = build_diversity_prompt_block(category, recently_used)

        prompt = f"""You are a Dribbble/Awwwards-level UI designer. Generate a STUNNING, BOLD color palette and typography for a website.
Return ONLY valid JSON, no markdown, no explanation.
{exact_colors_block}{reference_override}
BUSINESS: {business_name} - {business_description[:1200]}
{style_hint}
{harmony_palette_hint}
{palette_hint}
{variety_hint}
{reference_font_hint}
{theme_photo_hint}
{style_theme_hint}
{diversity_block}

=== COLOR THEORY RULES (follow these for professional palettes) ===
- PRIMARY: The brand's emotional core. Ask: "What feeling should this business evoke?" Warm = trust/comfort (amber, coral). Cool = innovation/clarity (blue, teal). Bold = energy/passion (red, purple).
- SECONDARY: Must create VISUAL TENSION with primary. Use analogous (adjacent on wheel) for harmony, or split-complementary for energy. NEVER pick a color that's just a lighter/darker shade of primary.
- ACCENT: This is the CTA/action color. It MUST pop against the background. Use the complementary of bg_color on the color wheel. If bg is dark blue, accent should be warm orange/amber. If bg is cream, accent should be deep violet/teal.
- BG vs BG_ALT: bg_alt must differ enough from bg to create visible section separation (at least 5% lightness difference in HSL).
- TEXT_MUTED: Not just "gray". Tint it slightly toward the primary color for cohesion (e.g., if primary is blue, text_muted should be a blue-gray, not pure gray).
- FORBIDDEN: Muddy browns, desaturated greens that look sick, pure gray (#808080), neon that hurts eyes on white bg.
- SATURATION: Keep all colors above 40% saturation (except neutrals). Washed-out colors = amateur design.

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
  "font_body_url": "FontName:wght@400;500;600",
  "border_radius_style": "sharp|soft|round|pill",
  "shadow_style": "none|soft|dramatic",
  "spacing_density": "compact|normal|generous"
}}

=== COLOR RULES (CRITICAL) ===
- primary_color: SATURATED and VIBRANT. High chroma, fully alive. Never desaturated, never grayish. Think #E63946 not #8b9da5, think #7C3AED not #6677aa.
- secondary_color: COMPLEMENTARY to primary, not just a darker shade. If primary is warm, secondary can be cool (and vice versa). Must be visually distinct.
- accent_color: must POP against the palette. Use a CONTRASTING hue from primary (not analogous). Examples: deep blue primary + electric amber accent, forest green primary + coral accent, purple primary + lime accent. The accent is for CTAs and highlights — it must DEMAND attention.
- bg_color: NEVER plain #ffffff or #000000. Use rich tones: warm cream (#FAF7F2), deep navy (#0A1628), charcoal slate (#1A1D23), soft sage (#F0F4F1), warm blush (#FFF5F5), ivory (#FFFDF7). The background sets the entire mood.
- bg_alt_color: must be NOTICEABLY different from bg_color (at least 8-12% lightness shift). If bg is light, bg_alt should be a tinted pastel (e.g. soft lavender, light sand). If bg is dark, bg_alt should be 2-3 shades lighter. Sections must visually alternate.
- text_color: WCAG AA contrast against bg_color (minimum 4.5:1). For dark bg use near-white (#F1F5F9), for light bg use rich dark (#0F172A or #1A1A2E).
- text_muted_color: MUST have WCAG AA contrast (4.5:1) against BOTH bg_color AND bg_alt_color. For dark themes (bg_color < #333): use light grays (#CBD5E1, #E2E8F0, #D1D5DB), NOT mid-grays (#94A3B8, #6B7280). For light themes: use dark grays (#4B5563, #374151), NOT light grays. CRITICAL: cards use bg_alt_color as background — text_muted MUST be readable on cards.
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

=== LAYOUT TOKEN RULES ===
- border_radius_style: "sharp" for brutalist/editorial designs (0px corners), "soft" for modern/clean (12px), "round" for playful/friendly (24px), "pill" for SaaS buttons/cards (99px). Pick based on brand personality.
- shadow_style: "none" for flat/minimal/brutalist, "soft" for most modern designs, "dramatic" for luxury/3D/premium look with deep shadows.
- spacing_density: "compact" for info-dense sites (news, dashboards), "normal" for balanced layouts, "generous" for luxury/minimal brands with lots of whitespace.

=== UNIQUENESS DIRECTIVE {'(SKIP — MATCH REFERENCE)' if has_reference or has_exact_colors else '(CRITICAL)'} ===
{'NOTE: A reference image was provided. MATCH those exact colors and style. Do NOT generate random colors.' if has_reference or has_exact_colors else '''IMPORTANT: Generate a UNIQUE palette. Do NOT repeat common web palettes.
Use the business personality to pick unexpected but fitting color combinations.
Each generation must feel fresh and different from the previous ones.
Pick a font pairing you have not used recently. Surprise the viewer.'''}

Return ONLY the JSON object"""

        # Temperature: low (0.3) for reference matching, higher (0.75) for creative generation
        temperature = 0.3 if has_exact_colors else 0.75

        if reference_image_url:
            # Build image message manually so we can control temperature
            image_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": reference_image_url}},
                    ],
                }
            ]
            result = await self.kimi.call(
                messages=image_messages,
                max_tokens=500, thinking=False, timeout=60.0,
                temperature=temperature, json_mode=True,
            )
        else:
            result = await self.kimi.call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500, thinking=False, timeout=60.0,
                temperature=temperature, top_p=0.95, json_mode=True,
            )

        if result.get("success"):
            try:
                theme = self._extract_json(result["content"])
                # Post-generation validation against reference
                if has_exact_colors:
                    theme = self._validate_theme_against_reference(theme, parsed_reference)
                result["parsed"] = theme
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[DataBinding] Theme JSON parse failed: {e}, using fallback")
                result["parsed"] = self._fallback_theme(style_preferences, reference_colors=parsed_reference)
        else:
            result["parsed"] = self._fallback_theme(style_preferences, reference_colors=parsed_reference)

        # === FINAL OVERRIDE: Force parsed reference colors into theme ===
        # Even after prompt instructions + validation, the AI may still deviate.
        # This guarantees exact color match as a last resort.
        if has_exact_colors and result.get("parsed"):
            theme = result["parsed"]
            color_fields = ["primary_color", "secondary_color", "accent_color",
                            "bg_color", "bg_alt_color", "text_color", "text_muted_color"]
            overridden = []
            for field in color_fields:
                if field in parsed_reference and parsed_reference[field]:
                    if theme.get(field) != parsed_reference[field]:
                        overridden.append(f"{field}: {theme.get(field)} -> {parsed_reference[field]}")
                    theme[field] = parsed_reference[field]
            # Derive bg_alt and text_muted if not in reference
            if "bg_alt_color" not in parsed_reference or not parsed_reference.get("bg_alt_color"):
                theme["bg_alt_color"] = self._derive_alt_bg(theme.get("bg_color", "#0F172A"))
            elif parsed_reference.get("bg_alt_color"):
                theme["bg_alt_color"] = parsed_reference["bg_alt_color"]
            if "text_muted_color" not in parsed_reference or not parsed_reference.get("text_muted_color"):
                theme["text_muted_color"] = self._derive_muted(theme.get("text_color", "#F1F5F9"), theme.get("bg_alt_color"))
            elif parsed_reference.get("text_muted_color"):
                theme["text_muted_color"] = parsed_reference["text_muted_color"]
            if overridden:
                logger.info(f"[DataBinding] Theme colors force-overridden from reference: {', '.join(overridden)}")
            result["parsed"] = theme

        # === CONSISTENCY GUARD: dark bg must not have light bg_alt ===
        # Catches edge cases where AI or derivation produces mismatched tones.
        if result.get("parsed"):
            theme = result["parsed"]
            bg_l = self._hex_lightness(theme.get("bg_color", "#FFFFFF"))
            alt_l = self._hex_lightness(theme.get("bg_alt_color", "#F8FAFC"))
            if bg_l < 20 and alt_l > 40:
                # Dark bg but light alt — force re-derive
                logger.warning(
                    f"[DataBinding] Consistency fix: bg_color L={bg_l} is dark but bg_alt_color L={alt_l} is light. Re-deriving."
                )
                theme["bg_alt_color"] = self._derive_alt_bg(theme["bg_color"])
            elif bg_l > 80 and alt_l < 40:
                # Light bg but dark alt — force re-derive
                logger.warning(
                    f"[DataBinding] Consistency fix: bg_color L={bg_l} is light but bg_alt_color L={alt_l} is dark. Re-deriving."
                )
                theme["bg_alt_color"] = self._derive_alt_bg(theme["bg_color"])
            result["parsed"] = theme

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
        reference_analysis: Optional[str] = None,
        photo_urls: Optional[List[str]] = None,
        template_style_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Kimi returns JSON with all text content for every section."""
        contact_str = ""
        if contact_info:
            contact_str = "CONTACT INFO: " + ", ".join(f"{k}: {v}" for k, v in contact_info.items())

        sections_str = ", ".join(sections)

        # Inject reference analysis mood/tone guidance for text generation
        reference_tone_hint = ""
        if reference_analysis:
            reference_tone_hint = f"""

=== REFERENCE SITE STYLE (match this tone in your copy) ===
The user provided a reference website. Match its communication tone and style:
{reference_analysis[:800]}
If the reference is bold/edgy, write bold/edgy copy. If elegant, write elegant copy. Do NOT default to generic corporate tone.
=== END REFERENCE ===
"""

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

        # === USER PHOTOS CONTEXT ===
        # Let AI know user has uploaded photos so it can write content that complements them
        photo_hint = ""
        if photo_urls and len(photo_urls) > 0:
            photo_hint = f"""

=== USER-UPLOADED PHOTOS ({len(photo_urls)} images provided) ===
The user has uploaded {len(photo_urls)} photo(s) of their business. These will be placed in the site automatically.
Write copy that WORKS WITH real photos: reference visual elements, create captions that complement imagery.
Avoid generic placeholder descriptions. The site will feature REAL business photos, so texts should feel authentic and grounded.
=== END PHOTOS CONTEXT ===
"""

        # === DYNAMIC SECTION SCHEMA ASSEMBLY ===
        # Only include JSON schemas for the sections the user actually requested.
        # This cuts prompt size by 40-60% and reduces noise for the LLM.
        section_schemas = []
        for section in sections:
            if section in _SECTION_SCHEMAS:
                section_schemas.append(_SECTION_SCHEMAS[section])
        sections_json = ",\n  ".join(section_schemas)

        # Build structure rules only for sections that have array constraints
        structure_rule_parts = []
        rule_num = 1
        for section in sections:
            if section in _SECTION_ARRAY_RULES:
                structure_rule_parts.append(f"{rule_num}. {_SECTION_ARRAY_RULES[section]}")
                rule_num += 1
        structure_rule_parts.append(f"{rule_num}. EVERY array must contain REAL, SUBSTANTIAL content. NO empty strings. Each description must be at least 15 words.")
        rule_num += 1
        structure_rule_parts.append(f'{rule_num}. DO NOT use short key names like "ICON", "TITLE", "DESCRIPTION" — always use the FULL prefixed key name as shown above.')
        structure_rules = "=== CRITICAL JSON STRUCTURE RULES (violating these = BROKEN website) ===\n" + "\n".join(structure_rule_parts) if structure_rule_parts else ""

        # === FEW-SHOT EXAMPLES & CATEGORY TONE ===
        category = _get_category_from_style_id(template_style_id)
        few_shot_block = _build_few_shot_block(category)

        # === STYLE-SPECIFIC TONE (overrides broad category tone) ===
        style_tone_block = _get_style_tone(template_style_id)

        # === DIVERSITY: inject creative direction seed for unique copy ===
        texts_diversity_block = ""
        if variety_context:
            from app.services.generation_tracker import generate_creative_seed
            recently_used = variety_context.get("_recently_used")
            seed = generate_creative_seed(category, recently_used)
            texts_diversity_block = f"""
=== CREATIVE DIRECTION (make this copy UNIQUE) ===
{seed['creative_direction']}
Write copy that fits this creative vision. Every section should feel like it belongs to THIS specific site, not a template.
=== END CREATIVE DIRECTION ===
"""

        prompt = f"""You are Italy's most awarded copywriter — think Oliviero Toscani meets Apple. You write text for websites that win design awards.
Return ONLY valid JSON, no markdown.
{reference_tone_hint}{knowledge_hint}{reference_hint}{photo_hint}{texts_diversity_block}
=== ABSOLUTE BANNED PHRASES (using ANY of these = automatic failure) ===
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
- "Scopri di piu" / "Per saperne di piu"
- Any text that could appear on ANY other business website. Be SPECIFIC to THIS business.

{few_shot_block}

{style_tone_block}

BUSINESS: {business_name}
DESCRIPTION: {business_description[:2000]}
SECTIONS NEEDED: {sections_str}
{contact_str}

=== CREATIVE PERSONALITY (this defines the ENTIRE tone) ===
{variety_context["personality"]["directive"] if variety_context else random.choice(PERSONALITY_POOL)["directive"]}
Headline style: {variety_context["personality"]["headline_style"] if variety_context else "varied and surprising"}

=== COPYWRITING RULES ===
- Hero headline: MAX 6 words. Metaphors, contrasts, provocations. See examples above.
- Section headings: NEVER generic. Be SPECIFIC and evocative.
- Subtitles: 1-2 sentences. Create CURIOSITY and DESIRE.
- Service/feature descriptions: Lead with BENEFIT, not feature. Sensory language. Each UNIQUE in tone.
- Testimonials: REAL humans with specific details, emotions, before/after. Real Italian names (Nome Cognome).
- Stats: SPECIFIC non-round numbers ("847" not "800", "99.2%" not "100%").
- CTA buttons: action verb + urgency ("Inizia la Trasformazione" NOT "Contattaci").
- Vary rhythm: alternate short punchy with longer flowing. Create MUSIC in text.
- Icons: UNIQUE, RELEVANT emoji per service/feature. NEVER repeat in same section.
- TESTIMONIAL_INITIAL = first letter of TESTIMONIAL_AUTHOR name.

Return this JSON (include ONLY the sections listed in SECTIONS NEEDED):
{{
  "meta": {{
    "title": "Page title (max 60 chars)",
    "description": "Meta description (max 155 chars)",
    "og_title": "OG title",
    "og_description": "OG description"
  }},
  {sections_json}
}}

{structure_rules}

=== MINIMUM WORD COUNTS (MANDATORY) ===
- HERO_SUBTITLE: MIN 15 parole
- ABOUT_TEXT: MIN 40 parole
- SERVICE_DESCRIPTION / FEATURE_DESCRIPTION: MIN 12 parole ciascuna
- TESTIMONIAL_TEXT: MIN 20 parole ciascuna
- CTA_SUBTITLE: MIN 12 parole
- MEMBER_BIO: MIN 15 parole

FINAL CHECK:
- ALL text in Italian, hyper-specific to THIS business
- Hero title MAX 6 words, ZERO generic text anywhere
- NO banned phrases, all arrays 3+ items with FULL key names (SERVICE_ICON not ICON)
- COUNT WORDS: expand any text below minimum immediately
- Return ONLY the JSON object"""

        result = await self.kimi_text.call(
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
                retry_result = await self.kimi_text.call(
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
    # Step 2.5: Reflexion Self-Critique (Optional)
    # =========================================================
    async def _reflexion_review(
        self,
        texts: Dict[str, Any],
        sections: List[str],
    ) -> Dict[str, Any]:
        """
        Optional AI self-critique step that reviews generated texts for quality issues.
        Only runs if GENERATION_REFLEXION is enabled in config.

        Reviews for:
        - Banned generic phrases
        - Descriptions shorter than minimum word counts
        - Repeated sentence structures
        - Consistent personality tone

        Returns corrected texts if issues found, or original texts if clean.
        NEVER breaks the pipeline - always wrapped in try/except.
        """
        if not settings.GENERATION_REFLEXION:
            logger.debug("[DataBinding] Reflexion disabled (GENERATION_REFLEXION=False)")
            return texts

        try:
            logger.info("[DataBinding] Running reflexion self-critique...")

            # Build a concise review prompt
            sections_str = ", ".join(sections)
            texts_json = json.dumps(texts, ensure_ascii=False, indent=2)

            review_prompt = f"""You are a quality reviewer for website copy. Review this JSON for quality issues:

{texts_json}

CHECK FOR THESE ISSUES:

1. BANNED PHRASES (auto-fail if found):
   - "Benvenuti" / "Benvenuto"
   - "Siamo un'azienda" / "Siamo un team" / "Siamo leader"
   - "I nostri servizi" / "Cosa offriamo"
   - "Qualita e professionalita" / "Eccellenza e innovazione"
   - "Contattaci per maggiori informazioni"
   - "Il nostro team di esperti"
   - "Soluzioni su misura" / "Soluzioni personalizzate"
   - "A 360 gradi" / "Chiavi in mano"
   - Any generic corporate jargon

2. MINIMUM WORD COUNTS:
   - HERO_SUBTITLE: min 15 words
   - ABOUT_TEXT: min 40 words
   - SERVICE_DESCRIPTION / FEATURE_DESCRIPTION: min 12 words each
   - TESTIMONIAL_TEXT: min 20 words each
   - CTA_SUBTITLE: min 12 words
   - MEMBER_BIO: min 15 words

3. REPEATED STRUCTURES:
   - Check if services/features use the same sentence pattern repeatedly
   - Each description should have unique phrasing

4. PERSONALITY CONSISTENCY:
   - Does the tone feel consistent across all sections?
   - Is it generic corporate or does it have character?

If you find issues, return the CORRECTED JSON with fixes applied.
If the text is clean, return the EXACT SAME JSON unchanged.

Return ONLY the JSON object, no explanation."""

            result = await kimi_refine.call(
                messages=[{"role": "user", "content": review_prompt}],
                max_tokens=2000,
                thinking=False,
                timeout=30.0,
                temperature=0.3,
                json_mode=True,
            )

            if result.get("success"):
                try:
                    reviewed_texts = self._extract_json(result["content"])

                    # Basic sanity check: does reviewed JSON have the same sections?
                    original_sections = set(texts.keys())
                    reviewed_sections = set(reviewed_texts.keys())

                    if original_sections == reviewed_sections:
                        logger.info("[DataBinding] Reflexion review completed successfully")
                        return reviewed_texts
                    else:
                        logger.warning(
                            f"[DataBinding] Reflexion changed structure "
                            f"(original: {original_sections}, reviewed: {reviewed_sections}), "
                            f"using original texts"
                        )
                        return texts

                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"[DataBinding] Reflexion returned invalid JSON: {e}, using original texts")
                    return texts
            else:
                logger.warning(f"[DataBinding] Reflexion call failed: {result.get('error', 'unknown')}, using original texts")
                return texts

        except Exception as e:
            # Critical safety: NEVER break the pipeline
            logger.error(f"[DataBinding] Reflexion error (non-fatal): {e}", exc_info=True)
            return texts

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
        "team": "team-grid-01",
        "blog": "blog-editorial-grid-01",
        "awards": "awards-timeline-01",
        "listings": "listings-cards-01",
        "donations": "donations-progress-01",
        "comparison": "comparison-table-01",
        "booking": "booking-form-01",
        "app-download": "app-download-01",
        "social-proof": "social-bar-01",
        "schedule": "schedule-tabbed-multi-01",
    }

    # Layout style keywords mapped to variant name fragments for reference-influenced selection
    _LAYOUT_VARIANT_KEYWORDS: Dict[str, List[str]] = {
        "clean": ["clean", "minimal", "simple"],
        "dense": ["bento", "grid", "masonry", "cards"],
        "spacious": ["split", "full", "hero", "centered"],
        "asymmetric": ["bento", "creative", "split", "asymmetric"],
        "minimal": ["minimal", "clean", "simple"],
        "brutalist": ["bold", "creative", "brutalist"],
    }

    def _get_recent_component_usage(self, category: str, limit: int = 10) -> Dict[str, int]:
        """Query recent generation logs to count component usage frequency.

        Returns {variant_id: usage_count} for the last `limit` generations
        in the same category. Used to penalize overused components.
        Tries PostgreSQL first, falls back to SQLite tracker.
        Never breaks the pipeline — returns empty dict on any error.
        """
        # Try PostgreSQL first (production)
        try:
            from app.core.database import SessionLocal
            from app.models.generation_log import GenerationLog
            db = SessionLocal()
            try:
                recent = (
                    db.query(GenerationLog)
                    .filter(GenerationLog.category == category)
                    .order_by(GenerationLog.created_at.desc())
                    .limit(limit)
                    .all()
                )
                counts: Dict[str, int] = {}
                for log in recent:
                    if log.components_used:
                        for variant_id in log.components_used.values():
                            counts[variant_id] = counts.get(variant_id, 0) + 1
                if counts:
                    return counts
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"[DataBinding] PostgreSQL diversity query failed, trying SQLite: {e}")

        # Fallback to SQLite tracker (always available, no DB setup needed)
        try:
            recently_used = get_recently_used(category=category, limit=limit)
            component_usage = recently_used.get("components", {})
            # Flatten {section: {variant: count}} -> {variant: count}
            flat: Dict[str, int] = {}
            for section_data in component_usage.values():
                for variant_id, count in section_data.items():
                    flat[variant_id] = flat.get(variant_id, 0) + count
            return flat
        except Exception as e:
            logger.debug(f"[DataBinding] SQLite diversity query also failed (non-fatal): {e}")
            return {}

    def _diversity_weighted_choice(
        self, pool: List[str], usage_counts: Dict[str, int], max_count: int = 10
    ) -> str:
        """Pick from pool with diversity weighting — less-used variants are preferred.

        Each variant gets weight = max_count + 1 - usage_count (minimum 1).
        This means a variant used 0 times has ~10x the chance of one used 10 times.
        """
        if not pool:
            return ""
        weights = []
        for v in pool:
            count = usage_counts.get(v, 0)
            weight = max(1, max_count + 1 - count)
            weights.append(weight)
        # random.choices returns a list
        return random.choices(pool, weights=weights, k=1)[0]

    @staticmethod
    def _compute_layout_hash(selections: Dict[str, str]) -> str:
        """Compute a deterministic hash from the component selection.

        Sorts by section name so the hash is order-independent.
        Used to detect duplicate layouts across generations.
        """
        import hashlib
        sorted_items = sorted(selections.items())
        key = "|".join(f"{s}={v}" for s, v in sorted_items)
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def _log_generation(
        self, category: str, template_style_id: str,
        selections: Dict[str, str], theme_summary: Optional[Dict[str, str]] = None,
        variety_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a generation to both PostgreSQL and SQLite tracker for diversity tracking.

        Stores the layout_hash, component selections, and variety choices.
        Never breaks the pipeline.
        """
        layout_hash = self._compute_layout_hash(selections)

        # Always log to SQLite tracker (lightweight, always available)
        try:
            theme = theme_summary or {}
            variety = variety_context or {}
            personality = variety.get("personality", {})
            color_mood = variety.get("color_mood", {})
            font_pair = variety.get("font_pairing", {})
            record_generation(
                category=category,
                style_id=template_style_id,
                color_primary=theme.get("primary_color", ""),
                color_mood=color_mood.get("mood", ""),
                font_heading=font_pair.get("heading", theme.get("font_heading", "")),
                font_body=font_pair.get("body", theme.get("font_body", "")),
                personality=personality.get("name", ""),
                components=selections,
                layout_hash=layout_hash,
                theme=theme,
            )
            # Periodic cleanup (keep last 200)
            cleanup_old_records(200)
        except Exception as e:
            logger.debug(f"[DataBinding] SQLite tracker logging failed (non-fatal): {e}")

        # Also log to PostgreSQL (production, if available)
        try:
            from app.core.database import SessionLocal
            from app.models.generation_log import GenerationLog
            db = SessionLocal()
            try:
                log = GenerationLog(
                    category=category,
                    style_mood=template_style_id,
                    color_primary=(theme_summary or {}).get("primary_color", ""),
                    components_used=selections,
                    layout_hash=layout_hash,
                )
                db.add(log)
                db.commit()
                logger.info(f"[DataBinding] Logged generation: hash={layout_hash}, style={template_style_id}")
            except Exception as e:
                db.rollback()
                if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                    logger.debug(f"[DataBinding] Duplicate layout hash (expected): {e}")
                else:
                    logger.warning(f"[DataBinding] Generation log insert failed: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"[DataBinding] PostgreSQL logging failed (non-fatal): {e}")

    def _select_components_deterministic(
        self,
        template_style_id: str,
        sections: List[str],
        parsed_reference: Optional[Dict[str, Any]] = None,
        harmony_keywords: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Select component variants with diversity-weighted randomization.

        For each section, picks from STYLE_VARIANT_POOL with a preference for
        less-recently-used variants. Falls back to fixed map, then defaults.

        Diversity system:
        - Queries last 10 generations for the same category
        - Weights each variant inversely by recent usage count
        - After selection, computes layout_hash and logs to DB
        - If exact same layout was generated before, re-rolls up to 3 times

        When harmony_keywords is provided, prefer variants matching the harmony group.
        When parsed_reference contains layout_style, prefer matching variants.
        """
        pool_map = STYLE_VARIANT_POOL.get(template_style_id, {})
        fixed_map = STYLE_VARIANT_MAP.get(template_style_id, {})
        available = self.assembler.get_variant_ids()

        # Get recent usage for diversity weighting
        category = _get_category_from_style_id(template_style_id)
        usage_counts = self._get_recent_component_usage(category)

        # Try up to 3 times to get a unique layout
        max_attempts = 3 if usage_counts else 1
        for attempt in range(max_attempts):
            selections = {}

            for section in sections:
                # Priority 1: Randomized pool for this style + section
                pool = pool_map.get(section, [])
                if pool:
                    # If reference layout matches, prefer matching variants
                    ref_layout = (parsed_reference or {}).get("layout_style", "").lower().strip()
                    ref_keywords = self._LAYOUT_VARIANT_KEYWORDS.get(ref_layout, [])
                    if ref_keywords:
                        matching = [v for v in pool if any(kw in v.lower() for kw in ref_keywords)]
                        if matching:
                            selections[section] = self._diversity_weighted_choice(matching, usage_counts)
                            continue

                    # If harmony group set, prefer variants matching the harmony keywords
                    if harmony_keywords:
                        harmonious = [
                            v for v in pool
                            if any(kw in v.lower() for kw in harmony_keywords)
                        ]
                        if harmonious:
                            selections[section] = self._diversity_weighted_choice(harmonious, usage_counts)
                            continue

                    selections[section] = self._diversity_weighted_choice(pool, usage_counts)
                # Priority 2: Build ad-hoc pool from ALL available variants for this section
                elif section in available:
                    all_variants = available[section]
                    if all_variants:
                        selections[section] = self._diversity_weighted_choice(all_variants, usage_counts)
                    elif section in fixed_map:
                        selections[section] = fixed_map[section]
                # Priority 3: Randomized pool for default section types (faq, pricing, etc.)
                elif section in _DEFAULT_SECTION_VARIANT_POOLS:
                    pool = _DEFAULT_SECTION_VARIANT_POOLS[section]
                    selections[section] = self._diversity_weighted_choice(pool, usage_counts)
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

            # Select nav style (not a section, handled separately by assembler)
            nav_pool = pool_map.get("nav", [])
            if nav_pool:
                selections["nav"] = self._diversity_weighted_choice(nav_pool, usage_counts)
            elif "nav" in fixed_map:
                selections["nav"] = fixed_map["nav"]

            # Check for duplicate layout (try PostgreSQL, fallback to SQLite tracker)
            layout_hash = self._compute_layout_hash(selections)
            if attempt < max_attempts - 1:
                is_duplicate = False
                # Try PostgreSQL
                try:
                    from app.core.database import SessionLocal
                    from app.models.generation_log import GenerationLog
                    db = SessionLocal()
                    try:
                        existing = db.query(GenerationLog).filter(
                            GenerationLog.layout_hash == layout_hash
                        ).first()
                        is_duplicate = existing is not None
                    finally:
                        db.close()
                except Exception:
                    # Fallback to SQLite tracker
                    try:
                        recently_used = get_recently_used(category=category, limit=20)
                        is_duplicate = layout_hash in recently_used.get("layout_hashes", set())
                    except Exception:
                        pass
                if is_duplicate:
                    logger.info(f"[DataBinding] Layout hash collision on attempt {attempt + 1}, re-rolling...")
                    continue  # Try again
            break  # No collision or last attempt

        logger.info(f"[DataBinding] Diversity selection for '{template_style_id}': {selections}")
        return selections

    async def _select_components(
        self,
        business_description: str,
        sections: List[str],
        style_mood: str,
        template_style_id: Optional[str] = None,
        parsed_reference: Optional[Dict[str, Any]] = None,
        harmony_keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Select component variants. Uses deterministic map if template_style_id is provided,
        otherwise falls back to Kimi AI selection."""

        # If we have a template_style_id with a mapping, use deterministic selection
        if template_style_id and template_style_id in STYLE_VARIANT_MAP:
            selections = self._select_components_deterministic(
                template_style_id, sections, parsed_reference,
                harmony_keywords=harmony_keywords,
            )
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
        reference_urls: Optional[List[str]] = None,
        hero_type: Optional[str] = None,
        hero_video_url: Optional[str] = None,
        user_id: Optional[int] = None,
        site_id: Optional[int] = None,
        generate_images: bool = False,
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
                    reference_analysis=reference_analysis,
                    logo_url=logo_url,
                    contact_info=contact_info,
                    on_progress=on_progress,
                    photo_urls=photo_urls,
                    template_style_id=template_style_id,
                    reference_urls=reference_urls,
                    hero_type=hero_type,
                    hero_video_url=hero_video_url,
                    user_id=user_id,
                    site_id=site_id,
                    generate_images=generate_images,
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
        reference_analysis: Optional[str] = None,
        logo_url: Optional[str] = None,
        contact_info: Optional[Dict[str, str]] = None,
        on_progress: ProgressCallback = None,
        photo_urls: Optional[List[str]] = None,
        template_style_id: Optional[str] = None,
        reference_urls: Optional[List[str]] = None,
        hero_type: Optional[str] = None,
        hero_video_url: Optional[str] = None,
        user_id: Optional[int] = None,
        site_id: Optional[int] = None,
        generate_images: bool = False,
    ) -> Dict[str, Any]:
        start_time = time.time()
        total_tokens_in = 0
        total_tokens_out = 0

        # Sanitize input
        business_name, business_description, sections = sanitize_input(
            business_name, business_description, sections
        )

        # === BLUEPRINT ORDERING: reorder sections by category narrative flow ===
        sections = self._apply_blueprint_ordering(sections, template_style_id)

        # === HARMONY GROUP: pick a visual family for cross-section cohesion ===
        pool_map = STYLE_VARIANT_POOL.get(template_style_id, {}) if template_style_id else {}
        harmony_keywords = self._pick_harmony_group(template_style_id, pool_map)

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
            # Priority 1: Use dedicated reference_urls field
            urls_to_analyze = []
            if reference_urls:
                urls_to_analyze = [u for u in reference_urls if u.startswith(("http://", "https://"))][:3]
            # Priority 2: Fallback to regex extraction from description
            if not urls_to_analyze:
                url_match = re.search(r'Siti di riferimento:\s*(https?://\S+)', business_description)
                if url_match:
                    urls_to_analyze = [url_match.group(1).strip()]

            for ref_url in urls_to_analyze:
                try:
                    analysis = await analyze_reference_url(ref_url)
                    if analysis:
                        ctx = format_analysis_for_prompt(analysis)
                        reference_url_context += ctx + "\n"
                        logger.info(f"[DataBinding] Analyzed reference URL: {ref_url}")
                except Exception as e:
                    logger.warning(f"[DataBinding] URL analysis failed for {ref_url}: {e}")

        # === ANALYZE REFERENCE IMAGE (if provided but not yet analyzed) ===
        parsed_reference = {}
        if reference_image_url and not reference_analysis:
            try:
                if on_progress:
                    on_progress(1, "Analisi immagine di riferimento...")
                logger.info(f"[DataBinding] Analyzing reference image: {reference_image_url[:80]}...")
                analysis_result = await self.kimi.call_with_image(
                    prompt="""Analyze this website screenshot and extract the EXACT visual design system.

You MUST return EXACTLY this format (one field per line, no other text):

PRIMARY_COLOR: #hexcode (the main brand/accent color)
SECONDARY_COLOR: #hexcode (supporting color)
ACCENT_COLOR: #hexcode (highlights, CTAs)
BG_COLOR: #hexcode (main background color)
BG_ALT_COLOR: #hexcode (alternate section background)
TEXT_COLOR: #hexcode (main text color)
TEXT_MUTED_COLOR: #hexcode (secondary/muted text)
IS_DARK_THEME: true/false
TYPOGRAPHY_STYLE: brutalist|elegant|minimal|modern|corporate|playful
FONT_WEIGHT: bold|normal|light
LAYOUT_STYLE: clean|dense|spacious|asymmetric
MOOD: one word
DESIGN_NOTES: one sentence about distinctive visual elements

RULES:
- Extract EXACT hex codes by sampling the dominant colors you see. Be precise.
- For dark sites (black/navy background), BG_COLOR must be dark (#000000-#1a1a2e range).
- For light sites, BG_COLOR must be light (#f5f5f5-#ffffff range).
- PRIMARY_COLOR is the most prominent brand color (e.g. neon green, electric blue).
- Do NOT guess or approximate. Report what you actually see in the image.""",
                    image_url=reference_image_url,
                    max_tokens=500,
                    thinking=False,
                    timeout=60.0,
                    temperature=0.3,
                )
                if analysis_result.get("success") and analysis_result.get("content"):
                    reference_analysis = analysis_result["content"]
                    parsed_reference = _parse_reference_analysis(reference_analysis)
                    logger.info(f"[DataBinding] Reference image analyzed: {len(reference_analysis)} chars, "
                                f"parsed {len(parsed_reference)} fields: {parsed_reference}")
                    # Prepend explicit hex summary for downstream consumers
                    if parsed_reference.get("primary_color"):
                        hex_summary = "\n".join(
                            f"EXTRACTED_{k.upper()}: {v}"
                            for k, v in parsed_reference.items()
                            if k.endswith("_color") and isinstance(v, str) and v.startswith("#")
                        )
                        if hex_summary:
                            reference_analysis = f"=== EXTRACTED HEX COLORS (use these exactly) ===\n{hex_summary}\n=== END EXTRACTED ===\n\n{reference_analysis}"
                else:
                    logger.warning(f"[DataBinding] Reference image analysis failed: {analysis_result.get('error', 'unknown')}")
                    if on_progress:
                        on_progress(1, "Analisi riferimento fallita, continuo con stile predefinito...", {
                            "phase": "reference_failed",
                            "warning": "L'immagine di riferimento non e' stata analizzata correttamente. I colori potrebbero non corrispondere.",
                        })
            except Exception as e:
                logger.warning(f"[DataBinding] Reference image analysis error: {e}")
                if on_progress:
                    on_progress(1, "Analisi riferimento fallita, continuo con stile predefinito...", {
                        "phase": "reference_failed",
                        "warning": str(e)[:100],
                    })
        elif reference_analysis:
            # If reference_analysis was passed in already, parse it too
            parsed_reference = _parse_reference_analysis(reference_analysis)

        # === SITE PLANNER: Consult quality guide + usage tracker for smart planning ===
        planning_context = ""
        try:
            from app.services.site_planner import site_planner
            category = _get_category_from_style_id(template_style_id)
            site_plan = await site_planner.create_plan(
                business_name=business_name,
                business_description=business_description,
                category=category,
                sections=sections,
                style_id=template_style_id,
                primary_color=(style_preferences or {}).get("primary_color"),
                logo_url=logo_url,
                contact_info=contact_info,
            )
            planning_context = site_plan.get("planning_prompt", "")
            # If planner resolved better sections order, use it
            if site_plan.get("sections"):
                sections = site_plan["sections"]
            logger.info(
                "[DataBinding] SitePlanner: quality_score=%.1f, %d sections, %d missing_info, context=%d chars",
                site_plan.get("quality_score", 0),
                len(site_plan.get("sections", [])),
                len(site_plan.get("missing_info", [])),
                len(planning_context),
            )
        except Exception as e:
            logger.warning("[DataBinding] SitePlanner failed (non-blocking): %s", e)

        # === PICK VARIETY CONTEXT (anti-repetition personality, color mood, font pairing) ===
        variety = _pick_variety_context(category=_get_category_from_style_id(template_style_id))
        # When user specified colors, disable color_mood to avoid contradictions
        user_has_colors = bool(style_preferences and style_preferences.get("primary_color"))
        if user_has_colors:
            variety["color_mood"] = {}  # Nullify — user colors take priority over random mood
            logger.info(
                f"[DataBinding] Variety: personality={variety['personality']['name']}, "
                f"color_mood=DISABLED (user specified colors), "
                f"font={variety['font_pairing']['heading']}/{variety['font_pairing']['body']}"
            )
        else:
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

        # Merge planning context into creative context for AI prompts
        enriched_context = creative_context
        if planning_context:
            enriched_context = f"{creative_context}\n\n{planning_context}" if creative_context else planning_context

        theme_task = self._generate_theme(
            business_name, business_description,
            style_preferences, reference_image_url,
            creative_context=enriched_context,
            reference_url_context=reference_url_context,
            variety_context=variety,
            reference_analysis=reference_analysis,
            parsed_reference=parsed_reference,
            photo_urls=photo_urls,
            template_style_id=template_style_id,
        )
        texts_task = self._generate_texts(
            business_name, business_description,
            sections, contact_info,
            creative_context=enriched_context,
            reference_url_context=reference_url_context,
            variety_context=variety,
            reference_analysis=reference_analysis,
            photo_urls=photo_urls,
            template_style_id=template_style_id,
        )
        theme_result, texts_result = await asyncio.gather(theme_task, texts_task)

        # Extract results (use reference colors in fallback if available)
        theme = theme_result.get("parsed", self._fallback_theme(style_preferences, reference_colors=parsed_reference))

        # === FORCE-OVERRIDE: User-specified colors ALWAYS win ===
        # This runs AFTER AI generation. Reference image colors (parsed_reference)
        # were already forced inside _generate_theme(), so skip when reference exists.
        has_exact_ref = bool(parsed_reference and parsed_reference.get("primary_color"))
        if style_preferences and not has_exact_ref:
            overridden_fields = []
            if style_preferences.get("primary_color"):
                old_val = theme.get("primary_color")
                theme["primary_color"] = style_preferences["primary_color"]
                if old_val != style_preferences["primary_color"]:
                    overridden_fields.append(f"primary: {old_val} -> {style_preferences['primary_color']}")
            if style_preferences.get("secondary_color"):
                old_val = theme.get("secondary_color")
                theme["secondary_color"] = style_preferences["secondary_color"]
                if old_val != style_preferences["secondary_color"]:
                    overridden_fields.append(f"secondary: {old_val} -> {style_preferences['secondary_color']}")
            if overridden_fields:
                logger.info(f"[DataBinding] User color force-override: {', '.join(overridden_fields)}")
                # Recalculate derived colors for harmony with forced primary/secondary
                theme["accent_color"] = self._derive_accent(
                    theme.get("primary_color", "#3b82f6"),
                    theme.get("bg_color", "#FAF7F2"),
                )
                theme["bg_alt_color"] = self._derive_alt_bg(theme.get("bg_color", "#FAF7F2"))
                theme["text_muted_color"] = self._derive_muted(theme.get("text_color", "#1A1A2E"), theme.get("bg_alt_color"))
                logger.info(
                    f"[DataBinding] Recalculated harmony: accent={theme['accent_color']}, "
                    f"bg_alt={theme['bg_alt_color']}, text_muted={theme['text_muted_color']}"
                )

        if not texts_result.get("success") or not texts_result.get("parsed"):
            logger.warning(f"[DataBinding] AI texts failed, using fallback: {texts_result.get('error', 'unknown')}")
            texts = self._fallback_texts(business_name, sections)
        else:
            texts = texts_result["parsed"]

        # === OPTIONAL REFLEXION: Self-critique and quality improvement ===
        texts = await self._reflexion_review(texts, sections)

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
            generate_images
            and _has_image_generation
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
            # Global timeout: 90s max for the entire image generation step
            selection_coro = self._select_components(
                business_description, sections, mood,
                template_style_id=template_style_id,
                parsed_reference=parsed_reference,
                harmony_keywords=harmony_keywords,
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
            try:
                selection_result, generated_images = await asyncio.wait_for(
                    asyncio.gather(selection_coro, images_coro),
                    timeout=90.0,
                )
            except asyncio.TimeoutError:
                logger.warning("[DataBinding] Image generation timed out (90s), using placeholders")
                # Run component selection alone (should be fast)
                selection_result = await self._select_components(
                    business_description, sections, mood,
                    template_style_id=template_style_id,
                    parsed_reference=parsed_reference,
                    harmony_keywords=harmony_keywords,
                )
                generated_images = {}

            # Replace placeholder URLs in texts with generated images
            total_ai_images = sum(
                1 for urls in generated_images.values()
                for u in urls if not (u.startswith("data:image/svg+xml,") or "placehold.co" in u)
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
                parsed_reference=parsed_reference,
                harmony_keywords=harmony_keywords,
            )

        selections = selection_result.get("parsed", self._default_selections(
            sections, self.assembler.get_variant_ids()
        ))

        # Override hero variant if user selected video hero
        if hero_type == "video" and "hero" in selections:
            selections["hero"] = "hero-video-bg-01"
            logger.info("[DataBinding] Hero override: using hero-video-bg-01 (user selected video)")

        if selection_result.get("success"):
            total_tokens_in += selection_result.get("tokens_input", 0)
            total_tokens_out += selection_result.get("tokens_output", 0)

        # Log generation for diversity tracking (non-blocking)
        category = _get_category_from_style_id(template_style_id)
        self._log_generation(
            category, template_style_id or "", selections,
            theme_summary=theme, variety_context=variety,
        )

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
            template_style_id=template_style_id,
        )

        # Inject YouTube video embed into hero if user selected video hero
        if hero_type == "video" and hero_video_url:
            video_embed = self._build_youtube_embed(hero_video_url)
            if video_embed:
                for comp in site_data.get("components", []):
                    if comp.get("variant_id") == "hero-video-bg-01":
                        comp["data"]["HERO_VIDEO_EMBED"] = video_embed
                        logger.info(f"[DataBinding] Injected YouTube video embed into hero")
                        break

        # === Interactive Photo Choice Flow ===
        # Scan for placeholder images and offer user a choice:
        # upload their own photo or use stock photos.
        photo_choices = self._scan_placeholder_photos(site_data, template_style_id)

        if photo_choices and site_id and on_progress:
            # Register an asyncio.Event so the API endpoint can signal us
            choice_event = asyncio.Event()
            _pending_photo_choices[site_id] = {
                "event": choice_event,
                "choices": None,  # Will be set by the API endpoint
                "site_data": site_data,
                "template_style_id": template_style_id,
            }

            # Send photo choices to frontend via progress callback
            on_progress(5, "Scelta foto...", {
                "phase": "photo_choices",
                "choices": photo_choices,
            })

            # Wait for user response (or timeout after 5 minutes)
            try:
                await asyncio.wait_for(choice_event.wait(), timeout=PHOTO_CHOICE_TIMEOUT)
                user_choices = _pending_photo_choices.get(site_id, {}).get("choices")
                if user_choices:
                    logger.info("[DataBinding] Applying %d user photo choices", len(user_choices))
                    site_data = self.apply_photo_choices(site_data, user_choices, template_style_id)
                else:
                    # Event was set but no choices provided — fallback to stock
                    logger.info("[DataBinding] Photo choice event set but no choices, using stock photos")
                    site_data = self._inject_stock_photos(site_data, template_style_id)
            except asyncio.TimeoutError:
                logger.info("[DataBinding] Photo choice timeout (%ds), auto-injecting stock photos", PHOTO_CHOICE_TIMEOUT)
                site_data = self._inject_stock_photos(site_data, template_style_id)
            finally:
                # Clean up the pending entry
                _pending_photo_choices.pop(site_id, None)
        else:
            # No placeholders found or no site_id — use stock photos directly
            site_data = self._inject_stock_photos(site_data, template_style_id)

        # Inject user-uploaded photos (override stock/placeholder photos)
        # Only runs if user provided photos at generation start (not via photo choice flow)
        if photo_urls:
            site_data = self._inject_user_photos(site_data, photo_urls)

        # Query recent effects for diversification (before assembly)
        _effect_db = None
        if user_id:
            try:
                from app.services.effect_diversifier import get_recent_effects
                from app.core.database import SessionLocal
                _effect_db = SessionLocal()
                recent = get_recent_effects(_effect_db, user_id=user_id, limit=5)
                site_data["_recent_effects"] = recent
            except Exception as e:
                logger.warning(f"[DataBinding] Could not fetch recent effects: {e}")
                site_data["_recent_effects"] = []

        try:
            html_content = self.assembler.assemble(site_data)
            html_content = sanitize_output(html_content, is_template_assembled=True)
            # Post-process: randomize GSAP animations for per-site uniqueness
            html_content = _randomize_animations(html_content)
            # Post-process: remove empty sections (better no section than blank space)
            html_content = self._post_process_html(html_content)
        except Exception as e:
            logger.exception("[DataBinding] Assembly failed")
            if _effect_db:
                _effect_db.close()
            return {"success": False, "error": f"Errore assemblaggio: {str(e)}"}

        # Save effect usage to DB (after assembly)
        if user_id and _effect_db:
            try:
                from app.services.effect_diversifier import save_effect_usage
                effects_used = getattr(self.assembler, '_last_effects_used', {})
                if effects_used:
                    from app.models.effect_usage import EffectUsage
                    usage = EffectUsage(
                        user_id=user_id,
                        site_id=site_id,
                        template_style=template_style_id,
                        effects_json=effects_used,
                    )
                    _effect_db.add(usage)
                    _effect_db.commit()
                    logger.info(f"[DataBinding] Saved effect usage for user {user_id}")
            except Exception as e:
                logger.warning(f"[DataBinding] Could not save effect usage: {e}")
                try:
                    _effect_db.rollback()
                except Exception:
                    pass
            finally:
                _effect_db.close()
                _effect_db = None
        elif _effect_db:
            _effect_db.close()

        if on_progress:
            on_progress(6, "Sito assemblato, controllo qualita'...", {
                "phase": "assembled",
            })

        # === Pre-Delivery Check (fast, deterministic) ===
        try:
            from app.services.pre_delivery_check import pre_delivery_check
            pdc_report = pre_delivery_check.check(
                html=html_content,
                requested_sections=sections,
            )
            if pdc_report.fixes_applied:
                html_content = pdc_report.html_fixed
                logger.info(
                    "[DataBinding] PreDeliveryCheck: score=%.1f, %d fix(es) applied, %d issue(s)",
                    pdc_report.score, len(pdc_report.fixes_applied), len(pdc_report.issues),
                )
            elif pdc_report.issues:
                logger.info(
                    "[DataBinding] PreDeliveryCheck: score=%.1f, %d issue(s), no auto-fixes needed",
                    pdc_report.score, len(pdc_report.issues),
                )
        except Exception as e:
            logger.warning("[DataBinding] PreDeliveryCheck failed (non-blocking): %s", e)

        # === Record generation in UsageTracker ===
        try:
            from app.services.usage_tracker import usage_tracker
            import uuid
            gen_id = f"{site_id or 'anon'}-{uuid.uuid4().hex[:8]}"
            usage_tracker.record_generation(
                generation_id=gen_id,
                category=category,
                style=template_style_id or "",
                components_dict=selections,
            )
        except Exception as e:
            logger.warning("[DataBinding] UsageTracker record failed (non-blocking): %s", e)

        # === Quality Control ===
        qc_report_data = None
        try:
            qc_report = await qc_pipeline.run_full_qc(
                html=html_content,
                theme_config=theme,
                requested_sections=sections,
                style_id=template_style_id or "custom-free",
                on_progress=on_progress,
                variant_selections=selections,
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
                on_progress(7, status_msg, {
                    "phase": "complete",
                    "qc_score": qc_report.final_score,
                    "qc_passed": qc_report.passed,
                })
        except Exception as e:
            logger.warning(f"[DataBinding] QC pipeline failed (non-blocking): {e}")
            # QC failure is non-blocking: return the original HTML
            if on_progress:
                on_progress(7, "Il tuo sito e' pronto!", {
                    "phase": "complete",
                })

        generation_time = int((time.time() - start_time) * 1000)

        # Calculate cost per-model for accuracy (text generation may use a different model)
        text_tok_in = texts_result.get("tokens_input", 0) if texts_result.get("success") else 0
        text_tok_out = texts_result.get("tokens_output", 0) if texts_result.get("success") else 0
        other_tok_in = total_tokens_in - text_tok_in
        other_tok_out = total_tokens_out - text_tok_out
        cost = (
            self.kimi.calculate_cost(other_tok_in, other_tok_out)
            + self.kimi_text.calculate_cost(text_tok_in, text_tok_out)
        )

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
            "pipeline_steps": 7,
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
        template_style_id: Optional[str] = None,
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
            "nav_style": selections.get("nav", "nav-classic-01"),
            "style_id": template_style_id or "",
            "per_style_css": _build_per_style_css(template_style_id) if template_style_id else "",
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
                "PEXELS_API_KEY": os.getenv("PEXELS_API_KEY", ""),
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

        if section == "hero":
            # Ensure HERO_IMAGE_URL has a placeholder so stock/AI image injection can find and replace it
            if "HERO_IMAGE_URL" not in data or not data["HERO_IMAGE_URL"]:
                data["HERO_IMAGE_URL"] = _svg_placeholder(1200, 800, business_name)
            if "HERO_IMAGE_ALT" not in data or not data["HERO_IMAGE_ALT"]:
                data["HERO_IMAGE_ALT"] = business_name

        elif section == "services":
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
                data["ABOUT_IMAGE_URL"] = _svg_placeholder(800, 600, business_name, bg_color="#3b82f6", text_color="#ffffff")
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
            url = gallery_photos[i % len(gallery_photos)] if gallery_photos else _svg_placeholder(600, 400, f"Foto {i+1}", bg_color="#eeeeee", text_color="#999999")
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

    @staticmethod
    def _build_youtube_embed(video_url: str) -> Optional[str]:
        """Convert a YouTube URL to a fullscreen background iframe embed."""
        import re as _re
        match = _re.search(r'(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})', video_url)
        if not match:
            return None
        video_id = match.group(1)
        return (
            f'<iframe src="https://www.youtube.com/embed/{video_id}'
            f'?autoplay=1&mute=1&loop=1&playlist={video_id}'
            f'&controls=0&showinfo=0&rel=0&modestbranding=1&playsinline=1"'
            f' class="absolute inset-0 w-full h-full pointer-events-none"'
            f' style="transform: scale(1.2);"'
            f' frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>'
        )

    @staticmethod
    def _is_placeholder_url(url: str) -> bool:
        """Check if a URL is a placeholder, empty, or missing — needs replacement."""
        if not url or not isinstance(url, str):
            return True
        url = url.strip()
        if not url:
            return True
        # Known placeholder patterns
        if "placehold.co" in url or url.startswith("data:image/svg+xml,"):
            return True
        # Template placeholders that weren't replaced
        if url.startswith("{{") or url == "#" or url == "placeholder" or url == "placeholder.jpg":
            return True
        return False

    def _inject_stock_photos(self, site_data: Dict[str, Any], template_style_id: Optional[str] = None) -> Dict[str, Any]:
        """Replace placeholder images with high-quality Unsplash stock photos.

        Handles: hero, about (+ numbered _2 through _10), gallery, team,
        blog posts, services, listings, and logos.
        Runs ALWAYS as a safety net — real URLs are never overwritten.
        """
        photos = _get_stock_photos(template_style_id or "default")

        hero_pool = photos.get("hero", [])
        gallery_pool = photos.get("gallery", [])
        about_pool = photos.get("about", [])
        team_pool = photos.get("team", [])
        replaced_count = 0

        for component in site_data.get("components", []):
            data = component.get("data", {})

            # Hero image
            if self._is_placeholder_url(str(data.get("HERO_IMAGE_URL", ""))):
                if hero_pool:
                    data["HERO_IMAGE_URL"] = hero_pool[0]
                    replaced_count += 1

            # About image (primary)
            if self._is_placeholder_url(str(data.get("ABOUT_IMAGE_URL", ""))):
                if about_pool:
                    data["ABOUT_IMAGE_URL"] = about_pool[0]
                    replaced_count += 1

            # About numbered images (ABOUT_IMAGE_URL_2 through _10)
            # New components from ThemeForest may use multiple about images
            for n in range(2, 11):
                key = f"ABOUT_IMAGE_URL_{n}"
                if key in data and self._is_placeholder_url(str(data.get(key, ""))):
                    pool = gallery_pool if gallery_pool else about_pool
                    if pool:
                        data[key] = pool[(n - 1) % len(pool)]
                        replaced_count += 1

            # Gallery images
            gallery_items = data.get("GALLERY_ITEMS", [])
            if isinstance(gallery_items, list):
                for i, item in enumerate(gallery_items):
                    if isinstance(item, dict) and self._is_placeholder_url(str(item.get("GALLERY_IMAGE_URL", ""))):
                        if gallery_pool:
                            item["GALLERY_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]
                            replaced_count += 1

            # Team member images
            team_members = data.get("TEAM_MEMBERS", [])
            if isinstance(team_members, list):
                for i, member in enumerate(team_members):
                    if isinstance(member, dict) and self._is_placeholder_url(str(member.get("MEMBER_IMAGE_URL", ""))):
                        if team_pool:
                            member["MEMBER_IMAGE_URL"] = team_pool[i % len(team_pool)]
                            replaced_count += 1

            # Blog post images
            blog_posts = data.get("BLOG_POSTS", [])
            if isinstance(blog_posts, list):
                for i, post in enumerate(blog_posts):
                    if isinstance(post, dict) and self._is_placeholder_url(str(post.get("POST_IMAGE_URL", ""))):
                        if gallery_pool:
                            post["POST_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]
                            replaced_count += 1

            # Service images (some service components use images)
            service_items = data.get("SERVICE_ITEMS", [])
            if isinstance(service_items, list):
                for i, svc in enumerate(service_items):
                    if isinstance(svc, dict) and self._is_placeholder_url(str(svc.get("SERVICE_IMAGE_URL", ""))):
                        if gallery_pool:
                            svc["SERVICE_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]
                            replaced_count += 1

            # Listing images
            listing_items = data.get("LISTING_ITEMS", [])
            if isinstance(listing_items, list):
                for i, item in enumerate(listing_items):
                    if isinstance(item, dict) and self._is_placeholder_url(str(item.get("LISTING_IMAGE_URL", ""))):
                        if gallery_pool:
                            item["LISTING_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]
                            replaced_count += 1

            # Donation images
            donation_items = data.get("DONATION_ITEMS", [])
            if isinstance(donation_items, list):
                for i, item in enumerate(donation_items):
                    if isinstance(item, dict) and self._is_placeholder_url(str(item.get("DONATION_IMAGE_URL", ""))):
                        if gallery_pool:
                            item["DONATION_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]
                            replaced_count += 1

            # App download image
            if self._is_placeholder_url(str(data.get("APP_IMAGE_URL", ""))):
                if hero_pool:
                    data["APP_IMAGE_URL"] = hero_pool[0]
                    replaced_count += 1

            # Logo partner images - use inline SVG placeholders instead of grey boxes
            logos_items = data.get("LOGOS_ITEMS", [])
            if isinstance(logos_items, list):
                for i, logo in enumerate(logos_items):
                    if isinstance(logo, dict) and self._is_placeholder_url(str(logo.get("LOGO_IMAGE_URL", ""))):
                        name = logo.get("LOGO_NAME", f"Partner {i+1}")
                        logo["LOGO_IMAGE_URL"] = _svg_placeholder(160, 60, name, bg_color="#f8fafc", text_color="#64748b")
                        replaced_count += 1

        logger.info(f"[DataBinding] Stock photo injection: {replaced_count} images replaced (category: {template_style_id or 'default'})")
        return site_data

    def _inject_user_photos(self, site_data: Dict[str, Any], photo_urls: List[str]) -> Dict[str, Any]:
        """Replace placeholder URLs with user-uploaded photos in site_data."""
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

    def _scan_placeholder_photos(
        self,
        site_data: Dict[str, Any],
        template_style_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Scan site_data components for placeholder images and build a photo_choices list.

        Returns a list of dicts, one per section needing a photo:
        {
            "section_type": "hero",
            "section_label": "Sezione Hero (immagine principale)",
            "placeholder_key": "HERO_IMAGE_URL",
            "stock_preview_url": "https://images.unsplash.com/...",
            "current_url": "data:image/svg+xml,...",
        }
        """
        from app.services.site_questioner import SiteQuestioner

        photos = _get_stock_photos(template_style_id or "default")
        choices: List[Dict[str, Any]] = []
        seen_sections: set = set()

        for component in site_data.get("components", []):
            data = component.get("data", {})
            variant_id = component.get("variant_id", "")

            # Detect section type from variant_id (e.g. "hero-classic-01" -> "hero")
            section_type = variant_id.split("-")[0] if variant_id else ""

            # Hero image
            hero_url = str(data.get("HERO_IMAGE_URL", ""))
            if self._is_placeholder_url(hero_url) and "hero" not in seen_sections:
                hero_pool = photos.get("hero", [])
                choices.append({
                    "section_type": "hero",
                    "section_label": SiteQuestioner.get_photo_choice_label("hero"),
                    "placeholder_key": "HERO_IMAGE_URL",
                    "stock_preview_url": hero_pool[0] if hero_pool else "",
                    "current_url": hero_url,
                })
                seen_sections.add("hero")

            # About image
            about_url = str(data.get("ABOUT_IMAGE_URL", ""))
            if self._is_placeholder_url(about_url) and "about" not in seen_sections:
                about_pool = photos.get("about", [])
                choices.append({
                    "section_type": "about",
                    "section_label": SiteQuestioner.get_photo_choice_label("about"),
                    "placeholder_key": "ABOUT_IMAGE_URL",
                    "stock_preview_url": about_pool[0] if about_pool else "",
                    "current_url": about_url,
                })
                seen_sections.add("about")

            # Gallery — check if any gallery items have placeholders
            gallery_items = data.get("GALLERY_ITEMS", [])
            if isinstance(gallery_items, list) and "gallery" not in seen_sections:
                has_placeholder = any(
                    isinstance(item, dict) and self._is_placeholder_url(str(item.get("GALLERY_IMAGE_URL", "")))
                    for item in gallery_items
                )
                if has_placeholder:
                    gallery_pool = photos.get("gallery", [])
                    choices.append({
                        "section_type": "gallery",
                        "section_label": SiteQuestioner.get_photo_choice_label("gallery"),
                        "placeholder_key": "GALLERY_IMAGE_URL",
                        "stock_preview_url": gallery_pool[0] if gallery_pool else "",
                        "current_url": "",
                    })
                    seen_sections.add("gallery")

            # Team members
            team_members = data.get("TEAM_MEMBERS", [])
            if isinstance(team_members, list) and "team" not in seen_sections:
                has_placeholder = any(
                    isinstance(m, dict) and self._is_placeholder_url(str(m.get("MEMBER_IMAGE_URL", "")))
                    for m in team_members
                )
                if has_placeholder:
                    team_pool = photos.get("team", [])
                    choices.append({
                        "section_type": "team",
                        "section_label": SiteQuestioner.get_photo_choice_label("team"),
                        "placeholder_key": "MEMBER_IMAGE_URL",
                        "stock_preview_url": team_pool[0] if team_pool else "",
                        "current_url": "",
                    })
                    seen_sections.add("team")

            # Services
            service_items = data.get("SERVICE_ITEMS", [])
            if isinstance(service_items, list) and "services" not in seen_sections:
                has_placeholder = any(
                    isinstance(s, dict) and self._is_placeholder_url(str(s.get("SERVICE_IMAGE_URL", "")))
                    for s in service_items
                )
                if has_placeholder:
                    gallery_pool = photos.get("gallery", [])
                    choices.append({
                        "section_type": "services",
                        "section_label": SiteQuestioner.get_photo_choice_label("services"),
                        "placeholder_key": "SERVICE_IMAGE_URL",
                        "stock_preview_url": gallery_pool[0] if gallery_pool else "",
                        "current_url": "",
                    })
                    seen_sections.add("services")

            # Blog posts
            blog_posts = data.get("BLOG_POSTS", [])
            if isinstance(blog_posts, list) and "blog" not in seen_sections:
                has_placeholder = any(
                    isinstance(p, dict) and self._is_placeholder_url(str(p.get("POST_IMAGE_URL", "")))
                    for p in blog_posts
                )
                if has_placeholder:
                    gallery_pool = photos.get("gallery", [])
                    choices.append({
                        "section_type": "blog",
                        "section_label": SiteQuestioner.get_photo_choice_label("blog"),
                        "placeholder_key": "POST_IMAGE_URL",
                        "stock_preview_url": gallery_pool[0] if gallery_pool else "",
                        "current_url": "",
                    })
                    seen_sections.add("blog")

        logger.info(
            "[DataBinding] Photo scan: %d sections need photos: %s",
            len(choices),
            [c["section_type"] for c in choices],
        )
        return choices

    def apply_photo_choices(
        self,
        site_data: Dict[str, Any],
        choices: List[Dict[str, Any]],
        template_style_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Apply user photo choices to site_data.

        Each choice dict has:
        - section_type: "hero", "about", "gallery", etc.
        - action: "stock" | "upload"
        - photo_url: URL of the uploaded photo (only for action="upload")

        For "stock" actions, injects stock photos for that section only.
        For "upload" actions, injects the user-provided photo_url.
        Sections not in the choices list are left with their current (placeholder) URLs.
        """
        if not choices:
            return site_data

        photos = _get_stock_photos(template_style_id or "default")

        # Build a lookup: section_type -> choice
        choice_map: Dict[str, Dict[str, Any]] = {}
        for choice in choices:
            section_type = choice.get("section_type", "")
            if section_type:
                choice_map[section_type] = choice

        for component in site_data.get("components", []):
            data = component.get("data", {})

            # Hero
            if "hero" in choice_map and self._is_placeholder_url(str(data.get("HERO_IMAGE_URL", ""))):
                c = choice_map["hero"]
                if c.get("action") == "upload" and c.get("photo_url"):
                    data["HERO_IMAGE_URL"] = c["photo_url"]
                elif c.get("action") == "stock":
                    hero_pool = photos.get("hero", [])
                    if hero_pool:
                        data["HERO_IMAGE_URL"] = hero_pool[0]

            # About
            if "about" in choice_map and self._is_placeholder_url(str(data.get("ABOUT_IMAGE_URL", ""))):
                c = choice_map["about"]
                if c.get("action") == "upload" and c.get("photo_url"):
                    data["ABOUT_IMAGE_URL"] = c["photo_url"]
                elif c.get("action") == "stock":
                    about_pool = photos.get("about", [])
                    if about_pool:
                        data["ABOUT_IMAGE_URL"] = about_pool[0]

            # Gallery
            gallery_items = data.get("GALLERY_ITEMS", [])
            if "gallery" in choice_map and isinstance(gallery_items, list):
                c = choice_map["gallery"]
                if c.get("action") == "upload" and c.get("photo_url"):
                    # Single upload: apply to first placeholder gallery item
                    photo_url = c["photo_url"]
                    photo_urls_list = c.get("photo_urls", [photo_url]) if isinstance(c.get("photo_urls"), list) else [photo_url]
                    for i, item in enumerate(gallery_items):
                        if isinstance(item, dict) and self._is_placeholder_url(str(item.get("GALLERY_IMAGE_URL", ""))):
                            if i < len(photo_urls_list):
                                item["GALLERY_IMAGE_URL"] = photo_urls_list[i]
                            elif photo_urls_list:
                                item["GALLERY_IMAGE_URL"] = photo_urls_list[i % len(photo_urls_list)]
                elif c.get("action") == "stock":
                    gallery_pool = photos.get("gallery", [])
                    for i, item in enumerate(gallery_items):
                        if isinstance(item, dict) and self._is_placeholder_url(str(item.get("GALLERY_IMAGE_URL", ""))):
                            if gallery_pool:
                                item["GALLERY_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]

            # Team
            team_members = data.get("TEAM_MEMBERS", [])
            if "team" in choice_map and isinstance(team_members, list):
                c = choice_map["team"]
                if c.get("action") == "upload" and c.get("photo_url"):
                    photo_urls_list = c.get("photo_urls", [c["photo_url"]]) if isinstance(c.get("photo_urls"), list) else [c["photo_url"]]
                    for i, member in enumerate(team_members):
                        if isinstance(member, dict) and self._is_placeholder_url(str(member.get("MEMBER_IMAGE_URL", ""))):
                            if i < len(photo_urls_list):
                                member["MEMBER_IMAGE_URL"] = photo_urls_list[i]
                elif c.get("action") == "stock":
                    team_pool = photos.get("team", [])
                    for i, member in enumerate(team_members):
                        if isinstance(member, dict) and self._is_placeholder_url(str(member.get("MEMBER_IMAGE_URL", ""))):
                            if team_pool:
                                member["MEMBER_IMAGE_URL"] = team_pool[i % len(team_pool)]

            # Services
            service_items = data.get("SERVICE_ITEMS", [])
            if "services" in choice_map and isinstance(service_items, list):
                c = choice_map["services"]
                gallery_pool = photos.get("gallery", [])
                if c.get("action") == "upload" and c.get("photo_url"):
                    photo_urls_list = c.get("photo_urls", [c["photo_url"]]) if isinstance(c.get("photo_urls"), list) else [c["photo_url"]]
                    for i, svc in enumerate(service_items):
                        if isinstance(svc, dict) and self._is_placeholder_url(str(svc.get("SERVICE_IMAGE_URL", ""))):
                            if i < len(photo_urls_list):
                                svc["SERVICE_IMAGE_URL"] = photo_urls_list[i]
                elif c.get("action") == "stock":
                    for i, svc in enumerate(service_items):
                        if isinstance(svc, dict) and self._is_placeholder_url(str(svc.get("SERVICE_IMAGE_URL", ""))):
                            if gallery_pool:
                                svc["SERVICE_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]

            # Blog
            blog_posts = data.get("BLOG_POSTS", [])
            if "blog" in choice_map and isinstance(blog_posts, list):
                c = choice_map["blog"]
                gallery_pool = photos.get("gallery", [])
                if c.get("action") == "upload" and c.get("photo_url"):
                    photo_urls_list = c.get("photo_urls", [c["photo_url"]]) if isinstance(c.get("photo_urls"), list) else [c["photo_url"]]
                    for i, post in enumerate(blog_posts):
                        if isinstance(post, dict) and self._is_placeholder_url(str(post.get("POST_IMAGE_URL", ""))):
                            if i < len(photo_urls_list):
                                post["POST_IMAGE_URL"] = photo_urls_list[i]
                elif c.get("action") == "stock":
                    for i, post in enumerate(blog_posts):
                        if isinstance(post, dict) and self._is_placeholder_url(str(post.get("POST_IMAGE_URL", ""))):
                            if gallery_pool:
                                post["POST_IMAGE_URL"] = gallery_pool[i % len(gallery_pool)]

        logger.info(
            "[DataBinding] Applied photo choices for %d sections",
            len(choice_map),
        )
        return site_data

    def _inject_ai_images(
        self,
        texts: Dict[str, Any],
        generated_images: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Replace placehold.co URLs in texts dict with AI-generated image URLs.

        Only replaces placeholder URLs (inline SVG data URIs or legacy placehold.co)
        so user-uploaded photos are not affected here.
        """
        def _is_placeholder(url: str) -> bool:
            return isinstance(url, str) and ("placehold.co" in url or url.startswith("data:image/svg+xml,"))

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
                "HERO_IMAGE_URL": _svg_placeholder(800, 600, business_name, bg_color="#3b82f6", text_color="#ffffff"),
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

    def _fallback_theme(self, style_preferences=None, reference_colors: Optional[Dict] = None) -> Dict[str, str]:
        """Default theme if Kimi theme generation fails. Uses reference colors if available, else random pool."""
        if reference_colors and reference_colors.get("primary_color"):
            # Build fallback from reference colors - never use random palette
            typo_style = reference_colors.get("typography_style", "")
            is_dark = reference_colors.get("is_dark", False)
            return {
                "primary_color": reference_colors["primary_color"],
                "secondary_color": reference_colors.get("secondary_color", reference_colors["primary_color"]),
                "accent_color": reference_colors.get("accent_color", reference_colors["primary_color"]),
                "bg_color": reference_colors.get("bg_color", "#0F172A" if is_dark else "#FAF7F2"),
                "bg_alt_color": self._derive_alt_bg(reference_colors.get("bg_color", "#0F172A" if is_dark else "#FAF7F2")),
                "text_color": reference_colors.get("text_color", "#F1F5F9" if is_dark else "#1A1A2E"),
                "text_muted_color": self._derive_muted(
                    reference_colors.get("text_color", "#F1F5F9" if is_dark else "#1A1A2E"),
                    self._derive_alt_bg(reference_colors.get("bg_color", "#0F172A" if is_dark else "#FAF7F2")),
                ),
                "font_heading": "Space Grotesk",
                "font_heading_url": "Space+Grotesk:wght@400;600;700;800",
                "font_body": "DM Sans",
                "font_body_url": "DM+Sans:wght@400;500;600",
                "border_radius_style": "sharp" if typo_style == "brutalist" else "soft",
                "shadow_style": "none" if is_dark else "soft",
                "spacing_density": "normal",
            }
        theme = random.choice(FALLBACK_THEME_POOL).copy()
        if style_preferences:
            if style_preferences.get("primary_color"):
                theme["primary_color"] = style_preferences["primary_color"]
            if style_preferences.get("secondary_color"):
                theme["secondary_color"] = style_preferences["secondary_color"]
            # Recalculate derived colors if user overrode primary or secondary
            if style_preferences.get("primary_color") or style_preferences.get("secondary_color"):
                theme["accent_color"] = self._derive_accent(
                    theme["primary_color"], theme.get("bg_color", "#FAF7F2")
                )
                theme["bg_alt_color"] = self._derive_alt_bg(theme.get("bg_color", "#FAF7F2"))
                theme["text_muted_color"] = self._derive_muted(theme.get("text_color", "#1A1A2E"), theme.get("bg_alt_color"))
        return theme

    @staticmethod
    def _hex_to_hsl(hex_color: str) -> tuple:
        """Convert hex color to HSL (h: 0-360, s: 0-100, l: 0-100)."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
        max_c, min_c = max(r, g, b), min(r, g, b)
        l = (max_c + min_c) / 2
        if max_c == min_c:
            h = s = 0.0
        else:
            d = max_c - min_c
            s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            if max_c == r:
                h = (g - b) / d + (6 if g < b else 0)
            elif max_c == g:
                h = (b - r) / d + 2
            else:
                h = (r - g) / d + 4
            h /= 6
        return round(h * 360), round(s * 100), round(l * 100)

    @staticmethod
    def _hsl_to_hex(h: int, s: int, l: int) -> str:
        """Convert HSL (h: 0-360, s: 0-100, l: 0-100) to hex color."""
        h, s, l = h / 360, s / 100, l / 100
        if s == 0:
            r = g = b = l
        else:
            def hue2rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue2rgb(p, q, h + 1/3)
            g = hue2rgb(p, q, h)
            b = hue2rgb(p, q, h - 1/3)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    def _hex_lightness(self, hex_color: str) -> int:
        """Get lightness (0-100) from a hex color."""
        try:
            return self._hex_to_hsl(hex_color)[2]
        except (ValueError, IndexError):
            return 50

    def _derive_alt_bg(self, bg_hex: str) -> str:
        """Derive an alternate background color by shifting lightness.

        Uses a smaller shift for very dark or very light backgrounds to keep
        the alt color tonally consistent (e.g. dark bg -> still-dark alt).
        """
        try:
            h, s, l = self._hex_to_hsl(bg_hex)
            # Adaptive shift: small for extremes, larger for mid-range
            if l < 15:
                shift = 6  # very dark: subtle lift (e.g. #000 -> ~#101010)
            elif l < 50:
                shift = 10  # dark: moderate lift
            elif l > 90:
                shift = 6  # very light: subtle dip
            else:
                shift = 10  # light: moderate dip
            new_l = min(100, l + shift) if l < 50 else max(0, l - shift)
            return self._hsl_to_hex(h, s, new_l)
        except (ValueError, IndexError):
            return bg_hex

    @staticmethod
    def _relative_luminance(hex_color: str) -> float:
        """Calculate WCAG relative luminance from hex color."""
        hex_color = hex_color.strip().lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
        r = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def _contrast_ratio(self, hex1: str, hex2: str) -> float:
        """WCAG contrast ratio between two hex colors. Returns 1.0-21.0."""
        l1 = self._relative_luminance(hex1)
        l2 = self._relative_luminance(hex2)
        lighter, darker = max(l1, l2), min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    def _derive_muted(self, text_hex: str, bg_alt_hex: str = None) -> str:
        """Derive a muted text color, ensuring WCAG AA contrast against bg_alt."""
        try:
            h, s, l = self._hex_to_hsl(text_hex)
            # Move lightness 40% toward middle (50)
            new_l = l + int((50 - l) * 0.4)
            # Reduce saturation slightly
            new_s = max(0, s - 15)
            muted = self._hsl_to_hex(h, new_s, new_l)
            # If bg_alt provided, ensure WCAG AA contrast (4.5:1)
            if bg_alt_hex:
                ratio = self._contrast_ratio(muted, bg_alt_hex)
                if ratio < 4.5:
                    bg_l = self._hex_to_hsl(bg_alt_hex)[2]
                    direction = 1 if bg_l < 50 else -1
                    for _ in range(30):
                        new_l = min(100, max(0, new_l + direction * 3))
                        muted = self._hsl_to_hex(h, new_s, new_l)
                        if self._contrast_ratio(muted, bg_alt_hex) >= 4.5:
                            break
            return muted
        except (ValueError, IndexError):
            return "#6B7280"

    def _derive_accent(self, primary_hex: str, bg_hex: str) -> str:
        """Derive a complementary accent color from primary that pops against bg.

        Uses split-complementary logic: shifts hue by ~150 degrees from primary,
        keeps high saturation, and adjusts lightness to contrast with background.
        """
        try:
            h, s, l = self._hex_to_hsl(primary_hex)
            bg_l = self._hex_lightness(bg_hex)
            # Split-complementary: 150 degree hue shift
            accent_h = (h + 150) % 360
            # Keep saturation high for a vibrant accent
            accent_s = max(60, min(90, s + 10))
            # Lightness: contrast with background
            if bg_l > 50:
                accent_l = max(35, min(55, l))  # Darker accent on light bg
            else:
                accent_l = max(50, min(70, l + 15))  # Brighter accent on dark bg
            return self._hsl_to_hex(accent_h, accent_s, accent_l)
        except (ValueError, IndexError):
            return "#F59E0B"  # Safe fallback: amber

    def _validate_theme_against_reference(self, theme: Dict[str, str], reference_colors: Dict[str, Any]) -> Dict[str, str]:
        """Post-generation validation: force-correct theme if it deviates from reference."""
        if not reference_colors:
            return theme

        # Force-correct dark/light mismatch
        ref_is_dark = reference_colors.get("is_dark", False)
        theme_bg_lightness = self._hex_lightness(theme.get("bg_color", "#FFFFFF"))

        if ref_is_dark and theme_bg_lightness > 40:
            # Reference is dark but theme bg is light - force correct
            logger.warning(f"[DataBinding] Theme bg_color {theme.get('bg_color')} is light but reference is dark. Forcing reference colors.")
            theme["bg_color"] = reference_colors.get("bg_color", "#0F172A")
            theme["bg_alt_color"] = self._derive_alt_bg(theme["bg_color"])
            theme["text_color"] = reference_colors.get("text_color", "#F1F5F9")
            theme["text_muted_color"] = self._derive_muted(theme["text_color"], theme["bg_alt_color"])
        elif not ref_is_dark and theme_bg_lightness < 40:
            # Reference is light but theme bg is dark - force correct
            logger.warning(f"[DataBinding] Theme bg_color {theme.get('bg_color')} is dark but reference is light. Forcing reference colors.")
            theme["bg_color"] = reference_colors.get("bg_color", "#FAF7F2")
            theme["bg_alt_color"] = self._derive_alt_bg(theme["bg_color"])
            theme["text_color"] = reference_colors.get("text_color", "#1A1A2E")
            theme["text_muted_color"] = self._derive_muted(theme["text_color"], theme["bg_alt_color"])

        # Force-correct primary/accent if they differ significantly from reference
        ref_primary = reference_colors.get("primary_color")
        if ref_primary and theme.get("primary_color") != ref_primary:
            logger.info(f"[DataBinding] Forcing primary_color from {theme.get('primary_color')} to {ref_primary}")
            theme["primary_color"] = ref_primary

        ref_accent = reference_colors.get("accent_color")
        if ref_accent and theme.get("accent_color") != ref_accent:
            theme["accent_color"] = ref_accent

        ref_secondary = reference_colors.get("secondary_color")
        if ref_secondary and theme.get("secondary_color") != ref_secondary:
            theme["secondary_color"] = ref_secondary

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


def submit_photo_choices(site_id: int, choices: List[Dict[str, Any]]) -> bool:
    """Submit user photo choices for an in-progress generation.

    Called by the API endpoint. Stores the choices and signals the
    asyncio.Event so the pipeline can resume.

    Returns True if choices were accepted, False if no pending generation found.
    """
    pending = _pending_photo_choices.get(site_id)
    if not pending:
        logger.warning("[DataBinding] No pending photo choice for site_id=%d", site_id)
        return False

    pending["choices"] = choices
    pending["event"].set()
    logger.info("[DataBinding] Photo choices submitted for site_id=%d (%d choices)", site_id, len(choices))
    return True


def get_pending_photo_choices(site_id: int) -> Optional[List[Dict[str, Any]]]:
    """Check if a generation is waiting for photo choices.

    Returns the photo_choices list if waiting, None otherwise.
    """
    pending = _pending_photo_choices.get(site_id)
    if pending and not pending["event"].is_set():
        return pending.get("scan_choices")
    return None
