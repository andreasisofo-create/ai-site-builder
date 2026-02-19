"""
Routes per gestione media: upload file, estrazione immagini da HTML,
sostituzione immagini e aggiunta video embed.
Includes wizard upload endpoints (no site_id required).
"""

import base64
import logging
import os
import re
import uuid
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import get_current_active_user
from app.models.site import Site
from app.models.site_version import SiteVersion
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload directory (relative to backend working dir)
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ============ SCHEMAS ============

class ImageInfo(BaseModel):
    src: str
    alt: str
    section: str
    index: int


class ImagesListResponse(BaseModel):
    images: List[ImageInfo]


class ReplaceImageRequest(BaseModel):
    old_src: str
    new_src: str


class AddVideoRequest(BaseModel):
    video_url: str
    after_section: str


class UploadResponse(BaseModel):
    url: str
    filename: str
    size: int
    mime_type: str


class Base64UploadRequest(BaseModel):
    data: str
    filename: str
    mime_type: str


# Mime type mapping for allowed extensions
ALLOWED_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


# ============ HELPERS ============

def _validate_and_save_upload(content: bytes, original_filename: str, user_id: int) -> UploadResponse:
    """Validate an image upload and save it to the user's upload directory.
    Returns an UploadResponse with the public URL and metadata."""
    if not original_filename:
        raise HTTPException(status_code=400, detail="Nome file mancante")

    _, ext = os.path.splitext(original_filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato non supportato: '{ext}'. Formati accettati: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File troppo grande ({len(content) / 1024 / 1024:.1f} MB). Massimo: 5 MB",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File vuoto")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    user_dir = os.path.join(UPLOAD_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, unique_name)
    with open(file_path, "wb") as f:
        f.write(content)

    base = settings.RENDER_EXTERNAL_URL or ""
    url = f"{base}/static/uploads/user_{user_id}/{unique_name}"
    mime = ALLOWED_MIME_TYPES.get(ext, "application/octet-stream")

    logger.info(f"Wizard upload: {url} ({len(content)} bytes) by user {user_id}")

    return UploadResponse(
        url=url,
        filename=unique_name,
        size=len(content),
        mime_type=mime,
    )


def _get_user_site(db: Session, site_id: int, user_id: int) -> Site:
    """Fetch a site owned by the given user, or raise 404."""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == user_id,
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    return site


def _save_version(db: Session, site: Site, html_content: str, description: str):
    """Save a new site version snapshot. Keeps max 10 versions."""
    latest = (
        db.query(SiteVersion)
        .filter(SiteVersion.site_id == site.id)
        .order_by(SiteVersion.version_number.desc())
        .first()
    )
    next_version = (latest.version_number + 1) if latest else 1

    version = SiteVersion(
        site_id=site.id,
        html_content=html_content,
        version_number=next_version,
        change_description=description,
    )
    db.add(version)

    # Delete old versions beyond the 10 most recent
    old_versions = (
        db.query(SiteVersion)
        .filter(SiteVersion.site_id == site.id)
        .order_by(SiteVersion.version_number.desc())
        .offset(10)
        .all()
    )
    for old in old_versions:
        db.delete(old)

    db.flush()


def _extract_video_id_youtube(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def _extract_video_id_vimeo(url: str) -> Optional[str]:
    """Extract Vimeo video ID from URL."""
    match = re.search(r'vimeo\.com/(?:video/)?(\d+)', url)
    return match.group(1) if match else None


def _build_video_section_html(embed_url: str) -> str:
    """Build a styled, responsive video section HTML block."""
    return f"""
<!-- Video Section -->
<section id="video" style="padding:80px 20px;background:var(--color-bg-dark, #111);text-align:center;" data-animate="fade-up">
  <div style="max-width:900px;margin:0 auto;">
    <div style="position:relative;width:100%;padding-bottom:56.25%;border-radius:16px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.4);">
      <iframe
        src="{embed_url}"
        style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
        loading="lazy"
        title="Video"
      ></iframe>
    </div>
  </div>
</section>
"""


# ============ ROUTES ============

@router.post("/upload")
@limiter.limit("20/minute")
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    site_id: int = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload an image file for a site.
    Accepted formats: jpg, png, webp, gif. Max 5 MB.
    Returns the public URL to access the uploaded file.
    """
    # Verify site ownership
    _get_user_site(db, site_id, current_user.id)

    # Validate extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome file mancante")

    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato non supportato: '{ext}'. Formati accettati: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File troppo grande ({len(content) / 1024 / 1024:.1f} MB). Massimo: 5 MB",
        )

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    site_dir = os.path.join(UPLOAD_DIR, str(site_id))
    os.makedirs(site_dir, exist_ok=True)

    file_path = os.path.join(site_dir, unique_name)
    with open(file_path, "wb") as f:
        f.write(content)

    # Build absolute URL so images work in srcdoc iframes (editor preview)
    base = settings.RENDER_EXTERNAL_URL or ""
    url = f"{base}/static/uploads/{site_id}/{unique_name}"
    logger.info(f"File uploaded: {url} ({len(content)} bytes) by user {current_user.id}")

    return {"url": url, "filename": unique_name}


@router.get("/sites/{site_id}/images", response_model=ImagesListResponse)
async def list_site_images(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Extract all <img> tags from the site HTML, grouped by section.
    Sections are detected by looking at ancestor elements with known section IDs.
    """
    site = _get_user_site(db, site_id, current_user.id)

    if not site.html_content:
        return ImagesListResponse(images=[])

    html = site.html_content

    # Known section IDs
    section_ids = [
        "hero", "about", "gallery", "services", "features",
        "team", "testimonials", "portfolio", "contact", "footer",
        "menu", "pricing", "cta", "blog", "event", "video",
    ]

    # Split HTML into section blocks by looking for id="section_name" patterns
    # Build a map of character positions to section names
    section_ranges: list[tuple[int, int, str]] = []
    for sec_id in section_ids:
        # Match section/div with id="hero" etc.
        pattern = re.compile(
            rf'<(?:section|div)[^>]*\bid=["\']({re.escape(sec_id)})["\'][^>]*>',
            re.IGNORECASE,
        )
        for m in pattern.finditer(html):
            section_ranges.append((m.start(), m.start(), sec_id))

    # Sort by position
    section_ranges.sort(key=lambda x: x[0])

    def _get_section_for_pos(pos: int) -> str:
        """Determine which section a given character position belongs to."""
        result = "unknown"
        for start, _, sec_id in section_ranges:
            if start <= pos:
                result = sec_id
            else:
                break
        return result

    # Find all <img> tags
    img_pattern = re.compile(
        r'<img\s[^>]*?>',
        re.IGNORECASE | re.DOTALL,
    )

    images: list[ImageInfo] = []
    section_counters: dict[str, int] = {}

    for match in img_pattern.finditer(html):
        tag = match.group(0)

        # Extract src
        src_match = re.search(r'src=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if not src_match:
            continue
        src = src_match.group(1)

        # Skip tiny tracking pixels and data URIs that are just placeholders
        if src.startswith("data:image/gif") or src.startswith("data:image/svg"):
            continue

        # Extract alt
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', tag, re.IGNORECASE)
        alt = alt_match.group(1) if alt_match else ""

        section = _get_section_for_pos(match.start())
        idx = section_counters.get(section, 0)
        section_counters[section] = idx + 1

        images.append(ImageInfo(src=src, alt=alt, section=section, index=idx))

    return ImagesListResponse(images=images)


@router.put("/sites/{site_id}/replace-image")
async def replace_image(
    site_id: int,
    data: ReplaceImageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Replace a specific image URL in the site HTML.
    Saves the updated HTML and creates a new version.
    """
    site = _get_user_site(db, site_id, current_user.id)

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Il sito non ha ancora contenuto HTML")

    if data.old_src not in site.html_content:
        raise HTTPException(status_code=404, detail="Immagine non trovata nell'HTML del sito")

    # Replace only the first occurrence of old_src (not all duplicates)
    updated_html = site.html_content.replace(data.old_src, data.new_src, 1)
    site.html_content = updated_html

    # Save version
    _save_version(db, site, updated_html, f"Sostituzione immagine")
    db.commit()

    logger.info(f"Image replaced in site {site_id} by user {current_user.id}")
    return {"success": True, "html_content": updated_html}


@router.post("/sites/{site_id}/add-video")
async def add_video(
    site_id: int,
    data: AddVideoRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Add a responsive video embed section after the specified section.
    Supports YouTube and Vimeo URLs.
    """
    site = _get_user_site(db, site_id, current_user.id)

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Il sito non ha ancora contenuto HTML")

    # Determine embed URL
    embed_url: Optional[str] = None

    video_id = _extract_video_id_youtube(data.video_url)
    if video_id:
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    else:
        video_id = _extract_video_id_vimeo(data.video_url)
        if video_id:
            embed_url = f"https://player.vimeo.com/video/{video_id}"

    if not embed_url:
        raise HTTPException(
            status_code=400,
            detail="URL video non valido. Supportati: YouTube e Vimeo.",
        )

    # Build video section HTML
    video_html = _build_video_section_html(embed_url)

    # Find the closing tag of the target section and insert after it
    html = site.html_content
    section_id = data.after_section.lower().strip()

    # Look for </section> or </div> that closes the target section
    # Strategy: find the section opening tag, then find its matching close
    open_pattern = re.compile(
        rf'<(section|div)[^>]*\bid=["\']({re.escape(section_id)})["\'][^>]*>',
        re.IGNORECASE,
    )
    open_match = open_pattern.search(html)

    if not open_match:
        raise HTTPException(
            status_code=404,
            detail=f"Sezione '{section_id}' non trovata nell'HTML del sito",
        )

    # Find the matching closing tag by counting nesting of the same tag type
    tag_name = open_match.group(1).lower()
    search_start = open_match.end()
    depth = 1
    pos = search_start

    open_re = re.compile(rf'<{tag_name}[\s>]', re.IGNORECASE)
    close_re = re.compile(rf'</{tag_name}\s*>', re.IGNORECASE)

    while depth > 0 and pos < len(html):
        next_open = open_re.search(html, pos)
        next_close = close_re.search(html, pos)

        if next_close is None:
            break

        if next_open and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
        else:
            depth -= 1
            if depth == 0:
                insert_pos = next_close.end()
                updated_html = html[:insert_pos] + "\n" + video_html + html[insert_pos:]

                site.html_content = updated_html
                _save_version(db, site, updated_html, f"Aggiunto video dopo sezione '{section_id}'")
                db.commit()

                logger.info(f"Video added to site {site_id} after section '{section_id}' by user {current_user.id}")
                return {"success": True, "html_content": updated_html}
            pos = next_close.end()

    raise HTTPException(
        status_code=500,
        detail=f"Impossibile trovare la chiusura della sezione '{section_id}'",
    )


# ============ WIZARD UPLOAD ROUTES (no site_id required) ============

@router.post("/upload-wizard", response_model=UploadResponse)
@limiter.limit("30/minute")
async def upload_wizard_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a single image for the wizard (logo, gallery photo, etc.).
    No site_id required -- files are stored in user-scoped directory.
    Accepted formats: jpg, png, webp, gif. Max 5 MB.
    """
    content = await file.read()
    return _validate_and_save_upload(content, file.filename or "", current_user.id)


@router.post("/upload-multiple")
@limiter.limit("10/minute")
async def upload_multiple_files(
    request: Request,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload multiple images at once for the wizard.
    Same validation per file: images only, max 5 MB each.
    Returns array of upload results.
    """
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Massimo 20 file per richiesta")

    results: List[dict] = []
    errors: List[dict] = []

    for i, file in enumerate(files):
        try:
            content = await file.read()
            result = _validate_and_save_upload(content, file.filename or "", current_user.id)
            results.append(result.model_dump())
        except HTTPException as e:
            errors.append({"index": i, "filename": file.filename or "", "error": e.detail})

    return {"uploaded": results, "errors": errors}


@router.post("/upload-base64", response_model=UploadResponse)
@limiter.limit("20/minute")
async def upload_base64_image(
    request: Request,
    body: Base64UploadRequest = Body(...),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a base64 encoded image (e.g. logo exported from canvas).
    Accepts: { data: "base64string", filename: "logo.png", mime_type: "image/png" }
    """
    # Strip data URI prefix if present (e.g. "data:image/png;base64,...")
    b64_data = body.data
    if "," in b64_data:
        b64_data = b64_data.split(",", 1)[1]

    try:
        content = base64.b64decode(b64_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Dati base64 non validi")

    return _validate_and_save_upload(content, body.filename, current_user.id)
