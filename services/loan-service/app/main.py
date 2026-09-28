from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import loans

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loan Service - Sistema de Préstamos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loans.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "loan-service"}