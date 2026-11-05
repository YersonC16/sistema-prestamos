from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.notifications.events import EVENT_TYPES


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    site: str
    asset_id: int | None = None
    asset_name: str | None = None
    recipient_email: str | None = None
    recipient_name: str | None = None
    channel: str
    status: str
    subject: str | None = None
    error: str | None = None
    created_at: datetime


class LabRunRequest(BaseModel):
    event_type: str
    site: str = Field(default="concreto", min_length=2, max_length=50)
    channel: Literal["simulado", "correo"] = "simulado"

    @field_validator("event_type")
    @classmethod
    def known_event(cls, value: str) -> str:
        if value not in EVENT_TYPES:
            raise ValueError("Evento desconocido")
        return value

    @field_validator("site")
    @classmethod
    def normalize_site(cls, value: str) -> str:
        return value.strip().lower()


class LabDelivery(BaseModel):
    recipient: str
    channel: str
    status: str
    error: str | None = None


class LabReportResponse(BaseModel):
    mode: str
    steps: list[str]
    deliveries: list[LabDelivery]
    elapsed_ms: float


class LabRunResponse(BaseModel):
    event_type: str
    site: str
    channel: str
    reports: list[LabReportResponse]