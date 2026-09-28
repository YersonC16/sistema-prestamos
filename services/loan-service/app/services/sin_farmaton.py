from datetime import datetime

from app.models.loan import Loan, LoanStatus
##sin farmaton

def create_loan(
    asset_id: int,
    responsible_name: str,
    loan_date: datetime,
    expected_return_date: datetime,
) -> Loan:
    """
    Crea directamente un préstamo.

    Este archivo NO utiliza el patrón Builder.
    Todos los datos necesarios se reciben directamente
    como parámetros de la función.
    """

    # Validar ID del activo
    if asset_id is None or asset_id <= 0:
        raise ValueError(
            "El ID del activo debe ser mayor que 0"
        )

    # Validar responsable
    if not responsible_name or not responsible_name.strip():
        raise ValueError(
            "El responsable es obligatorio"
        )

    # Validar fecha de préstamo
    if loan_date is None:
        raise ValueError(
            "La fecha de préstamo es obligatoria"
        )

    # Validar fecha esperada de devolución
    if expected_return_date is None:
        raise ValueError(
            "La fecha de devolución es obligatoria"
        )

    # Validar que la devolución sea posterior al préstamo
    if expected_return_date <= loan_date:
        raise ValueError(
            "La fecha de devolución debe ser posterior "
            "a la fecha de préstamo"
        )

    # Crear directamente el objeto Loan
    return Loan(
        asset_id=asset_id,
        responsible_name=responsible_name.strip(),
        loan_date=loan_date,
        expected_return_date=expected_return_date,
        status=LoanStatus.ACTIVO,
    )