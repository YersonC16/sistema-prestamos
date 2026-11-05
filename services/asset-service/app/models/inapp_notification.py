import os

from sqlalchemy import Boolean, Column, DateTime, Integer, String, false

from app.core.database import Base
from app.core.timeutils import utc_now

_table_args = {} if os.getenv("TESTING") == "true" else {"schema": "assets"}


class InAppNotification(Base):
    """Aviso dentro del sistema (la campanita) para un usuario."""

    __tablename__ = "inapp_notifications"
    __table_args__ = _table_args

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(60), nullable=False)
    site = Column(String(50), nullable=False)
    asset_id = Column(Integer, nullable=True)
    title = Column(String(150), nullable=False)
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False, server_default=false())
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)