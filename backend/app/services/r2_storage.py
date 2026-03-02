"""
Cloudflare R2 storage service for persistent image uploads.

R2 is S3-compatible, so we use boto3. Falls back to local filesystem
if R2 is not configured (development mode).

Required env vars for R2:
  R2_ACCOUNT_ID        - Cloudflare account ID
  R2_ACCESS_KEY_ID     - R2 API token access key
  R2_SECRET_ACCESS_KEY - R2 API token secret key
  R2_BUCKET_NAME       - R2 bucket name (e.g. "site-builder-uploads")
  R2_PUBLIC_URL        - Public URL prefix (e.g. "https://media.e-quipe.app")
"""

import logging
import os
import uuid
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy-init boto3 client (only when R2 is configured)
_s3_client = None
_r2_available = False


def _get_s3_client():
    """Get or create the S3 client for R2."""
    global _s3_client, _r2_available

    if _s3_client is not None:
        return _s3_client

    if not settings.R2_ACCOUNT_ID or not settings.R2_ACCESS_KEY_ID:
        _r2_available = False
        logger.info("R2 not configured — using local filesystem for uploads")
        return None

    try:
        import boto3
        from botocore.config import Config as BotoConfig

        _s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=BotoConfig(
                signature_version="s3v4",
                retries={"max_attempts": 2, "mode": "standard"},
            ),
            region_name="auto",
        )
        _r2_available = True
        logger.info("R2 storage initialized (bucket: %s)", settings.R2_BUCKET_NAME)
        return _s3_client
    except ImportError:
        logger.warning("boto3 not installed — R2 storage unavailable, using local filesystem")
        _r2_available = False
        return None
    except Exception as e:
        logger.error("Failed to initialize R2 client: %s", e)
        _r2_available = False
        return None


def is_r2_available() -> bool:
    """Check if R2 storage is configured and available."""
    _get_s3_client()
    return _r2_available


# MIME type mapping
_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def upload_to_r2(
    content: bytes,
    ext: str,
    site_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Optional[str]:
    """Upload file content to R2 and return the public URL.

    Key format: sites/{site_id}/{uuid}.{ext} or users/{user_id}/{uuid}.{ext}

    Returns None if R2 is not available (caller should fall back to local).
    """
    client = _get_s3_client()
    if client is None:
        return None

    unique_name = f"{uuid.uuid4().hex}{ext}"

    if site_id:
        key = f"sites/{site_id}/{unique_name}"
    elif user_id:
        key = f"users/{user_id}/{unique_name}"
    else:
        key = f"misc/{unique_name}"

    content_type = _MIME_TYPES.get(ext.lower(), "application/octet-stream")

    try:
        client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=content,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
        )

        public_url = f"{settings.R2_PUBLIC_URL.rstrip('/')}/{key}"
        logger.info("Uploaded to R2: %s (%d bytes)", key, len(content))
        return public_url
    except Exception as e:
        logger.error("R2 upload failed for key %s: %s", key, e)
        return None


def delete_from_r2(url: str) -> bool:
    """Delete a file from R2 by its public URL.

    Returns True if deleted successfully, False otherwise.
    """
    client = _get_s3_client()
    if client is None:
        return False

    public_base = settings.R2_PUBLIC_URL.rstrip("/")
    if not url.startswith(public_base):
        return False

    key = url[len(public_base):].lstrip("/")

    try:
        client.delete_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
        )
        logger.info("Deleted from R2: %s", key)
        return True
    except Exception as e:
        logger.error("R2 delete failed for key %s: %s", key, e)
        return False
