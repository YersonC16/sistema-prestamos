import os

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base
from app.core.timeutils import utc_now

_table_args = {} if os.getenv("TESTING") == "true" else {"schema": "assets"}


class Maintenance(Base):
    __tablename__ = "maintenances"
    __table_args__ = _table_args

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, nullable=False, index=True)
    asset_name = Column(String(150), nullable=True)
    assigned_to = Column(String(150), nullable=False)  # persona a quien se asigna
    maintenance_type = Column(String(20), nullable=False)  # preventivo | correctivo
    reason = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="en_proceso")  # en_proceso | finalizado
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expected_end_date = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    finish_notes = Column(String(500), nullable=True)
    created_by = Column(String(150), nullable=True)