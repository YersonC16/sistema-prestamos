import os

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base
from app.core.timeutils import utc_now

_table_args = {} if os.getenv("TESTING") == "true" else {"schema": "assets"}


class AuditLog(Base):
    """Registro de operaciones: quién hizo qué, sobre qué y cuándo."""

    __tablename__ = "audit_log"
    __table_args__ = _table_args

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(30), nullable=False, index=True)  # asset | user
    entity_id = Column(Integer, nullable=True, index=True)
    action = Column(String(60), nullable=False)
    detail = Column(String(500), nullable=True)
    performed_by = Column(String(150), nullable=False)
    performed_by_role = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)