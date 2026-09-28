from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import assets, auth
from app.services.event_consumer import start_consumer_thread

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que corre al iniciar la aplicación
    start_consumer_thread()
    yield
    # Código que correría al apagar la aplicación (no necesitamos nada aquí)


app = FastAPI(title="Asset Service - Sistema de Préstamos", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(assets.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "asset-service"}