"""
Design Knowledge Service — Lightweight In-Memory Pattern Store

Stores design patterns and retrieves them via keyword-based relevance scoring.
Replaces ChromaDB (which required ~300MB for sentence-transformers) to fit
within Render free tier's 512MB memory limit.

Same public API as the previous ChromaDB-based implementation.
"""
import re
import random
import logging
from collections import Counter
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory pattern store
# ---------------------------------------------------------------------------
_patterns: Dict[str, dict] = {}  # id -> {document, metadata, tokens}
_ready = False

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

# Simple tokenizer: split on non-alphanumeric, lowercase, drop short tokens
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 2]


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
):
    """Add a design pattern to the knowledge base."""
    metadata = {
        "category": category,
        "tags": ",".join(tags or []),
        "complexity": complexity,
        "impact_score": impact_score,
    }
    if code_snippet:
        metadata["code_snippet"] = code_snippet[:4000]

    document = f"{content}\n\nCode:\n{code_snippet}" if code_snippet else content
    tokens = _tokenize(document + " " + " ".join(tags or []))

    _patterns[pattern_id] = {
        "document": document,
        "metadata": metadata,
        "tokens": tokens,
        "token_set": set(tokens),
    }


def add_patterns_batch(
    ids: List[str],
    documents: List[str],
    metadatas: List[dict],
):
    """Batch-add patterns (used by seed_all for speed)."""
    for pid, doc, meta in zip(ids, documents, metadatas):
        tags_str = meta.get("tags", "")
        tokens = _tokenize(doc + " " + tags_str)
        _patterns[pid] = {
            "document": doc,
            "metadata": meta,
            "tokens": tokens,
            "token_set": set(tokens),
        }


def search_patterns(query: str, n_results: int = 5, category: Optional[str] = None) -> List[Dict]:
    """Search for design patterns by keyword relevance scoring."""
    if not _patterns:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    query_set = set(query_tokens)
    scored = []

    for pid, data in _patterns.items():
        meta = data["metadata"]
        if category and meta.get("category") != category:
            continue

        # Score: count of matching unique tokens + bonus for tag matches
        common = query_set & data["token_set"]
        if not common:
            continue

        score = len(common)
        # Bonus for high impact patterns
        score += meta.get("impact_score", 5) * 0.1
        # Small random jitter to vary results across calls
        score += random.random() * 0.3

        scored.append((score, pid, data))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, pid, data in scored[:n_results]:
        results.append({
            "id": pid,
            "content": data["document"],
            "metadata": data["metadata"],
            "relevance": min(score / max(len(query_tokens), 1), 1.0),
        })
    return results


def get_patterns_by_category(category: str, limit: int = 20) -> List[Dict]:
    """Get all patterns in a category."""
    results = []
    for pid, data in _patterns.items():
        if data["metadata"].get("category") == category:
            results.append({
                "id": pid,
                "content": data["document"],
                "metadata": data["metadata"],
            })
            if len(results) >= limit:
                break
    return results


def get_creative_context(style_id: str, category_label: str, sections: Optional[List[str]] = None) -> str:
    """
    Build a creative context string for AI generation.
    Queries the knowledge base for relevant patterns based on the template style.
    Returns a formatted string to inject into AI prompts.
    """
    context_parts = []

    # PRIORITY 1: Professional blueprint for this business category
    blueprint_query = f"{category_label} professional website blueprint design guide"
    blueprints = search_patterns(blueprint_query, n_results=2, category="professional_blueprints")
    if blueprints:
        context_parts.append("## PROFESSIONAL SITE BLUEPRINT (follow this closely):")
        for bp in blueprints:
            context_parts.append(bp['content'][:600])

    # PRIORITY 2: Section-specific design references
    if sections:
        section_query = " ".join(sections[:4]) + " professional section design reference"
        refs = search_patterns(section_query, n_results=3, category="section_references")
        if refs:
            context_parts.append("\n## Section Design References:")
            for r in refs:
                meta = r["metadata"]
                context_parts.append(f"- {r['content'][:300]}")
                if meta.get("code_snippet"):
                    context_parts.append(f"  HTML: {meta['code_snippet'][:400]}")

    # Search for style-relevant animations
    style_query = f"{category_label} {style_id} website animations effects"
    animations = search_patterns(style_query, n_results=4, category="scroll_effects")
    if animations:
        context_parts.append("\n## Animation Effects to Apply:")
        for a in animations:
            meta = a["metadata"]
            context_parts.append(f"- {a['content'][:200]}")
            if meta.get("code_snippet"):
                context_parts.append(f"  Code: {meta['code_snippet'][:300]}")

    # Search for layout patterns
    layout_patterns = search_patterns(f"{category_label} layout design", n_results=3, category="layout_patterns")
    if layout_patterns:
        context_parts.append("\n## Layout Patterns:")
        for lp in layout_patterns:
            context_parts.append(f"- {lp['content'][:200]}")

    # Get creative prompts
    creative = search_patterns(f"creative {category_label} professional", n_results=4, category="creative_prompts")
    if creative:
        context_parts.append("\n## Creative Directives:")
        for c in creative:
            context_parts.append(f"- {c['content'][:150]}")

    # Get color palette suggestion
    palette = search_patterns(f"{category_label} color palette", n_results=2, category="color_palettes")
    if palette:
        context_parts.append("\n## Color Inspiration:")
        for p in palette:
            context_parts.append(f"- {p['content'][:200]}")

    # Get GSAP snippets for sections
    if sections:
        gsap_query = " ".join(sections[:3]) + " animation gsap"
        gsap = search_patterns(gsap_query, n_results=3, category="gsap_snippets")
        if gsap:
            context_parts.append("\n## GSAP Animations to Include:")
            for g in gsap:
                meta = g["metadata"]
                if meta.get("code_snippet"):
                    context_parts.append(f"- {meta['code_snippet'][:400]}")

    return "\n".join(context_parts) if context_parts else ""


def get_collection_stats() -> dict:
    """Get statistics about the knowledge base."""
    return {
        "total_patterns": len(_patterns),
        "collection_name": "design_patterns",
        "storage_path": "in-memory",
    }
