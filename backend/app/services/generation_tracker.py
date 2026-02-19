"""
Generation Tracker — Lightweight SQLite-based memory for diversity.

Tracks recent generations (colors, fonts, components, personality) so the
diversity system can avoid repetition. Works without PostgreSQL.

Uses the same SQLite DB as design_knowledge.py for zero extra infrastructure.
"""

import json
import logging
import os
import random
import sqlite3
import time
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "design_knowledge.db")


def _get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS generation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at REAL NOT NULL DEFAULT (strftime('%s','now')),
            category TEXT NOT NULL,
            style_id TEXT,
            user_id TEXT,
            -- Theme choices
            color_primary TEXT,
            color_mood TEXT,
            font_heading TEXT,
            font_body TEXT,
            personality TEXT,
            -- Component choices (JSON dict: section -> variant)
            components_json TEXT,
            -- Layout fingerprint
            layout_hash TEXT,
            -- Full theme JSON for deep comparison
            theme_json TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_gen_history_category
        ON generation_history(category, created_at DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_gen_history_style
        ON generation_history(style_id, created_at DESC)
    """)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Record a generation
# ---------------------------------------------------------------------------
def record_generation(
    category: str,
    style_id: str = "",
    user_id: str = "",
    color_primary: str = "",
    color_mood: str = "",
    font_heading: str = "",
    font_body: str = "",
    personality: str = "",
    components: Optional[Dict[str, str]] = None,
    layout_hash: str = "",
    theme: Optional[Dict[str, Any]] = None,
) -> None:
    """Record a completed generation for diversity tracking."""
    try:
        conn = _get_db()
        conn.execute(
            """INSERT INTO generation_history
               (category, style_id, user_id, color_primary, color_mood,
                font_heading, font_body, personality, components_json,
                layout_hash, theme_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                category,
                style_id or "",
                user_id or "",
                color_primary or "",
                color_mood or "",
                font_heading or "",
                font_body or "",
                personality or "",
                json.dumps(components) if components else "{}",
                layout_hash or "",
                json.dumps(theme) if theme else "{}",
            ),
        )
        conn.commit()
        conn.close()
        logger.info(
            f"[Tracker] Recorded generation: category={category}, style={style_id}, "
            f"mood={color_mood}, font={font_heading}"
        )
    except Exception as e:
        logger.warning(f"[Tracker] Failed to record generation: {e}")


# ---------------------------------------------------------------------------
# Query recent generations
# ---------------------------------------------------------------------------
def get_recent_generations(
    category: str = "",
    style_id: str = "",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Get recent generations, optionally filtered by category/style."""
    try:
        conn = _get_db()
        conditions = []
        params: List[Any] = []

        if category:
            conditions.append("category = ?")
            params.append(category)
        if style_id:
            conditions.append("style_id = ?")
            params.append(style_id)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = conn.execute(
            f"SELECT * FROM generation_history {where} ORDER BY created_at DESC LIMIT ?",
            params + [limit],
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.warning(f"[Tracker] Failed to query recent generations: {e}")
        return []


# ---------------------------------------------------------------------------
# Get recently used values (for anti-repetition)
# ---------------------------------------------------------------------------
def get_recently_used(
    category: str = "",
    limit: int = 15,
) -> Dict[str, Set[str]]:
    """Get sets of recently used values per dimension.

    Returns:
        {
            "color_moods": {"Ocean Depth", "Sunset Warmth", ...},
            "font_headings": {"Space Grotesk", "Playfair Display", ...},
            "font_bodies": {"Inter", "DM Sans", ...},
            "personalities": {"bold+poetic", "minimal+warm", ...},
            "primaries": {"#7C3AED", "#3B82F6", ...},
            "layout_hashes": {"abc123", ...},
            "components": {"hero": {"hero-zen-01": 3, "hero-split-01": 1}, ...}
        }
    """
    recent = get_recent_generations(category=category, limit=limit)
    result: Dict[str, Any] = {
        "color_moods": set(),
        "font_headings": set(),
        "font_bodies": set(),
        "personalities": set(),
        "primaries": set(),
        "layout_hashes": set(),
        "components": {},  # section -> {variant: count}
    }

    for gen in recent:
        if gen.get("color_mood"):
            result["color_moods"].add(gen["color_mood"])
        if gen.get("font_heading"):
            result["font_headings"].add(gen["font_heading"])
        if gen.get("font_body"):
            result["font_bodies"].add(gen["font_body"])
        if gen.get("personality"):
            result["personalities"].add(gen["personality"])
        if gen.get("color_primary"):
            result["primaries"].add(gen["color_primary"])
        if gen.get("layout_hash"):
            result["layout_hashes"].add(gen["layout_hash"])

        # Parse component usage
        try:
            comps = json.loads(gen.get("components_json") or "{}")
            for section, variant in comps.items():
                if section not in result["components"]:
                    result["components"][section] = {}
                result["components"][section][variant] = (
                    result["components"][section].get(variant, 0) + 1
                )
        except (json.JSONDecodeError, TypeError):
            pass

    return result


# ---------------------------------------------------------------------------
# Anti-repetition choice helpers
# ---------------------------------------------------------------------------
def pick_avoiding_recent(
    pool: List[Any],
    recently_used: Set[str],
    key_fn=None,
    max_recent_penalty: float = 0.15,
) -> Any:
    """Pick from pool with penalty for recently used items.

    Items used recently get a lower weight (max_recent_penalty),
    unused items get weight 1.0. Falls back to random if all used.

    Args:
        pool: List of items to choose from
        recently_used: Set of string keys of recently used items
        key_fn: Function to extract the key from a pool item (default: str)
        max_recent_penalty: Weight for recently used items (0.0 = never, 1.0 = no penalty)
    """
    if not pool:
        return None
    if not recently_used:
        return random.choice(pool)

    if key_fn is None:
        key_fn = str

    weights = []
    for item in pool:
        k = key_fn(item)
        if k in recently_used:
            weights.append(max_recent_penalty)
        else:
            weights.append(1.0)

    # If all items are recently used, reset to equal weights
    if all(w == max_recent_penalty for w in weights):
        weights = [1.0] * len(pool)

    return random.choices(pool, weights=weights, k=1)[0]


def pick_variant_avoiding_recent(
    pool: List[str],
    section: str,
    component_usage: Dict[str, Dict[str, int]],
) -> str:
    """Pick a component variant with anti-repetition weighting.

    Items used more frequently in recent generations get lower weight.
    """
    if not pool:
        return ""
    if not component_usage or section not in component_usage:
        return random.choice(pool)

    section_usage = component_usage[section]
    max_uses = max(section_usage.values()) if section_usage else 0

    weights = []
    for variant in pool:
        uses = section_usage.get(variant, 0)
        if uses == 0:
            weights.append(1.0)
        else:
            # Inverse weight: more uses = less likely
            weights.append(max(0.05, 1.0 - (uses / (max_uses + 1))))

    return random.choices(pool, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Creative Seed Generator — unique per generation
# ---------------------------------------------------------------------------

# Creative direction templates that shape the AI's approach
_CREATIVE_DIRECTIONS = [
    "Imagine this site as a magazine spread — editorial pacing, generous whitespace, every element placed with intention.",
    "Think of this site as a conversation — direct, personal, no corporate veneer. Every section should feel like talking to a friend.",
    "Approach this like a film opening — dramatic first impression, build tension, reveal the story gradually.",
    "Design this like a luxury unboxing experience — anticipation, reveal, delight at every scroll.",
    "Think museum exhibition — each section is a room. Clear hierarchy, focused attention, elegant transitions.",
    "Imagine the brand as a person at a dinner party — charming, memorable, with one unforgettable story.",
    "Approach this as street art meets Swiss design — raw energy contained in a perfect grid.",
    "Think of each section as a vinyl record side — Side A is the hook, Side B is the depth.",
    "Design this like an architect — structure first, then texture, then the one bold material choice.",
    "Imagine the reader has 8 seconds — every word must earn its place, every image must stop the scroll.",
    "Think of this as a playlist — each section has a different energy but the same vibe runs through all.",
    "Approach this like Japanese wabi-sabi — beauty in imperfection, asymmetry, the space between elements.",
    "Design as if this site will be printed on a poster — is every section visually striking enough to hang on a wall?",
    "Think of the brand as a soundtrack — what's the opening track, the bridge, the finale?",
    "Imagine this as a chef's tasting menu — surprise, delight, never boring, build to the climax.",
    "Approach this like a fashion lookbook — visual impact first, story second, details reward close attention.",
]

# Layout rhythm variations
_LAYOUT_RHYTHMS = [
    "Use ASYMMETRIC section layout: alternate between full-width and contained, between 60/40 splits and centered.",
    "Use STACKING rhythm: dense sections followed by breathing space. Like music: verse-chorus-bridge.",
    "Use PROGRESSIVE REVEAL: start minimal, add complexity. Hero is sparse, middle sections are rich, CTA is back to sparse.",
    "Use CONTRAST rhythm: dark section → light section → accent section. Never two similar-looking sections in a row.",
    "Use EDITORIAL rhythm: one big visual, then text, then gallery, then text. Like a magazine layout.",
    "Use BENTO rhythm: mix grid sizes within sections. One large hero card + 2 small. Then 3 equal. Never the same grid twice.",
]


def generate_creative_seed(
    category: str = "",
    recently_used: Optional[Dict[str, Set[str]]] = None,
) -> Dict[str, str]:
    """Generate a unique creative direction seed for this generation.

    Returns dict with:
        - creative_direction: A metaphorical creative brief
        - layout_rhythm: How sections should flow visually
        - surprise_element: One unexpected design choice to make this site unique
    """
    if recently_used is None:
        recently_used = get_recently_used(category=category, limit=10)

    direction = random.choice(_CREATIVE_DIRECTIONS)
    rhythm = random.choice(_LAYOUT_RHYTHMS)

    # Surprise elements — one random "twist" per generation
    surprises = [
        "Add ONE section with an oversized heading (150%+ normal size) for dramatic impact.",
        "Include a full-width image or color band between two text sections to break the rhythm.",
        "Make the CTA section visually DIFFERENT from everything else — different background color, different spacing.",
        "Use a pull quote or large text callout in the middle of the page as a visual anchor.",
        "Add subtle texture or grain to one section's background to add depth.",
        "Make the about section feel like a story — use narrative pacing, not bullet points.",
        "Use a counter/statistics bar between sections as a visual separator and credibility builder.",
        "Include a marquee/ticker tape element for keywords, skills, or client names.",
    ]
    surprise = random.choice(surprises)

    return {
        "creative_direction": direction,
        "layout_rhythm": rhythm,
        "surprise_element": surprise,
    }


def build_diversity_prompt_block(
    category: str = "",
    recently_used: Optional[Dict[str, Set[str]]] = None,
) -> str:
    """Build a prompt block that injects creative diversity into the generation.

    This is injected into the theme/text prompts to push the AI
    toward unique outputs.
    """
    seed = generate_creative_seed(category, recently_used)

    if recently_used is None:
        recently_used = get_recently_used(category=category, limit=10)

    # Build "avoid these" hints
    avoid_hints = []
    if recently_used.get("font_headings"):
        recent_fonts = list(recently_used["font_headings"])[:5]
        avoid_hints.append(
            f"AVOID these heading fonts (used recently): {', '.join(recent_fonts)}. "
            f"Pick something DIFFERENT."
        )
    if recently_used.get("primaries"):
        recent_colors = list(recently_used["primaries"])[:5]
        avoid_hints.append(
            f"AVOID colors too similar to these recently used primaries: {', '.join(recent_colors)}. "
            f"Choose a distinctly different hue."
        )

    avoid_block = "\n".join(avoid_hints) if avoid_hints else ""

    return f"""
=== CREATIVE SEED (make this site UNIQUE) ===
{seed['creative_direction']}

Layout rhythm: {seed['layout_rhythm']}

Surprise element: {seed['surprise_element']}

{avoid_block}
=== END CREATIVE SEED ===
"""


# ---------------------------------------------------------------------------
# Cleanup old records (keep last 200)
# ---------------------------------------------------------------------------
def cleanup_old_records(keep: int = 200) -> int:
    """Delete old generation records, keeping the most recent `keep`."""
    try:
        conn = _get_db()
        result = conn.execute(
            """DELETE FROM generation_history
               WHERE id NOT IN (
                   SELECT id FROM generation_history
                   ORDER BY created_at DESC LIMIT ?
               )""",
            (keep,),
        )
        deleted = result.rowcount
        conn.commit()
        conn.close()
        if deleted > 0:
            logger.info(f"[Tracker] Cleaned up {deleted} old generation records")
        return deleted
    except Exception as e:
        logger.warning(f"[Tracker] Cleanup failed: {e}")
        return 0
