"""
Design Memory — remembers past generation briefs and results.

Uses SQLite (same DB as design_knowledge) to store:
- Design Briefs from the Director
- Generated theme/text summaries
- Quality scores

This allows the Director to avoid repeating the same design decisions
and learn from what worked well (high quality scores).
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_DB_PATH = _DB_DIR / "design_memory.db"

_initialized = False


def _ensure_db() -> None:
    """Create the memory database and tables."""
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(_DB_PATH))
    try:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS generation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                style_id TEXT NOT NULL DEFAULT '',
                business_name TEXT NOT NULL DEFAULT '',
                brief_json TEXT NOT NULL DEFAULT '{}',
                theme_summary TEXT NOT NULL DEFAULT '',
                quality_score REAL DEFAULT 0,
                hero_layout TEXT DEFAULT '',
                color_mood TEXT DEFAULT '',
                font_heading TEXT DEFAULT '',
                voice TEXT DEFAULT '',
                animation_intensity TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_memory_category
                ON generation_memory(category);
            CREATE INDEX IF NOT EXISTS idx_memory_created
                ON generation_memory(created_at DESC);

            -- FTS5 for searching past briefs by content
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                business_name, brief_json, theme_summary,
                content=generation_memory, content_rowid=id
            );

            CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON generation_memory BEGIN
                INSERT INTO memory_fts(rowid, business_name, brief_json, theme_summary)
                VALUES (new.id, new.business_name, new.brief_json, new.theme_summary);
            END;

            CREATE TRIGGER IF NOT EXISTS memory_ad AFTER DELETE ON generation_memory BEGIN
                INSERT INTO memory_fts(memory_fts, rowid, business_name, brief_json, theme_summary)
                VALUES ('delete', old.id, old.business_name, old.brief_json, old.theme_summary);
            END;
        """)
    finally:
        con.close()


def _get_conn() -> sqlite3.Connection:
    """Return a new connection, initializing the DB on first call."""
    global _initialized
    if not _initialized:
        _ensure_db()
        _initialized = True
    con = sqlite3.connect(str(_DB_PATH))
    con.row_factory = sqlite3.Row
    return con


def save_generation(
    category: str,
    style_id: str,
    business_name: str,
    brief: Dict[str, Any],
    theme_summary: str = "",
    quality_score: float = 0.0,
) -> int:
    """Save a completed generation's brief and results to memory."""
    brief_json = json.dumps(brief, ensure_ascii=False)

    hero_layout = brief.get("layout_strategy", {}).get("hero_layout", "")
    color_mood = brief.get("color_direction", {}).get("mood", "")
    font_heading = brief.get("typography_direction", {}).get("suggested_pairing", {}).get("heading", "")
    voice = brief.get("copywriting_direction", {}).get("voice", "")
    anim_intensity = brief.get("animation_direction", {}).get("intensity", "")

    con = _get_conn()
    try:
        cursor = con.execute(
            """INSERT INTO generation_memory
               (category, style_id, business_name, brief_json, theme_summary,
                quality_score, hero_layout, color_mood, font_heading, voice,
                animation_intensity)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (category, style_id, business_name, brief_json, theme_summary,
             quality_score, hero_layout, color_mood, font_heading, voice,
             anim_intensity),
        )
        con.commit()
        row_id = cursor.lastrowid
        logger.info(
            "[DesignMemory] Saved generation #%d: cat=%s, style=%s, mood=%s, score=%.0f",
            row_id, category, style_id, color_mood, quality_score,
        )
        return row_id
    finally:
        con.close()


def get_recent_briefs(
    category: str = "",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Get recent generation briefs, optionally filtered by category."""
    con = _get_conn()
    try:
        if category:
            rows = con.execute(
                """SELECT * FROM generation_memory
                   WHERE category = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (category, limit),
            ).fetchall()
        else:
            rows = con.execute(
                """SELECT * FROM generation_memory
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]
    finally:
        con.close()


def get_anti_repetition_context(
    category: str,
    limit: int = 5,
) -> str:
    """
    Build a concise context string for the Design Director
    describing what was used recently (to avoid repetition).

    Returns a formatted string like:
        Recent layouts: split-screen (2x), editorial (1x)
        Recent color moods: Nordic Clean, Ocean Depth
        Recent fonts: Space Grotesk, Playfair Display
        Recent voices: provocative+minimal, warm+storytelling
    """
    recent = get_recent_briefs(category=category, limit=limit)
    if not recent:
        return ""

    layouts = {}
    moods = []
    fonts = []
    voices = []

    for gen in recent:
        hl = gen.get("hero_layout", "")
        if hl:
            layouts[hl] = layouts.get(hl, 0) + 1
        cm = gen.get("color_mood", "")
        if cm and cm not in moods:
            moods.append(cm)
        fh = gen.get("font_heading", "")
        if fh and fh not in fonts:
            fonts.append(fh)
        v = gen.get("voice", "")
        if v and v not in voices:
            voices.append(v)

    parts = []
    if layouts:
        layout_str = ", ".join(f"{k} ({v}x)" for k, v in layouts.items())
        parts.append(f"Recent layouts used: {layout_str}")
    if moods:
        parts.append(f"Recent color moods: {', '.join(moods[:5])}")
    if fonts:
        parts.append(f"Recent heading fonts: {', '.join(fonts[:5])}")
    if voices:
        parts.append(f"Recent copy voices: {', '.join(voices[:5])}")

    if not parts:
        return ""

    return "AVOID REPEATING THESE (use something DIFFERENT):\n" + "\n".join(parts)


def get_best_briefs(
    category: str = "",
    min_score: float = 70.0,
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """Get the highest-scoring briefs for learning from successes."""
    con = _get_conn()
    try:
        if category:
            rows = con.execute(
                """SELECT * FROM generation_memory
                   WHERE category = ? AND quality_score >= ?
                   ORDER BY quality_score DESC LIMIT ?""",
                (category, min_score, limit),
            ).fetchall()
        else:
            rows = con.execute(
                """SELECT * FROM generation_memory
                   WHERE quality_score >= ?
                   ORDER BY quality_score DESC LIMIT ?""",
                (min_score, limit),
            ).fetchall()

        return [dict(row) for row in rows]
    finally:
        con.close()


def get_memory_stats() -> Dict[str, Any]:
    """Get statistics about the memory database."""
    con = _get_conn()
    try:
        total = con.execute("SELECT COUNT(*) as cnt FROM generation_memory").fetchone()
        avg_score = con.execute("SELECT AVG(quality_score) as avg FROM generation_memory").fetchone()
        categories = con.execute(
            "SELECT category, COUNT(*) as cnt FROM generation_memory GROUP BY category"
        ).fetchall()

        return {
            "total_generations": total["cnt"] if total else 0,
            "avg_quality_score": round(avg_score["avg"] or 0, 1) if avg_score else 0,
            "by_category": {row["category"]: row["cnt"] for row in categories},
        }
    finally:
        con.close()


def cleanup_old_records(keep_last: int = 50) -> int:
    """Delete old memory records, keeping the most recent N."""
    con = _get_conn()
    try:
        result = con.execute(
            """DELETE FROM generation_memory
               WHERE id NOT IN (
                   SELECT id FROM generation_memory
                   ORDER BY created_at DESC LIMIT ?
               )""",
            (keep_last,),
        )
        con.commit()
        deleted = result.rowcount
        if deleted > 0:
            logger.info("[DesignMemory] Cleaned up %d old records (kept %d)", deleted, keep_last)
        return deleted
    finally:
        con.close()
