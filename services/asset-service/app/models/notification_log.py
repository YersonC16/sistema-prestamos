import os

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base
from app.core.timeutils import utc_now

_table_args = {} if os.getenv("TESTING") == "true" else {"schema": "assets"}


class NotificationLog(Base):
    """Cada intento de notificación: a quién, por qué canal y cómo terminó."""

    __tablename__ = "notification_log"
    __table_args__ = _table_args

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(60), nullable=False, index=True)
    site = Column(String(50), nullable=False, index=True)
    asset_id = Column(Integer, nullable=True)
    asset_name = Column(String(150), nullable=True)
    recipient_email = Column(String(150), nullable=True)
    recipient_name = Column(String(150), nullable=True)
    channel = Column(String(20), nullable=False)  # correo | simulado | -
    status = Column(String(20), nullable=False)  # enviado | simulado | fallido | sin_destinatario
    subject = Column(String(255), nullable=True)
    error = Column(String(300), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)