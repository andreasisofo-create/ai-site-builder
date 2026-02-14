"""
Design Knowledge Vector Database Service
Uses ChromaDB to store and retrieve design patterns, animation effects,
GSAP code snippets, layout patterns, and creative prompts.
"""
import chromadb
from chromadb.config import Settings
import os
from typing import Dict, List, Optional

# Persistent storage path
CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")

# Singleton client
_client = None
_collection = None

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
]

def get_collection():
    """Get or create the design_patterns collection."""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name="design_patterns",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


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
    col = get_collection()
    metadata = {
        "category": category,
        "tags": ",".join(tags or []),
        "complexity": complexity,
        "impact_score": impact_score,
    }
    if code_snippet:
        metadata["code_snippet"] = code_snippet[:4000]  # ChromaDB metadata limit

    # Full document = content + code for better semantic search
    document = f"{content}\n\nCode:\n{code_snippet}" if code_snippet else content

    col.upsert(
        ids=[pattern_id],
        documents=[document],
        metadatas=[metadata],
    )


def search_patterns(query: str, n_results: int = 5, category: Optional[str] = None) -> List[Dict]:
    """Search for design patterns relevant to a query."""
    col = get_collection()
    where = {"category": category} if category else None

    results = col.query(
        query_texts=[query],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    patterns = []
    if results and results["ids"] and results["ids"][0]:
        for i, pid in enumerate(results["ids"][0]):
            patterns.append({
                "id": pid,
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "relevance": 1 - results["distances"][0][i],  # Convert distance to similarity
            })
    return patterns


def get_patterns_by_category(category: str, limit: int = 20) -> List[Dict]:
    """Get all patterns in a category."""
    col = get_collection()
    results = col.get(
        where={"category": category},
        limit=limit,
        include=["documents", "metadatas"],
    )

    patterns = []
    if results and results["ids"]:
        for i, pid in enumerate(results["ids"]):
            patterns.append({
                "id": pid,
                "content": results["documents"][i],
                "metadata": results["metadatas"][i],
            })
    return patterns


def get_creative_context(style_id: str, category_label: str, sections: Optional[List[str]] = None) -> str:
    """
    Build a creative context string for AI generation.
    Queries the knowledge base for relevant patterns based on the template style.
    Returns a formatted string to inject into AI prompts.
    """
    context_parts = []

    # Search for style-relevant animations
    style_query = f"{category_label} {style_id} website animations effects"
    animations = search_patterns(style_query, n_results=5, category="scroll_effects")
    if animations:
        context_parts.append("## Animation Effects to Apply:")
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
    creative = search_patterns(f"creative {category_label} professional", n_results=5, category="creative_prompts")
    if creative:
        context_parts.append("\n## Creative Directives:")
        for c in creative:
            context_parts.append(f"- {c['content'][:150]}")

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
    col = get_collection()
    count = col.count()
    return {
        "total_patterns": count,
        "collection_name": "design_patterns",
        "storage_path": CHROMA_PATH,
    }
