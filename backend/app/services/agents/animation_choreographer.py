"""
Animation Choreographer Agent — plans GSAP animations per section.

Takes the Design Brief's animation directives + the list of sections
and outputs an Animation Map: which data-animate effect to apply
to each element type in each section.

The choreographer ensures:
- No two adjacent sections use the same entrance animation
- Hero has a unique "signature" effect
- CTAs always use magnetic
- Scroll philosophy is consistent throughout
- Animation intensity matches the brief
"""

import json
import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Available GSAP effects from gsap-universal.js
ENTRANCE_EFFECTS = [
    "fade-up", "fade-down", "fade-left", "fade-right",
    "scale-in", "scale-up", "rotate-in", "flip-up",
    "blur-in", "slide-up", "blur-slide",
    "reveal-left", "reveal-right", "reveal-up", "reveal-down",
    "bounce-in", "zoom-out", "clip-reveal", "rotate-3d",
]

HEADING_EFFECTS = [
    "text-split", "text-reveal", "typewriter",
]

INTERACTIVE_EFFECTS = [
    "tilt", "magnetic", "card-hover-3d", "float",
]

SIGNATURE_EFFECTS = [
    "clip-reveal", "blur-slide", "rotate-3d", "scale-in",
    "reveal-up", "text-split", "zoom-out",
]

# Intensity presets control how many elements get animated
INTENSITY_LIMITS = {
    "subtle": {"max_per_section": 2, "skip_probability": 0.3},
    "balanced": {"max_per_section": 4, "skip_probability": 0.1},
    "cinematic": {"max_per_section": 6, "skip_probability": 0.0},
    "experimental": {"max_per_section": 8, "skip_probability": 0.0},
}


class AnimationChoreographer:
    """Plans GSAP animation assignments for each section."""

    def __init__(self, ai_client=None):
        self.ai_client = ai_client

    async def create_animation_map(
        self,
        sections: List[str],
        brief: Dict[str, Any],
        style_id: str = "",
    ) -> Dict[str, Any]:
        """
        Generate an animation map for all sections.

        If AI client is available, uses Gemini Flash for creative choreography.
        Otherwise falls back to algorithmic assignment.

        Returns:
            {
                "hero": {"heading": "text-split", "subtitle": "blur-slide", "cta": "magnetic", ...},
                "about": {"heading": "text-reveal", "text": "fade-up", "image": "clip-reveal"},
                ...
            }
        """
        anim_dir = brief.get("animation_direction", {})
        intensity = anim_dir.get("intensity", "balanced")
        signature = anim_dir.get("signature_effect", "")
        scroll_phil = anim_dir.get("scroll_philosophy", "reveal")

        if self.ai_client:
            try:
                return await self._ai_choreograph(
                    sections, brief, style_id, intensity, signature, scroll_phil,
                )
            except Exception as e:
                logger.warning("[AnimChoreographer] AI call failed, using algorithmic: %s", e)

        return self._algorithmic_choreograph(
            sections, intensity, signature, scroll_phil,
        )

    async def _ai_choreograph(
        self,
        sections: List[str],
        brief: Dict[str, Any],
        style_id: str,
        intensity: str,
        signature: str,
        scroll_phil: str,
    ) -> Dict[str, Any]:
        """Use Gemini Flash to create a creative animation choreography."""
        from app.services.agents.design_director import DesignDirector
        anim_prompt = DesignDirector.brief_to_animation_prompt(brief)

        sections_list = ", ".join(sections)

        prompt = f"""You are a GSAP animation choreographer for a one-page website.

{anim_prompt}

SECTIONS: {sections_list}
STYLE: {style_id}

Available data-animate effects:
ENTRANCE: {', '.join(ENTRANCE_EFFECTS)}
HEADINGS: {', '.join(HEADING_EFFECTS)}
INTERACTIVE: {', '.join(INTERACTIVE_EFFECTS)}

RULES:
1. Hero heading MUST use "text-split" (signature effect)
2. All CTA buttons MUST use "magnetic"
3. NO two adjacent sections can use the same entrance effect
4. Intensity "{intensity}" means {"few, subtle animations" if intensity == "subtle" else "rich, varied animations on most elements" if intensity in ("cinematic", "experimental") else "balanced mix, animate key elements"}
5. Scroll philosophy "{scroll_phil}" means {"parallax depth layers" if scroll_phil == "parallax" else "elements reveal on scroll" if scroll_phil == "reveal" else "sections pin while content scrolls" if scroll_phil == "pinned" else "smooth cascade of staggered elements"}

Return ONLY this JSON (no markdown):
{{
  "section_name": {{
    "heading": "effect",
    "subtitle": "effect or null",
    "text": "effect or null",
    "image": "effect or null",
    "cards": "effect or null",
    "cta": "effect or null",
    "section_entrance": "effect or null"
  }}
}}

Include EVERY section from the list. Use null for elements that should NOT be animated (based on intensity level)."""

        result = await self.ai_client.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            thinking=False,
            timeout=30.0,
            temperature=0.7,
            json_mode=True,
        )

        if result.get("success"):
            try:
                animation_map = self._parse_map(result["content"])
                logger.info(
                    "[AnimChoreographer] AI map created: %d sections, %d total effects",
                    len(animation_map),
                    sum(
                        1 for sec in animation_map.values()
                        for v in sec.values() if v
                    ),
                )
                return animation_map
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("[AnimChoreographer] JSON parse failed: %s", e)

        # Fallback to algorithmic
        return self._algorithmic_choreograph(sections, intensity, signature, scroll_phil)

    def _algorithmic_choreograph(
        self,
        sections: List[str],
        intensity: str = "balanced",
        signature: str = "",
        scroll_phil: str = "reveal",
    ) -> Dict[str, Any]:
        """Deterministic fallback: assign animations algorithmically."""
        limits = INTENSITY_LIMITS.get(intensity, INTENSITY_LIMITS["balanced"])
        skip_prob = limits["skip_probability"]

        # Shuffle entrance effects to avoid repetition
        available_entrances = list(ENTRANCE_EFFECTS)
        random.shuffle(available_entrances)
        entrance_idx = 0

        animation_map = {}

        for i, section in enumerate(sections):
            section_map = {}

            if section == "hero":
                section_map["heading"] = "text-split"
                section_map["subtitle"] = "blur-slide"
                section_map["cta"] = "magnetic"
                if signature:
                    section_map["section_entrance"] = None  # hero doesn't need entrance
                animation_map[section] = section_map
                continue

            # Pick entrance effect (no repeat from previous section)
            entrance = available_entrances[entrance_idx % len(available_entrances)]
            entrance_idx += 1

            section_map["section_entrance"] = entrance

            # Heading: always animate (text-split or text-reveal, alternating)
            section_map["heading"] = "text-split" if i % 2 == 0 else "text-reveal"

            # Subtitle
            if random.random() > skip_prob:
                section_map["subtitle"] = random.choice(["fade-up", "blur-in", "blur-slide"])
            else:
                section_map["subtitle"] = None

            # Text blocks
            if random.random() > skip_prob:
                section_map["text"] = random.choice(["fade-up", "blur-slide", "fade-left"])
            else:
                section_map["text"] = None

            # Images
            if section in ("about", "gallery", "team"):
                section_map["image"] = random.choice(["clip-reveal", "scale-in", "image-zoom"])

            # Cards (services, features, pricing, team)
            if section in ("services", "features", "pricing", "team", "testimonials"):
                section_map["cards"] = random.choice(["tilt", "card-hover-3d", "fade-up"])

            # CTA
            if section in ("cta", "hero", "contact"):
                section_map["cta"] = "magnetic"

            animation_map[section] = section_map

        return animation_map

    def _parse_map(self, content: str) -> Dict[str, Any]:
        """Parse the animation map JSON."""
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content.strip())
