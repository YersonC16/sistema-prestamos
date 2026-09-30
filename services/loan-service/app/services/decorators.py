import time

from app.core.errors import PermissionDeniedError
from app.services.event_publisher import publish_event
from app.services.history_service import record_history
from app.services.operations import Operation, OperationContext


class OperationDecorator(Operation):
    """Decorador base: tiene la MISMA interfaz que la operación que envuelve
    y le delega el trabajo. Los decoradores concretos agregan comportamiento
    antes o después de esa delegación."""

    def __init__(self, wrapped: Operation):
        self._wrapped = wrapped
        self.name = wrapped.name

    def execute(self, context: OperationContext):
        return self._wrapped.execute(context)


class RoleGuardDecorator(OperationDecorator):
    """Antes: verifica que el rol del usuario pueda ejecutar la operación."""

    def __init__(self, wrapped: Operation, allowed_roles: tuple[str, ...]):
        super().__init__(wrapped)
        self._allowed_roles = allowed_roles

    def execute(self, context: OperationContext):
        if context.user["role"] not in self._allowed_roles:
            raise PermissionDeniedError("No tienes permisos para realizar esta acción")
        return super().execute(context)


class AuditDecorator(OperationDecorator):
    """Después: registra quién hizo qué. Solo si la operación tuvo éxito."""

    def __init__(self, wrapped: Operation, action: str, detail_builder, recorder=None):
        super().__init__(wrapped)
        self._action = action
        self._detail_builder = detail_builder
        self._recorder = recorder

    def execute(self, context: OperationContext):
        loan = super().execute(context)
        recorder = self._recorder or record_history
        recorder(
            db=context.db,
            loan_id=loan.id,
            asset_id=loan.asset_id,
            action=self._action,
            detail=self._detail_builder(context, loan),
            performed_by=context.user["name"],
            role=context.user["role"],
        )
        return loan


class EventPublisherDecorator(OperationDecorator):
    """Después: avisa al broker para que otros servicios reaccionen."""

    def __init__(self, wrapped: Operation, routing_key: str, payload_builder, publisher=None):
        super().__init__(wrapped)
        self._routing_key = routing_key
        self._payload_builder = payload_builder
        self._publisher = publisher

    def execute(self, context: OperationContext):
        loan = super().execute(context)
        publisher = self._publisher or publish_event
        publisher(self._routing_key, self._payload_builder(context, loan))
        return loan


class TimingDecorator(OperationDecorator):
    """Alrededor: mide cuánto tarda toda la cadena."""

    def execute(self, context: OperationContext):
        start = time.perf_counter()
        try:
            return super().execute(context)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(f"[timing] {self.name} tardó {elapsed_ms:.2f} ms")