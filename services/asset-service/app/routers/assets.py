from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.timeutils import utc_now
from app.models.asset import Asset, AssetStatus
from app.models.audit_log import AuditLog
from app.models.maintenance import Maintenance
from app.models.user import User, UserRole
from app.schemas.asset import AssetCreate, AssetDecommission, AssetDetailResponse, AssetResponse
from app.schemas.audit import AuditEntryResponse
from app.services.asset_factory import AssetFactory
from app.services.asset_flyweight import AssetCatalog
from app.services.audit_service import record_audit
from app.services.notifications.subject import emit_event

router = APIRouter(prefix="/assets", tags=["Activos"])
managers = require_roles(UserRole.ADMINISTRADOR, UserRole.ALMACENISTA)


def _load_catalog(db: Session) -> AssetCatalog:
    """Consulta solo lo necesario y arma el catálogo con flyweights compartidos."""
    rows = (
        db.query(
            Asset.id, Asset.code, Asset.status, Asset.name, Asset.asset_type,
            Asset.description, Asset.brand, Asset.serial_number,
        )
        .order_by(Asset.id)
        .all()
    )
    return AssetCatalog.from_rows(rows)


def _serial_exists(db: Session, brand: str | None, serial_number: str) -> bool:
    """La misma marca no repite un número de serie (sin distinguir mayúsculas)."""
    query = db.query(Asset.id).filter(func.lower(Asset.serial_number) == serial_number.lower())
    if brand:
        query = query.filter(func.lower(Asset.brand) == brand.lower())
    else:
        query = query.filter(Asset.brand.is_(None))
    return query.first() is not None


def _label(asset: Asset) -> str:
    parts = [f"{asset.name} ({asset.asset_type.value})"]
    if asset.brand:
        parts.append(f"marca {asset.brand}")
    if asset.serial_number:
        parts.append(f"serie {asset.serial_number}")
    if asset.code:
        parts.append(f"código {asset.code}")
    return ", ".join(parts)


@router.post("/", response_model=AssetResponse)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db), current_user: User = Depends(managers)):
    if payload.code and db.query(Asset).filter(Asset.code == payload.code).first():
        raise HTTPException(409, "Ya existe un activo con ese código")
    if payload.serial_number and _serial_exists(db, payload.brand, payload.serial_number):
        raise HTTPException(409, "Ya existe un activo con esa marca y número de serie")

    asset = AssetFactory.create_asset(
        asset_type=payload.asset_type,
        name=payload.name,
        description=payload.description,
        code=payload.code,
        brand=payload.brand,
        serial_number=payload.serial_number,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    record_audit(db, "asset", asset.id, "activo_registrado", _label(asset), current_user.full_name, current_user.role.value)
    # Observer: solo se avisa que pasó algo; quién reacciona no se sabe aquí
    emit_event(
        "activo_registrado", asset_id=asset.id, asset_name=asset.name,
        actor=current_user.full_name, detail=_label(asset),
    )
    return asset


@router.get("/", response_model=list[AssetResponse])
def list_assets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _load_catalog(db).summaries()


@router.get("/available", response_model=list[AssetResponse])
def list_available_assets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Asset).filter(Asset.status == AssetStatus.DISPONIBLE).order_by(Asset.id).all()


@router.get("/summary")
def assets_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Asset.status, func.count(Asset.id)).group_by(Asset.status).all()
    counts = {s.value: 0 for s in AssetStatus}
    for status, total in rows:
        counts[status.value] = total
    # "total" es el inventario vigente: los dados de baja se cuentan aparte
    active_total = sum(value for key, value in counts.items() if key != AssetStatus.BAJA.value)
    return {"total": active_total, **counts}


@router.get("/catalog/stats")
def catalog_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Muestra el efecto del Flyweight: cuántos activos y cuántos modelos compartidos."""
    catalog = _load_catalog(db)
    return {
        "assets": catalog.total_items,
        "shared_models": catalog.shared_models,
        "duplicates_avoided": catalog.total_items - catalog.shared_models,
    }


@router.get("/{asset_id}", response_model=AssetDetailResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset is None:
        raise HTTPException(404, "Activo no encontrado")
    return asset


@router.post("/{asset_id}/decommission", response_model=AssetDetailResponse)
def decommission_asset(
    asset_id: int,
    payload: AssetDecommission,
    db: Session = Depends(get_db),
    user: User = Depends(managers),
):
    """Baja definitiva: el activo sale de circulación y queda en el historial."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if asset is None:
        raise HTTPException(404, "Activo no encontrado")
    if asset.status == AssetStatus.BAJA:
        raise HTTPException(409, "El activo ya está dado de baja")
    if asset.status == AssetStatus.PRESTADO:
        raise HTTPException(400, "El activo está prestado: debe devolverse antes de darlo de baja")

    open_maintenance = (
        db.query(Maintenance).filter(Maintenance.asset_id == asset.id, Maintenance.status == "en_proceso").first()
    )
    if open_maintenance is not None:
        open_maintenance.status = "finalizado"
        open_maintenance.finished_at = utc_now()
        open_maintenance.finish_notes = f"Cerrado por baja del activo: {payload.reason}"[:500]

    asset.status = AssetStatus.BAJA
    asset.decommissioned_at = utc_now()
    asset.decommission_reason = payload.reason
    asset.decommissioned_by = user.full_name
    db.commit()
    db.refresh(asset)

    detail = f"Motivo: {payload.reason}"
    record_audit(db, "asset", asset.id, "activo_dado_de_baja", detail, user.full_name, user.role.value)
    emit_event("activo_dado_de_baja", asset_id=asset.id, asset_name=asset.name, actor=user.full_name, detail=detail)
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