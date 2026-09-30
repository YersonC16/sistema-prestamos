from datetime import datetime

from app.models.loan import Loan, LoanStatus


class LoanBuilder:
    """Construye un objeto Loan paso a paso, validando cada dato."""

    def __init__(self):
        self._asset_id: int | None = None
        self._asset_name: str | None = None
        self._responsible_name: str | None = None
        self._loan_date: datetime | None = None
        self._expected_return_date: datetime | None = None
        self._notes: str | None = None
        self._registered_by_id: int | None = None
        self._registered_by_name: str | None = None

    def with_asset(self, asset_id: int) -> "LoanBuilder":
        self._asset_id = asset_id
        return self

    def with_asset_name(self, name: str | None) -> "LoanBuilder":
        self._asset_name = name
        return self

    def with_responsible(self, name: str) -> "LoanBuilder":
        if not name or not name.strip():
            raise ValueError("El responsable es obligatorio")
        self._responsible_name = name.strip()
        return self

    def with_loan_date(self, date: datetime) -> "LoanBuilder":
        self._loan_date = date
        return self

    def with_expected_return(self, date: datetime) -> "LoanBuilder":
        if self._loan_date and date <= self._loan_date:
            raise ValueError("La fecha de devolución debe ser posterior a la de préstamo")
        self._expected_return_date = date
        return self

    def with_notes(self, notes: str | None) -> "LoanBuilder":
        self._notes = notes.strip() if notes and notes.strip() else None
        return self

    def with_registered_by(self, user_id: int, user_name: str) -> "LoanBuilder":
        self._registered_by_id = user_id
        self._registered_by_name = user_name
        return self

    def build(self) -> Loan:
        required = [
            self._asset_id,
            self._responsible_name,
            self._loan_date,
            self._expected_return_date,
            self._registered_by_name,
        ]
        if not all(required):
            raise ValueError("Faltan datos obligatorios para construir el préstamo")
        return Loan(
            asset_id=self._asset_id,
            asset_name=self._asset_name,
            responsible_name=self._responsible_name,
            notes=self._notes,
            loan_date=self._loan_date,
            expected_return_date=self._expected_return_date,
            status=LoanStatus.ACTIVO,
            registered_by_id=self._registered_by_id,
            registered_by_name=self._registered_by_name,
        )