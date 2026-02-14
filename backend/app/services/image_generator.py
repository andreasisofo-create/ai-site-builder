"""
Image Generation Service - Flux via fal.ai

Generates contextual AI images for site sections using Flux models:
- fal-ai/flux/schnell: Fast generation (~2s), good quality, $0.025/img
- fal-ai/flux-pro/v1.1-ultra: Premium quality, $0.04/img

Each section type gets tailored prompts based on business context,
style mood, and color palette.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List, Callable

import fal_client

from app.core.config import settings

logger = logging.getLogger(__name__)

# fal_client authenticates via FAL_KEY env var.
# Sync from our config if not already set.
if settings.FAL_API_KEY and not os.environ.get("FAL_KEY"):
    os.environ["FAL_KEY"] = settings.FAL_API_KEY

# Type alias for progress callbacks: (percent, message)
ProgressCallback = Optional[Callable[[int, str], None]]

# ---------------------------------------------------------------------------
# Flux model endpoints
# ---------------------------------------------------------------------------
MODEL_FAST = "fal-ai/flux/schnell"          # ~2s, $0.025/img
MODEL_QUALITY = "fal-ai/flux-pro/v1.1-ultra"  # ~8s, $0.04/img

# ---------------------------------------------------------------------------
# Image size presets per section type (fal.ai size keys)
# ---------------------------------------------------------------------------
SECTION_IMAGE_SIZES: Dict[str, str] = {
    "hero": "landscape_16_9",
    "about": "landscape_16_9",
    "gallery": "landscape_4_3",
    "services": "landscape_4_3",
    "features": "landscape_4_3",
    "team": "square",
    "testimonials": "square",
    "portfolio": "landscape_4_3",
    "contact": "landscape_16_9",
    "cta": "landscape_16_9",
    "blog": "landscape_4_3",
    "event": "landscape_16_9",
}

# Default image counts per section
SECTION_IMAGE_COUNTS: Dict[str, int] = {
    "hero": 1,
    "about": 1,
    "gallery": 4,
    "services": 3,
    "features": 1,
    "team": 3,
    "testimonials": 3,
    "portfolio": 4,
    "contact": 1,
    "cta": 1,
    "blog": 3,
    "event": 1,
}

# Placeholder fallback URL pattern
PLACEHOLDER_URL = "https://placehold.co/{width}x{height}/1a1a2e/e0e0e0?text={text}"

PLACEHOLDER_DIMENSIONS: Dict[str, tuple] = {
    "landscape_16_9": (1280, 720),
    "landscape_4_3": (1024, 768),
    "square": (512, 512),
    "square_hd": (1024, 1024),
    "portrait_4_3": (768, 1024),
    "portrait_16_9": (720, 1280),
}


def _has_api_key() -> bool:
    """Check if fal.ai API key is configured."""
    return bool(os.environ.get("FAL_KEY") or settings.FAL_API_KEY)


# ---------------------------------------------------------------------------
# Prompt engineering
# ---------------------------------------------------------------------------

# Style mood -> photographic direction
MOOD_DIRECTIONS: Dict[str, str] = {
    "elegant": "warm ambient lighting, rich textures, sophisticated atmosphere, luxury feel",
    "modern": "clean minimalist aesthetic, sharp lines, contemporary design, bright natural light",
    "cozy": "warm golden tones, inviting atmosphere, soft natural lighting, comfortable setting",
    "dark": "moody dramatic lighting, deep shadows, high contrast, cinematic noir feel",
    "vibrant": "bold vivid colors, energetic composition, dynamic lighting, high saturation",
    "minimal": "whitespace, subtle tones, simple composition, soft diffused light",
    "creative": "artistic composition, expressive colors, unconventional angles, editorial style",
    "corporate": "professional setting, neutral tones, clean composition, business environment",
    "fresh": "bright airy feel, pastel accents, natural greenery, light and breezy atmosphere",
    "gradient": "smooth color transitions, modern tech aesthetic, neon accents, futuristic glow",
    "luxury": "opulent materials, gold accents, premium textures, dramatic studio lighting",
    "editorial": "magazine-quality composition, strong typography space, editorial layout feel",
}

# Section type -> base prompt templates
SECTION_PROMPTS: Dict[str, str] = {
    "hero": (
        "Professional cinematic photograph for a {business_type} website hero section. "
        "{business_context}. {mood_direction}. "
        "Wide establishing shot, stunning composition, 8k quality, ultra-detailed, "
        "professional commercial photography, shallow depth of field"
    ),
    "about": (
        "Professional photograph for an about section of a {business_type}. "
        "{business_context}. {mood_direction}. "
        "Authentic workspace or team environment, storytelling composition, "
        "natural lighting, editorial quality photography"
    ),
    "gallery": (
        "Professional photograph showcasing {business_type} work or products. "
        "{business_context}. {mood_direction}. "
        "Product photography, perfect lighting, high detail, commercial quality, "
        "clean background, studio-grade"
    ),
    "services": (
        "Professional photograph representing a service offered by a {business_type}. "
        "{business_context}. {mood_direction}. "
        "Clear subject, professional composition, relevant context, commercial photography"
    ),
    "features": (
        "Abstract professional visual representing technology and innovation for a {business_type}. "
        "{business_context}. {mood_direction}. "
        "Clean modern aesthetic, tech-forward, conceptual photography, sleek composition"
    ),
    "team": (
        "Professional headshot portrait for a team member at a {business_type}. "
        "Neutral blurred background, warm studio lighting, friendly confident expression, "
        "business casual attire, {mood_direction}. "
        "High-end portrait photography, sharp focus on face, bokeh background"
    ),
    "testimonials": (
        "Professional portrait of a satisfied client or customer. "
        "Neutral background, natural warm lighting, genuine smile, approachable look. "
        "{mood_direction}. Portrait photography, sharp focus"
    ),
    "portfolio": (
        "Stunning showcase photograph of creative work by a {business_type}. "
        "{business_context}. {mood_direction}. "
        "Portfolio-quality, perfect composition, editorial style, high detail"
    ),
    "contact": (
        "Professional welcoming environment photograph for a {business_type} contact page. "
        "{business_context}. {mood_direction}. "
        "Inviting atmosphere, warm tones, professional setting, wide angle"
    ),
    "cta": (
        "Inspiring motivational photograph for a {business_type} call-to-action section. "
        "{business_context}. {mood_direction}. "
        "Dynamic composition, aspirational feel, vibrant energy, commercial quality"
    ),
    "blog": (
        "Professional editorial photograph for a {business_type} blog post. "
        "{business_context}. {mood_direction}. "
        "Editorial photography, magazine quality, relevant subject matter"
    ),
    "event": (
        "Professional event photography for a {business_type}. "
        "{business_context}. {mood_direction}. "
        "Atmosphere capture, dynamic crowd or venue, professional event documentation"
    ),
}

# Business type keyword -> contextual hints
BUSINESS_CONTEXT_MAP: Dict[str, str] = {
    "ristorante": "beautifully plated Italian dishes, elegant table setting, warm restaurant interior",
    "restaurant": "beautifully plated dishes, elegant table setting, warm restaurant interior",
    "pizzeria": "wood-fired pizza, rustic Italian kitchen, fresh ingredients on display",
    "bar": "crafted cocktails, ambient bar lighting, modern lounge atmosphere",
    "cafe": "artisan coffee, cozy cafe interior, pastries and warm beverages",
    "hotel": "luxury hotel lobby, premium accommodation, sophisticated hospitality",
    "salon": "modern beauty salon interior, professional styling, elegant decor",
    "barbiere": "classic barbershop, precision grooming, vintage masculine aesthetic",
    "palestra": "modern gym equipment, fitness training, energetic workout environment",
    "gym": "modern gym equipment, fitness training, energetic workout environment",
    "studio": "creative design studio, artistic workspace, modern office environment",
    "agenzia": "professional agency office, collaborative workspace, modern business",
    "tech": "sleek technology devices, digital interfaces, modern tech workspace",
    "software": "code on screens, modern development environment, tech startup office",
    "ecommerce": "premium product display, clean shopping environment, lifestyle products",
    "negozio": "retail storefront, curated product display, welcoming shop interior",
    "immobiliare": "luxury property interior, modern architecture, real estate showcase",
    "wedding": "romantic wedding venue, floral arrangements, elegant celebration",
    "fotografo": "professional camera equipment, photography studio, creative workspace",
    "avvocato": "professional law office, legal library, sophisticated business setting",
    "dentista": "modern dental clinic, clean medical environment, professional healthcare",
    "medico": "modern medical office, clean healthcare facility, professional clinical setting",
    "architetto": "architectural models, modern design plans, creative blueprint workspace",
    "scuola": "modern classroom, educational environment, learning spaces",
    "musica": "musical instruments, recording studio, live performance stage",
}


def _detect_business_type(description: str) -> str:
    """Extract business type hint from description for better prompt context."""
    desc_lower = description.lower()
    for keyword, context in BUSINESS_CONTEXT_MAP.items():
        if keyword in desc_lower:
            return context
    return "professional business environment, high-quality commercial setting"


def _get_mood_direction(style_mood: str) -> str:
    """Get photographic direction from style mood."""
    mood_lower = style_mood.lower()
    for mood_key, direction in MOOD_DIRECTIONS.items():
        if mood_key in mood_lower:
            return direction
    return MOOD_DIRECTIONS.get("modern", "clean modern aesthetic, professional lighting")


def _build_color_hint(color_palette: Optional[Dict[str, str]]) -> str:
    """Build a subtle color hint from the palette."""
    if not color_palette:
        return ""
    primary = color_palette.get("primary_color", "")
    if not primary:
        return ""
    return f"Color mood inspired by {primary} tones"


def build_prompt(
    section_type: str,
    business_name: str,
    business_description: str,
    style_mood: str,
    color_palette: Optional[Dict[str, str]] = None,
    variant_index: int = 0,
) -> str:
    """
    Build an optimized image prompt for a given section.

    Args:
        section_type: hero, gallery, team, about, etc.
        business_name: Name of the business
        business_description: What the business does
        style_mood: Visual mood (elegant, modern, cozy, etc.)
        color_palette: Optional dict with primary_color, secondary_color, etc.
        variant_index: For multiple images in same section, shifts the prompt slightly

    Returns:
        Optimized prompt string
    """
    template = SECTION_PROMPTS.get(section_type, SECTION_PROMPTS["hero"])
    business_context = _detect_business_type(business_description)
    mood_direction = _get_mood_direction(style_mood)
    color_hint = _build_color_hint(color_palette)

    business_type = business_description[:80] if business_description else business_name

    prompt = template.format(
        business_type=business_type,
        business_context=business_context,
        mood_direction=mood_direction,
    )

    if color_hint:
        prompt += f". {color_hint}"

    # Add variation seed words for multiple images in same section
    if variant_index > 0:
        variations = [
            "different angle and perspective",
            "alternative composition and framing",
            "varied lighting and atmosphere",
            "unique viewpoint and arrangement",
        ]
        prompt += f". {variations[variant_index % len(variations)]}"

    # Universal quality suffix
    prompt += ". No text, no watermark, no logos, photorealistic"

    return prompt


def _get_placeholder(section_type: str, index: int = 0) -> str:
    """Generate a placehold.co fallback URL for a given section."""
    size_key = SECTION_IMAGE_SIZES.get(section_type, "landscape_4_3")
    w, h = PLACEHOLDER_DIMENSIONS.get(size_key, (1024, 768))
    label = f"{section_type}+{index + 1}"
    return PLACEHOLDER_URL.format(width=w, height=h, text=label)


# ---------------------------------------------------------------------------
# Core generation functions
# ---------------------------------------------------------------------------

async def generate_single_image(
    prompt: str,
    image_size: str = "landscape_4_3",
    quality: str = "fast",
    num_steps: int = 4,
) -> Optional[str]:
    """
    Generate a single image via fal.ai Flux.

    Args:
        prompt: The generation prompt
        image_size: fal.ai size key (landscape_16_9, landscape_4_3, square, etc.)
        quality: "fast" for schnell ($0.025), "quality" for pro ($0.04)
        num_steps: Inference steps (1-12 for schnell, higher for pro)

    Returns:
        Image URL string or None on failure
    """
    model = MODEL_QUALITY if quality == "quality" else MODEL_FAST

    arguments: Dict[str, Any] = {
        "prompt": prompt,
        "image_size": image_size,
        "num_inference_steps": num_steps,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "jpeg",
    }

    try:
        result = await fal_client.run_async(model, arguments=arguments)

        images = result.get("images", [])
        if images and len(images) > 0:
            url = images[0].get("url", "")
            if url:
                logger.info(f"Flux generated image: {url[:80]}...")
                return url

        logger.warning(f"Flux returned empty images for prompt: {prompt[:60]}...")
        return None

    except Exception as e:
        logger.error(f"Flux generation failed: {e}")
        return None


async def generate_section_images(
    business_name: str,
    business_description: str,
    section_type: str,
    style_mood: str,
    color_palette: Optional[Dict[str, str]] = None,
    count: int = 1,
    size: str = "auto",
    quality: str = "fast",
) -> List[str]:
    """
    Generate images for a specific site section.

    Args:
        business_name: Name of the business
        business_description: What the business does
        section_type: hero, gallery, team, about, services, etc.
        style_mood: Visual mood (elegant, modern, cozy, dark, etc.)
        color_palette: Optional {primary_color, secondary_color, ...}
        count: Number of images to generate
        size: fal.ai size key or "auto" to pick from SECTION_IMAGE_SIZES
        quality: "fast" (schnell $0.025) or "quality" (pro $0.04)

    Returns:
        List of image URLs. Falls back to placehold.co on failure.
    """
    if not _has_api_key():
        logger.warning("FAL_API_KEY not configured, returning placeholder images")
        return [_get_placeholder(section_type, i) for i in range(count)]

    if size == "auto":
        size = SECTION_IMAGE_SIZES.get(section_type, "landscape_4_3")

    # Build prompts for each image (with variation for multi-image sections)
    prompts = [
        build_prompt(
            section_type=section_type,
            business_name=business_name,
            business_description=business_description,
            style_mood=style_mood,
            color_palette=color_palette,
            variant_index=i,
        )
        for i in range(count)
    ]

    # Generate all images concurrently
    tasks = [
        generate_single_image(prompt=p, image_size=size, quality=quality)
        for p in prompts
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect URLs, replace failures with placeholders
    urls: List[str] = []
    for i, result in enumerate(results):
        if isinstance(result, str) and result:
            urls.append(result)
        else:
            if isinstance(result, Exception):
                logger.error(f"Image {i} for {section_type} failed: {result}")
            urls.append(_get_placeholder(section_type, i))

    return urls


async def generate_all_site_images(
    business_name: str,
    business_description: str,
    sections: List[str],
    style_mood: str,
    color_palette: Optional[Dict[str, str]] = None,
    user_photos: Optional[List[str]] = None,
    quality: str = "fast",
    progress_callback: ProgressCallback = None,
) -> Dict[str, List[str]]:
    """
    Generate images for all sections of a site.

    Args:
        business_name: Name of the business
        business_description: What the business does
        sections: List of section types (hero, about, gallery, etc.)
        style_mood: Visual mood
        color_palette: Optional color palette dict
        user_photos: Optional list of user-uploaded photo URLs to preserve
        quality: "fast" (schnell $0.025) or "quality" (pro $0.04)
        progress_callback: Optional (percent, message) callback

    Returns:
        Dict mapping section_type -> list of image URLs
        Example: {"hero": ["url1"], "gallery": ["url1", "url2", "url3", "url4"]}
    """
    if not _has_api_key():
        logger.warning("FAL_API_KEY not configured, returning all placeholders")
        result: Dict[str, List[str]] = {}
        for section in sections:
            count = SECTION_IMAGE_COUNTS.get(section, 1)
            result[section] = [_get_placeholder(section, i) for i in range(count)]
        return result

    total_sections = len(sections)
    all_images: Dict[str, List[str]] = {}

    for idx, section in enumerate(sections):
        count = SECTION_IMAGE_COUNTS.get(section, 1)

        if progress_callback:
            pct = int((idx / total_sections) * 100)
            progress_callback(pct, f"Generating {section} images...")

        logger.info(f"Generating {count} image(s) for section '{section}' [{idx+1}/{total_sections}]")

        urls = await generate_section_images(
            business_name=business_name,
            business_description=business_description,
            section_type=section,
            style_mood=style_mood,
            color_palette=color_palette,
            count=count,
            quality=quality,
        )

        all_images[section] = urls

    if progress_callback:
        progress_callback(100, "Image generation complete")

    total_generated = sum(len(v) for v in all_images.values())
    placeholder_count = sum(
        1 for urls in all_images.values() for u in urls if "placehold.co" in u
    )
    logger.info(
        f"Image generation complete: {total_generated} images, "
        f"{placeholder_count} placeholders"
    )

    return all_images


# ---------------------------------------------------------------------------
# Convenience: top-level wrapper
# ---------------------------------------------------------------------------

async def generate_images_for_site(
    business_name: str,
    business_description: str,
    sections: List[str],
    style_mood: str,
    color_palette: Optional[Dict[str, str]] = None,
    quality: str = "fast",
    progress_callback: ProgressCallback = None,
) -> Dict[str, List[str]]:
    """Top-level convenience wrapper for generate_all_site_images."""
    return await generate_all_site_images(
        business_name=business_name,
        business_description=business_description,
        sections=sections,
        style_mood=style_mood,
        color_palette=color_palette,
        quality=quality,
        progress_callback=progress_callback,
    )
