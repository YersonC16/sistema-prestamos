from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: int | None = None
    action: str
    detail: str | None = None
    performed_by: str
    performed_by_role: str | None = None
    created_at: datetime