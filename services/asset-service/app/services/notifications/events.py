from dataclasses import dataclass, field
from datetime import datetime, timezone

EVENT_TYPES = (
    "activo_registrado",
    "prestamo_creado",
    "prestamo_devuelto",
    "devolucion_con_novedad",
    "prestamo_atrasado",
    "mantenimiento_iniciado",
    "mantenimiento_escalado_externo",
    "mantenimiento_finalizado",
)


@dataclass(frozen=True)
class DomainEvent:
    """Lo que ocurrió: es lo único que viaja del sujeto a los observadores."""

    type: str
    site: str
    asset_id: int | None = None
    asset_name: str | None = None
    actor: str = "Sistema"
    detail: str = ""
    label: str | None = None  # la pestaña de pruebas marca así cada variante
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))