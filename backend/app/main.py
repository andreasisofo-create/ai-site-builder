"""
Site Builder - FastAPI Backend
API per la gestione dei siti web, componenti e deploy
"""

import logging
import sys
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Configurazione logging PRIMA di tutto
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("🚀 Inizializzazione backend...")

# Import config
try:
    from app.core.config import settings
    logger.info("✅ Config caricata")
except Exception as e:
    logger.error(f"❌ Errore caricamento config: {e}")
    logger.error(traceback.format_exc())
    raise

# Import database
try:
    from app.core.database import engine, Base
    logger.info("✅ Database module caricato")
except Exception as e:
    logger.error(f"❌ Errore caricamento database: {e}")
    logger.error(traceback.format_exc())
    raise

# ===== MIDDLEWARE CORS PERSONALIZZATO =====
# Questo gestisce CORS per TUTTE le richieste, inclusi gli errori
class CORSMiddlewareCustom(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Leggi origin dalla richiesta (necessario per CORS con credentials)
        origin = request.headers.get("origin", "")

        # Gestione preflight OPTIONS
        if request.method == "OPTIONS":
            response = JSONResponse(content={})
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
            return response

        # Normale richiesta
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Errore durante richiesta: {exc}")
            response = JSONResponse(
                status_code=500,
                content={"detail": "Errore interno", "error": str(exc)}
            )

        # Aggiungi header CORS a TUTTE le risposte
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        if origin:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestione del ciclo di vita dell'applicazione"""
    logger.info("🚀 Avvio Site Builder API...")
    
    try:
        logger.info("📦 Connessione al database...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database inizializzato correttamente")
    except Exception as e:
        logger.error(f"❌ Errore connessione database: {e}")
        logger.error(traceback.format_exc())
    
    yield
    
    logger.info("👋 Server spento")

# Creazione app
logger.info("🏗️  Creazione FastAPI app...")
app = FastAPI(
    title="Site Builder API",
    description="API per la creazione e gestione di siti web",
    version="0.2.2",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware CUSTOM - DEVE ESSERE IL PRIMO!
logger.info("🔧 Configurazione CORS custom...")
app.add_middleware(CORSMiddlewareCustom)

# Anche il CORS standard di FastAPI (doppia protezione)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "https://site-generator-v2.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
logger.info("✅ CORS configurato")

# Error handler globale
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Errore globale: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Errore interno del server", "error": str(exc)}
    )

# Import e registrazione routes
logger.info("📝 Registrazione routes...")
try:
    from app.api.routes import sites, components, deploy, auth, generate

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(sites.router, prefix="/api/sites", tags=["sites"])
    app.include_router(components.router, prefix="/api/components", tags=["components"])
    app.include_router(deploy.router, prefix="/api/deploy", tags=["deploy"])
    app.include_router(generate.router, prefix="/api", tags=["generate"])

    # test_ai e' opzionale
    try:
        from app.api.routes import test_ai
        app.include_router(test_ai.router, prefix="/api", tags=["test"])
        logger.info("✅ Test routes registrate")
    except ImportError:
        logger.warning("⚠️ test_ai routes non trovate, skip")

    logger.info("✅ Routes registrate")
except Exception as e:
    logger.error(f"❌ Errore registrazione routes: {e}")
    logger.error(traceback.format_exc())
    raise

# ===== ENDPOINTS BASE (senza prefisso /api) =====
@app.get("/")
async def root():
    return {
        "message": "Site Builder API",
        "version": "0.2.2",
        "docs": "/docs",
        "health": "/health",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "unknown"
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check DB fallito: {e}")
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "version": "0.2.2",
        "database": db_status
    }

@app.get("/ping")
async def ping():
    return {"pong": True, "status": "alive"}

@app.head("/")
@app.head("/health")
async def head_endpoints():
    """Gestisce richieste HEAD per health checks"""
    return JSONResponse(content={})

logger.info("✅ App inizializzata!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
