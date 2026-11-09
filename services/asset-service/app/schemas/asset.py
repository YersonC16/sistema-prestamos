from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.models.asset import AssetStatus, AssetType

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)]


class AssetCreate(BaseModel):
    name: Name
    asset_type: AssetType
    description: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=50)
    brand: str | None = Field(default=None, max_length=100)
    serial_number: str | None = Field(default=None, max_length=100)

    @field_validator("description", "code", "brand", "serial_number")
    @classmethod
    def empty_text_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class AssetDecommission(BaseModel):
    reason: Reason


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None = None
    brand: str | None = None
    serial_number: str | None = None
    asset_type: AssetType
    status: AssetStatus
    description: str | None = None


class AssetDetailResponse(AssetResponse):
    decommissioned_at: datetime | None = None
    decommission_reason: str | None = None
    decommissioned_by: str | None = None