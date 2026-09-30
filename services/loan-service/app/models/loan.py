import enum
import os

from sqlalchemy import Column, DateTime, Enum, Integer, String

from app.core.database import Base


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
    asset_id = Column(Integer, nullable=False, index=True)
    asset_name = Column(String(150), nullable=True)
    responsible_id = Column(Integer, nullable=True, index=True)
    responsible_name = Column(String(150), nullable=False)
    responsible_document = Column(String(50), nullable=True)
    notes = Column(String(255), nullable=True)
    loan_date = Column(DateTime, nullable=False)
    expected_return_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime, nullable=True)
    status = Column(
        Enum(LoanStatus, name="loanstatus", schema=_enum_schema, values_callable=lambda e: [m.value for m in e]),
        default=LoanStatus.ACTIVO,
    )
    registered_by_id = Column(Integer, nullable=True)
    registered_by_name = Column(String(150), nullable=True)
    returned_by_name = Column(String(150), nullable=True)
    return_condition = Column(String(30), nullable=True)
    return_notes = Column(String(500), nullable=True)