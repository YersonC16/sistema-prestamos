from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
import enum
import os

class AssetType(str, enum.Enum):
    EQUIPO = "equipo"
    HERRAMIENTA = "herramienta"
    OTRO = "otro"

class AssetStatus(str, enum.Enum):
    DISPONIBLE = "disponible"
    PRESTADO = "prestado"
    MANTENIMIENTO = "mantenimiento"

_IS_TESTING = os.getenv("TESTING") == "true"
_table_args = {} if _IS_TESTING else {"schema": "assets"}
_enum_schema = None if _IS_TESTING else "assets"

class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = _table_args

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    asset_type = Column(
        Enum(
            AssetType,
            name="assettype",
            schema=_enum_schema,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    status = Column(
        Enum(
            AssetStatus,
            name="assetstatus",
            schema=_enum_schema,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=AssetStatus.DISPONIBLE,
    )
    description = Column(String(255), nullable=True)