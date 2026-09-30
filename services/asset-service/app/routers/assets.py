from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.asset import Asset, AssetStatus
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.asset import AssetCreate, AssetResponse
from app.schemas.audit import AuditEntryResponse
from app.services.asset_factory import AssetFactory
from app.services.audit_service import record_audit

router = APIRouter(prefix="/assets", tags=["Activos"])


@router.post("/", response_model=AssetResponse)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMINISTRADOR, UserRole.ALMACENISTA)),
):
    if payload.code and db.query(Asset).filter(Asset.code == payload.code).first():
        raise HTTPException(409, "Ya existe un activo con ese código")

    asset = AssetFactory.create_asset(
        asset_type=payload.asset_type,
        name=payload.name,
        description=payload.description,
        code=payload.code,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    code_text = f", código {asset.code}" if asset.code else ""
    record_audit(
        db, "asset", asset.id, "activo_registrado",
        f"{asset.name} ({asset.asset_type.value}){code_text}",
        current_user.full_name, current_user.role.value,
    )
    return asset


@router.get("/", response_model=list[AssetResponse])
def list_assets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Asset).order_by(Asset.id).all()


@router.get("/available", response_model=list[AssetResponse])
def list_available_assets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Asset).filter(Asset.status == AssetStatus.DISPONIBLE).order_by(Asset.id).all()


@router.get("/summary")
def assets_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Asset.status, func.count(Asset.id)).group_by(Asset.status).all()
    counts = {s.value: 0 for s in AssetStatus}
    for status, total in rows:
        counts[status.value] = total
    return {"total": sum(counts.values()), **counts}


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset is None:
        raise HTTPException(404, "Activo no encontrado")
    return asset


@router.get("/{asset_id}/history", response_model=list[AuditEntryResponse])
def asset_history(asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.query(Asset.id).filter(Asset.id == asset_id).first() is None:
        raise HTTPException(404, "Activo no encontrado")
    return (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == "asset", AuditLog.entity_id == asset_id)
        .order_by(AuditLog.id.desc())
        .all()
    )