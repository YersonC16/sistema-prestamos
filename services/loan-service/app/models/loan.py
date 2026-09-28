from sqlalchemy import Column, Integer, String, DateTime, Enum
from app.core.database import Base
import enum
import os

class LoanStatus(str, enum.Enum):
    ACTIVO = "activo"
    DEVUELTO = "devuelto"
    ATRASADO = "atrasado"

_IS_TESTING = os.getenv("TESTING") == "true"
_table_args = {} if _IS_TESTING else {"schema": "loans"}
_enum_schema = None if _IS_TESTING else "loans"

class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = _table_args

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, nullable=False)
    responsible_name = Column(String(150), nullable=False)
    loan_date = Column(DateTime, nullable=False)
    expected_return_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime, nullable=True)
    status = Column(
        Enum(
            LoanStatus,
            name="loanstatus",
            schema=_enum_schema,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=LoanStatus.ACTIVO,
    )