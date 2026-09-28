from datetime import datetime, timedelta, timezone
import pytest
from app.services.loan_builder import LoanBuilder


def test_builder_construye_prestamo_valido():
    hoy = datetime.now(timezone.utc)
    manana = hoy + timedelta(days=1)
    loan = (
        LoanBuilder()
        .with_asset(1)
        .with_responsible("Juan Pérez")
        .with_loan_date(hoy)
        .with_expected_return(manana)
        .build()
    )
    assert loan.asset_id == 1
    assert loan.responsible_name == "Juan Pérez"
    assert loan.status == "activo"


def test_builder_falla_sin_responsable():
    with pytest.raises(ValueError, match="responsable"):
        LoanBuilder().with_responsible("")


def test_builder_falla_si_devolucion_es_antes_del_prestamo():
    hoy = datetime.now(timezone.utc)
    ayer = hoy - timedelta(days=1)
    with pytest.raises(ValueError, match="posterior"):
        LoanBuilder().with_loan_date(hoy).with_expected_return(ayer)


def test_builder_falla_si_faltan_campos():
    with pytest.raises(ValueError, match="Faltan datos"):
        LoanBuilder().with_asset(1).build()