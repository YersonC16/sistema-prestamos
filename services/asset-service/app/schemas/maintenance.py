from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Person = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]


class MaintenanceCreate(BaseModel):
    asset_id: int
    assigned_to: Person
    maintenance_type: Literal["preventivo", "correctivo"]
    reason: Reason
    expected_end_date: datetime | None = None


class MaintenanceFinish(BaseModel):
    notes: str | None = Field(default=None, max_length=500)


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    asset_name: str | None = None
    assigned_to: str
    maintenance_type: str
    reason: str
    status: str
    started_at: datetime
    expected_end_date: datetime | None = None
    finished_at: datetime | None = None
    finish_notes: str | None = None
    created_by: str | None = None