import os

from sqlalchemy import Boolean, Column, Integer, String, true

from app.core.database import Base

_table_args = {} if os.getenv("TESTING") == "true" else {"schema": "loans"}


class Responsible(Base):
    """Persona a quien se le puede asignar un préstamo. No es un usuario
    del sistema: no inicia sesión, solo se registra para trazabilidad."""

    __tablename__ = "responsibles"
    __table_args__ = _table_args

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    document_type = Column(String(15), nullable=False)  # CC | TI | CE | PASAPORTE
    document_number = Column(String(30), unique=True, nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default=true())