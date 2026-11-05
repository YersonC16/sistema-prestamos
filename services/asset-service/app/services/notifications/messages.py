from datetime import timedelta, timezone

from app.core.config import settings
from app.services.notifications.events import DomainEvent

TITLES = {
    "activo_registrado": "Nuevo activo registrado",
    "prestamo_creado": "Préstamo registrado",
    "prestamo_devuelto": "Devolución registrada",
    "devolucion_con_novedad": "Devolución con novedad",
    "prestamo_atrasado": "Préstamo atrasado",
    "mantenimiento_iniciado": "Mantenimiento iniciado",
    "mantenimiento_escalado_externo": "Mantenimiento escalado a proveedor externo",
    "mantenimiento_finalizado": "Mantenimiento finalizado",
}


def _title(event: DomainEvent) -> str:
    return TITLES.get(event.type, event.type.replace("_", " ").capitalize())


def build_message(event: DomainEvent) -> tuple[str, str]:
    """Asunto y cuerpo completos para el correo."""
    title = _title(event)
    prefix = f"[Prueba: {event.label}] " if event.label else ""
    asset = event.asset_name or (f"activo #{event.asset_id}" if event.asset_id else None)
    site = event.site.capitalize()

    subject = f"{prefix}[{site}] {title}" + (f": {asset}" if asset else "")

    local_time = event.occurred_at.astimezone(timezone(timedelta(hours=settings.local_utc_offset_hours)))
    lines = [f"Sede: {site}", f"Evento: {title}"]
    if asset:
        lines.append(f"Activo: {asset}")
    if event.detail:
        lines.append(f"Detalle: {event.detail}")
    lines += [
        f"Realizado por: {event.actor}",
        f"Fecha: {local_time:%d/%m/%Y %H:%M}",
        "",
        "Mensaje automático del sistema de control de préstamos.",
    ]
    return subject, "\n".join(lines)


def build_short_message(event: DomainEvent) -> tuple[str, str]:
    """Título y una línea de detalle para la campanita."""
    asset = event.asset_name or (f"activo #{event.asset_id}" if event.asset_id else None)
    parts = [part for part in (asset, event.detail) if part]
    parts.append(f"Por {event.actor}")
    return _title(event), " · ".join(parts)[:500]