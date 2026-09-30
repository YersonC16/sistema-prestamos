from app.core.errors import BusinessRuleError, ConflictError, ExternalServiceError, NotFoundError
from app.core.timeutils import to_naive_utc, utc_now_naive
from app.models.loan import Loan, LoanStatus
from app.models.responsible import Responsible
from app.services.asset_client import AssetServiceClient, AssetServiceError
from app.services.loan_builder import LoanBuilder

OPEN_STATUSES = (LoanStatus.ACTIVO, LoanStatus.ATRASADO)


class OperationContext:
    """Datos que viajan por toda la cadena de decoradores."""

    def __init__(self, db, user: dict, data: dict | None = None, token: str | None = None):
        self.db = db
        self.user = user
        self.data = data or {}
        self.token = token


class Operation:
    """Componente del patrón Decorator: contrato común de toda operación."""

    name = "operacion"

    def execute(self, context: OperationContext):
        raise NotImplementedError("Toda operación debe implementar execute()")


class CreateLoanOperation(Operation):
    name = "prestamo.crear"

    def execute(self, context: OperationContext) -> Loan:
        data = context.data

        responsible = (
            context.db.query(Responsible).filter(Responsible.id == data["responsible_id"]).first()
        )
        if responsible is None:
            raise BusinessRuleError("El responsable seleccionado no existe")
        if not responsible.is_active:
            raise BusinessRuleError("El responsable seleccionado está desactivado")

        try:
            available = AssetServiceClient(context.token).get_available_assets()
        except AssetServiceError as exc:
            raise ExternalServiceError(str(exc)) from exc

        asset = next((item for item in available if item["id"] == data["asset_id"]), None)
        if asset is None:
            raise BusinessRuleError("El activo no está disponible para préstamo")

        open_loan = (
            context.db.query(Loan).filter(Loan.asset_id == asset["id"], Loan.status.in_(OPEN_STATUSES)).first()
        )
        if open_loan is not None:
            raise ConflictError("El activo ya tiene un préstamo abierto")

        try:
            loan = (
                LoanBuilder()
                .with_asset(asset["id"])
                .with_asset_name(asset["name"])
                .with_responsible(responsible)
                .with_loan_date(utc_now_naive())
                .with_expected_return(to_naive_utc(data["expected_return_date"]))
                .with_notes(data.get("notes"))
                .with_registered_by(context.user["id"], context.user["name"])
                .build()
            )
        except ValueError as exc:
            raise BusinessRuleError(str(exc)) from exc

        context.db.add(loan)
        context.db.commit()
        context.db.refresh(loan)
        return loan


class ReturnLoanOperation(Operation):
    name = "prestamo.devolver"

    def execute(self, context: OperationContext) -> Loan:
        data = context.data
        loan = context.db.query(Loan).filter(Loan.id == data["loan_id"]).first()
        if loan is None:
            raise NotFoundError("Préstamo no encontrado")
        if loan.status == LoanStatus.DEVUELTO:
            raise ConflictError("Este préstamo ya fue devuelto")

        loan.status = LoanStatus.DEVUELTO
        loan.actual_return_date = utc_now_naive()
        loan.returned_by_name = context.user["name"]
        loan.return_condition = data["condition"]
        loan.return_notes = data.get("notes")
        context.db.commit()
        context.db.refresh(loan)
        return loan