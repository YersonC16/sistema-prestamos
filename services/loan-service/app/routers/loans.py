from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, oauth2_scheme, require_roles
from app.schemas.loan import LoanCreate, LoanHistoryResponse, LoanResponse, LoanReturn
from app.services.loan_facade import LoanFacade

router = APIRouter(prefix="/loans", tags=["Préstamos"])


def get_facade(db: Session = Depends(get_db)) -> LoanFacade:
    return LoanFacade(db)


@router.post("/", response_model=LoanResponse)
def create_loan(
    payload: LoanCreate,
    user: dict = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    facade: LoanFacade = Depends(get_facade),
):
    return facade.register_loan(payload.model_dump(), user, token)


@router.get("/", response_model=list[LoanResponse])
def list_loans(
    status: str | None = None,
    asset_id: int | None = None,
    _: dict = Depends(get_current_user),
    facade: LoanFacade = Depends(get_facade),
):
    return facade.list_loans(status, asset_id)


@router.get("/summary")
def loans_summary(_: dict = Depends(get_current_user), facade: LoanFacade = Depends(get_facade)):
    return facade.summary()


@router.get("/history", response_model=list[LoanHistoryResponse])
def movement_log(
    limit: int = Query(default=50, ge=1, le=200),
    _: dict = Depends(require_roles("administrador", "almacenista")),
    facade: LoanFacade = Depends(get_facade),
):
    return facade.movement_log(limit)


@router.get("/asset/{asset_id}/current", response_model=LoanResponse | None)
def current_holder(asset_id: int, _: dict = Depends(get_current_user), facade: LoanFacade = Depends(get_facade)):
    return facade.current_holder(asset_id)


@router.get("/{loan_id}/history", response_model=list[LoanHistoryResponse])
def loan_history(loan_id: int, _: dict = Depends(get_current_user), facade: LoanFacade = Depends(get_facade)):
    return facade.history_of_loan(loan_id)


@router.put("/{loan_id}/return", response_model=LoanResponse)
def return_loan(
    loan_id: int,
    payload: LoanReturn | None = None,
    user: dict = Depends(get_current_user),
    facade: LoanFacade = Depends(get_facade),
):
    data = payload or LoanReturn()
    return facade.register_return(loan_id, data.condition, data.notes, user)