"""Image optimizer — resize, convert to WebP, upload to R2 CDN.

Converts user-uploaded base64 images to optimized CDN URLs.
Also handles stock photo proxying through R2 for reliability.

Usage:
    from app.services.images.optimizer import optimize_and_upload, process_user_photos

    cdn_url = await optimize_and_upload(raw_bytes, "hero-bg.jpg", site_id=42)
    cdn_urls = await process_user_photos(["data:image/png;base64,..."], site_id=42)
"""

import base64
import io
import logging
import re
import uuid
from typing import Dict, List, Optional, Tuple

from app.core.config import settings
from app.services.r2_storage import upload_to_r2, is_r2_available

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_WIDTH = 1920
WEBP_QUALITY = 80
SRCSET_WIDTHS = (400, 800, 1200)

# Regex for data URL parsing: data:image/png;base64,iVBOR...
_DATA_URL_RE = re.compile(
    r"^data:image/(?P<fmt>[a-zA-Z0-9+.-]+);base64,(?P<data>.+)$",
    re.DOTALL,
)


# ---------------------------------------------------------------------------
# Pillow lazy import (optional dependency)
# ---------------------------------------------------------------------------

def _get_pil():
    """Lazy-import Pillow. Returns (Image module, True) or (None, False)."""
    try:
        from PIL import Image
        return Image, True
    except ImportError:
        logger.warning(
            "Pillow not installed — image optimization disabled. "
            "Install with: pip install Pillow"
        )
        return None, False


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def _decode_data_url(data_url: str) -> Tuple[Optional[bytes], str]:
    """Decode a base64 data URL into raw bytes and format name.

    Args:
        data_url: A string like "data:image/png;base64,iVBOR..."

    Returns:
        (raw_bytes, format_name) or (None, "") on failure.
    """
    match = _DATA_URL_RE.match(data_url)
    if not match:
        logger.warning("Invalid data URL format (no match)")
        return None, ""

    fmt = match.group("fmt").lower()
    b64_data = match.group("data")

    try:
        raw = base64.b64decode(b64_data)
        return raw, fmt
    except Exception as exc:
        logger.error("Base64 decode failed: %s", exc)
        return None, ""


def _resize_image(img, max_width: int):
    """Resize image to max_width preserving aspect ratio.

    Args:
        img: PIL Image object.
        max_width: Maximum width in pixels.

    Returns:
        New PIL Image (never mutates the original).
    """
    if img.width <= max_width:
        return img.copy()

    ratio = max_width / img.width
    new_height = int(img.height * ratio)
    return img.resize((max_width, new_height), resample=3)  # LANCZOS = 3


def _to_webp_bytes(img, quality: int = WEBP_QUALITY) -> bytes:
    """Convert a PIL Image to WebP bytes.

    Args:
        img: PIL Image object.
        quality: WebP quality (0-100).

    Returns:
        Raw WebP bytes.
    """
    buffer = io.BytesIO()
    # Convert RGBA to RGB for WebP (avoids issues with some images)
    if img.mode in ("RGBA", "LA", "P"):
        rgb_img = img.convert("RGB")
    else:
        rgb_img = img
    rgb_img.save(buffer, format="WEBP", quality=quality, method=4)
    return buffer.getvalue()


def _generate_srcset_variants(
    img,
    widths: Tuple[int, ...] = SRCSET_WIDTHS,
    quality: int = WEBP_QUALITY,
) -> Dict[int, bytes]:
    """Generate multiple width variants for srcset.

    Args:
        img: PIL Image object (original size).
        widths: Tuple of target widths.
        quality: WebP quality.

    Returns:
        Dict mapping width -> WebP bytes. Only includes widths smaller
        than the original image.
    """
    variants: Dict[int, bytes] = {}
    for w in widths:
        if w >= img.width:
            continue
        resized = _resize_image(img, w)
        variants[w] = _to_webp_bytes(resized, quality)
    return variants


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def optimize_and_upload(
    image_data: bytes,
    filename: str,
    site_id: int,
    generate_srcset: bool = False,
) -> Optional[str]:
    """Optimize an image and upload to R2 CDN.

    Pipeline:
    1. Open with Pillow
    2. Resize to max 1920px width
    3. Convert to WebP (80% quality)
    4. Upload to R2
    5. Optionally generate srcset variants (400w, 800w, 1200w)

    Args:
        image_data: Raw image bytes (any format Pillow supports).
        filename: Base filename (extension will be replaced with .webp).
        site_id: Site ID for R2 key path.
        generate_srcset: If True, also upload 400w/800w/1200w variants.

    Returns:
        R2 CDN URL of the main (largest) image, or None on failure.
    """
    Image, pil_available = _get_pil()

    if not pil_available:
        # Without Pillow, upload the raw bytes unchanged
        ext = _extract_extension(filename)
        url = upload_to_r2(image_data, ext, site_id=site_id)
        return url

    try:
        img = Image.open(io.BytesIO(image_data))
    except Exception as exc:
        logger.error("Failed to open image '%s': %s", filename, exc)
        return None

    # Resize main image
    main_img = _resize_image(img, MAX_WIDTH)
    main_bytes = _to_webp_bytes(main_img)

    # Derive clean filename
    base_name = _strip_extension(filename)
    main_key = f"{base_name}.webp"

    # Upload main image
    main_url = upload_to_r2(main_bytes, ".webp", site_id=site_id)
    if main_url is None:
        logger.error("R2 upload failed for '%s'", main_key)
        return None

    logger.info(
        "Optimized '%s': %dx%d -> %dx%d, %d bytes -> %d bytes WebP",
        filename, img.width, img.height,
        main_img.width, main_img.height,
        len(image_data), len(main_bytes),
    )

    # Optional srcset variants
    if generate_srcset:
        variants = _generate_srcset_variants(img)
        for width, variant_bytes in variants.items():
            variant_key = f"{base_name}-{width}w.webp"
            variant_url = upload_to_r2(variant_bytes, ".webp", site_id=site_id)
            if variant_url:
                logger.info("Uploaded srcset variant %dw (%d bytes)", width, len(variant_bytes))

    return main_url


async def process_user_photos(
    photo_data_urls: List[str],
    site_id: int,
    generate_srcset: bool = False,
) -> List[str]:
    """Process a list of base64 data URLs into optimized R2 CDN URLs.

    Each data URL is decoded, optimized (resize + WebP), and uploaded.
    Failed images are skipped (logged, not raised).

    Args:
        photo_data_urls: List of "data:image/...;base64,..." strings.
        site_id: Site ID for R2 key paths.
        generate_srcset: If True, generate srcset width variants.

    Returns:
        List of R2 CDN URLs (may be shorter than input if some failed).
    """
    if not is_r2_available():
        logger.warning("R2 not available — cannot process user photos")
        return []

    cdn_urls: List[str] = []

    for idx, data_url in enumerate(photo_data_urls):
        raw_bytes, fmt = _decode_data_url(data_url)
        if raw_bytes is None:
            logger.warning("Skipping photo %d: invalid data URL", idx)
            continue

        filename = f"user-photo-{uuid.uuid4().hex[:8]}.{fmt}"

        url = await optimize_and_upload(
            image_data=raw_bytes,
            filename=filename,
            site_id=site_id,
            generate_srcset=generate_srcset,
        )

        if url:
            cdn_urls.append(url)
        else:
            logger.warning("Skipping photo %d: optimization/upload failed", idx)

    logger.info(
        "Processed %d/%d user photos for site %d",
        len(cdn_urls), len(photo_data_urls), site_id,
    )
    return cdn_urls


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_extension(filename: str) -> str:
    """Remove file extension: 'photo.jpg' -> 'photo'."""
    dot_idx = filename.rfind(".")
    if dot_idx > 0:
        return filename[:dot_idx]
    return filename


def _extract_extension(filename: str) -> str:
    """Extract file extension with dot: 'photo.jpg' -> '.jpg'."""
    dot_idx = filename.rfind(".")
    if dot_idx > 0:
        return filename[dot_idx:]
    return ".bin"
