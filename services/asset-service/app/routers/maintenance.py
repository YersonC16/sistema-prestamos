from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.timeutils import utc_now
from app.models.asset import Asset, AssetStatus
from app.models.maintenance import Maintenance
from app.models.user import User, UserRole
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceEscalate,
    MaintenanceFinish,
    MaintenanceResponse,
)
from app.services.audit_service import record_audit

router = APIRouter(prefix="/maintenance", tags=["Mantenimiento"])
managers = require_roles(UserRole.ADMINISTRADOR, UserRole.ALMACENISTA)


@router.post("/", response_model=MaintenanceResponse)
def start_maintenance(payload: MaintenanceCreate, db: Session = Depends(get_db), user: User = Depends(managers)):
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if asset is None:
        raise HTTPException(404, "Activo no encontrado")
    if asset.status == AssetStatus.PRESTADO:
        raise HTTPException(400, "El activo está prestado: debe devolverse antes de enviarlo a mantenimiento")

    already_open = (
        db.query(Maintenance).filter(Maintenance.asset_id == asset.id, Maintenance.status == "en_proceso").first()
    )
    if already_open:
        raise HTTPException(409, "El activo ya tiene un mantenimiento en proceso")

    maintenance = Maintenance(
        asset_id=asset.id,
        asset_name=asset.name,
        location=payload.location,
        assigned_to=payload.assigned_to,
        provider_name=payload.provider_name,
        maintenance_type=payload.maintenance_type,
        reason=payload.reason,
        expected_end_date=payload.expected_end_date,
        source="manual",
        created_by=user.full_name,
    )
    asset.status = AssetStatus.MANTENIMIENTO
    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)

    destination = (
        f"Asignado a {maintenance.assigned_to}" if payload.location == "interno" else f"Enviado a {maintenance.provider_name}"
    )
    record_audit(
        db, "asset", asset.id, "mantenimiento_iniciado",
        f"{destination} ({maintenance.maintenance_type}): {maintenance.reason}",
        user.full_name, user.role.value,
    )
    return maintenance


@router.put("/{maintenance_id}/escalate", response_model=MaintenanceResponse)
def escalate_maintenance(
    maintenance_id: int,
    payload: MaintenanceEscalate,
    db: Session = Depends(get_db),
    user: User = Depends(managers),
):
    """Un mantenimiento interno que no se pudo resolver pasa a externo,
    conservando el mismo registro (no crea uno nuevo)."""
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
    if maintenance is None:
        raise HTTPException(404, "Mantenimiento no encontrado")
    if maintenance.status != "en_proceso":
        raise HTTPException(409, "Solo se puede escalar un mantenimiento en proceso")
    if maintenance.location == "externo":
        raise HTTPException(409, "Este mantenimiento ya está con un proveedor externo")

    maintenance.location = "externo"
    maintenance.provider_name = payload.provider_name
    db.commit()
    db.refresh(maintenance)

    detail = f"No se pudo resolver internamente, se envía a {payload.provider_name}"
    if payload.notes:
        detail += f": {payload.notes}"
    record_audit(db, "asset", maintenance.asset_id, "mantenimiento_escalado_externo", detail, user.full_name, user.role.value)
    return maintenance


@router.put("/{maintenance_id}/finish", response_model=MaintenanceResponse)
def finish_maintenance(
    maintenance_id: int,
    payload: MaintenanceFinish | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(managers),
):
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
    if maintenance is None:
        raise HTTPException(404, "Mantenimiento no encontrado")
    if maintenance.status == "finalizado":
        raise HTTPException(409, "Este mantenimiento ya fue finalizado")

    maintenance.status = "finalizado"
    maintenance.finished_at = utc_now()
    maintenance.finish_notes = payload.notes if payload else None

    asset = db.query(Asset).filter(Asset.id == maintenance.asset_id).first()
    if asset is not None:
        asset.status = AssetStatus.DISPONIBLE
    db.commit()
    db.refresh(maintenance)

    where = maintenance.assigned_to if maintenance.location == "interno" else maintenance.provider_name
    record_audit(
        db, "asset", maintenance.asset_id, "mantenimiento_finalizado",
        f"Finalizado por {where}" + (f": {maintenance.finish_notes}" if maintenance.finish_notes else ""),
        user.full_name, user.role.value,
    )
    return maintenance


@router.get("/", response_model=list[MaintenanceResponse])
def list_maintenances(
    status: str | None = None,
    asset_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Maintenance)
    if status:
        query = query.filter(Maintenance.status == status)
    if asset_id:
        query = query.filter(Maintenance.asset_id == asset_id)
    return query.order_by(Maintenance.id.desc()).all()