"""
Design Director Agent — the creative brain of the multi-agent pipeline.

Takes business info + full creative context + memory of past generations
and outputs a Design Brief JSON that guides all downstream agents
(Color & Typography, Copywriter, Animation Choreographer).

The Director's job is to THINK about design before generating — layout
strategy, color direction, typography personality, copy voice, animation
philosophy, and anti-bias rules — so every site is unique.
"""

import json
import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Layout strategies the Director can choose from
LAYOUT_STRATEGIES = [
    {"id": "split-screen", "desc": "Hero diviso a metà: testo a sx, visual a dx (o viceversa)"},
    {"id": "editorial", "desc": "Layout da rivista: testo grande, asimmetrie, whitespace generoso"},
    {"id": "bento-grid", "desc": "Griglia bento stile Apple: card di dimensioni diverse, dense e ordinate"},
    {"id": "zigzag", "desc": "Sezioni alternate: testo-immagine, immagine-testo, ritmo visivo"},
    {"id": "asymmetric", "desc": "Layout asimmetrico: elementi fuori griglia, overlap, dinamismo"},
    {"id": "fullscreen-hero", "desc": "Hero a schermo intero con scroll reveal per le sezioni sotto"},
    {"id": "stacked-panels", "desc": "Pannelli impilati full-width con transizioni tra sezioni"},
    {"id": "sidebar-content", "desc": "Layout con sidebar fissa e contenuto scrollabile"},
]

# Grid styles for multi-item sections
GRID_STYLES = [
    "zigzag",       # alternated left-right
    "bento",        # variable-size grid cells
    "masonry",      # Pinterest-style staggered
    "staggered",    # offset grid with varying heights
    "cards-3col",   # classic but with variation
    "featured+grid", # one big item + smaller grid
]

# Animation intensities
ANIMATION_INTENSITIES = ["subtle", "balanced", "cinematic", "experimental"]

# Scroll philosophies
SCROLL_PHILOSOPHIES = ["parallax", "reveal", "pinned", "smooth-cascade", "staggered-entrance"]

# Forbidden defaults (anti-bias)
FORBIDDEN_COLORS = ["#7C3AED", "#6366F1", "#8B5CF6"]  # AI purple bias
FORBIDDEN_FONTS = ["Inter", "Roboto", "Open Sans", "Arial", "Helvetica"]
FORBIDDEN_HERO_LAYOUTS = ["centered-text-only"]
FORBIDDEN_COPY = [
    "Benvenuti", "Siamo un'azienda", "leader nel settore",
    "eccellenza e innovazione", "a 360 gradi", "soluzioni su misura",
]


class DesignDirector:
    """Creates a Design Brief that shapes all downstream generation."""

    def __init__(self, ai_client):
        self.ai_client = ai_client

    async def create_brief(
        self,
        business_name: str,
        business_description: str,
        category: str,
        style_id: str,
        sections: List[str],
        creative_context: str = "",
        memory_context: str = "",
        variety_context: Optional[Dict[str, Any]] = None,
        user_color: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a Design Brief via Gemini Pro.

        Returns a structured dict with layout_strategy, color_direction,
        typography_direction, copywriting_direction, animation_direction,
        and anti_bias_rules.
        """
        # Build anti-bias rules based on memory and recent generations
        anti_bias = self._build_anti_bias_rules(variety_context)

        # Pick random layout suggestions (not the final choice — Director decides)
        layout_options = random.sample(LAYOUT_STRATEGIES, min(4, len(LAYOUT_STRATEGIES)))
        layout_options_str = "\n".join(
            f"  - {lo['id']}: {lo['desc']}" for lo in layout_options
        )

        grid_options_str = ", ".join(random.sample(GRID_STYLES, min(4, len(GRID_STYLES))))

        # Color constraint
        color_constraint = ""
        if user_color:
            color_constraint = f"""
The user chose primary color: {user_color}. Your palette_strategy MUST harmonize with this color.
Do NOT override it. Build the mood AROUND this color."""

        # Personality hint from variety
        personality_name = ""
        if variety_context and variety_context.get("personality"):
            personality_name = variety_context["personality"].get("name", "")

        prompt = f"""You are a world-class Creative Director at a top design agency (Pentagram, Sagmeister, IDEO).

Your job: create a DESIGN BRIEF for a one-page website. This brief will guide the Color Designer, Copywriter, and Animation Choreographer. Think deeply about what makes THIS specific business unique and how the design should reflect that.

=== BUSINESS ===
Name: {business_name}
Category: {category}
Style: {style_id}
Description: {business_description[:1500]}
Sections: {", ".join(sections)}
{color_constraint}

=== CREATIVE CONTEXT (from design knowledge database) ===
{creative_context[:3000] if creative_context else "(nessun contesto disponibile)"}

=== MEMORY OF PAST GENERATIONS (avoid repeating these) ===
{memory_context[:1500] if memory_context else "(prima generazione)"}

=== LAYOUT OPTIONS (choose ONE or propose your own) ===
{layout_options_str}
Grid styles for multi-item sections: {grid_options_str}

=== ANTI-BIAS RULES (MANDATORY — violating these = REJECTED) ===
{chr(10).join(f"- {r}" for r in anti_bias)}

=== YOUR TASK ===
Create a Design Brief JSON. Think about:
1. LAYOUT: How should this specific business present itself? Not every business needs a split hero.
2. COLOR: What mood fits? A cozy restaurant ≠ a SaaS platform ≠ a luxury portfolio.
3. TYPOGRAPHY: What personality should the fonts express? Bold geometric ≠ elegant serif.
4. COPY: What voice? Provocative? Warm? Data-driven? Minimal?
5. ANIMATION: Subtle or cinematic? What's the signature scroll effect?
6. What makes THIS site different from the last 10 sites in this category?

Return ONLY this JSON (no markdown, no explanation):
{{
  "layout_strategy": {{
    "hero_layout": "split-screen|editorial|fullscreen|asymmetric",
    "grid_style": "zigzag|bento|masonry|staggered|cards-3col|featured+grid",
    "visual_density": "sparse|balanced|dense"
  }},
  "color_direction": {{
    "mood": "one evocative name (e.g. Nordic Clean, Desert Sunset, Neon City)",
    "palette_strategy": "describe the color feeling in 10 words",
    "dark_mode": false,
    "primary_feeling": "warm|cool|neutral|vivid",
    "forbidden_colors": ["#hex1", "#hex2"]
  }},
  "typography_direction": {{
    "heading_personality": "geometric-bold|elegant-serif|warm-rounded|editorial|futuristic|handwritten",
    "body_personality": "clean-readable|warm-humanist|technical|editorial",
    "scale_contrast": "high|medium|low",
    "suggested_pairing": {{"heading": "Font Name", "body": "Font Name"}},
    "forbidden_fonts": ["Inter", "Roboto"]
  }},
  "copywriting_direction": {{
    "voice": "provocative+minimal|warm+storytelling|data-driven+bold|poetic+sensory|irreverent+fun",
    "headline_strategy": "metaphorical|question|statement|single-word|number-led|contrast",
    "narrative_arc": "dal problema alla trasformazione|dalla curiosità alla scoperta|dall'emozione all'azione",
    "tone_temperature": "cold-professional|warm-friendly|hot-passionate|cool-ironic"
  }},
  "animation_direction": {{
    "intensity": "subtle|balanced|cinematic|experimental",
    "signature_effect": "describe ONE unique animation for the hero (e.g. curtain-reveal, split-slide, text-scramble)",
    "scroll_philosophy": "parallax|reveal|pinned|smooth-cascade|staggered-entrance",
    "micro_interactions": true
  }},
  "anti_bias_rules": [
    "rule 1",
    "rule 2",
    "rule 3 (minimum 3, maximum 7)"
  ]
}}"""

        result = await self.ai_client.call(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            thinking=False,
            timeout=30.0,
            temperature=0.85,
            json_mode=True,
        )

        if result.get("success"):
            try:
                brief = self._parse_brief(result["content"])
                logger.info(
                    "[DesignDirector] Brief created: layout=%s, mood=%s, voice=%s, intensity=%s",
                    brief.get("layout_strategy", {}).get("hero_layout", "?"),
                    brief.get("color_direction", {}).get("mood", "?"),
                    brief.get("copywriting_direction", {}).get("voice", "?"),
                    brief.get("animation_direction", {}).get("intensity", "?"),
                )
                return {
                    "success": True,
                    "brief": brief,
                    "tokens_input": result.get("tokens_input", 0),
                    "tokens_output": result.get("tokens_output", 0),
                }
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("[DesignDirector] Brief JSON parse failed: %s", e)
                return {
                    "success": False,
                    "brief": self._fallback_brief(category, style_id, variety_context),
                    "error": str(e),
                }

        logger.warning("[DesignDirector] AI call failed: %s", result.get("error"))
        return {
            "success": False,
            "brief": self._fallback_brief(category, style_id, variety_context),
            "error": result.get("error", "unknown"),
        }

    def _parse_brief(self, content: str) -> Dict[str, Any]:
        """Parse and validate the Design Brief JSON."""
        # Strip markdown fences if present
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        brief = json.loads(content)

        # Validate required top-level keys
        required = [
            "layout_strategy", "color_direction", "typography_direction",
            "copywriting_direction", "animation_direction",
        ]
        for key in required:
            if key not in brief:
                brief[key] = {}

        # Ensure anti_bias_rules is a list
        if not isinstance(brief.get("anti_bias_rules"), list):
            brief["anti_bias_rules"] = []

        return brief

    def _build_anti_bias_rules(
        self, variety_context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Build anti-bias rules combining static rules with variety context."""
        rules = [
            "NO hero centrato con testo al centro (usa split-screen, asimmetrico, o editorial)",
            "NO griglia di 3 card identiche uguali (usa zigzag, bento, masonry, featured+grid)",
            "NO gradiente viola/blu tipico dell'AI (evita #7C3AED, #6366F1, #8B5CF6)",
            "NO Inter, Roboto, Open Sans come font (usa font con personalità)",
            "NO 'Benvenuti', 'Siamo un'azienda', 'leader nel settore' nel copy",
            "NO numeri tondi nelle stats (usa 47.2%, 1.847, 89.3% — numeri 'sporchi')",
            "NO nomi finti come John Doe, Mario Rossi generico, Acme Corp nelle testimonial",
        ]

        # Add variety-based anti-repetition
        if variety_context:
            recently_used = variety_context.get("_recently_used", {})
            recent_fonts = recently_used.get("font_headings", set())
            if recent_fonts:
                rules.append(
                    f"NO questi font heading usati di recente: {', '.join(list(recent_fonts)[:3])}"
                )
            recent_moods = recently_used.get("color_moods", set())
            if recent_moods:
                rules.append(
                    f"NO questi mood colore usati di recente: {', '.join(list(recent_moods)[:3])}"
                )

        return rules

    def _fallback_brief(
        self,
        category: str,
        style_id: str,
        variety_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a reasonable fallback brief without AI."""
        layout = random.choice(LAYOUT_STRATEGIES)
        grid = random.choice(GRID_STYLES)
        intensity = random.choice(ANIMATION_INTENSITIES)
        scroll = random.choice(SCROLL_PHILOSOPHIES)

        personality_name = ""
        if variety_context and variety_context.get("personality"):
            personality_name = variety_context["personality"].get("name", "")

        color_mood = "Modern Bold"
        if variety_context and variety_context.get("color_mood"):
            color_mood = variety_context["color_mood"].get("mood", "Modern Bold")

        return {
            "layout_strategy": {
                "hero_layout": layout["id"],
                "grid_style": grid,
                "visual_density": "balanced",
            },
            "color_direction": {
                "mood": color_mood,
                "palette_strategy": "follow the variety context color mood",
                "dark_mode": "dark" in style_id,
                "primary_feeling": "vivid",
                "forbidden_colors": FORBIDDEN_COLORS,
            },
            "typography_direction": {
                "heading_personality": "geometric-bold",
                "body_personality": "clean-readable",
                "scale_contrast": "high",
                "suggested_pairing": {"heading": "Space Grotesk", "body": "DM Sans"},
                "forbidden_fonts": FORBIDDEN_FONTS,
            },
            "copywriting_direction": {
                "voice": personality_name or "bold+provocative",
                "headline_strategy": "metaphorical",
                "narrative_arc": "dal problema alla trasformazione",
                "tone_temperature": "warm-friendly",
            },
            "animation_direction": {
                "intensity": intensity,
                "signature_effect": "split-reveal su hero",
                "scroll_philosophy": scroll,
                "micro_interactions": True,
            },
            "anti_bias_rules": self._build_anti_bias_rules(variety_context),
        }

    @staticmethod
    def brief_to_theme_prompt(brief: Dict[str, Any]) -> str:
        """Convert Design Brief into a prompt block for the theme generator."""
        color = brief.get("color_direction", {})
        typo = brief.get("typography_direction", {})
        layout = brief.get("layout_strategy", {})

        parts = [
            "=== DESIGN BRIEF DIRECTIVES (from Creative Director — follow closely) ===",
            f"COLOR MOOD: {color.get('mood', 'Modern Bold')}",
            f"PALETTE STRATEGY: {color.get('palette_strategy', '')}",
            f"PRIMARY FEELING: {color.get('primary_feeling', 'vivid')}",
            f"DARK MODE: {color.get('dark_mode', False)}",
        ]
        forbidden_c = color.get("forbidden_colors", [])
        if forbidden_c:
            parts.append(f"FORBIDDEN COLORS: {', '.join(forbidden_c)}")

        parts.append(f"\nTYPOGRAPHY PERSONALITY: heading={typo.get('heading_personality', '')}, body={typo.get('body_personality', '')}")
        suggested = typo.get("suggested_pairing", {})
        if suggested:
            parts.append(f"SUGGESTED FONTS: heading=\"{suggested.get('heading', '')}\", body=\"{suggested.get('body', '')}\"")
        parts.append(f"SCALE CONTRAST: {typo.get('scale_contrast', 'high')}")
        forbidden_f = typo.get("forbidden_fonts", [])
        if forbidden_f:
            parts.append(f"FORBIDDEN FONTS: {', '.join(forbidden_f)}")

        parts.append(f"\nLAYOUT: hero={layout.get('hero_layout', '')}, grid={layout.get('grid_style', '')}, density={layout.get('visual_density', 'balanced')}")
        parts.append("=== END DESIGN BRIEF ===")

        return "\n".join(parts)

    @staticmethod
    def brief_to_texts_prompt(brief: Dict[str, Any]) -> str:
        """Convert Design Brief into a prompt block for the text generator."""
        copy = brief.get("copywriting_direction", {})
        anti = brief.get("anti_bias_rules", [])

        parts = [
            "=== DESIGN BRIEF — COPYWRITING DIRECTIVES (from Creative Director) ===",
            f"VOICE: {copy.get('voice', 'bold+provocative')}",
            f"HEADLINE STRATEGY: {copy.get('headline_strategy', 'metaphorical')}",
            f"NARRATIVE ARC: {copy.get('narrative_arc', '')}",
            f"TONE TEMPERATURE: {copy.get('tone_temperature', 'warm-friendly')}",
        ]
        if anti:
            parts.append("\nANTI-BIAS RULES (MANDATORY):")
            for rule in anti:
                parts.append(f"  - {rule}")
        parts.append("=== END DESIGN BRIEF ===")

        return "\n".join(parts)

    @staticmethod
    def brief_to_animation_prompt(brief: Dict[str, Any]) -> str:
        """Convert Design Brief into a prompt block for the animation choreographer."""
        anim = brief.get("animation_direction", {})
        layout = brief.get("layout_strategy", {})

        parts = [
            "=== DESIGN BRIEF — ANIMATION DIRECTIVES (from Creative Director) ===",
            f"INTENSITY: {anim.get('intensity', 'balanced')}",
            f"SIGNATURE EFFECT: {anim.get('signature_effect', '')}",
            f"SCROLL PHILOSOPHY: {anim.get('scroll_philosophy', 'reveal')}",
            f"MICRO-INTERACTIONS: {anim.get('micro_interactions', True)}",
            f"HERO LAYOUT: {layout.get('hero_layout', '')}",
            f"GRID STYLE: {layout.get('grid_style', '')}",
            "=== END DESIGN BRIEF ===",
        ]

        return "\n".join(parts)
