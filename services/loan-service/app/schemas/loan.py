from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.loan import LoanStatus


class LoanCreate(BaseModel):
    asset_id: int
    responsible_id: int
    expected_return_date: datetime
    notes: str | None = Field(default=None, max_length=255)


class LoanReturn(BaseModel):
    condition: Literal["bueno", "con_novedad"] = "bueno"
    notes: str | None = Field(default=None, max_length=500)
    maintenance_location: Literal["interno", "externo"] | None = None
    maintenance_assigned_to: str | None = None
    maintenance_provider: str | None = None

    @model_validator(mode="after")
    def novelty_needs_description(self):
        if self.condition == "con_novedad":
            if not (self.notes and self.notes.strip()):
                raise ValueError("Describe la novedad encontrada en el activo")
            if self.maintenance_location is None:
                raise ValueError("Indica si el mantenimiento es interno o con el proveedor")
            if self.maintenance_location == "interno" and not (self.maintenance_assigned_to and self.maintenance_assigned_to.strip()):
                raise ValueError("Indica a quién se asigna el mantenimiento interno")
            if self.maintenance_location == "externo" and not (self.maintenance_provider and self.maintenance_provider.strip()):
                raise ValueError("Indica el proveedor o taller externo")
        return self

class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    asset_name: str | None = None
    responsible_id: int | None = None
    responsible_name: str
    responsible_document: str | None = None
    notes: str | None = None
    loan_date: datetime
    expected_return_date: datetime
    actual_return_date: datetime | None = None
    status: LoanStatus
    registered_by_name: str | None = None
    returned_by_name: str | None = None
    return_condition: str | None = None
    return_notes: str | None = None


class LoanHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    loan_id: int
    asset_id: int
    action: str
    detail: str | None = None
    performed_by: str
    performed_by_role: str | None = None
    created_at: datetime