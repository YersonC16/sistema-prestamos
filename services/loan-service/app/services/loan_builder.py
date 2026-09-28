from datetime import datetime
from app.models.loan import Loan, LoanStatus
##Un préstamo tiene varios campos obligatorios y opcionales 
# que se arman en pasos (activo → responsable → fechas → estado). 
# El Builder evita un constructor con 6 parámetros 
# posicionales confusos y permite validar cada paso 
# antes de "construir" el objeto final.
class LoanBuilder:
    """Construye un objeto Loan paso a paso, validando cada dato."""
    "Aqui esta el constructor de la clase LoanBuilder, que inicializa los atributos privados a None"
    "leaaaaa"
    def __init__(self):
        self._asset_id: int | None = None
        self._responsible_name: str | None = None
        self._loan_date: datetime | None = None
        self._expected_return_date: datetime | None = None
    "Esto no construye el Loan todavía — "
    "solo prepara la mesa de trabajo del builder, "
    "dejando todos los campos vacíos (None), listos para irse llenando paso a paso"


    "Cada método with_... representa un paso de construcción del Loan, "
    def with_asset(self, asset_id: int) -> "LoanBuilder":
        self._asset_id = asset_id
        return self

    "Esto es unos de los pasos de construcción del Loan, es la clave que permite encadenar llamadas"
    def with_responsible(self, name: str) -> "LoanBuilder":
        if not name or not name.strip():
            raise ValueError("El responsable es obligatorio")
        self._responsible_name = name
        return self

    "se valida en el momento exacto en que se agrega, no todo junto al final."
    def with_loan_date(self, date: datetime) -> "LoanBuilder":
        self._loan_date = date
        return self

    "Esto es el último paso de construcción del Prestamo, donde se valida la fecha de devolución respecto a la de préstamo"
    def with_expected_return(self, date: datetime) -> "LoanBuilder":
        if self._loan_date and date <= self._loan_date:
            raise ValueError("La fecha de devolución debe ser posterior a la de préstamo")
        self._expected_return_date = date
        return self

    "Por esto se eligio builder, permite validar cada campo en el momento"
    "Que se agrega y no todo junto al final, a diferencia de un constructor "
    "con muchos parámetros posicionales confusos"
    def build(self) -> Loan:
        if not all([self._asset_id, self._responsible_name, self._loan_date, self._expected_return_date]):
            raise ValueError("Faltan datos obligatorios para construir el préstamo")
        return Loan(
            asset_id=self._asset_id,
            responsible_name=self._responsible_name,
            loan_date=self._loan_date,
            expected_return_date=self._expected_return_date,
            status=LoanStatus.ACTIVO,
        )