"""
Usage Tracker - Persistent anti-repetition memory for component diversity.

Tracks which components have been used across ALL generations and provides
priority scoring so the selection algorithm picks less-used components.

Uses a dedicated SQLite database (usage_history.db) separate from the
generation_tracker design_knowledge.db. Thread-safe.

Integration points:
  - databinding_generator._select_components_deterministic() can call
    score_candidates() to rank variant pools before selection.
  - databinding_generator._log_generation() can call record_generation()
    after each successful build.
  - is_duplicate_layout() / get_similar_layouts() complement the existing
    layout_hash collision detection.
"""

import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_DB_PATH = os.path.join(_DB_DIR, "usage_history.db")

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS component_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id TEXT NOT NULL,
    generation_id TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT '',
    style TEXT NOT NULL DEFAULT '',
    used_at REAL NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE TABLE IF NOT EXISTS generation_log (
    generation_id TEXT PRIMARY KEY,
    category TEXT NOT NULL DEFAULT '',
    style TEXT NOT NULL DEFAULT '',
    components_used TEXT NOT NULL DEFAULT '{}',
    layout_hash TEXT NOT NULL DEFAULT '',
    created_at REAL NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_cu_component
    ON component_usage(component_id, used_at DESC);
CREATE INDEX IF NOT EXISTS idx_cu_category
    ON component_usage(category, used_at DESC);
CREATE INDEX IF NOT EXISTS idx_cu_generation
    ON component_usage(generation_id);
CREATE INDEX IF NOT EXISTS idx_gl_category
    ON generation_log(category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_gl_hash
    ON generation_log(layout_hash);
"""


class UsageTracker:
    """Persistent, thread-safe tracker for component usage across generations."""

    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _DB_PATH
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    # ------------------------------------------------------------------
    # Database setup
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        """Create database, tables, and indexes on first use."""
        db_dir = os.path.dirname(self._db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = self._get_conn()
        conn.executescript(_SCHEMA_SQL)

    def _get_conn(self) -> sqlite3.Connection:
        """Return (and cache) a single long-lived connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
        return self._conn

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_generation(
        self,
        generation_id: str,
        category: str,
        style: str,
        components_dict: Dict[str, str],
    ) -> None:
        """Record a completed generation and all its component usages.

        Args:
            generation_id: Unique ID for this generation.
            category: Template category (e.g. "restaurant", "saas").
            style: Template style ID (e.g. "restaurant-elegant").
            components_dict: Mapping of section -> variant_id
                (e.g. {"hero": "hero-split-01", "about": "about-team-01"}).
        """
        layout_hash = self.compute_layout_hash(components_dict)
        now = time.time()

        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO generation_log"
                    " (generation_id, category, style, components_used, layout_hash, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        generation_id,
                        category,
                        style,
                        json.dumps(components_dict, ensure_ascii=False),
                        layout_hash,
                        now,
                    ),
                )

                rows = [
                    (comp_id, generation_id, category, style, now)
                    for comp_id in components_dict.values()
                    if comp_id
                ]
                conn.executemany(
                    "INSERT INTO component_usage"
                    " (component_id, generation_id, category, style, used_at)"
                    " VALUES (?, ?, ?, ?, ?)",
                    rows,
                )

                conn.commit()
                logger.info(
                    "[UsageTracker] Recorded generation %s: %d components, hash=%s",
                    generation_id, len(rows), layout_hash[:8],
                )
            except Exception as e:
                logger.warning("[UsageTracker] Failed to record generation: %s", e)

    # ------------------------------------------------------------------
    # Usage queries
    # ------------------------------------------------------------------

    def get_usage_count(self, component_id: str, days: int = 30) -> int:
        """Return how many times a component was used in the last N days."""
        cutoff = time.time() - (days * 86400)
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM component_usage"
                " WHERE component_id = ? AND used_at >= ?",
                (component_id, cutoff),
            ).fetchone()
            return row["cnt"] if row else 0

    def get_usage_stats(self) -> Dict[str, Any]:
        """Return an overview of component usage across all recorded history.

        Returns dict with keys: total_generations, total_component_uses,
        most_used, least_used, never_used, by_section.
        """
        with self._lock:
            conn = self._get_conn()
            total_gen = conn.execute(
                "SELECT COUNT(*) AS cnt FROM generation_log"
            ).fetchone()["cnt"]

            total_uses = conn.execute(
                "SELECT COUNT(*) AS cnt FROM component_usage"
            ).fetchone()["cnt"]

            most = conn.execute(
                "SELECT component_id, COUNT(*) AS cnt"
                " FROM component_usage"
                " GROUP BY component_id"
                " ORDER BY cnt DESC LIMIT 10"
            ).fetchall()

            least = conn.execute(
                "SELECT component_id, COUNT(*) AS cnt"
                " FROM component_usage"
                " GROUP BY component_id"
                " ORDER BY cnt ASC LIMIT 10"
            ).fetchall()

            by_section: Dict[str, Dict[str, int]] = {}
            log_rows = conn.execute(
                "SELECT components_used FROM generation_log"
            ).fetchall()
            for row in log_rows:
                try:
                    comps = json.loads(row["components_used"] or "{}")
                    for section, variant in comps.items():
                        if section not in by_section:
                            by_section[section] = {}
                        by_section[section][variant] = (
                            by_section[section].get(variant, 0) + 1
                        )
                except (json.JSONDecodeError, TypeError):
                    pass

            never_used = self._find_never_used_components(conn)

            return {
                "total_generations": total_gen,
                "total_component_uses": total_uses,
                "most_used": [(r["component_id"], r["cnt"]) for r in most],
                "least_used": [(r["component_id"], r["cnt"]) for r in least],
                "never_used": never_used,
                "by_section": by_section,
            }

    def _find_never_used_components(self, conn: sqlite3.Connection) -> List[str]:
        """Cross-reference components.json with usage data to find unused variants."""
        components_json_path = os.path.join(
            os.path.dirname(__file__), "..", "components", "components.json"
        )
        try:
            with open(components_json_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        all_ids: set = set()
        categories = registry.get("categories", {})
        for cat_data in categories.values():
            for variant in cat_data.get("variants", []):
                vid = variant.get("id")
                if vid:
                    all_ids.add(vid)

        used_ids = set()
        rows = conn.execute(
            "SELECT DISTINCT component_id FROM component_usage"
        ).fetchall()
        for row in rows:
            used_ids.add(row["component_id"])

        return sorted(all_ids - used_ids)

    # ------------------------------------------------------------------
    # Priority scoring
    # ------------------------------------------------------------------

    def get_priority_score(
        self, component_id: str, category: str, days: int = 30
    ) -> float:
        """Return a novelty priority score for a component (0.0 to 1.0).

        Higher = less used = should be preferred.
        Tiers: 0 uses -> 1.0, 1-2 -> 0.8, 3-5 -> 0.6,
               6-10 -> 0.4, 11-20 -> 0.2, 20+ -> 0.1
        """
        cutoff = time.time() - (days * 86400)
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM component_usage"
                " WHERE component_id = ? AND category = ? AND used_at >= ?",
                (component_id, category, cutoff),
            ).fetchone()
            count = row["cnt"] if row else 0

        return self._count_to_priority(count)

    @staticmethod
    def _count_to_priority(count: int) -> float:
        """Map usage count to a priority score."""
        if count == 0:
            return 1.0
        elif count <= 2:
            return 0.8
        elif count <= 5:
            return 0.6
        elif count <= 10:
            return 0.4
        elif count <= 20:
            return 0.2
        else:
            return 0.1

    def score_candidates(
        self,
        candidates: List[str],
        category: str,
        relevance_scores: Optional[Dict[str, float]] = None,
        days: int = 30,
    ) -> List[Tuple[str, float]]:
        """Score and rank candidate components by combined relevance + novelty.

        combined_score = relevance * 0.6 + novelty_priority * 0.4

        Args:
            candidates: List of component variant IDs to evaluate.
            category: Template category for scoped usage lookup.
            relevance_scores: Optional dict mapping component_id to float 0-1.
                If not provided, all candidates get relevance=1.0.
            days: Lookback window in days.

        Returns:
            List of (component_id, combined_score) sorted best-first.
        """
        if not candidates:
            return []

        if relevance_scores is None:
            relevance_scores = {}

        cutoff = time.time() - (days * 86400)

        with self._lock:
            conn = self._get_conn()
            placeholders = ",".join("?" for _ in candidates)
            query = (
                "SELECT component_id, COUNT(*) AS cnt"
                " FROM component_usage"
                " WHERE component_id IN (%s)"
                " AND category = ? AND used_at >= ?"
                " GROUP BY component_id"
            ) % placeholders
            rows = conn.execute(
                query,
                [*candidates, category, cutoff],
            ).fetchall()
            counts = {r["component_id"]: r["cnt"] for r in rows}

        scored: List[Tuple[str, float]] = []
        for cid in candidates:
            relevance = relevance_scores.get(cid, 1.0)
            novelty = self._count_to_priority(counts.get(cid, 0))
            combined = relevance * 0.6 + novelty * 0.4
            scored.append((cid, combined))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    # ------------------------------------------------------------------
    # Layout hash / duplicate detection
    # ------------------------------------------------------------------

    @staticmethod
    def compute_layout_hash(components_dict: Dict[str, str]) -> str:
        """Compute an MD5 hash of the component combination.

        Sorted by section name for order-independence.
        """
        sorted_items = sorted(components_dict.items())
        key = "|".join(f"{s}={v}" for s, v in sorted_items)
        return hashlib.md5(key.encode()).hexdigest()

    def is_duplicate_layout(self, layout_hash: str) -> bool:
        """Check if this exact component combination was already generated."""
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT 1 FROM generation_log WHERE layout_hash = ? LIMIT 1",
                (layout_hash,),
            ).fetchone()
            return row is not None

    def get_similar_layouts(
        self, components_dict: Dict[str, str], threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find past layouts with >= threshold overlap with the given components.

        Uses Jaccard similarity: |intersection| / |union| on the component set.

        Returns list of dicts with generation_id, category, style, overlap, created_at.
        """
        target_set = set(f"{s}={v}" for s, v in components_dict.items())
        if not target_set:
            return []

        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT generation_id, category, style, components_used, created_at"
                " FROM generation_log ORDER BY created_at DESC LIMIT 200"
            ).fetchall()

        similar: List[Dict[str, Any]] = []
        for row in rows:
            try:
                comps = json.loads(row["components_used"] or "{}")
            except (json.JSONDecodeError, TypeError):
                continue
            other_set = set(f"{s}={v}" for s, v in comps.items())
            if not other_set:
                continue
            intersection = len(target_set & other_set)
            union = len(target_set | other_set)
            overlap = intersection / union if union > 0 else 0.0

            if overlap >= threshold:
                similar.append({
                    "generation_id": row["generation_id"],
                    "category": row["category"],
                    "style": row["style"],
                    "overlap": round(overlap, 3),
                    "created_at": row["created_at"],
                })

        similar.sort(key=lambda x: x["overlap"], reverse=True)
        return similar

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def prune_old_records(self, days: int = 90) -> int:
        """Remove component_usage and generation_log records older than N days.

        Returns number of deleted rows across both tables.
        """
        cutoff = time.time() - (days * 86400)
        deleted = 0

        with self._lock:
            conn = self._get_conn()
            try:
                r1 = conn.execute(
                    "DELETE FROM component_usage WHERE used_at < ?", (cutoff,)
                )
                deleted += r1.rowcount

                r2 = conn.execute(
                    "DELETE FROM generation_log WHERE created_at < ?", (cutoff,)
                )
                deleted += r2.rowcount

                conn.commit()
                if deleted > 0:
                    logger.info(
                        "[UsageTracker] Pruned %d records older than %d days",
                        deleted, days,
                    )
            except Exception as e:
                logger.warning("[UsageTracker] Prune failed: %s", e)

        return deleted


# ---------------------------------------------------------------------------
# Module-level singleton for easy import
# ---------------------------------------------------------------------------
usage_tracker = UsageTracker()
