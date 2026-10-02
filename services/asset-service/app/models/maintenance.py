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
    location = Column(String(10), nullable=False, default="interno")  # interno | externo
    assigned_to = Column(String(150), nullable=True)  # persona interna (si location=interno)
    provider_name = Column(String(150), nullable=True)  # taller/proveedor (si location=externo)
    maintenance_type = Column(String(20), nullable=False)  # preventivo | correctivo
    reason = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="en_proceso")  # en_proceso | finalizado
    source = Column(String(30), nullable=False, default="manual")  # manual | devolucion_con_novedad
    source_loan_id = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expected_end_date = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    finish_notes = Column(String(500), nullable=True)
    created_by = Column(String(150), nullable=True)