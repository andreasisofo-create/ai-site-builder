"""Routes per gestione siti"""

import logging
import re
from datetime import datetime
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from pydantic import BaseModel, field_serializer

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.site import Site, SiteStatus
from app.models.site_version import SiteVersion
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_image_url(url: str) -> bool:
    """Validate image URL to prevent SSRF. Allow data:image/ URIs and public HTTPS URLs."""
    if url.startswith("data:image/"):
        return True
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname or ""
    blocked = (
        "localhost", "127.0.0.1", "0.0.0.0", "169.254.",
        "10.", "172.16.", "192.168.", "::1", "[::1]",
    )
    for b in blocked:
        if host.startswith(b) or host == b:
            return False
    return True


# ============ SCHEMAS ============

class SiteCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    template: Optional[str] = "default"


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    status: Optional[str] = None
    html_content: Optional[str] = None
    thumbnail: Optional[str] = None
    is_published: Optional[bool] = None


class SiteResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    status: str
    is_published: bool
    thumbnail: Optional[str]
    created_at: Any
    updated_at: Optional[Any] = None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, val: Any) -> Optional[str]:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val.isoformat()
        return str(val)

    class Config:
        from_attributes = True


class SiteDetailResponse(SiteResponse):
    """Response con html_content incluso (per editor/singolo sito)."""
    html_content: Optional[str] = None


# ============ ROUTES ============

@router.get("/", response_model=List[SiteResponse])
async def list_sites(
    status: Optional[str] = Query(None, description="Filtra per stato"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lista siti dell'utente corrente"""
    query = db.query(Site).filter(Site.owner_id == current_user.id)
    
    if status:
        query = query.filter(Site.status == status)
    
    sites = query.order_by(Site.updated_at.desc()).all()
    return sites


@router.post("/", response_model=SiteResponse)
async def create_site(
    data: SiteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crea un nuovo sito"""
    # Genera slug unico: se esiste, aggiunge -2, -3, ecc.
    slug = data.slug
    if db.query(Site).filter(Site.slug == slug).first():
        counter = 2
        while db.query(Site).filter(Site.slug == f"{slug}-{counter}").first():
            counter += 1
        slug = f"{slug}-{counter}"

    site = Site(
        name=data.name,
        slug=slug,
        description=data.description,
        template=data.template,
        owner_id=current_user.id,
        status=SiteStatus.DRAFT.value
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/{site_id}", response_model=SiteDetailResponse)
async def get_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ottiene un sito specifico (solo se proprietario)"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    return site


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    data: SiteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Aggiorna un sito"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    # Aggiorna i campi forniti
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)
    
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}")
async def delete_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Elimina un sito"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    db.query(SiteVersion).filter(SiteVersion.site_id == site_id).delete()
    db.delete(site)
    db.commit()
    return {"message": "Sito eliminato"}


@router.post("/{site_id}/generate")
async def update_site_html(
    site_id: int,
    html_content: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Aggiorna l'HTML generato di un sito"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()
    
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    
    site.html_content = html_content
    site.status = SiteStatus.READY.value
    db.commit()
    db.refresh(site)
    return {"message": "HTML aggiornato", "site": site}


@router.get("/{site_id}/preview")
async def preview_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ottiene l'HTML preview di un sito"""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Sito non ancora generato")

    return {
        "html": site.html_content,
        "name": site.name,
        "status": site.status
    }


@router.get("/{site_id}/versions")
async def list_versions(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Lista versioni di un sito (solo proprietario)."""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    versions = (
        db.query(SiteVersion)
        .filter(SiteVersion.site_id == site_id)
        .order_by(SiteVersion.version_number.desc())
        .all()
    )

    return [
        {
            "id": v.id,
            "version_number": v.version_number,
            "change_description": v.change_description,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]


@router.post("/{site_id}/versions/{version_id}/rollback")
async def rollback_version(
    site_id: int,
    version_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ripristina il sito a una versione precedente."""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    version = db.query(SiteVersion).filter(
        SiteVersion.id == version_id,
        SiteVersion.site_id == site_id,
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="Versione non trovata")

    # Ripristina HTML
    site.html_content = version.html_content
    site.status = "ready"

    # Salva nuova versione di rollback
    latest = (
        db.query(SiteVersion)
        .filter(SiteVersion.site_id == site.id)
        .order_by(SiteVersion.version_number.desc())
        .first()
    )
    next_version = (latest.version_number + 1) if latest else 1

    rollback_entry = SiteVersion(
        site_id=site.id,
        html_content=version.html_content,
        version_number=next_version,
        change_description=f"Rollback alla versione {version.version_number}",
    )
    db.add(rollback_entry)
    db.commit()

    return {
        "success": True,
        "html_content": version.html_content,
        "restored_version": version.version_number,
        "new_version": next_version,
    }


# ============ PHOTO MAP ============

# Italian section metadata for photo-map endpoint
_SECTION_META = {
    "hero": {
        "label": "Immagine principale del sito (Hero)",
        "description": "La prima foto che i visitatori vedono. Occupa tutta la larghezza in alto.",
        "size_hint": "Orizzontale, 1920x1080 ideale",
    },
    "about": {
        "label": "Foto sezione Chi Siamo",
        "description": "Mostra chi sei: il tuo locale, il tuo team, o te stesso al lavoro.",
        "size_hint": "Verticale o quadrata, 800x1000 ideale",
    },
    "gallery": {
        "label": "Galleria foto",
        "description": "Mostra i tuoi lavori, piatti, prodotti o ambienti.",
        "size_hint": "Quadrata, 800x800 ideale",
    },
    "team": {
        "label": "Foto membro del team",
        "description": "Le persone del tuo team. Usa foto professionali.",
        "size_hint": "Verticale, 400x500 ideale",
    },
    "services": {
        "label": "Foto servizio",
        "description": "Rappresenta il servizio che offri.",
        "size_hint": "Orizzontale o quadrata, 800x600 ideale",
    },
    "blog": {
        "label": "Immagine articolo",
        "description": "Immagine di copertina del post del blog.",
        "size_hint": "Orizzontale, 1200x630 ideale",
    },
    "portfolio": {
        "label": "Foto progetto portfolio",
        "description": "Mostra i tuoi progetti e lavori migliori.",
        "size_hint": "Orizzontale o quadrata, 800x800 ideale",
    },
    "listings": {
        "label": "Foto annuncio",
        "description": "Immagine dell'elemento in vetrina.",
        "size_hint": "Quadrata, 600x600 ideale",
    },
    "menu": {
        "label": "Foto piatto del menu",
        "description": "Foto appetitosa del piatto o prodotto.",
        "size_hint": "Quadrata, 600x600 ideale",
    },
    "donations": {
        "label": "Foto causa/donazione",
        "description": "Immagine che rappresenta la causa.",
        "size_hint": "Orizzontale, 800x600 ideale",
    },
    "app-download": {
        "label": "Immagine app/prodotto digitale",
        "description": "Screenshot o mockup della tua app.",
        "size_hint": "Verticale, 400x800 ideale",
    },
    "video": {
        "label": "Anteprima video",
        "description": "Immagine di copertina per il video.",
        "size_hint": "Orizzontale, 1280x720 ideale",
    },
    "testimonials": {
        "label": "Foto cliente/testimonianza",
        "description": "Foto del cliente che ha lasciato la recensione.",
        "size_hint": "Quadrata, 200x200 ideale",
    },
    "contact": {
        "label": "Foto sezione contatti",
        "description": "Immagine della sezione contattaci.",
        "size_hint": "Orizzontale, 800x600 ideale",
    },
    "cta": {
        "label": "Immagine call-to-action",
        "description": "Immagine di sfondo della sezione azione.",
        "size_hint": "Orizzontale, 1920x600 ideale",
    },
    "features": {
        "label": "Foto funzionalita",
        "description": "Immagine che illustra una funzionalita o vantaggio.",
        "size_hint": "Quadrata, 600x600 ideale",
    },
    "pricing": {
        "label": "Foto piano/offerta",
        "description": "Immagine della sezione prezzi.",
        "size_hint": "Quadrata, 600x600 ideale",
    },
}

_DEFAULT_SECTION_META = {
    "label": "Foto del sito",
    "description": "Immagine usata nel sito.",
    "size_hint": "800x600 ideale",
}


def _is_stock_url(url: str) -> bool:
    """Check if a URL is a stock photo (Unsplash)."""
    if not url:
        return False
    return "images.unsplash.com" in url or "unsplash.com" in url


def _is_real_photo_url(url: str) -> bool:
    """Return True only for real image URLs (http/https), skip SVGs and data URIs."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if url.startswith("data:"):
        return False
    if url.startswith("#") or url == "placeholder" or url == "placeholder.jpg":
        return False
    if url.startswith("{{"):
        return False
    if url.startswith("http://") or url.startswith("https://"):
        return True
    return False


def _extract_photos_from_html(html: str) -> list:
    """Parse HTML to extract all real photo <img> tags with their section context."""
    photos = []

    section_pattern = re.compile(
        r'<section[^>]*\bid=["\']([^"\']+)["\']', re.IGNORECASE
    )
    img_pattern = re.compile(
        r'<img\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE
    )

    # Find all section start positions and their IDs
    section_starts = []
    for m in section_pattern.finditer(html):
        section_starts.append((m.start(), m.group(1).lower().strip()))

    # For each img, determine which section it belongs to
    for img_match in img_pattern.finditer(html):
        src = img_match.group(1).strip()

        if not _is_real_photo_url(src):
            continue

        img_pos = img_match.start()

        # Find the closest section that starts before this img
        current_section = "other"
        for sec_start, sec_id in reversed(section_starts):
            if sec_start <= img_pos:
                current_section = sec_id
                break

        # Extract alt text
        alt_match = re.search(
            r'alt=["\']([^"\']*)["\']', img_match.group(0), re.IGNORECASE
        )
        alt_text = alt_match.group(1) if alt_match else ""

        photos.append({
            "section_type": current_section,
            "current_url": src,
            "alt": alt_text,
        })

    return photos


def _build_photo_map(photos: list) -> list:
    """Convert raw extracted photos into the final photo-map with Italian labels."""
    result = []
    # Count totals per section first for "N di X" labels
    section_totals: dict = {}
    for photo in photos:
        s = photo["section_type"]
        section_totals[s] = section_totals.get(s, 0) + 1

    section_counters: dict = {}
    for photo in photos:
        section = photo["section_type"]
        section_counters[section] = section_counters.get(section, 0) + 1
        idx = section_counters[section]
        total = section_totals[section]

        meta = _SECTION_META.get(section, _DEFAULT_SECTION_META)

        # Build unique ID
        if total == 1:
            photo_id = f"{section}_main"
        else:
            photo_id = f"{section}_{idx}"

        # Build label: singular if only one, "N di X" if multiple
        if total == 1:
            label = meta["label"]
        else:
            label = f"{meta['label']} {idx} di {total}"

        result.append({
            "id": photo_id,
            "section_type": section,
            "label": label,
            "description": meta["description"],
            "current_url": photo["current_url"],
            "is_stock": _is_stock_url(photo["current_url"]),
            "size_hint": meta["size_hint"],
            "alt": photo.get("alt", ""),
        })

    return result


@router.get("/{site_id}/photo-map")
async def get_photo_map(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Returns a map of all photos in the site with Italian labels and section context.

    Scans the site's generated HTML for <img> tags, identifies the enclosing
    section (hero, about, gallery, team, etc.), and returns a structured list
    with user-friendly Italian labels, stock detection, and size hints.
    """
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Sito non ancora generato")

    raw_photos = _extract_photos_from_html(site.html_content)
    photo_map = _build_photo_map(raw_photos)

    stock_count = sum(1 for p in photo_map if p["is_stock"])
    custom_count = len(photo_map) - stock_count

    return {
        "photos": photo_map,
        "total_photos": len(photo_map),
        "stock_count": stock_count,
        "custom_count": custom_count,
    }


@router.get("/{site_id}/export")
async def export_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Scarica il file HTML completo del sito."""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Sito non ancora generato")

    # Aggiungi meta commento
    html = site.html_content
    meta_comment = f"<!-- Generated by E-quipe AI Site Builder | {site.name} -->\n"
    if not html.startswith("<!--"):
        html = meta_comment + html

    filename = f"{site.slug}.html"

    return Response(
        content=html,
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


# ============ PHOTO SWAP ============

class PhotoSwapRequest(BaseModel):
    """Request to swap a single photo in a generated site."""
    photo_id: str  # e.g. "hero_main", "gallery_2", "team_1"
    action: str  # "upload" or "keep_stock"
    photo_url: Optional[str] = None  # New URL (required when action="upload")
    current_url: Optional[str] = None  # Current URL to replace (from photo-map)


@router.post("/{site_id}/photo-swap")
async def swap_photo(
    site_id: int,
    data: PhotoSwapRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Swap a single photo in a generated site's HTML.

    Finds the image by its current URL and replaces it with the new URL.
    Works for both <img src="..."> and background-image: url(...) patterns.
    """
    # Validate action
    if data.action not in ("upload", "keep_stock"):
        raise HTTPException(
            status_code=400,
            detail="action deve essere 'upload' o 'keep_stock'",
        )

    # keep_stock: nothing to do
    if data.action == "keep_stock":
        return {
            "success": True,
            "photo_id": data.photo_id,
            "action": "keep_stock",
            "message": "Foto stock mantenuta",
        }

    # For upload action, photo_url is required
    if not data.photo_url:
        raise HTTPException(
            status_code=400,
            detail="photo_url e' obbligatorio per action='upload'",
        )

    # current_url is required to know what to replace
    if not data.current_url:
        raise HTTPException(
            status_code=400,
            detail="current_url e' obbligatorio per identificare la foto da sostituire",
        )

    # Validate the new URL (SSRF protection)
    if not _validate_image_url(data.photo_url):
        raise HTTPException(
            status_code=400,
            detail="URL immagine non valido. Usa https:// o data:image/",
        )

    # Block dangerous URL schemes in current_url too
    if data.current_url.startswith(("javascript:", "file:", "data:text/html")):
        raise HTTPException(
            status_code=400,
            detail="current_url non valido",
        )

    # Load site (owner check)
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id,
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    if not site.html_content:
        raise HTTPException(status_code=400, detail="Sito non ancora generato")

    html = site.html_content
    old_url = data.current_url

    # Check that the old URL actually exists in the HTML
    if old_url not in html:
        raise HTTPException(
            status_code=404,
            detail=f"Foto con URL corrente non trovata nell'HTML del sito (photo_id: {data.photo_id})",
        )

    # Replace: simple string replacement (URLs are unique in the HTML)
    new_html = html.replace(old_url, data.photo_url)

    # Verify replacement actually happened
    if new_html == html:
        raise HTTPException(
            status_code=500,
            detail="Sostituzione foto fallita",
        )

    # Save updated HTML
    site.html_content = new_html
    db.commit()
    db.refresh(site)

    logger.info(
        "[PhotoSwap] User %d swapped photo '%s' in site %d",
        current_user.id, data.photo_id, site_id,
    )

    return {
        "success": True,
        "photo_id": data.photo_id,
        "old_url": old_url,
        "new_url": data.photo_url,
    }


# ============================================================
# NOTIFICATION EMAIL — imposta email per ricezione form contatti
# ============================================================

class NotificationEmailRequest(BaseModel):
    email: str


@router.put("/{site_id}/notification-email")
def set_notification_email(
    site_id: int,
    data: NotificationEmailRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Imposta l'email del proprietario per ricevere i messaggi dal form contatti.
    Aggiorna il valore BIZ_EMAIL nello script Web3Forms dell'HTML generato
    e lo salva in site.config["_notification_email"].
    """
    email = data.email.strip().lower()

    # Validazione email base
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Email non valida")

    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id,
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")
    if not site.html_content:
        raise HTTPException(status_code=400, detail="Sito non ancora generato")

    html = site.html_content

    # Sostituisce BIZ_EMAIL nella variabile JS del form handler
    # Pattern: var BIZ_EMAIL = '...' (qualsiasi valore precedente, anche vuoto)
    new_html = re.sub(
        r"var BIZ_EMAIL\s*=\s*'[^']*'",
        f"var BIZ_EMAIL = '{email}'",
        html,
    )

    if new_html == html and f"var BIZ_EMAIL = '{email}'" not in html:
        # Il form handler potrebbe non esserci (sito vecchio) — aggiunge in testa al </body>
        inject_script = f"""<script>
(function(){{
  document.querySelectorAll('#contact form').forEach(function(form){{
    form.addEventListener('submit', function(e){{
      e.preventDefault();
      var data = {{}};
      form.querySelectorAll('input,textarea').forEach(function(el){{
        if(el.name) data[el.name]=el.value;
        else if(el.type==='email') data['email']=el.value;
        else if(el.type==='text'&&!data['name']) data['name']=el.value;
        else if(el.tagName==='TEXTAREA') data['message']=el.value;
      }});
      form.innerHTML='<div class="text-center py-12"><h3 style="color:var(--color-text)">Messaggio inviato!</h3><p style="color:var(--color-text-muted)">Grazie, ti risponderemo al pi\\u00f9 presto.</p></div>';
      fetch('https://api.web3forms.com/submit',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{access_key:'{site.html_content.count("WEB3FORMS_KEY")}',to:'{email}',...data}})}}).catch(function(){{}});
    }});
  }});
}})();
</script>"""
        new_html = html.replace("</body>", inject_script + "\n</body>")

    # Salva email in config per riferimento futuro
    config = site.config if isinstance(site.config, dict) else {}
    config["_notification_email"] = email
    site.config = config
    site.html_content = new_html

    db.commit()

    logger.info("[NotificationEmail] Site %d: BIZ_EMAIL set to %s by user %d", site_id, email, current_user.id)

    return {
        "success": True,
        "email": email,
        "message": f"Email di notifica impostata: {email}",
    }


@router.get("/{site_id}/notification-email")
def get_notification_email(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ritorna l'email di notifica corrente del sito."""
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.owner_id == current_user.id,
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    # Prima cerca in config, poi nell'HTML
    config = site.config if isinstance(site.config, dict) else {}
    email = config.get("_notification_email", "")

    if not email and site.html_content:
        m = re.search(r"var BIZ_EMAIL\s*=\s*'([^']*)'", site.html_content)
        if m:
            email = m.group(1)

    # Fallback: email dell'account utente
    if not email:
        email = ""

    return {
        "email": email,
        "account_email": current_user.email,
    }
