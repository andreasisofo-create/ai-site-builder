"""
Effect Diversifier - Ensures every generated site has rich, varied animations.

Post-processes assembled HTML to:
1. Inject data-animate attributes on elements that lack them
2. Vary effects across sites to avoid repetition (deprioritize recently used)
3. Add staggered data-delay for sequential elements within each section
4. Track effect usage per user for cross-site diversity
"""

import json
import re
import random
import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text as sql_text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Effect pools per element type.
# For text-split variants, use "text-split|chars" meaning
# data-animate="text-split" data-split-type="chars"
# ---------------------------------------------------------------------------
EFFECT_POOLS: Dict[str, List[str]] = {
    "h1": ["text-split|chars", "text-split|words", "text-reveal", "text-fill", "blur-in"],
    "h2": ["text-split|words", "text-split|lines", "text-reveal", "blur-in", "fade-up", "blur-slide"],
    "h3": ["blur-in", "fade-up", "blur-slide", "reveal-up", "text-split|words"],
    "p": ["blur-slide", "fade-up", "blur-in", "reveal-up", "fade-left", "fade-right"],
    "img": ["clip-reveal", "image-zoom", "scale-in", "blur-in", "reveal-up", "reveal-left", "reveal-right", "fade-up"],
    "card": ["tilt", "fade-up", "scale-in", "blur-in", "border-beam", "shimmer"],
    "cta": ["magnetic", "scale-in", "fade-up", "shimmer"],
    "section_entrance": ["fade-up", "fade-left", "fade-right", "reveal-up", "reveal-left", "reveal-right", "blur-slide", "scale-in"],
    "counter": ["data-counter"],
    "decorative": ["float", "parallax", "gradient-flow"],
}

# Probability of swapping an existing effect for a different one from the same pool
SWAP_PROBABILITY = 0.3

# Regex to detect skip regions (nav, script, style, head) for placeholder protection
_SKIP_REGIONS_RE = re.compile(
    r'(<nav[\s>].*?</nav>|<script[\s>].*?</script>|<style[\s>].*?</style>|<head[\s>].*?</head>)',
    re.IGNORECASE | re.DOTALL,
)


def _pick_effect(pool_key: str, used_effects: Optional[List[dict]] = None) -> str:
    """Pick an effect from the pool, deprioritizing recently used ones.

    Uses weighted random selection: effects used fewer times recently
    get higher weight, making them more likely to be picked.
    """
    pool = EFFECT_POOLS.get(pool_key, [])
    if not pool:
        return "fade-up"

    if not used_effects:
        return random.choice(pool)

    # Count how many times each effect was used recently
    usage_counts: Dict[str, int] = {}
    for usage in used_effects:
        if pool_key in usage:
            for eff in usage[pool_key]:
                base_eff = eff.split("|")[0] if "|" in eff else eff
                usage_counts[base_eff] = usage_counts.get(base_eff, 0) + 1

    # Build weighted list: less-used effects get higher weight
    max_uses = max(usage_counts.values()) if usage_counts else 0
    weighted: List[str] = []
    for eff in pool:
        base_eff = eff.split("|")[0] if "|" in eff else eff
        uses = usage_counts.get(base_eff, 0)
        weight = max(1, max_uses + 1 - uses)
        weighted.extend([eff] * weight)

    return random.choice(weighted) if weighted else random.choice(pool)


def _build_animate_attr(effect: str) -> str:
    """Convert an effect string to data-animate (and optionally data-split-type) attributes."""
    if "|" in effect:
        animate, split_type = effect.split("|", 1)
        return f'data-animate="{animate}" data-split-type="{split_type}"'
    return f'data-animate="{effect}"'


def diversify_effects(
    html: str,
    used_effects: Optional[List[dict]] = None,
) -> Tuple[str, dict]:
    """Post-process assembled HTML to ensure all key elements have animations.

    - Injects data-animate on elements missing one
    - Optionally swaps existing effects (30% chance) for variation
    - Adds staggered data-delay within each section (resets per <section>)
    - Skips elements inside <nav>, <script>, <style>, <head>

    Args:
        html: The assembled HTML string.
        used_effects: List of effects_used dicts from previous sites
                      (for deprioritizing recently used effects).

    Returns:
        Tuple of (modified_html, effects_used_dict).
        effects_used_dict format: {"h1": ["text-split"], "img": ["clip-reveal", "scale-in"], ...}
    """
    if not html:
        return html, {}

    effects_used: Dict[str, List[str]] = {}

    def _record(pool_key: str, effect: str):
        base = effect.split("|")[0] if "|" in effect else effect
        effects_used.setdefault(pool_key, [])
        if base not in effects_used[pool_key]:
            effects_used[pool_key].append(base)

    # -----------------------------------------------------------------------
    # Step 1: Protect skip regions by replacing with placeholders
    # -----------------------------------------------------------------------
    skip_regions: List[Tuple[str, str]] = []

    def _save_skip(match):
        placeholder = f"__SKIP_{len(skip_regions)}__"
        skip_regions.append((placeholder, match.group(0)))
        return placeholder

    working = _SKIP_REGIONS_RE.sub(_save_skip, html)

    # -----------------------------------------------------------------------
    # Step 2: Delay counter state (resets per section)
    # -----------------------------------------------------------------------
    delay_counter = [0]

    def _next_delay() -> str:
        val = round(delay_counter[0] * 0.1, 1)
        delay_counter[0] += 1
        return f"{min(val, 0.8):.1f}"

    # -----------------------------------------------------------------------
    # Helper: inject or swap a data-animate on a matched tag
    # -----------------------------------------------------------------------
    def _inject_or_swap(
        tag_open: str, attrs: str, tag_close: str,
        pool_key: str, *, add_delay: bool = False,
    ) -> Optional[str]:
        """Returns new tag string, or None if no change needed."""
        has_animate = 'data-animate' in attrs

        if not has_animate:
            # Inject new effect
            effect = _pick_effect(pool_key, used_effects)
            animate_attr = _build_animate_attr(effect)
            delay_attr = ""
            if add_delay:
                dv = _next_delay()
                if float(dv) > 0:
                    delay_attr = f' data-delay="{dv}"'
            _record(pool_key, effect)
            return f'{tag_open} {animate_attr}{delay_attr}{attrs}{tag_close}'

        elif random.random() < SWAP_PROBABILITY:
            # Swap existing effect to a different one from the same pool
            effect = _pick_effect(pool_key, used_effects)
            animate_val = effect.split("|")[0] if "|" in effect else effect
            new_attrs = re.sub(
                r'data-animate="[^"]*"',
                f'data-animate="{animate_val}"',
                attrs,
            )
            if "|" in effect:
                split_type = effect.split("|")[1]
                if 'data-split-type' in new_attrs:
                    new_attrs = re.sub(
                        r'data-split-type="[^"]*"',
                        f'data-split-type="{split_type}"',
                        new_attrs,
                    )
                else:
                    new_attrs += f' data-split-type="{split_type}"'
            else:
                # Remove stale split-type if new effect doesn't use it
                new_attrs = re.sub(r'\s*data-split-type="[^"]*"', '', new_attrs)
            _record(pool_key, effect)
            return f'{tag_open}{new_attrs}{tag_close}'
        else:
            # Keep existing, just record it
            existing = re.search(r'data-animate="([^"]*)"', attrs)
            if existing:
                _record(pool_key, existing.group(1))
            return None  # no change

    # -----------------------------------------------------------------------
    # Step 3: Process each element type via regex (reverse order for safety)
    # -----------------------------------------------------------------------

    # --- Sections (entrance animation + delay counter reset) ---
    sec_pat = re.compile(r'(<section\b)([^>]*?)(>)', re.IGNORECASE | re.DOTALL)
    for m in reversed(list(sec_pat.finditer(working))):
        delay_counter[0] = 0  # reset delay for each section
        result = _inject_or_swap(m.group(1), m.group(2), m.group(3), "section_entrance")
        if result is not None:
            working = working[:m.start()] + result + working[m.end():]

    # --- Headings: h1, h2, h3 ---
    for tag in ["h1", "h2", "h3"]:
        pattern = re.compile(rf'(<{tag}\b)([^>]*?)(>)', re.IGNORECASE | re.DOTALL)
        for m in reversed(list(pattern.finditer(working))):
            result = _inject_or_swap(m.group(1), m.group(2), m.group(3), tag, add_delay=True)
            if result is not None:
                working = working[:m.start()] + result + working[m.end():]

    # --- Paragraphs ---
    p_pat = re.compile(r'(<p\b)([^>]*?)(>)', re.IGNORECASE | re.DOTALL)
    for m in reversed(list(p_pat.finditer(working))):
        result = _inject_or_swap(m.group(1), m.group(2), m.group(3), "p", add_delay=True)
        if result is not None:
            working = working[:m.start()] + result + working[m.end():]

    # --- Images ---
    img_pat = re.compile(r'(<img\b)([^>]*?)(/?>)', re.IGNORECASE | re.DOTALL)
    for m in reversed(list(img_pat.finditer(working))):
        attrs = m.group(2)
        if 'data-animate' not in attrs:
            effect = _pick_effect("img", used_effects)
            animate_attr = _build_animate_attr(effect)
            new_tag = f'{m.group(1)} {animate_attr}{attrs}{m.group(3)}'
            working = working[:m.start()] + new_tag + working[m.end():]
            _record("img", effect)

    # --- CTA links (with btn/cta/button/primary/action class) ---
    cta_link_pat = re.compile(
        r'(<a\b)([^>]*?class="[^"]*(?:btn|cta|button|primary|action)[^"]*"[^>]*?)(>)',
        re.IGNORECASE | re.DOTALL,
    )
    for m in reversed(list(cta_link_pat.finditer(working))):
        result = _inject_or_swap(m.group(1), m.group(2), m.group(3), "cta")
        if result is not None:
            working = working[:m.start()] + result + working[m.end():]

    # --- Buttons ---
    btn_pat = re.compile(r'(<button\b)([^>]*?)(>)', re.IGNORECASE | re.DOTALL)
    for m in reversed(list(btn_pat.finditer(working))):
        result = _inject_or_swap(m.group(1), m.group(2), m.group(3), "cta")
        if result is not None:
            working = working[:m.start()] + result + working[m.end():]

    # --- Divs with card/counter/decorative classes ---
    div_pat = re.compile(r'(<div\b)([^>]*?class="[^"]*"[^>]*?)(>)', re.IGNORECASE | re.DOTALL)
    for m in reversed(list(div_pat.finditer(working))):
        classes_match = re.search(r'class="([^"]*)"', m.group(2), re.IGNORECASE)
        if not classes_match:
            continue
        classes = classes_match.group(1).lower()
        pool_key = None
        if any(kw in classes for kw in ("card", "bento", "stagger-item", "feature-card", "pricing-card")):
            pool_key = "card"
        elif "counter" in classes or "data-counter" in m.group(2).lower():
            pool_key = "counter"
        elif any(kw in classes for kw in ("float", "decorative", "blob", "shape")):
            pool_key = "decorative"
        if pool_key:
            result = _inject_or_swap(
                m.group(1), m.group(2), m.group(3), pool_key,
                add_delay=(pool_key == "card"),
            )
            if result is not None:
                working = working[:m.start()] + result + working[m.end():]

    # -----------------------------------------------------------------------
    # Step 4: Restore skip regions
    # -----------------------------------------------------------------------
    for placeholder, original in skip_regions:
        working = working.replace(placeholder, original)

    count_added = sum(len(v) for v in effects_used.values())
    logger.info(
        f"Effect diversifier: applied/recorded {count_added} effect types "
        f"across {len(effects_used)} element categories"
    )

    return working, effects_used


# ---------------------------------------------------------------------------
# Database helpers for tracking effect usage per user
# ---------------------------------------------------------------------------

def get_recent_effects(db: Session, user_id: int, limit: int = 5) -> List[dict]:
    """Query the effect_usage table for a user's last N sites.

    Returns a list of effects_used dicts (most recent first).
    """
    try:
        result = db.execute(sql_text("""
            SELECT effects_json
            FROM effect_usage
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"user_id": user_id, "limit": limit})

        rows = result.fetchall()
        effects_list = []
        for row in rows:
            raw = row[0]
            if isinstance(raw, str):
                effects_list.append(json.loads(raw))
            elif isinstance(raw, dict):
                effects_list.append(raw)
        return effects_list
    except Exception as e:
        logger.warning(f"Could not fetch recent effects for user {user_id}: {e}")
        return []


def save_effect_usage(db: Session, user_id: int, site_id: int, effects_used: dict):
    """Insert a record into the effect_usage table."""
    try:
        db.execute(sql_text("""
            INSERT INTO effect_usage (user_id, site_id, effects_json, created_at)
            VALUES (:user_id, :site_id, :effects_json, NOW())
        """), {
            "user_id": user_id,
            "site_id": site_id,
            "effects_json": json.dumps(effects_used),
        })
        db.commit()
        logger.info(f"Saved effect usage for user {user_id}, site {site_id}")
    except Exception as e:
        logger.error(f"Failed to save effect usage for user {user_id}, site {site_id}: {e}")
        db.rollback()
