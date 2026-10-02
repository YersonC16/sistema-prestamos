from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Person = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]
Provider = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]


class MaintenanceCreate(BaseModel):
    asset_id: int
    location: Literal["interno", "externo"]
    assigned_to: Person | None = None
    provider_name: Provider | None = None
    maintenance_type: Literal["preventivo", "correctivo"]
    reason: Reason
    expected_end_date: datetime | None = None

    @model_validator(mode="after")
    def check_destination(self):
        if self.location == "interno" and not self.assigned_to:
            raise ValueError("Indica la persona a quien se asigna el mantenimiento interno")
        if self.location == "externo" and not self.provider_name:
            raise ValueError("Indica el proveedor o taller externo")
        return self


class MaintenanceEscalate(BaseModel):
    provider_name: Provider
    notes: str | None = Field(default=None, max_length=500)


class MaintenanceFinish(BaseModel):
    notes: str | None = Field(default=None, max_length=500)


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    asset_name: str | None = None
    location: str
    assigned_to: str | None = None
    provider_name: str | None = None
    maintenance_type: str
    reason: str
    status: str
    source: str
    source_loan_id: int | None = None
    started_at: datetime
    expected_end_date: datetime | None = None
    finished_at: datetime | None = None
    finish_notes: str | None = None
    created_by: str | None = None