"""
Diversity Engine - 4-layer anti-repetition system.
Ensures no two clients receive visually identical sites.
"""
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text

logger = logging.getLogger(__name__)


def select_with_diversity(
    candidates: List[Dict[str, Any]],
    section_type: str,
    category: str,
    db: Session,
    lookback_days: int = 30
) -> Optional[Dict[str, Any]]:
    """Layer 2: Apply diversity penalty to pgvector similarity candidates."""
    if not candidates:
        return None

    # Get usage counts from last N days
    try:
        result = db.execute(sql_text("""
            SELECT component_id::text, COUNT(*) as uses
            FROM generation_log_components
            WHERE section_type = :section_type AND category = :category
              AND created_at > NOW() - MAKE_INTERVAL(days => :days)
            GROUP BY component_id
        """), {"section_type": section_type, "category": category, "days": lookback_days})

        usage_map = {str(r[0]): r[1] for r in result}
    except Exception as e:
        logger.warning(f"Could not fetch usage counts, skipping diversity penalty: {e}")
        usage_map = {}

    for c in candidates:
        uses = usage_map.get(str(c["id"]), 0)
        if uses == 0:
            multiplier = 1.00
        elif uses < 3:
            multiplier = 0.85
        elif uses < 10:
            multiplier = 0.65
        elif uses < 20:
            multiplier = 0.40
        else:
            multiplier = 0.20
        c["final_score"] = c.get("similarity_score", 0.5) * multiplier

    return max(candidates, key=lambda c: c["final_score"])


def compute_layout_hash(components_selected: Dict[str, str]) -> str:
    """Layer 3: Generate fingerprint for a component combination."""
    sorted_items = sorted(components_selected.items())
    hash_str = "|".join([f"{sec}:{comp}" for sec, comp in sorted_items])
    return hashlib.md5(hash_str.encode()).hexdigest()[:12]


def ensure_unique_layout(
    category: str,
    components: Dict[str, str],
    db: Session,
    max_retries: int = 3
) -> Tuple[Dict[str, str], str]:
    """Layer 3: Check hash uniqueness, force diversity if duplicate."""
    layout_hash = compute_layout_hash(components)

    try:
        existing = db.execute(sql_text(
            "SELECT id FROM generation_log WHERE layout_hash = :hash"
        ), {"hash": layout_hash}).fetchone()

        if existing:
            logger.warning(f"Layout hash {layout_hash} already exists, forcing diversity")
            components = force_diversity(components, category, db, n_replacements=2)
            layout_hash = compute_layout_hash(components)
    except Exception as e:
        logger.warning(f"Could not check layout uniqueness: {e}")

    return components, layout_hash


def force_diversity(
    components: Dict[str, str],
    category: str,
    db: Session,
    n_replacements: int = 2
) -> Dict[str, str]:
    """Force replace N components with alternatives to break duplicates."""
    priority_sections = ["hero", "about", "services", "gallery"]
    replaced = 0

    for section in priority_sections:
        if section not in components or replaced >= n_replacements:
            break

        current = components[section]
        try:
            result = db.execute(sql_text("""
                SELECT name FROM components_v2
                WHERE section_type = :section_type
                  AND name != :current_name
                  AND (cooldown_until IS NULL OR cooldown_until < NOW())
                  AND (:category = ANY(compatible_categories) OR compatible_categories IS NULL)
                ORDER BY usage_count ASC, RANDOM()
                LIMIT 1
            """), {"section_type": section, "current_name": current, "category": category})

            row = result.fetchone()
            if row:
                components[section] = row[0]
                replaced += 1
        except Exception as e:
            logger.warning(f"Could not find alternative for section {section}: {e}")

    return components


def update_cooldown(component_id: str, db: Session):
    """Layer 4: Set cooldown proportional to usage (4h base, 72h max)."""
    try:
        db.execute(sql_text("""
            UPDATE components_v2
            SET usage_count = usage_count + 1,
                last_used_at = NOW(),
                cooldown_until = NOW() + (INTERVAL '1 hour' * LEAST(72, 4 * (usage_count + 1)))
            WHERE id = :id::uuid
        """), {"id": component_id})
        db.commit()
    except Exception as e:
        logger.error(f"Failed to update cooldown for component {component_id}: {e}")
        db.rollback()


def get_diversity_metrics(db: Session, category: Optional[str] = None) -> Dict[str, Any]:
    """Dashboard: Return diversity health metrics."""
    try:
        # Diversity score per category
        query = """
            SELECT category,
                COUNT(DISTINCT layout_hash) as unique_layouts,
                COUNT(*) as total_generated,
                ROUND(COUNT(DISTINCT layout_hash)::numeric / NULLIF(COUNT(*), 0) * 100, 1) AS diversity_pct
            FROM generation_log
        """
        if category:
            query += " WHERE category = :category"
        query += " GROUP BY category ORDER BY diversity_pct ASC"

        params = {"category": category} if category else {}
        diversity_rows = db.execute(sql_text(query), params).fetchall()

        # Components at risk (used > 15 times in 30 days)
        risk_query = """
            SELECT c.name, c.section_type, COUNT(*) as uses_30d
            FROM generation_log_components glc
            JOIN components_v2 c ON glc.component_id = c.id
            WHERE glc.created_at > NOW() - INTERVAL '30 days'
            GROUP BY c.name, c.section_type
            HAVING COUNT(*) > 15
            ORDER BY uses_30d DESC
        """
        risk_rows = db.execute(sql_text(risk_query)).fetchall()

        # Components currently in cooldown
        cooldown_query = """
            SELECT COUNT(*) as in_cooldown,
                   (SELECT COUNT(*) FROM components_v2) as total
            FROM components_v2
            WHERE cooldown_until IS NOT NULL AND cooldown_until > NOW()
        """
        cooldown = db.execute(sql_text(cooldown_query)).fetchone()

        return {
            "diversity_by_category": [
                {
                    "category": r[0],
                    "unique_layouts": r[1],
                    "total_generated": r[2],
                    "diversity_pct": float(r[3]) if r[3] else 0
                }
                for r in diversity_rows
            ],
            "at_risk_components": [
                {"name": r[0], "section_type": r[1], "uses_30d": r[2]}
                for r in risk_rows
            ],
            "cooldown": {
                "in_cooldown": cooldown[0] if cooldown else 0,
                "total": cooldown[1] if cooldown else 0,
                "pct": round(cooldown[0] / max(cooldown[1], 1) * 100, 1) if cooldown else 0
            }
        }
    except Exception as e:
        logger.error(f"Failed to compute diversity metrics: {e}")
        return {
            "diversity_by_category": [],
            "at_risk_components": [],
            "cooldown": {"in_cooldown": 0, "total": 0, "pct": 0}
        }
