from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.schemas.asset import AssetCreate, AssetResponse
from app.services.asset_factory import AssetFactory
from app.models.asset import Asset
from app.models.user import User, UserRole

router = APIRouter(prefix="/assets", tags=["Activos"])

@router.post("/", response_model=AssetResponse)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMINISTRADOR, UserRole.ALMACENISTA)),
):
    asset = AssetFactory.create_asset(
        asset_type=payload.asset_type,
        name=payload.name,
        description=payload.description,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.get("/", response_model=list[AssetResponse])
def list_assets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Asset).all()

@router.get("/available", response_model=list[AssetResponse])
def list_available_assets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Asset).filter(Asset.status == "disponible").all()