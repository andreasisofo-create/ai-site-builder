"""Stock photo API client — Pexels (primary) + Unsplash (fallback).

Provides category-aware, section-aware image search for site generation.
Images are returned as CDN URLs ready for direct use in HTML.

Usage:
    from app.services.images.stock_api import stock_client

    photos = await stock_client.get_section_photos("restaurant", "hero")
"""

import logging
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, FrozenSet, List, Optional, Tuple

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StockPhoto:
    """A single stock photo ready for HTML embedding."""

    url: str
    width: int
    height: int
    photographer: str
    alt_text: str
    source: str = "pexels"  # "pexels" or "unsplash"


# ---------------------------------------------------------------------------
# Category-specific search keywords
# ---------------------------------------------------------------------------

_CATEGORY_KEYWORDS: Dict[str, str] = {
    "restaurant": "restaurant food cuisine dining interior",
    "saas": "technology software workspace modern",
    "portfolio": "creative design art studio",
    "ecommerce": "products shopping retail luxury",
    "business": "corporate office professional team",
    "blog": "writing workspace creative coffee",
    "event": "event conference celebration party",
}

# Section-type search configuration
# (query_suffix, default_orientation, default_count)
_SECTION_CONFIG: Dict[str, Dict[str, str]] = {
    "hero": {
        "suffix": "professional",
        "orientation": "landscape",
        "size": "large",
    },
    "gallery": {
        "suffix": "",
        "orientation": "landscape",
        "size": "medium",
    },
    "about": {
        "suffix": "team workspace",
        "orientation": "landscape",
        "size": "medium",
    },
    "team": {
        "suffix": "professional portrait business",
        "orientation": "portrait",
        "size": "small",
    },
    "services": {
        "suffix": "service professional",
        "orientation": "landscape",
        "size": "medium",
    },
    "testimonials": {
        "suffix": "professional portrait headshot",
        "orientation": "square",
        "size": "small",
    },
}

# Gallery sub-keywords by category (more specific than hero)
_GALLERY_KEYWORDS: Dict[str, str] = {
    "restaurant": "food dishes cuisine plating",
    "saas": "dashboard interface app screen",
    "portfolio": "artwork project creative work",
    "ecommerce": "products items merchandise",
    "business": "office workspace meeting",
    "blog": "writing laptop notebook desk",
    "event": "party celebration gathering venue",
}


# ---------------------------------------------------------------------------
# In-memory LRU cache with TTL
# ---------------------------------------------------------------------------

class _TTLCache:
    """Thread-safe in-memory cache with time-to-live eviction.

    Stores immutable tuples of StockPhoto to avoid mutation issues.
    Max 256 entries, 1 hour TTL.
    """

    def __init__(self, max_size: int = 256, ttl_seconds: int = 3600) -> None:
        self._store: Dict[str, Tuple[float, Tuple[StockPhoto, ...]]] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Tuple[StockPhoto, ...]]:
        entry = self._store.get(key)
        if entry is None:
            return None
        ts, value = entry
        if time.monotonic() - ts > self._ttl:
            del self._store[key]
            return None
        return value

    def put(self, key: str, value: List[StockPhoto]) -> None:
        # Evict oldest entries if at capacity
        if len(self._store) >= self._max_size:
            oldest_key = min(self._store, key=lambda k: self._store[k][0])
            del self._store[oldest_key]
        self._store[key] = (time.monotonic(), tuple(value))

    def clear(self) -> None:
        self._store.clear()


# ---------------------------------------------------------------------------
# Rate limiter (sliding window)
# ---------------------------------------------------------------------------

class _RateLimiter:
    """Simple sliding-window rate limiter.

    Pexels allows 200 requests/hour. We track timestamps of recent requests
    and reject if the window is full.
    """

    def __init__(self, max_requests: int = 180, window_seconds: int = 3600) -> None:
        # Use 180 instead of 200 to leave headroom
        self._max = max_requests
        self._window = window_seconds
        self._timestamps: List[float] = []

    def allow(self) -> bool:
        now = time.monotonic()
        # Remove timestamps outside the window
        self._timestamps = [t for t in self._timestamps if now - t < self._window]
        if len(self._timestamps) >= self._max:
            return False
        self._timestamps.append(now)
        return True

    @property
    def remaining(self) -> int:
        now = time.monotonic()
        self._timestamps = [t for t in self._timestamps if now - t < self._window]
        return max(0, self._max - len(self._timestamps))


# ---------------------------------------------------------------------------
# Pexels client
# ---------------------------------------------------------------------------

class PexelsClient:
    """Async Pexels API client with Unsplash fallback.

    Attributes:
        _pexels_key: Pexels API key (from env).
        _unsplash_key: Unsplash access key (optional fallback).
        _http: Shared httpx.AsyncClient (created lazily).
        _cache: In-memory TTL cache for search results.
        _rate_limiter: Sliding-window rate limiter for Pexels.
    """

    PEXELS_BASE = "https://api.pexels.com/v1"
    UNSPLASH_BASE = "https://api.unsplash.com"

    def __init__(self) -> None:
        self._pexels_key: str = getattr(settings, "PEXELS_API_KEY", "")
        self._unsplash_key: str = getattr(settings, "UNSPLASH_ACCESS_KEY", "")
        self._http: Optional[httpx.AsyncClient] = None
        self._cache = _TTLCache(max_size=256, ttl_seconds=3600)
        self._rate_limiter = _RateLimiter(max_requests=180, window_seconds=3600)

    # -- lifecycle -----------------------------------------------------------

    def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=10.0)
        return self._http

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._http is not None and not self._http.is_closed:
            await self._http.aclose()
            self._http = None

    # -- public API ----------------------------------------------------------

    async def search_photos(
        self,
        query: str,
        section_type: str = "hero",
        count: int = 6,
        orientation: str = "landscape",
    ) -> List[StockPhoto]:
        """Search for stock photos with caching and fallback.

        Args:
            query: Search terms (e.g. "restaurant food professional").
            section_type: Section context for sizing hints.
            count: Number of photos to return.
            orientation: "landscape", "portrait", or "square".

        Returns:
            List of StockPhoto (may be empty on total failure).
        """
        cache_key = f"{query}|{orientation}|{count}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return list(cached[:count])

        # Try Pexels first
        photos = await self._search_pexels(query, count, orientation)

        # Fallback to Unsplash if Pexels returned nothing
        if not photos and self._unsplash_key:
            logger.info("Pexels returned no results, falling back to Unsplash")
            photos = await self._search_unsplash(query, count, orientation)

        if photos:
            self._cache.put(cache_key, photos)

        return photos[:count]

    async def get_section_photos(
        self,
        business_category: str,
        section_type: str,
        business_name: str = "",
        count: int = 6,
    ) -> List[StockPhoto]:
        """Get photos tailored to a specific website section.

        Builds an optimized search query from the business category,
        section type, and optional business name.

        Args:
            business_category: One of restaurant, saas, portfolio, etc.
            section_type: hero, gallery, about, team, services, testimonials.
            business_name: Optional business name for more relevant results.
            count: Number of photos to return.

        Returns:
            List of StockPhoto (may be empty on total failure).
        """
        # Normalize category (strip variant suffix like "restaurant-elegant")
        base_category = self._normalize_category(business_category)

        # Build query
        query = self._build_section_query(base_category, section_type, business_name)

        # Get section config
        config = _SECTION_CONFIG.get(section_type, _SECTION_CONFIG["hero"])
        orientation = config["orientation"]

        # Gallery needs more photos
        if section_type == "gallery":
            count = max(count, 9)

        return await self.search_photos(
            query=query,
            section_type=section_type,
            count=count,
            orientation=orientation,
        )

    # -- private: Pexels -----------------------------------------------------

    async def _search_pexels(
        self,
        query: str,
        count: int,
        orientation: str,
    ) -> List[StockPhoto]:
        """Search the Pexels API.

        Returns an empty list on any error (logged, never raised).
        """
        if not self._pexels_key:
            logger.debug("Pexels API key not configured, skipping")
            return []

        if not self._rate_limiter.allow():
            logger.warning(
                "Pexels rate limit reached (%d remaining), skipping",
                self._rate_limiter.remaining,
            )
            return []

        # Pexels orientation param: landscape, portrait, square
        pexels_orientation = orientation if orientation in ("landscape", "portrait", "square") else "landscape"

        params = {
            "query": query,
            "per_page": min(count, 40),  # Pexels max is 80, keep conservative
            "orientation": pexels_orientation,
        }

        try:
            client = self._get_http()
            resp = await client.get(
                f"{self.PEXELS_BASE}/search",
                params=params,
                headers={"Authorization": self._pexels_key},
            )
            resp.raise_for_status()
            data = resp.json()

            photos: List[StockPhoto] = []
            for item in data.get("photos", []):
                src = item.get("src", {})
                # Pick appropriate size based on section
                url = src.get("large2x") or src.get("large") or src.get("original", "")
                if not url:
                    continue

                photos.append(StockPhoto(
                    url=url,
                    width=item.get("width", 1200),
                    height=item.get("height", 800),
                    photographer=item.get("photographer", ""),
                    alt_text=item.get("alt", query),
                    source="pexels",
                ))

            logger.info(
                "Pexels search '%s' returned %d photos (requested %d)",
                query, len(photos), count,
            )
            return photos

        except httpx.HTTPStatusError as exc:
            logger.error("Pexels API HTTP error %d: %s", exc.response.status_code, exc)
            return []
        except httpx.TimeoutException:
            logger.error("Pexels API timeout for query '%s'", query)
            return []
        except Exception as exc:
            logger.error("Pexels API unexpected error: %s", exc)
            return []

    # -- private: Unsplash fallback ------------------------------------------

    async def _search_unsplash(
        self,
        query: str,
        count: int,
        orientation: str,
    ) -> List[StockPhoto]:
        """Search the Unsplash API as fallback.

        Returns an empty list on any error (logged, never raised).
        """
        if not self._unsplash_key:
            logger.debug("Unsplash API key not configured, skipping fallback")
            return []

        # Unsplash orientation: landscape, portrait, squarish
        unsplash_orientation = "squarish" if orientation == "square" else orientation

        params = {
            "query": query,
            "per_page": min(count, 30),
            "orientation": unsplash_orientation,
        }

        try:
            client = self._get_http()
            resp = await client.get(
                f"{self.UNSPLASH_BASE}/search/photos",
                params=params,
                headers={"Authorization": f"Client-ID {self._unsplash_key}"},
            )
            resp.raise_for_status()
            data = resp.json()

            photos: List[StockPhoto] = []
            for item in data.get("results", []):
                urls = item.get("urls", {})
                # Use 'regular' size (1080px wide) for good quality
                url = urls.get("regular") or urls.get("full") or urls.get("raw", "")
                if not url:
                    continue

                photos.append(StockPhoto(
                    url=url,
                    width=item.get("width", 1200),
                    height=item.get("height", 800),
                    photographer=item.get("user", {}).get("name", ""),
                    alt_text=item.get("alt_description") or item.get("description") or query,
                    source="unsplash",
                ))

            logger.info(
                "Unsplash search '%s' returned %d photos (requested %d)",
                query, len(photos), count,
            )
            return photos

        except httpx.HTTPStatusError as exc:
            logger.error("Unsplash API HTTP error %d: %s", exc.response.status_code, exc)
            return []
        except httpx.TimeoutException:
            logger.error("Unsplash API timeout for query '%s'", query)
            return []
        except Exception as exc:
            logger.error("Unsplash API unexpected error: %s", exc)
            return []

    # -- private: query building ---------------------------------------------

    @staticmethod
    def _normalize_category(category: str) -> str:
        """Extract base category from style IDs like 'restaurant-elegant'."""
        if not category:
            return "business"
        for known in _CATEGORY_KEYWORDS:
            if category.startswith(known):
                return known
        return "business"

    @staticmethod
    def _build_section_query(
        category: str,
        section_type: str,
        business_name: str = "",
    ) -> str:
        """Build an optimized search query for a given section.

        Combines category keywords, section-specific suffixes,
        and optional business name into a focused search string.
        """
        parts: List[str] = []

        # Category base keywords
        cat_keywords = _CATEGORY_KEYWORDS.get(category, _CATEGORY_KEYWORDS["business"])

        # Section-specific logic
        config = _SECTION_CONFIG.get(section_type, _SECTION_CONFIG["hero"])

        if section_type == "hero":
            # Hero: category + business name + "professional"
            parts.append(category)
            if business_name:
                parts.append(business_name)
            parts.append(config["suffix"])

        elif section_type == "gallery":
            # Gallery: use category-specific gallery keywords
            gallery_kw = _GALLERY_KEYWORDS.get(category, "work professional")
            parts.append(category)
            parts.append(gallery_kw)

        elif section_type in ("team", "testimonials"):
            # People-focused: override with portrait-specific query
            parts.append(config["suffix"])

        else:
            # about, services, etc.
            parts.append(category)
            parts.append(config["suffix"])

        query = " ".join(parts)
        # Keep query concise (Pexels works best with 2-5 words)
        words = query.split()
        if len(words) > 6:
            words = words[:6]
        return " ".join(words)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

stock_client = PexelsClient()
"""Singleton stock photo client. Import and use directly:

    from app.services.images.stock_api import stock_client
    photos = await stock_client.get_section_photos("restaurant", "hero")
"""
