from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.services.notifications.events import DomainEvent
from app.services.notifications.lab.report import LabReport
from app.services.notifications.lab.with_observer_strategy import STRATEGIES
from app.services.notifications.messages import build_message
from app.services.notifications.observers import write_notification_log


def run_with_strategy_only(db: Session, event: DomainEvent, channel: str, report: LabReport) -> None:
    """SOLO Strategy: el canal es una clase intercambiable, pero quien detecta
    el evento sigue llamando DIRECTO a esta función (no hay Observer)."""
    report.step("El código que detecta el evento llama DIRECTO a esta función (sin Observer)")

    strategy = STRATEGIES[channel]()
    report.step(f"Estrategia elegida en ejecución: '{strategy.name}'")

    managers = (
        db.query(User.email, User.full_name)
        .filter(User.role == UserRole.JEFE_DE_PLANTA, User.site == event.site, User.is_active.is_(True))
        .all()
    )
    report.step(f"Busca a los jefes de planta dentro de la misma función: {len(managers)} encontrado(s)")

    subject, body = build_message(event)

    if not managers:
        write_notification_log(event, None, None, "-", "sin_destinatario", subject)
        report.step("No hay jefe de planta activo en la sede: registra 'sin destinatario'")
        return

    for email, name in managers:
        try:
            used = strategy.deliver(email, subject, body)
        except Exception as exc:
            write_notification_log(event, email, name, strategy.name, "fallido", subject, str(exc))
            report.delivery(email, strategy.name, "fallido", str(exc))
            report.step(f"La estrategia '{strategy.name}' no pudo enviar a {email}")
            continue

        status = "enviado" if used == "correo" else "simulado"
        write_notification_log(event, email, name, used, status, subject)
        report.delivery(email, used, status)
        report.step(f"La estrategia '{strategy.name}' entrega a {email}")

    report.step("Si mañana hay que avisar también a otra cosa (auditoría), hay que EDITAR esta función")