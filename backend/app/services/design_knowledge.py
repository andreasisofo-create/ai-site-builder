"""
Design Knowledge Service — SQLite FTS5 Pattern Store

Stores design patterns and retrieves them via BM25 full-text search with
diversity jitter.  Uses SQLite FTS5 (stdlib, zero dependencies) for proper
ranked retrieval while staying within Render free-tier memory limits.

Same public API as the previous in-memory implementation.
"""
import os
import re
import math
import random
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database location
# ---------------------------------------------------------------------------
_DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_DB_PATH = _DB_DIR / "design_knowledge.db"

CATEGORIES = [
    "scroll_effects",
    "text_animations",
    "image_effects",
    "section_transitions",
    "micro_interactions",
    "color_palettes",
    "layout_patterns",
    "typography",
    "gsap_snippets",
    "creative_prompts",
    "professional_blueprints",
    "section_references",
]

# ---------------------------------------------------------------------------
# Connection helpers (thread-safe: one connection per call)
# ---------------------------------------------------------------------------

def _ensure_db() -> None:
    """Create the database directory, tables, and FTS triggers if needed."""
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(_DB_PATH))
    try:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                html_snippet TEXT DEFAULT '',
                category TEXT NOT NULL,
                section_type TEXT DEFAULT '',
                style_tags TEXT DEFAULT '',
                mood TEXT DEFAULT '',
                complexity TEXT DEFAULT 'medium',
                impact_score INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts USING fts5(
                content, html_snippet, style_tags, mood,
                content=patterns, content_rowid=rowid
            );

            -- Triggers to keep FTS in sync with the main table
            CREATE TRIGGER IF NOT EXISTS patterns_ai AFTER INSERT ON patterns BEGIN
                INSERT INTO patterns_fts(rowid, content, html_snippet, style_tags, mood)
                VALUES (new.rowid, new.content, new.html_snippet, new.style_tags, new.mood);
            END;

            CREATE TRIGGER IF NOT EXISTS patterns_ad AFTER DELETE ON patterns BEGIN
                INSERT INTO patterns_fts(patterns_fts, rowid, content, html_snippet, style_tags, mood)
                VALUES ('delete', old.rowid, old.content, old.html_snippet, old.style_tags, old.mood);
            END;

            CREATE TRIGGER IF NOT EXISTS patterns_au AFTER UPDATE ON patterns BEGIN
                INSERT INTO patterns_fts(patterns_fts, rowid, content, html_snippet, style_tags, mood)
                VALUES ('delete', old.rowid, old.content, old.html_snippet, old.style_tags, old.mood);
                INSERT INTO patterns_fts(rowid, content, html_snippet, style_tags, mood)
                VALUES (new.rowid, new.content, new.html_snippet, new.style_tags, new.mood);
            END;

            CREATE INDEX IF NOT EXISTS idx_patterns_category ON patterns(category);

            -- Category design guides table
            CREATE TABLE IF NOT EXISTS category_guides (
                category TEXT PRIMARY KEY,
                structure TEXT NOT NULL DEFAULT '',
                visual_style TEXT NOT NULL DEFAULT '',
                ux_patterns TEXT NOT NULL DEFAULT '',
                hero_section TEXT NOT NULL DEFAULT '',
                content_strategy TEXT NOT NULL DEFAULT '',
                animations TEXT NOT NULL DEFAULT '',
                cta_design TEXT NOT NULL DEFAULT '',
                photo_treatment TEXT NOT NULL DEFAULT '',
                typography TEXT NOT NULL DEFAULT '',
                common_mistakes TEXT NOT NULL DEFAULT '',
                trends_2025 TEXT NOT NULL DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    finally:
        con.close()


_initialized = False


def _get_conn() -> sqlite3.Connection:
    """Return a new connection, initializing the DB on first call."""
    global _initialized
    if not _initialized:
        _ensure_db()
        _initialized = True
    con = sqlite3.connect(str(_DB_PATH))
    con.row_factory = sqlite3.Row
    return con


# ---------------------------------------------------------------------------
# FTS query builder
# ---------------------------------------------------------------------------
_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _fts_query(text: str) -> str:
    """Convert free-form text into an FTS5 OR query, stripping short tokens."""
    tokens = [t.lower() for t in _TOKEN_RE.findall(text) if len(t) > 2]
    if not tokens:
        return ""
    # Use OR matching with implicit prefix for partial matches
    return " OR ".join(f'"{t}"' for t in dict.fromkeys(tokens))


# ---------------------------------------------------------------------------
# Public API (drop-in replacement)
# ---------------------------------------------------------------------------

def add_pattern(
    pattern_id: str,
    content: str,
    category: str,
    tags: Optional[List[str]] = None,
    complexity: str = "medium",
    impact_score: int = 5,
    code_snippet: str = "",
) -> None:
    """Add a design pattern to the knowledge base."""
    document = f"{content}\n\nCode:\n{code_snippet}" if code_snippet else content
    style_tags = ",".join(tags or [])

    con = _get_conn()
    try:
        con.execute(
            """INSERT OR REPLACE INTO patterns
               (id, content, html_snippet, category, style_tags, complexity, impact_score)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (pattern_id, document, code_snippet[:4000] if code_snippet else "",
             category, style_tags, complexity, impact_score),
        )
        con.commit()
    finally:
        con.close()


def add_patterns_batch(
    ids: List[str],
    documents: List[str],
    metadatas: List[dict],
) -> None:
    """Batch-add patterns (used by seed_all for speed)."""
    con = _get_conn()
    try:
        rows = []
        for pid, doc, meta in zip(ids, documents, metadatas):
            rows.append((
                pid,
                doc,
                meta.get("code_snippet", ""),
                meta.get("category", ""),
                meta.get("tags", ""),
                meta.get("complexity", "medium"),
                meta.get("impact_score", 5),
            ))
        con.executemany(
            """INSERT OR REPLACE INTO patterns
               (id, content, html_snippet, category, style_tags, complexity, impact_score)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        con.commit()
    finally:
        con.close()


def add_html_snippet(
    pattern_id: str,
    content: str,
    html_snippet: str,
    category: str,
    section_type: str = "",
    mood: str = "",
    style_tags: str = "",
    impact_score: int = 5,
) -> None:
    """Add a pattern with an HTML snippet (richer variant of add_pattern)."""
    con = _get_conn()
    try:
        con.execute(
            """INSERT OR REPLACE INTO patterns
               (id, content, html_snippet, category, section_type, mood, style_tags, impact_score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (pattern_id, content, html_snippet, category, section_type,
             mood, style_tags, impact_score),
        )
        con.commit()
    finally:
        con.close()


def search_patterns(
    query: str,
    n_results: int = 5,
    category: Optional[str] = None,
) -> List[Dict]:
    """Search for design patterns using FTS5 BM25 ranking with diversity jitter."""
    fts_q = _fts_query(query)
    if not fts_q:
        return []

    con = _get_conn()
    try:
        if category:
            sql = """
                SELECT p.*, bm25(patterns_fts) AS score
                FROM patterns p
                JOIN patterns_fts ON patterns_fts.rowid = p.rowid
                WHERE patterns_fts MATCH ? AND p.category = ?
                ORDER BY score * (0.8 + 0.4 * abs(random()) / 9223372036854775807.0)
                LIMIT ?
            """
            rows = con.execute(sql, (fts_q, category, n_results)).fetchall()
        else:
            sql = """
                SELECT p.*, bm25(patterns_fts) AS score
                FROM patterns p
                JOIN patterns_fts ON patterns_fts.rowid = p.rowid
                WHERE patterns_fts MATCH ?
                ORDER BY score * (0.8 + 0.4 * abs(random()) / 9223372036854775807.0)
                LIMIT ?
            """
            rows = con.execute(sql, (fts_q, n_results)).fetchall()

        results = []
        for row in rows:
            # bm25() returns negative values; lower = better match
            raw_score = abs(row["score"]) if row["score"] else 0
            metadata = {
                "category": row["category"],
                "tags": row["style_tags"] or "",
                "complexity": row["complexity"],
                "impact_score": row["impact_score"],
            }
            if row["html_snippet"]:
                metadata["code_snippet"] = row["html_snippet"]
            results.append({
                "id": row["id"],
                "content": row["content"],
                "metadata": metadata,
                "relevance": min(raw_score / 10.0, 1.0),
            })
        return results
    finally:
        con.close()


def get_patterns_by_category(category: str, limit: int = 20) -> List[Dict]:
    """Get all patterns in a category."""
    con = _get_conn()
    try:
        rows = con.execute(
            "SELECT * FROM patterns WHERE category = ? LIMIT ?",
            (category, limit),
        ).fetchall()
        results = []
        for row in rows:
            metadata = {
                "category": row["category"],
                "tags": row["style_tags"] or "",
                "complexity": row["complexity"],
                "impact_score": row["impact_score"],
            }
            if row["html_snippet"]:
                metadata["code_snippet"] = row["html_snippet"]
            results.append({
                "id": row["id"],
                "content": row["content"],
                "metadata": metadata,
            })
        return results
    finally:
        con.close()


# ---------------------------------------------------------------------------
# MMR (Maximal Marginal Relevance) for diversity
# ---------------------------------------------------------------------------

def _jaccard_similarity(a: str, b: str) -> float:
    """Token-level Jaccard similarity between two strings."""
    tokens_a = set(t.lower() for t in _TOKEN_RE.findall(a) if len(t) > 2)
    tokens_b = set(t.lower() for t in _TOKEN_RE.findall(b) if len(t) > 2)
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def _mmr_rerank(
    results: List[Dict],
    target_count: int,
    lambda_param: float = 0.6,
) -> List[Dict]:
    """
    Re-rank results using Maximal Marginal Relevance.
    Balances relevance vs. diversity: higher lambda = more relevance.
    """
    if len(results) <= target_count:
        return results

    selected: List[Dict] = []
    remaining = list(results)

    # Always pick the top-scoring result first
    selected.append(remaining.pop(0))

    while len(selected) < target_count and remaining:
        best_idx = 0
        best_mmr = -float("inf")

        for i, candidate in enumerate(remaining):
            relevance = candidate.get("relevance", 0)
            # Max similarity to any already-selected result
            max_sim = max(
                _jaccard_similarity(candidate["content"], s["content"])
                for s in selected
            )
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr_score > best_mmr:
                best_mmr = mmr_score
                best_idx = i

        selected.append(remaining.pop(best_idx))

    return selected


# ---------------------------------------------------------------------------
# Creative context builder
# ---------------------------------------------------------------------------

def get_creative_context(
    style_id: str,
    category_label: str,
    sections: Optional[List[str]] = None,
) -> str:
    """
    Build a creative context string for AI generation.
    Queries the knowledge base for relevant patterns based on the template style.
    Uses MMR re-ranking to maximize diversity across results.
    Returns a formatted string to inject into AI prompts.
    """
    context_parts: List[str] = []

    # PRIORITY 0: Category-specific design guide (comprehensive expert knowledge)
    category_guide_text = get_category_guide_prompt(category_label)
    if category_guide_text:
        context_parts.append(category_guide_text)

    # PRIORITY 1: Professional blueprint for this business category
    blueprint_query = f"{category_label} professional website blueprint design guide"
    blueprints = search_patterns(blueprint_query, n_results=4, category="professional_blueprints")
    blueprints = _mmr_rerank(blueprints, 2)
    if blueprints:
        context_parts.append("## PROFESSIONAL SITE BLUEPRINT (follow this closely):")
        for bp in blueprints:
            context_parts.append(bp["content"][:600])

    # PRIORITY 2: Section-specific design references
    if sections:
        section_query = " ".join(sections[:4]) + " professional section design reference"
        refs = search_patterns(section_query, n_results=6, category="section_references")
        refs = _mmr_rerank(refs, 3)
        if refs:
            context_parts.append("\n## Section Design References:")
            for r in refs:
                meta = r["metadata"]
                context_parts.append(f"- {r['content'][:300]}")
                if meta.get("code_snippet"):
                    context_parts.append(f"  HTML: {meta['code_snippet'][:400]}")

    # Search for style-relevant animations
    style_query = f"{category_label} {style_id} website animations effects"
    animations = search_patterns(style_query, n_results=8, category="scroll_effects")
    animations = _mmr_rerank(animations, 4)
    if animations:
        context_parts.append("\n## Animation Effects to Apply:")
        for a in animations:
            meta = a["metadata"]
            context_parts.append(f"- {a['content'][:200]}")
            if meta.get("code_snippet"):
                context_parts.append(f"  Code: {meta['code_snippet'][:300]}")

    # Search for layout patterns
    layout_patterns = search_patterns(f"{category_label} layout design", n_results=6, category="layout_patterns")
    layout_patterns = _mmr_rerank(layout_patterns, 3)
    if layout_patterns:
        context_parts.append("\n## Layout Patterns:")
        for lp in layout_patterns:
            context_parts.append(f"- {lp['content'][:200]}")

    # Get creative prompts
    creative = search_patterns(f"creative {category_label} professional", n_results=8, category="creative_prompts")
    creative = _mmr_rerank(creative, 4)
    if creative:
        context_parts.append("\n## Creative Directives:")
        for c in creative:
            context_parts.append(f"- {c['content'][:150]}")

    # Get color palette suggestion
    palette = search_patterns(f"{category_label} color palette", n_results=4, category="color_palettes")
    palette = _mmr_rerank(palette, 2)
    if palette:
        context_parts.append("\n## Color Inspiration:")
        for p in palette:
            context_parts.append(f"- {p['content'][:200]}")

    # Get GSAP snippets for sections
    if sections:
        gsap_query = " ".join(sections[:3]) + " animation gsap"
        gsap = search_patterns(gsap_query, n_results=6, category="gsap_snippets")
        gsap = _mmr_rerank(gsap, 3)
        if gsap:
            context_parts.append("\n## GSAP Animations to Include:")
            for g in gsap:
                meta = g["metadata"]
                if meta.get("code_snippet"):
                    context_parts.append(f"- {meta['code_snippet'][:400]}")

    return "\n".join(context_parts) if context_parts else ""


# ---------------------------------------------------------------------------
# Category Design Guides
# ---------------------------------------------------------------------------

def upsert_category_guide(category: str, guide: Dict[str, str]) -> None:
    """Insert or update a category design guide."""
    con = _get_conn()
    try:
        con.execute(
            """INSERT OR REPLACE INTO category_guides
               (category, structure, visual_style, ux_patterns, hero_section,
                content_strategy, animations, cta_design, photo_treatment,
                typography, common_mistakes, trends_2025)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                category,
                guide.get("structure", ""),
                guide.get("visual_style", ""),
                guide.get("ux_patterns", ""),
                guide.get("hero_section", ""),
                guide.get("content_strategy", ""),
                guide.get("animations", ""),
                guide.get("cta_design", ""),
                guide.get("photo_treatment", ""),
                guide.get("typography", ""),
                guide.get("common_mistakes", ""),
                guide.get("trends_2025", ""),
            ),
        )
        con.commit()
    finally:
        con.close()


def get_category_guide(category: str) -> Optional[Dict[str, str]]:
    """Get the design guide for a specific category. Returns None if not found."""
    con = _get_conn()
    try:
        row = con.execute(
            "SELECT * FROM category_guides WHERE category = ?", (category,)
        ).fetchone()
        if not row:
            return None
        return {
            "category": row["category"],
            "structure": row["structure"],
            "visual_style": row["visual_style"],
            "ux_patterns": row["ux_patterns"],
            "hero_section": row["hero_section"],
            "content_strategy": row["content_strategy"],
            "animations": row["animations"],
            "cta_design": row["cta_design"],
            "photo_treatment": row["photo_treatment"],
            "typography": row["typography"],
            "common_mistakes": row["common_mistakes"],
            "trends_2025": row["trends_2025"],
        }
    finally:
        con.close()


def get_category_guide_prompt(category: str) -> str:
    """Get a formatted prompt string with design guidance for the category.
    This is the main function called by the generation pipeline."""
    guide = get_category_guide(category)
    if not guide:
        return ""

    parts = [f"## DESIGN GUIDE: {category.upper()} WEBSITE"]
    field_labels = {
        "structure": "Site Structure & Section Flow",
        "visual_style": "Visual Style & Colors",
        "ux_patterns": "UX Patterns & Navigation",
        "hero_section": "Hero Section Design",
        "content_strategy": "Content Strategy",
        "animations": "Animations & Scroll Effects",
        "cta_design": "CTA & Button Design",
        "photo_treatment": "Photo & Image Treatment",
        "typography": "Typography Rules",
        "common_mistakes": "AVOID These Mistakes",
        "trends_2025": "Current Trends (2025-2026)",
    }
    for field, label in field_labels.items():
        value = guide.get(field, "")
        if value:
            parts.append(f"\n### {label}\n{value}")

    return "\n".join(parts)


def get_collection_stats() -> dict:
    """Get statistics about the knowledge base."""
    con = _get_conn()
    try:
        row = con.execute("SELECT COUNT(*) as cnt FROM patterns").fetchone()
        total = row["cnt"] if row else 0
        return {
            "total_patterns": total,
            "collection_name": "design_patterns",
            "storage_path": str(_DB_PATH),
        }
    finally:
        con.close()
