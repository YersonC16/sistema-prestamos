from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from app.core.database import get_db
from app.core.config import settings
from app.core.deps import get_current_user_payload, oauth2_scheme
from app.schemas.loan import LoanCreate, LoanResponse
from app.services.loan_builder import LoanBuilder
from app.services.event_publisher import publish_event
from app.models.loan import Loan, LoanStatus
from datetime import datetime, timezone

router = APIRouter(prefix="/loans", tags=["Préstamos"])

@router.post("/", response_model=LoanResponse)
def create_loan(
    payload: LoanCreate,
    db: Session = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload),
    token: str = Depends(oauth2_scheme),
):
    resp = requests.get(
        f"{settings.asset_service_url}/assets/available",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code != 200:
        raise HTTPException(502, "No se pudo verificar la disponibilidad del activo")

    available_ids = [a["id"] for a in resp.json()]
    if payload.asset_id not in available_ids:
        raise HTTPException(400, "El activo no está disponible para préstamo")

    loan = (
        LoanBuilder()
        .with_asset(payload.asset_id)
        .with_responsible(payload.responsible_name)
        .with_loan_date(payload.loan_date)
        .with_expected_return(payload.expected_return_date)
        .build()
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)

    publish_event("prestamo.creado", {"asset_id": loan.asset_id, "loan_id": loan.id})

    return loan

@router.put("/{loan_id}/return", response_model=LoanResponse)
def return_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    user_payload: dict = Depends(get_current_user_payload),
):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(404, "Préstamo no encontrado")
    loan.actual_return_date = datetime.now(timezone.utc)
    loan.status = LoanStatus.DEVUELTO
    db.commit()
    db.refresh(loan)

    publish_event("prestamo.devuelto", {"asset_id": loan.asset_id, "loan_id": loan.id})

    return loan

@router.get("/", response_model=list[LoanResponse])
def list_loans(db: Session = Depends(get_db), user_payload: dict = Depends(get_current_user_payload)):
    return db.query(Loan).all()