import smtplib
from email.message import EmailMessage

from app.core.config import settings


def smtp_configured() -> bool:
    return bool(settings.smtp_host)


def send_smtp(to: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)


def send_email(to: str, subject: str, body: str) -> str:
    """Envía por SMTP si está configurado. Si no, lo simula. Devuelve el canal usado."""
    if smtp_configured():
        send_smtp(to, subject, body)
        return "correo"
    print(f"[correo simulado] Para: {to} | Asunto: {subject}")
    return "simulado"