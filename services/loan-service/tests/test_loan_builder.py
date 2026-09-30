from datetime import datetime, timedelta, timezone

import pytest

from app.models.responsible import Responsible
from app.services.loan_builder import LoanBuilder


def _responsible(id_=1, name="Juan Pérez"):
    return Responsible(id=id_, full_name=name, document_type="CC", document_number="123456", phone="3001234567")


def _complete_builder():
    hoy = datetime.now(timezone.utc)
    return (
        LoanBuilder()
        .with_asset(1)
        .with_responsible(_responsible())
        .with_loan_date(hoy)
        .with_expected_return(hoy + timedelta(days=1))
        .with_registered_by(1, "Ana")
    )


def test_builder_construye_prestamo_valido():
    loan = _complete_builder().build()
    assert loan.asset_id == 1
    assert loan.responsible_name == "Juan Pérez"
    assert loan.responsible_document == "CC 123456"
    assert loan.registered_by_name == "Ana"
    assert loan.status == "activo"


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
        .with_responsible(_responsible())
        .with_loan_date(hoy)
        .with_expected_return(hoy + timedelta(days=1))
    )
    with pytest.raises(ValueError, match="Faltan datos"):
        builder.build()