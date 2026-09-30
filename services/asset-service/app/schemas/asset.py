from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.models.asset import AssetStatus, AssetType

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]


class AssetCreate(BaseModel):
    name: Name
    asset_type: AssetType
    description: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=50)

    @field_validator("description", "code")
    @classmethod
    def empty_text_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None = None
    asset_type: AssetType
    status: AssetStatus
    description: str | None = None