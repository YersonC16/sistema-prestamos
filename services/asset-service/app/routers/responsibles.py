from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.responsible import Responsible
from app.schemas.responsible import ResponsibleCreate, ResponsibleResponse, ResponsibleUpdate

router = APIRouter(prefix="/responsibles", tags=["Responsables"])
managers = require_roles("administrador", "almacenista")


@router.post("/", response_model=ResponsibleResponse)
def create_responsible(payload: ResponsibleCreate, db: Session = Depends(get_db), _: dict = Depends(managers)):
    exists = db.query(Responsible).filter(Responsible.document_number == payload.document_number).first()
    if exists:
        raise HTTPException(409, "Ya existe un responsable con ese número de documento")

    responsible = Responsible(**payload.model_dump())
    db.add(responsible)
    db.commit()
    db.refresh(responsible)
    return responsible


@router.get("/", response_model=list[ResponsibleResponse])
def list_responsibles(
    active_only: bool = False,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    query = db.query(Responsible)
    if active_only:
        query = query.filter(Responsible.is_active.is_(True))
    return query.order_by(Responsible.full_name).all()


@router.patch("/{responsible_id}", response_model=ResponsibleResponse)
def update_responsible(
    responsible_id: int,
    payload: ResponsibleUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(managers),
):
    responsible = db.query(Responsible).filter(Responsible.id == responsible_id).first()
    if responsible is None:
        raise HTTPException(404, "Responsable no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(responsible, field, value)

    db.commit()
    db.refresh(responsible)
    return responsible