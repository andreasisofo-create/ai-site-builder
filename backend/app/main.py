"""
Site Builder - FastAPI Backend
API per la gestione dei siti web, componenti e deploy
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import sites, components, deploy, auth, generate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestione del ciclo di vita dell'applicazione"""
    # Startup: crea le tabelle nel database
    Base.metadata.create_all(bind=engine)
    print("🚀 Database inizializzato")
    yield
    # Shutdown
    print("👋 Server spento")


app = FastAPI(
    title="Site Builder API",
    description="API per la creazione e gestione di siti web",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
