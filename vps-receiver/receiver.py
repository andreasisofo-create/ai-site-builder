"""
E-quipe Deploy Receiver
Riceve HTML dal backend FastAPI (Render) e lo salva su disco.
Ascolta su 0.0.0.0:8090, autenticato con shared secret.
"""
import os
import re
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(title="E-quipe Deploy Receiver")

# Config
SITES_DIR = Path("/var/www/sites")
DEPLOY_SECRET = os.environ.get("DEPLOY_SECRET", "CHANGE_ME_IN_PRODUCTION")

# Blocklist sottodomini riservati
BLOCKED_SLUGS = {
    "www", "api", "app", "admin", "mail", "ftp", "smtp",
    "pop", "imap", "ns1", "ns2", "cdn", "staging", "dev",
    "test", "n8n", "dashboard", "login", "register", "blog",
    "shop", "store", "help", "support", "docs", "status"
}

# Regex per validare slug
SLUG_REGEX = re.compile(r"^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")


def validate_slug(slug: str) -> bool:
    """Valida che lo slug sia sicuro e non riservato."""
    if not SLUG_REGEX.match(slug):
        return False
    if slug in BLOCKED_SLUGS:
        return False
    if ".." in slug or "/" in slug or "\\" in slug:
        return False
    return True


def verify_secret(x_deploy_secret: str = Header(None)):
    """Verifica il shared secret nell'header."""
    if not x_deploy_secret or x_deploy_secret != DEPLOY_SECRET:
        raise HTTPException(status_code=403, detail="Invalid deploy secret")


class DeployRequest(BaseModel):
    slug: str
    html: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "deploy-receiver"}


@app.post("/deploy")
async def deploy_site(req: DeployRequest, x_deploy_secret: str = Header(None)):
    """Riceve HTML e lo salva su disco."""
    verify_secret(x_deploy_secret)

    if not validate_slug(req.slug):
        raise HTTPException(status_code=400, detail=f"Invalid slug: {req.slug}")

    site_dir = SITES_DIR / req.slug
    site_dir.mkdir(parents=True, exist_ok=True)

    # Scrivi index.html
    (site_dir / "index.html").write_text(req.html, encoding="utf-8")

    # Imposta permessi corretti
    os.system(f"chown -R www-data:www-data {site_dir}")

    url = f"https://{req.slug}.e-quipe.app"
    size = len(req.html.encode("utf-8"))

    return {
        "status": "deployed",
        "url": url,
        "slug": req.slug,
        "size_bytes": size
    }


@app.delete("/deploy/{slug}")
async def undeploy_site(slug: str, x_deploy_secret: str = Header(None)):
    """Rimuove un sito pubblicato."""
    verify_secret(x_deploy_secret)

    if not validate_slug(slug):
        raise HTTPException(status_code=400, detail=f"Invalid slug: {slug}")

    site_dir = SITES_DIR / slug
    if site_dir.exists():
        shutil.rmtree(site_dir)
        return {"status": "removed", "slug": slug}
    else:
        raise HTTPException(status_code=404, detail=f"Site not found: {slug}")


@app.get("/sites")
async def list_sites(x_deploy_secret: str = Header(None)):
    """Lista tutti i siti pubblicati."""
    verify_secret(x_deploy_secret)

    sites = []
    if SITES_DIR.exists():
        for d in sorted(SITES_DIR.iterdir()):
            if d.is_dir():
                index = d / "index.html"
                sites.append({
                    "slug": d.name,
                    "has_index": index.exists(),
                    "size_bytes": index.stat().st_size if index.exists() else 0
                })
    return {"sites": sites, "total": len(sites)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
