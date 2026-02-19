"""
Style DNA Service - Gemini 2.5 Pro
Analyzes logo + user inputs to extract visual DNA as structured JSON.
"""
import httpx
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

STYLE_DNA_PROMPT = """Sei un designer esperto in brand identity e web design.
Analizza questi input e restituisci SOLO un JSON valido, senza spiegazioni.

INPUT:
- Logo: [analizza l'immagine allegata]
- Colore primario: {color_hex}
- Categoria: {category}
- Descrizione: {description}

OUTPUT (JSON esatto, nessun testo extra):
{{
  "mood": "luxury|professional|creative|energetic|minimal|warm|tech",
  "density": "minimal|balanced|dense",
  "typography": "serif|sans|display|mixed",
  "color_palette": ["#hex1","#hex2","#hex3","#hex4","#hex5"],
  "variant_cluster": "V1|V2|V3|V4|V5",
  "sections_order": ["hero","servizi","galleria","testimonial","cta","contatti"],
  "animation_level": "subtle|moderate|dynamic",
  "has_video_bg": false,
  "typography_heading": "nome font Google consigliato",
  "typography_body": "nome font Google consigliato",
  "industry_tags": ["tag1","tag2"]
}}"""


async def extract_style_dna(
    category: str,
    color_primary: str,
    description: str,
    logo_base64: Optional[str] = None,
    logo_mime_type: str = "image/png"
) -> Dict[str, Any]:
    """Extract Style DNA using Gemini 2.5 Pro vision."""
    prompt_text = STYLE_DNA_PROMPT.format(
        color_hex=color_primary,
        category=category,
        description=description
    )

    # Build content parts
    parts = []
    if logo_base64:
        parts.append({
            "inline_data": {
                "mime_type": logo_mime_type,
                "data": logo_base64
            }
        })
    parts.append({"text": prompt_text})

    try:
        # Use OpenRouter if available, else direct Gemini API
        if settings.OPENROUTER_API_KEY:
            return await _call_openrouter(parts, prompt_text, logo_base64, logo_mime_type)
        elif settings.GEMINI_API_KEY:
            return await _call_gemini_direct(parts)
        else:
            logger.warning("No Gemini/OpenRouter API key, returning default DNA")
            return _default_dna(category)
    except httpx.HTTPStatusError as e:
        logger.error(f"Style DNA API HTTP error {e.response.status_code}: {e.response.text}")
        return _default_dna(category)
    except httpx.RequestError as e:
        logger.error(f"Style DNA API request error: {e}")
        return _default_dna(category)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Style DNA response parsing error: {e}")
        return _default_dna(category)


async def _call_gemini_direct(parts: list) -> Dict[str, Any]:
    """Call Gemini 2.5 Pro directly."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{GEMINI_URL}?key={settings.GEMINI_API_KEY}",
            json={
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1024
                }
            }
        )
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        # Parse JSON from response (strip markdown fences if present)
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)


async def _call_openrouter(parts, prompt_text, logo_base64, logo_mime_type) -> Dict[str, Any]:
    """Call Gemini via OpenRouter."""
    messages_content = []
    if logo_base64:
        messages_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{logo_mime_type};base64,{logo_base64}"}
        })
    messages_content.append({"type": "text", "text": prompt_text})

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.OPENROUTER_API_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": messages_content}],
                "temperature": 0.3,
                "max_tokens": 1024
            }
        )
        response.raise_for_status()
        data = response.json()
        text = data["choices"][0]["message"]["content"].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)


def dna_to_query_text(dna: Dict[str, Any], category: str) -> str:
    """Convert Style DNA JSON to text for embedding generation."""
    return f"""mood: {dna.get('mood', '')}
density: {dna.get('density', '')}
typography: {dna.get('typography', '')}
animation: {dna.get('animation_level', '')}
category: {category}
tags: {' '.join(dna.get('industry_tags', []))}"""


def _default_dna(category: str) -> Dict[str, Any]:
    """Fallback DNA when no AI is available."""
    cluster_map = {
        "ristorante": "V1", "fitness": "V1", "bellezza": "V1",
        "studio_professionale": "V2", "salute": "V2", "agenzia": "V2",
        "saas": "V3", "ecommerce": "V3",
        "portfolio": "V4",
        "artigiani": "V5"
    }
    return {
        "mood": "professional",
        "density": "balanced",
        "typography": "sans",
        "color_palette": ["#3b82f6", "#1e40af", "#f59e0b", "#ffffff", "#111827"],
        "variant_cluster": cluster_map.get(category, "V2"),
        "sections_order": ["hero", "about", "services", "testimonials", "contact"],
        "animation_level": "moderate",
        "has_video_bg": False,
        "typography_heading": "Inter",
        "typography_body": "Inter",
        "industry_tags": [category]
    }
