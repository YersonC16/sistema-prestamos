from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.services.notifications.events import DomainEvent
from app.services.notifications.lab.report import LabReport
from app.services.notifications.mailer import send_email
from app.services.notifications.messages import build_message
from app.services.notifications.observers import write_notification_log


def notify_without_pattern(db: Session, event: DomainEvent, channel: str, report: LabReport) -> None:
    """SIN patrón: quien detecta el evento llama directo a esta función, y ella lo hace
    TODO: busca destinatarios, arma el mensaje, elige el canal, envía y registra."""
    report.step("El código que detecta el evento llama DIRECTO a esta función (acoplamiento)")

    managers = (
        db.query(User.email, User.full_name)
        .filter(User.role == UserRole.JEFE_DE_PLANTA, User.site == event.site, User.is_active.is_(True))
        .all()
    )
    report.step(f"Busca a los jefes de planta dentro de la misma función: {len(managers)} encontrado(s)")

    subject, body = build_message(event)
    report.step("Arma el mensaje en la misma función")

    if not managers:
        write_notification_log(event, None, None, "-", "sin_destinatario", subject)
        report.step("No hay jefe de planta activo en la sede: registra 'sin destinatario'")
        return

    for email, name in managers:
        try:
            if channel == "correo":
                used = send_email(email, subject, body)
            elif channel == "simulado":
                print(f"[simulado] Para: {email} | Asunto: {subject}")
                used = "simulado"
            # elif channel == "whatsapp":   <- agregar un canal obliga a EDITAR esta función
            else:
                raise ValueError(f"Canal desconocido: {channel}")
        except Exception as exc:
            write_notification_log(event, email, name, channel, "fallido", subject, str(exc))
            report.delivery(email, channel, "fallido", str(exc))
            report.step(f"El envío a {email} falló")
            continue

        status = "enviado" if used == "correo" else "simulado"
        write_notification_log(event, email, name, used, status, subject)
        report.delivery(email, used, status)
        report.step(f"Envía por '{used}' a {email} con un if/else dentro de la misma función")