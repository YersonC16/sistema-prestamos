from datetime import datetime, timedelta, timezone

import pytest

from app.services.loan_builder import LoanBuilder


def _complete_builder():
    hoy = datetime.now(timezone.utc)
    return (
        LoanBuilder()
        .with_asset(1)
        .with_responsible("Juan Pérez")
        .with_loan_date(hoy)
        .with_expected_return(hoy + timedelta(days=1))
        .with_registered_by(1, "Ana")
    )


def test_builder_construye_prestamo_valido():
    loan = _complete_builder().build()
    assert loan.asset_id == 1
    assert loan.responsible_name == "Juan Pérez"
    assert loan.registered_by_name == "Ana"
    assert loan.status == "activo"


def test_builder_falla_sin_responsable():
    with pytest.raises(ValueError, match="responsable"):
        LoanBuilder().with_responsible("")


def test_builder_falla_si_devolucion_es_antes_del_prestamo():
    hoy = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="posterior"):
        LoanBuilder().with_loan_date(hoy).with_expected_return(hoy - timedelta(days=1))


def test_builder_falla_si_faltan_campos():
    with pytest.raises(ValueError, match="Faltan datos"):
        LoanBuilder().with_asset(1).build()


def test_builder_falla_sin_usuario_que_registra():
    hoy = datetime.now(timezone.utc)
    builder = (
        LoanBuilder()
        .with_asset(1)
        .with_responsible("Juan")
        .with_loan_date(hoy)
        .with_expected_return(hoy + timedelta(days=1))
    )
    with pytest.raises(ValueError, match="Faltan datos"):
        builder.build()