import enum
import os

from sqlalchemy import Boolean, Column, Enum, Integer, String, true

from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMINISTRADOR = "administrador"
    ALMACENISTA = "almacenista"
    PERSONAL_AUTORIZADO = "personal_autorizado"


_IS_TESTING = os.getenv("TESTING") == "true"
_table_args = {} if _IS_TESTING else {"schema": "assets"}
_enum_schema = None if _IS_TESTING else "assets"


class User(Base):
    __tablename__ = "users"
    __table_args__ = _table_args

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="userrole", schema=_enum_schema, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=UserRole.PERSONAL_AUTORIZADO,
    )
    is_active = Column(Boolean, nullable=False, default=True, server_default=true())