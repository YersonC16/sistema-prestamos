from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.errors import BusinessRuleError, NotFoundError
from app.models.loan import Loan, LoanStatus
from app.models.loan_history import LoanHistory
from app.services.decorators import (
    AuditDecorator,
    EventPublisherDecorator,
    RoleGuardDecorator,
    TimingDecorator,
)
from app.services.operations import CreateLoanOperation, Operation, OperationContext, OPEN_STATUSES, ReturnLoanOperation

ROLES_THAT_MANAGE_LOANS = ("administrador", "almacenista")


def _was_late(loan: Loan) -> bool:
    return bool(loan.actual_return_date and loan.actual_return_date > loan.expected_return_date)


def _created_detail(context, loan: Loan) -> str:
    return f"Prestado a {loan.responsible_name}. Devolución prevista: {loan.expected_return_date:%d/%m/%Y}"


def _created_event(context, loan: Loan) -> dict:
    return {
        "asset_id": loan.asset_id,
        "loan_id": loan.id,
        "responsible_name": loan.responsible_name,
        "expected_return_date": loan.expected_return_date.isoformat(),
        "registered_by": loan.registered_by_name,
    }


def _returned_detail(context, loan: Loan) -> str:
    text = f"Devuelto por {loan.responsible_name}"
    if _was_late(loan):
        text += " (fuera de plazo)"
    if loan.return_condition == "con_novedad":
        text += f" con novedad: {loan.return_notes}"
    return text


def _returned_event(context, loan: Loan) -> dict:
    return {
        "asset_id": loan.asset_id,
        "loan_id": loan.id,
        "responsible_name": loan.responsible_name,
        "condition": loan.return_condition,
        "notes": loan.return_notes,
        "returned_by": loan.returned_by_name,
        "was_late": _was_late(loan),
        "maintenance_location": context.data.get("maintenance_location"),
        "maintenance_assigned_to": context.data.get("maintenance_assigned_to"),
        "maintenance_provider": context.data.get("maintenance_provider"),
    }


class LoanFacade:
    """Fachada: una entrada simple al módulo de préstamos. Esconde cómo se
    arma la cadena de decoradores, el Builder y las consultas."""

    def __init__(self, db: Session):
        self._db = db
        self._create_chain = self._compose(
            CreateLoanOperation(), "prestamo.creado", "prestamo_creado", _created_event, _created_detail
        )
        self._return_chain = self._compose(
            ReturnLoanOperation(), "prestamo.devuelto", "prestamo_devuelto", _returned_event, _returned_detail
        )

    @staticmethod
    def _compose(core: Operation, routing_key: str, action: str, event_builder, detail_builder) -> Operation:
        """Apila las capas: de adentro hacia afuera."""
        operation = EventPublisherDecorator(core, routing_key, event_builder)
        operation = AuditDecorator(operation, action, detail_builder)
        operation = RoleGuardDecorator(operation, ROLES_THAT_MANAGE_LOANS)
        return TimingDecorator(operation)

    # ---- Operaciones con efectos (pasan por la cadena de decoradores) ----

    def register_loan(self, data: dict, user: dict, token: str | None) -> Loan:
        return self._create_chain.execute(OperationContext(self._db, user, data, token))

    def register_return(self, loan_id: int, payload: dict, user: dict) -> Loan:
        data = {"loan_id": loan_id, **payload}
        return self._return_chain.execute(OperationContext(self._db, user, data))
    
    # ---- Consultas ----

    def list_loans(self, status: str | None = None, asset_id: int | None = None) -> list[Loan]:
        query = self._db.query(Loan)
        if status:
            try:
                query = query.filter(Loan.status == LoanStatus(status))
            except ValueError as exc:
                raise BusinessRuleError(f"Estado de préstamo desconocido: {status}") from exc
        if asset_id:
            query = query.filter(Loan.asset_id == asset_id)
        return query.order_by(Loan.id.desc()).all()

    def current_holder(self, asset_id: int) -> Loan | None:
        """Préstamo abierto del activo: quién lo tiene ahora."""
        return (
            self._db.query(Loan)
            .filter(Loan.asset_id == asset_id, Loan.status.in_(OPEN_STATUSES))
            .order_by(Loan.id.desc())
            .first()
        )

    def history_of_loan(self, loan_id: int) -> list[LoanHistory]:
        if self._db.query(Loan.id).filter(Loan.id == loan_id).first() is None:
            raise NotFoundError("Préstamo no encontrado")
        return self._db.query(LoanHistory).filter(LoanHistory.loan_id == loan_id).order_by(LoanHistory.id.desc()).all()

    def movement_log(self, limit: int = 50) -> list[LoanHistory]:
        return self._db.query(LoanHistory).order_by(LoanHistory.id.desc()).limit(limit).all()

    def summary(self) -> dict:
        rows = self._db.query(Loan.status, func.count(Loan.id)).group_by(Loan.status).all()
        counts = {s.value: 0 for s in LoanStatus}
        for status, total in rows:
            counts[status.value] = total
        return {"total": sum(counts.values()), **counts}