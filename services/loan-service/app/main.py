import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine
from app.core.errors import DomainError

# Importar los modelos los registra en Base.metadata (lo necesita create_all)
from app.models import loan as _loan_model  # noqa: F401
from app.models import loan_history as _loan_history_model  # noqa: F401
from app.models import responsible as _responsible_model  # noqa: F401
from app.routers import loans, responsibles
from app.services.overdue_checker import start_overdue_checker_thread

IS_TESTING = os.getenv("TESTING") == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not IS_TESTING:
        Base.metadata.create_all(bind=engine)
        start_overdue_checker_thread()
    yield


app = FastAPI(title="Loan Service - Sistema de Préstamos", lifespan=lifespan)

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


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


app.include_router(loans.router)
app.include_router(responsibles.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "loan-service"}