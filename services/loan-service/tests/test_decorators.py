import pytest

from app.core.errors import PermissionDeniedError
from app.services.decorators import AuditDecorator, EventPublisherDecorator, RoleGuardDecorator
from app.services.operations import Operation, OperationContext


class FakeLoan:
    id = 1
    asset_id = 7


class RecordingOperation(Operation):
    name = "prueba"

    def __init__(self, calls: list, fail: bool = False):
        self._calls = calls
        self._fail = fail

    def execute(self, context):
        self._calls.append("nucleo")
        if self._fail:
            raise RuntimeError("falló la operación")
        return FakeLoan()


def _context(role: str) -> OperationContext:
    return OperationContext(db=None, user={"id": 1, "name": "Ana", "role": role})


def _compose(calls: list, fail: bool = False):
    operation = RecordingOperation(calls, fail)
    operation = EventPublisherDecorator(
        operation, "x.y", lambda ctx, loan: {}, publisher=lambda key, payload: calls.append("evento")
    )
    operation = AuditDecorator(
        operation, "accion", lambda ctx, loan: "detalle", recorder=lambda **kwargs: calls.append("auditoria")
    )
    return RoleGuardDecorator(operation, ("almacenista",))


def test_los_decoradores_se_ejecutan_en_capas():
    calls = []
    _compose(calls).execute(_context("almacenista"))
    assert calls == ["nucleo", "evento", "auditoria"]


def test_el_guardia_de_roles_bloquea_antes_de_ejecutar_nada():
    calls = []
    with pytest.raises(PermissionDeniedError):
        _compose(calls).execute(_context("personal_autorizado"))
    assert calls == []


def test_no_se_audita_ni_se_publica_si_la_operacion_falla():
    calls = []
    with pytest.raises(RuntimeError):
        _compose(calls, fail=True).execute(_context("almacenista"))
    assert calls == ["nucleo"]