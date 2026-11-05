from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.notification_log import NotificationLog
from app.models.user import User, UserRole
from app.services.notifications.events import DomainEvent
from app.services.notifications.mailer import send_email
from app.services.notifications.messages import build_message
from app.services.notifications.subject import Observer

Sender = Callable[[str, str, str], str]  # (para, asunto, cuerpo) -> canal usado


class SynchronousExecutor:
    """Ejecuta de inmediato, sin hilos. Se usa en pruebas y en la pestaña de pruebas."""

    def submit(self, fn, *args, **kwargs):
        fn(*args, **kwargs)


def find_plant_managers(site: str) -> list[tuple[str, str]]:
    """Jefes de planta activos de la sede: (correo, nombre)."""
    db = SessionLocal()
    try:
        rows = (
            db.query(User.email, User.full_name)
            .filter(User.role == UserRole.JEFE_DE_PLANTA, User.site == site, User.is_active.is_(True))
            .all()
        )
        return [(email, name) for email, name in rows]
    finally:
        db.close()


def write_notification_log(
    event: DomainEvent,
    email: str | None,
    name: str | None,
    channel: str,
    status: str,
    subject: str | None,
    error: str | None = None,
) -> None:
    db = SessionLocal()
    try:
        db.add(
            NotificationLog(
                event_type=event.type,
                site=event.site,
                asset_id=event.asset_id,
                asset_name=event.asset_name,
                recipient_email=email,
                recipient_name=name,
                channel=channel,
                status=status,
                subject=(subject or "")[:255] or None,
                error=(error or "")[:300] or None,
            )
        )
        db.commit()
    finally:
        db.close()


class PlantManagerEmailObserver(Observer):
    """Observador real: avisa por correo al jefe de planta de la sede del evento.
    El envío corre en segundo plano para no hacer lenta la petición original."""

    def __init__(self, sender: Sender = send_email, executor=None):
        self._sender = sender
        self._executor = executor or ThreadPoolExecutor(max_workers=2, thread_name_prefix="notify")

    def update(self, event: DomainEvent) -> None:
        if not settings.notifications_enabled:
            return

        managers = find_plant_managers(event.site)
        subject, body = build_message(event)

        if not managers:
            self._safe_log(event, None, None, "-", "sin_destinatario", subject)
            return

        for email, name in managers:
            self._executor.submit(self._deliver, event, email, name, subject, body)

    def _deliver(self, event: DomainEvent, email: str, name: str, subject: str, body: str) -> None:
        try:
            channel = self._sender(email, subject, body)
        except Exception as exc:
            self._safe_log(event, email, name, "correo", "fallido", subject, str(exc))
            return
        status = "enviado" if channel == "correo" else "simulado"
        self._safe_log(event, email, name, channel, status, subject)

    @staticmethod
    def _safe_log(event, email, name, channel, status, subject, error=None) -> None:
        try:
            write_notification_log(event, email, name, channel, status, subject, error)
        except Exception as exc:
            print(f"[notificaciones] No se pudo registrar el envío: {exc}")