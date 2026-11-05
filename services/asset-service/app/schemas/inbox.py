from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InboxItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    site: str
    asset_id: int | None = None
    title: str
    message: str
    is_read: bool
    created_at: datetime


class InboxResponse(BaseModel):
    unread_count: int
    items: list[InboxItemResponse]