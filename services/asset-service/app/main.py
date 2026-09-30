import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine

# Importar los modelos los registra en Base.metadata (lo necesita create_all)
from app.models import asset as _asset_model  # noqa: F401
from app.models import audit_log as _audit_model  # noqa: F401
from app.models import maintenance as _maintenance_model  # noqa: F401
from app.models import user as _user_model  # noqa: F401
from app.routers import assets, audit, auth, users
from app.routers import maintenance as maintenance_router
from app.services.event_consumer import start_consumer_thread

IS_TESTING = os.getenv("TESTING") == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # En pruebas no se toca la base real ni se abren hilos de fondo
    if not IS_TESTING:
        Base.metadata.create_all(bind=engine)
        start_consumer_thread()
    yield


app = FastAPI(title="Asset Service - Sistema de Préstamos", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assets.router)
app.include_router(maintenance_router.router)
app.include_router(audit.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "asset-service"}