from pydantic import BaseModel, ConfigDict
from app.models.asset import AssetType, AssetStatus

class AssetCreate(BaseModel):
    name: str
    asset_type: AssetType
    description: str | None = None

class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    asset_type: AssetType
    status: AssetStatus
    description: str | None = None