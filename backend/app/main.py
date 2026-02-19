"""
Site Builder - FastAPI Backend
API per la gestione dei siti web, componenti e deploy
"""

import logging
import os
import sys
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Configurazione logging PRIMA di tutto
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("Inizializzazione backend...")

# Rate Limiter (importato dal modulo dedicato per evitare import circolari)
from app.core.rate_limiter import limiter

# Import config
try:
    from app.core.config import settings
    logger.info("Config caricata")
except Exception as e:
    logger.error(f"Errore caricamento config: {e}")
    logger.error(traceback.format_exc())
    raise

# Import database (non crashare se il DB non e' raggiungibile)
engine = None
Base = None
try:
    from app.core.database import engine, Base
    logger.info("Database module caricato")
except Exception as e:
    logger.error(f"Errore caricamento database: {e}")
    logger.error(traceback.format_exc())
    logger.warning("Il server partira' senza database - gli endpoint DB non funzioneranno")

# ===== MIDDLEWARE CORS PERSONALIZZATO =====
# Questo gestisce CORS per TUTTE le richieste, inclusi gli errori
class CORSMiddlewareCustom(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Leggi origin dalla richiesta (necessario per CORS con credentials)
        origin = request.headers.get("origin", "")

        # Verifica se l'origin e' nella whitelist
        allowed = origin and (
            origin in settings.CORS_ORIGINS
            or settings.CORS_ALLOW_ALL
        )
        cors_origin = origin if allowed else ""

        # Gestione preflight OPTIONS
        if request.method == "OPTIONS":
            response = JSONResponse(content={})
            if cors_origin:
                response.headers["Access-Control-Allow-Origin"] = cors_origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "3600"
            return response

        # Normale richiesta
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Errore durante richiesta: {exc}")
            response = JSONResponse(
                status_code=500,
                content={"detail": "Errore interno del server"}
            )

        # Aggiungi header CORS solo per origini consentite
        if cors_origin:
            response.headers["Access-Control-Allow-Origin"] = cors_origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Allow-Credentials"] = "true"

        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestione del ciclo di vita dell'applicazione"""
    logger.info("Avvio Site Builder API...")

    if engine and Base:
        try:
            logger.info("Connessione al database...")
            # Ensure required extensions exist before creating tables
            from sqlalchemy import text as sql_text_ext
            with engine.connect() as conn:
                conn.execute(sql_text_ext("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.execute(sql_text_ext('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                conn.commit()
            logger.info("Estensioni PostgreSQL (vector, uuid-ossp) verificate")

            Base.metadata.create_all(bind=engine)
            logger.info("Database inizializzato correttamente")

            # Add new columns to existing tables (create_all doesn't ALTER)
            from sqlalchemy import text as sql_text
            migrations = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token_expires TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS refines_used INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS refines_limit INTEGER DEFAULT 3",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS pages_used INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS pages_limit INTEGER DEFAULT 1",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS plan VARCHAR DEFAULT 'free'",
                "ALTER TABLE sites ADD COLUMN IF NOT EXISTS qc_score FLOAT",
                "ALTER TABLE sites ADD COLUMN IF NOT EXISTS qc_report JSON",
                "ALTER TABLE sites ADD COLUMN IF NOT EXISTS generation_cost FLOAT",
                "ALTER TABLE sites ADD COLUMN IF NOT EXISTS tokens_input INTEGER",
                "ALTER TABLE sites ADD COLUMN IF NOT EXISTS tokens_output INTEGER",
                "ALTER TABLE sites ADD COLUMN IF NOT EXISTS ai_model VARCHAR",
                # Service tables (user_subscriptions, payment_history, service_catalog)
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS revolut_customer_id VARCHAR",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS revolut_payment_method_id VARCHAR",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS setup_order_id VARCHAR",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS activated_by VARCHAR",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS notes TEXT",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS current_period_start TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS current_period_end TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE user_subscriptions ADD COLUMN IF NOT EXISTS next_billing_date TIMESTAMP WITH TIME ZONE",
            ]
            with engine.connect() as conn:
                for stmt in migrations:
                    try:
                        conn.execute(sql_text(stmt))
                    except Exception:
                        pass  # Column already exists or different DB dialect
                conn.commit()
            logger.info("Migrazioni colonne completate")

            # Enable RLS on all tables (Supabase Security Advisor).
            # The backend connects as `postgres` superuser which bypasses RLS.
            # This blocks direct access via Supabase anon/authenticated roles.
            rls_tables = [
                "users", "sites", "site_versions", "components", "components_v2",
                "generation_logs", "generation_log_components", "category_blueprints",
                "service_catalog", "user_subscriptions", "payment_history",
                "global_counters", "ad_leads", "ad_platform_configs", "ad_clients",
                "ad_campaigns", "ad_optimization_logs", "ad_ai_activities",
                "ad_metrics", "ad_wizard_progress", "ad_market_research",
                "ad_strategies", "effect_usage",
            ]
            with engine.connect() as conn:
                for table in rls_tables:
                    try:
                        conn.execute(sql_text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY'))
                    except Exception:
                        pass  # Table may not exist yet
                conn.commit()
            logger.info("RLS abilitato su tutte le tabelle")
        except Exception as e:
            logger.error(f"Errore connessione database: {e}")
            logger.error(traceback.format_exc())
    else:
        logger.warning("Database non disponibile - skip inizializzazione tabelle")

    # Seed service catalog if empty
    try:
        from app.services.seed_services import seed_service_catalog
        seed_service_catalog()
    except Exception as e:
        logger.warning(f"Seed catalogo servizi fallito: {e}")

    # Seed category blueprints if empty
    try:
        from app.services.seed_category_blueprints import seed_category_blueprints
        seed_category_blueprints()
    except Exception as e:
        logger.warning(f"Seed category blueprints fallito: {e}")

    # Seed design knowledge (in-memory keyword store, instant)
    try:
        from app.services.design_knowledge import get_collection_stats
        stats = get_collection_stats()
        if stats.get("total_patterns", 0) == 0:
            logger.info("Design knowledge vuoto - seeding...")
            from app.services.seed_design_knowledge import seed_all
            seed_all()
            stats = get_collection_stats()
            logger.info(f"Design knowledge seeded: {stats['total_patterns']} patterns")
        else:
            logger.info(f"Design knowledge ready: {stats['total_patterns']} patterns")
    except Exception as e:
        logger.warning(f"Design knowledge non disponibile: {e}")

    yield

    # Cleanup: close AI client connections
    try:
        from app.services.kimi_client import kimi, kimi_refine
        await kimi.close()
        if kimi_refine is not kimi:
            await kimi_refine.close()
        logger.info("AI client connections closed")
    except Exception as e:
        logger.warning(f"Error closing AI clients: {e}")

    logger.info("Server spento")

# Creazione app
logger.info("Creazione FastAPI app...")
app = FastAPI(
    title="Site Builder API",
    description="API per la creazione e gestione di siti web",
    version="0.3.0",
    lifespan=lifespan,
    redirect_slashes=True,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate Limiter - registra handler per 429 Too Many Requests
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger.info("Rate limiter configurato")

# CORS Middleware CUSTOM - DEVE ESSERE IL PRIMO!
logger.info("Configurazione CORS custom...")
app.add_middleware(CORSMiddlewareCustom)

# Anche il CORS standard di FastAPI (doppia protezione)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
logger.info("CORS configurato")

# Error handler globale
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Errore globale: {exc}", exc_info=True)
    # Don't leak internal error details to clients in production
    content = {"detail": "Errore interno del server"}
    if settings.DEBUG:
        content["error"] = str(exc)
    return JSONResponse(status_code=500, content=content)

# Import e registrazione routes
logger.info("Registrazione routes...")
try:
    from app.api.routes import auth
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    logger.info("Route auth registrate")
except Exception as e:
    logger.error(f"Errore registrazione route auth: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import sites
    app.include_router(sites.router, prefix="/api/sites", tags=["sites"])
    logger.info("Route sites registrate")
except Exception as e:
    logger.error(f"Errore registrazione route sites: {e}")
    logger.error(traceback.format_exc())

_generate_import_error = None
try:
    from app.api.routes import generate
    app.include_router(generate.router, prefix="/api", tags=["generate"])
    logger.info("Route generate registrate")
except Exception as e:
    _generate_import_error = f"{type(e).__name__}: {e}"
    logger.error(f"Errore registrazione route generate: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import components
    app.include_router(components.router, prefix="/api/components", tags=["components"])
    logger.info("Route components registrate")
except Exception as e:
    logger.error(f"Errore registrazione route components: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import deploy
    app.include_router(deploy.router, prefix="/api/deploy", tags=["deploy"])
    logger.info("Route deploy registrate")
except Exception as e:
    logger.error(f"Errore registrazione route deploy: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import admin
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    logger.info("Route admin registrate")
except Exception as e:
    logger.error(f"Errore registrazione route admin: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import payments
    app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
    logger.info("Route payments registrate")
except Exception as e:
    logger.error(f"Errore registrazione route payments: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import images
    app.include_router(images.router, prefix="/api/images", tags=["images"])
    logger.info("Route images registrate")
except Exception as e:
    logger.error(f"Errore registrazione route images: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import media
    app.include_router(media.router, prefix="/api/media", tags=["media"])
    logger.info("Route media registrate")
except Exception as e:
    logger.error(f"Errore registrazione route media: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes.chat import router as chat_router
    app.include_router(chat_router)
    logger.info("Route chat registrate")
except Exception as e:
    logger.error(f"Errore registrazione route chat: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import test_ai
    app.include_router(test_ai.router, prefix="/api", tags=["test"])
    logger.info("Test routes registrate")
except ImportError:
    pass
except Exception as e:
    logger.error(f"Errore registrazione test routes: {e}")

try:
    from app.api.routes import ads
    app.include_router(ads.router, prefix="/api/ads", tags=["ads"])
    logger.info("Route ads registrate")
except Exception as e:
    logger.error(f"Errore registrazione route ads: {e}")
    logger.error(traceback.format_exc())

try:
    from app.api.routes import v2_generate
    app.include_router(v2_generate.router, prefix="/api/v2", tags=["v2"])
    logger.info("Route v2 registrate")
except Exception as e:
    logger.error(f"Errore registrazione route v2: {e}")
    logger.error(traceback.format_exc())

logger.info("Routes registrate")

# ===== STATIC FILE SERVING (uploads) =====
try:
    from fastapi.staticfiles import StaticFiles
    _uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(_uploads_dir, exist_ok=True)
    app.mount("/static/uploads", StaticFiles(directory=_uploads_dir), name="uploads")
    logger.info(f"Static uploads mounted at /static/uploads -> {_uploads_dir}")
except Exception as e:
    logger.error(f"Errore mount static uploads: {e}")

# ===== ENDPOINTS BASE (senza prefisso /api) =====
@app.get("/")
async def root():
    return {
        "message": "Site Builder API",
        "version": "0.3.0",
        "docs": "/docs",
        "health": "/health",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "unknown"
    if engine is None:
        db_status = "not configured"
    else:
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            logger.error(f"Health check DB fallito: {e}")
            db_status = f"error: {str(e)}"
    
    result = {
        "status": "ok",
        "version": "0.3.0",
        "database": db_status
    }
    if _generate_import_error:
        result["generate_routes_error"] = _generate_import_error
    return result

@app.get("/ping")
async def ping():
    return {"pong": True, "status": "alive"}

@app.get("/debug/db-test")
async def debug_db_test():
    """Temporary diagnostic: test actual DB queries."""
    import traceback as _tb
    results = {}
    try:
        from sqlalchemy import text as _txt
        with engine.connect() as conn:
            r = conn.execute(_txt("SELECT COUNT(*) FROM users"))
            results["users_count"] = r.scalar()
    except Exception as e:
        results["users_query_error"] = f"{type(e).__name__}: {e}"
        results["traceback"] = _tb.format_exc()
    try:
        from app.core.database import get_db, SessionLocal
        db = SessionLocal()
        from app.models.user import User
        u = db.query(User).first()
        results["user_query"] = "OK" if u else "no users"
        db.close()
    except Exception as e:
        results["orm_query_error"] = f"{type(e).__name__}: {e}"
        results["orm_traceback"] = _tb.format_exc()
    return results

@app.get("/debug/imports")
async def debug_imports():
    """Diagnostica: prova a importare ogni modulo e riporta errori."""
    import traceback as _tb
    results = {}
    modules = [
        "app.services.sanitizer",
        "app.services.kimi_client",
        "app.services.swarm_generator",
        "app.services.quality_control",
        "app.services.databinding_generator",
        "app.services.ai_service",
        "app.models.global_counter",
        "app.models.site_version",
        "app.api.routes.sites",
        "app.api.routes.generate",
        "app.api.routes.components",
        "app.api.routes.deploy",
    ]
    for mod_name in modules:
        try:
            __import__(mod_name)
            results[mod_name] = "OK"
        except Exception as e:
            results[mod_name] = f"ERRORE: {type(e).__name__}: {e}\n{''.join(_tb.format_exception(e)[-3:])}"
    # Also list registered routes
    results["_registered_routes"] = sorted(set(
        f"{r.methods} {r.path}" for r in app.routes if hasattr(r, "methods")
    ))
    return results

@app.head("/")
@app.head("/health")
async def head_endpoints():
    """Gestisce richieste HEAD per health checks"""
    return JSONResponse(content={})

logger.info("App inizializzata!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
