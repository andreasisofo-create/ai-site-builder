"""
Site Builder - FastAPI Backend
API per la gestione dei siti web, componenti e deploy
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import sites, components, deploy, auth, generate

# Configurazione logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestione del ciclo di vita dell'applicazione"""
    logger.info("🚀 Avvio Site Builder API...")
    
    try:
        # Startup: crea le tabelle nel database
        logger.info("📦 Connessione al database...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database inizializzato correttamente")
    except Exception as e:
        logger.error(f"❌ Errore connessione database: {e}")
        # Non blocchiamo l'avvio, ma logghiamo l'errore
    
    yield
    
    # Shutdown
    logger.info("👋 Server spento")


app = FastAPI(
    title="Site Builder API",
    description="API per la creazione e gestione di siti web",
    version="0.2.0",
    lifespan=lifespan,
)

# Error handler globale
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Errore globale: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Errore interno del server", "error": str(exc)}
    )

# CORS Configuration - PER PRODUZIONE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permetti tutte le origini temporaneamente
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configurato per: {settings.CORS_ORIGINS}")

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sites.router, prefix="/api/sites", tags=["sites"])
app.include_router(components.router, prefix="/api/components", tags=["components"])
app.include_router(deploy.router, prefix="/api/deploy", tags=["deploy"])
app.include_router(generate.router, prefix="/api/generate", tags=["generate"])


@app.get("/")
async def root():
    return {
        "message": "Site Builder API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - verifica che il servizio sia vivo"""
    try:
        # Test connessione database
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check DB fallito: {e}")
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "version": "0.2.0",
        "database": db_status,
        "debug": settings.DEBUG
    }


@app.get("/api/test")
async def test_endpoint():
    """Endpoint di test per verificare connessione"""
    return {
        "message": "Backend funziona!",
        "cors": "enabled",
        "timestamp": "2024"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
