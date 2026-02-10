"""Routes per deploy su Vercel"""

import hashlib
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user
from app.models.site import Site, SiteStatus
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

VERCEL_API = "https://api.vercel.com"


def _vercel_headers() -> dict:
    """Headers di autenticazione per Vercel API."""
    headers = {
        "Authorization": f"Bearer {settings.VERCEL_TOKEN}",
        "Content-Type": "application/json",
    }
    if settings.VERCEL_TEAM_ID:
        headers["x-vercel-team-id"] = settings.VERCEL_TEAM_ID
    return headers


def _team_params() -> dict:
    """Query params per team Vercel (se configurato)."""
    if settings.VERCEL_TEAM_ID:
        return {"teamId": settings.VERCEL_TEAM_ID}
    return {}


@router.post("/{site_id}")
async def deploy_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Deploy del sito su Vercel.

    Crea un deployment Vercel con l'HTML generato dal site builder.
    Richiede piano base o premium (il piano free non puo pubblicare).
    """
    # --- Validazione token Vercel ---
    if not settings.VERCEL_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Servizio deploy non configurato. Contatta l'amministratore.",
        )

    # --- Recupera il sito ---
    site = (
        db.query(Site)
        .filter(Site.id == site_id, Site.owner_id == current_user.id)
        .first()
    )
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    # --- Controlla piano utente ---
    if not current_user.can_publish:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Il tuo piano non permette la pubblicazione. Passa al piano Base o Premium.",
                "upgrade_required": True,
                "current_plan": current_user.plan,
            },
        )

    # --- Controlla che ci sia HTML da deployare ---
    if not site.html_content:
        raise HTTPException(
            status_code=400,
            detail="Il sito non ha contenuto HTML. Genera il sito prima di pubblicarlo.",
        )

    if site.status not in (SiteStatus.READY.value, SiteStatus.PUBLISHED.value):
        raise HTTPException(
            status_code=400,
            detail="Il sito deve essere nello stato 'pronto' per essere pubblicato.",
        )

    # --- Prepara i file per Vercel ---
    html_bytes = site.html_content.encode("utf-8")
    html_sha1 = hashlib.sha1(html_bytes).hexdigest()
    html_size = len(html_bytes)

    project_name = f"sb-{site.slug}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Step 1: Upload del file tramite Vercel File API
            upload_headers = {
                "Authorization": f"Bearer {settings.VERCEL_TOKEN}",
                "Content-Type": "application/octet-stream",
                "x-vercel-digest": html_sha1,
                "Content-Length": str(html_size),
            }
            if settings.VERCEL_TEAM_ID:
                upload_headers["x-vercel-team-id"] = settings.VERCEL_TEAM_ID

            upload_resp = await client.post(
                f"{VERCEL_API}/v2/files",
                headers=upload_headers,
                content=html_bytes,
                params=_team_params(),
            )

            # 200 = uploaded, 409 = already exists (both OK)
            if upload_resp.status_code not in (200, 409):
                logger.error(
                    "Vercel file upload failed: %s %s",
                    upload_resp.status_code,
                    upload_resp.text,
                )
                raise HTTPException(
                    status_code=502,
                    detail="Errore durante l'upload dei file su Vercel.",
                )

            # Step 2: Crea il deployment
            deploy_payload = {
                "name": project_name,
                "files": [
                    {
                        "file": "index.html",
                        "sha": html_sha1,
                        "size": html_size,
                    }
                ],
                "projectSettings": {
                    "framework": None,
                },
                "target": "production",
            }

            deploy_resp = await client.post(
                f"{VERCEL_API}/v13/deployments",
                headers=_vercel_headers(),
                json=deploy_payload,
                params=_team_params(),
            )

            if deploy_resp.status_code not in (200, 201):
                logger.error(
                    "Vercel deployment failed: %s %s",
                    deploy_resp.status_code,
                    deploy_resp.text,
                )
                error_data = deploy_resp.json() if deploy_resp.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", {}).get("message", "Errore sconosciuto da Vercel")
                raise HTTPException(
                    status_code=502,
                    detail=f"Deploy fallito: {error_msg}",
                )

            deploy_data = deploy_resp.json()

    except httpx.TimeoutException:
        logger.error("Vercel API timeout for site %s", site_id)
        raise HTTPException(
            status_code=504,
            detail="Timeout nella comunicazione con Vercel. Riprova tra qualche minuto.",
        )
    except httpx.HTTPError as e:
        logger.error("Vercel HTTP error for site %s: %s", site_id, str(e))
        raise HTTPException(
            status_code=502,
            detail="Errore di rete nella comunicazione con Vercel.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected deploy error for site %s: %s", site_id, str(e))
        raise HTTPException(
            status_code=500,
            detail="Errore interno durante il deploy.",
        )

    # --- Aggiorna il record del sito ---
    deployed_url = f"https://{deploy_data.get('url', '')}"
    vercel_project_id = deploy_data.get("projectId", "")
    deployment_id = deploy_data.get("id", "")

    site.status = SiteStatus.PUBLISHED.value
    site.is_published = True
    site.published_at = datetime.now(timezone.utc)
    site.vercel_project_id = vercel_project_id
    site.domain = deployed_url

    db.commit()
    db.refresh(site)

    logger.info(
        "Site %s deployed to Vercel: %s (deployment_id=%s)",
        site_id,
        deployed_url,
        deployment_id,
    )

    return {
        "success": True,
        "site_id": site.id,
        "deployment_id": deployment_id,
        "url": deployed_url,
        "project_id": vercel_project_id,
        "status": "deployed",
    }


@router.get("/{site_id}/status")
async def deploy_status(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Stato del deploy per un sito."""
    site = (
        db.query(Site)
        .filter(Site.id == site_id, Site.owner_id == current_user.id)
        .first()
    )
    if not site:
        raise HTTPException(status_code=404, detail="Sito non trovato")

    result = {
        "site_id": site_id,
        "is_published": site.is_published,
        "status": site.status,
        "domain": site.domain,
        "vercel_project_id": site.vercel_project_id,
        "published_at": site.published_at.isoformat() if site.published_at else None,
    }

    # Se c'e un project ID, controlla lo stato del deployment su Vercel
    if site.vercel_project_id and settings.VERCEL_TOKEN:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{VERCEL_API}/v13/deployments",
                    headers=_vercel_headers(),
                    params={
                        "projectId": site.vercel_project_id,
                        "limit": 1,
                        "target": "production",
                        **_team_params(),
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    deployments = data.get("deployments", [])
                    if deployments:
                        latest = deployments[0]
                        result["vercel_status"] = latest.get("readyState", "unknown")
                        result["vercel_url"] = f"https://{latest.get('url', '')}"
                        result["vercel_created"] = latest.get("createdAt")
        except Exception as e:
            logger.warning("Could not fetch Vercel status for site %s: %s", site_id, str(e))
            result["vercel_status"] = "unknown"

    return result
