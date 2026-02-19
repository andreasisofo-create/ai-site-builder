"""
Embedding Service - Google text-embedding-004
Generates 768-dimensional vectors for semantic search via pgvector.
"""
import httpx
import logging
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"


async def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate a 768-dim embedding vector for the given text."""
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set, cannot generate embeddings")
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EMBED_URL}?key={settings.GEMINI_API_KEY}",
                json={
                    "model": "models/text-embedding-004",
                    "content": {"parts": [{"text": text}]},
                    "outputDimensionality": 768
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]["values"]
    except httpx.HTTPStatusError as e:
        logger.error(f"Embedding API HTTP error {e.response.status_code}: {e.response.text}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Embedding API request error: {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected embedding API response format: {e}")
        return None


async def generate_embeddings_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """Generate embeddings for multiple texts. Returns list of vectors."""
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set, cannot generate embeddings")
        return [None] * len(texts)

    if not texts:
        return []

    BATCH_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents"

    requests = [
        {
            "model": "models/text-embedding-004",
            "content": {"parts": [{"text": t}]},
            "outputDimensionality": 768
        }
        for t in texts
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BATCH_URL}?key={settings.GEMINI_API_KEY}",
                json={"requests": requests}
            )
            response.raise_for_status()
            data = response.json()
            return [emb["values"] for emb in data["embeddings"]]
    except httpx.HTTPStatusError as e:
        logger.error(f"Batch embedding API HTTP error {e.response.status_code}: {e.response.text}")
        return [None] * len(texts)
    except httpx.RequestError as e:
        logger.error(f"Batch embedding API request error: {e}")
        return [None] * len(texts)
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected batch embedding API response format: {e}")
        return [None] * len(texts)


def build_component_description(metadata: dict) -> str:
    """Build a descriptive text from component metadata for embedding generation."""
    parts = []
    if metadata.get("section_type"):
        parts.append(f"section type: {metadata['section_type']}")
    if metadata.get("variant_cluster"):
        parts.append(f"visual style: {metadata['variant_cluster']}")
    if metadata.get("mood_tags"):
        parts.append(f"mood: {' '.join(metadata['mood_tags'])}")
    if metadata.get("density"):
        parts.append(f"density: {metadata['density']}")
    if metadata.get("typography_style"):
        parts.append(f"typography: {metadata['typography_style']}")
    if metadata.get("animation_level"):
        parts.append(f"animation: {metadata['animation_level']}")
    if metadata.get("compatible_categories"):
        parts.append(f"categories: {' '.join(metadata['compatible_categories'])}")
    if metadata.get("gsap_effects"):
        parts.append(f"animations: {' '.join(metadata['gsap_effects'])}")
    return "\n".join(parts)
