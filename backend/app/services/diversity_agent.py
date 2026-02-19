"""
Diversity Agent - Secondary AI for CSS/animation variation suggestions.

Calls a lightweight AI model (Qwen3 Coder via OpenRouter free tier, or
LLaMA 3.1 via Groq as fallback) to suggest per-generation micro-variations
in spacing, border-radius, shadow, font scale, and animation choices.

Non-blocking: if no API keys are configured or the call fails, a pure-Python
random fallback produces similar diversity without any external dependency.
"""

import json
import logging
import os
import random
import time
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
_PRIMARY_MODEL = "qwen/qwen3-coder:30b-a3b"
_FALLBACK_MODEL = "meta-llama/llama-3.1-8b-instruct"

# ---------------------------------------------------------------------------
# In-memory cache: (style_id) -> (timestamp, result)
# ---------------------------------------------------------------------------
_cache: Dict[str, tuple] = {}
_CACHE_TTL = 30  # seconds


def _get_cached(style_id: str) -> Optional[Dict[str, Any]]:
    entry = _cache.get(style_id)
    if entry and (time.time() - entry[0]) < _CACHE_TTL:
        logger.debug("Diversity agent: cache hit for style_id=%s", style_id)
        return entry[1]
    return None


def _set_cache(style_id: str, result: Dict[str, Any]) -> None:
    _cache[style_id] = (time.time(), result)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------
def _build_prompt(
    style_id: str,
    sections: List[str],
    current_css_profile: Dict[str, str],
    business_type: str,
) -> str:
    return f"""You are a creative web design assistant. Given a website style profile, suggest UNIQUE micro-variations to make this site look different from others with the same template.

Style: {style_id}
Business: {business_type}
Sections: {json.dumps(sections)}
Current CSS: {json.dumps(current_css_profile)}

Respond in JSON only:
{{
  "css_tweaks": {{
    "space_section_delta": "-0.5rem to +1rem range",
    "radius_delta": "-0.25rem to +0.5rem range",
    "shadow_intensity": "0.5 to 1.5 multiplier",
    "h1_scale_factor": "0.9 to 1.15 multiplier"
  }},
  "animation_suggestions": {{
    "hero_heading": "one of: text-split, text-reveal, typewriter, blur-in",
    "hero_subtitle": "one of: blur-slide, fade-up, fade-left, slide-up",
    "hero_cta": "one of: bounce-in, scale-in, magnetic, blur-in",
    "cards": "one of: stagger, stagger-scale, fade-up, scale-in",
    "section_entrance": "one of: fade-up, fade-left, fade-right, reveal-up, blur-in"
  }},
  "layout_hint": "brief creative direction for this specific site"
}}"""


# ---------------------------------------------------------------------------
# Pure-Python random diversity (no AI needed)
# ---------------------------------------------------------------------------
def _generate_local_diversity() -> Dict[str, Any]:
    """Pure-Python random diversity when no AI available."""
    return {
        "css_tweaks": {
            "space_section_delta": f"{random.uniform(-0.8, 1.0):.2f}rem",
            "radius_delta": f"{random.uniform(-0.2, 0.4):.2f}rem",
            "shadow_intensity": round(random.uniform(0.6, 1.4), 2),
            "h1_scale_factor": round(random.uniform(0.92, 1.12), 2),
        },
        "animation_suggestions": {
            "hero_heading": random.choice(["text-split", "text-reveal", "typewriter", "blur-in"]),
            "hero_subtitle": random.choice(["blur-slide", "fade-up", "fade-left", "slide-up"]),
            "hero_cta": random.choice(["bounce-in", "scale-in", "magnetic", "blur-in"]),
            "cards": random.choice(["stagger", "stagger-scale", "fade-up", "scale-in"]),
            "section_entrance": random.choice(["fade-up", "fade-left", "fade-right", "reveal-up", "blur-in"]),
        },
        "layout_hint": "",
    }


# ---------------------------------------------------------------------------
# Empty defaults (returned on graceful failure)
# ---------------------------------------------------------------------------
_EMPTY_DEFAULTS: Dict[str, Any] = {
    "css_tweaks": {},
    "animation_suggestions": {},
    "layout_hint": "",
}


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------
def _parse_response(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from the AI response, handling markdown fences."""
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None
        else:
            return None

    # Validate expected keys
    if not isinstance(data, dict):
        return None
    if "css_tweaks" not in data and "animation_suggestions" not in data:
        return None
    return data


# ---------------------------------------------------------------------------
# API callers
# ---------------------------------------------------------------------------
async def _call_openrouter(prompt: str) -> Optional[Dict[str, Any]]:
    """Call Qwen3 Coder via OpenRouter (free tier)."""
    api_key = settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return None

    url = f"{settings.OPENROUTER_API_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://e-quipe.app",
        "X-Title": "Site Builder Diversity Agent",
    }
    payload = {
        "model": _PRIMARY_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.9,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        return _parse_response(content)


async def _call_groq(prompt: str) -> Optional[Dict[str, Any]]:
    """Call LLaMA 3.1 via Groq as fallback."""
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _FALLBACK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.9,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        return _parse_response(content)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
async def get_diversity_suggestions(
    style_id: str,
    sections: List[str],
    current_css_profile: Dict[str, str],
    business_type: str = "",
) -> Dict[str, Any]:
    """Get CSS and animation diversity suggestions from secondary AI.

    Returns dict with:
    - css_tweaks: dict of CSS property overrides (spacing, radius, shadow adjustments)
    - animation_suggestions: dict mapping element role -> suggested animation type
    - layout_hint: str with a layout suggestion

    Non-blocking: never raises exceptions, returns defaults on any failure.
    """
    # Check cache first
    cached = _get_cached(style_id)
    if cached is not None:
        return cached

    prompt = _build_prompt(style_id, sections, current_css_profile, business_type)

    # Try primary (OpenRouter / Qwen3 Coder)
    try:
        result = await _call_openrouter(prompt)
        if result:
            logger.info("Diversity agent: got suggestions from OpenRouter (%s)", _PRIMARY_MODEL)
            _set_cache(style_id, result)
            return result
    except Exception as e:
        logger.warning("Diversity agent: OpenRouter call failed: %s", e)

    # Try fallback (Groq / LLaMA)
    try:
        result = await _call_groq(prompt)
        if result:
            logger.info("Diversity agent: got suggestions from Groq (%s)", _FALLBACK_MODEL)
            _set_cache(style_id, result)
            return result
    except Exception as e:
        logger.warning("Diversity agent: Groq call failed: %s", e)

    # Final fallback: local random diversity
    logger.info("Diversity agent: using local random diversity (no AI keys or all calls failed)")
    result = _generate_local_diversity()
    _set_cache(style_id, result)
    return result
