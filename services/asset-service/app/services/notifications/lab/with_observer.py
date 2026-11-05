from app.services.notifications.events import DomainEvent
from app.services.notifications.lab.report import LabReport
from app.services.notifications.mailer import send_email
from app.services.notifications.observers import PlantManagerEmailObserver, SynchronousExecutor
from app.services.notifications.subject import EventSubject, Observer


class ExtraReactionObserver(Observer):
    """Otra reacción al MISMO evento. Se agrega con attach() sin tocar nada de lo demás."""

    def __init__(self, report: LabReport):
        self._report = report

    def update(self, event: DomainEvent) -> None:
        self._report.step(f"Observador extra recibió '{event.type}' y reaccionó por su cuenta")


def run_with_observer(event: DomainEvent, channel: str, report: LabReport) -> None:
    """CON Observer: quien detecta el evento solo llama notify(). Los observadores deciden qué hacer."""

    def sender(to: str, subject: str, body: str) -> str:
        # El canal sigue siendo un if/else: Observer solo no resuelve esto
        try:
            if channel == "correo":
                used = send_email(to, subject, body)
            else:
                print(f"[simulado] Para: {to} | Asunto: {subject}")
                used = "simulado"
        except Exception as exc:
            report.delivery(to, channel, "fallido", str(exc))
            report.step(f"El observador no pudo enviar a {to}")
            raise
        report.delivery(to, used, "enviado" if used == "correo" else "simulado")
        report.step(f"El observador envía por '{used}' a {to}")
        return used

    event_subject = EventSubject()
    event_subject.attach(PlantManagerEmailObserver(sender=sender, executor=SynchronousExecutor()))
    event_subject.attach(ExtraReactionObserver(report))
    report.step("Se crea el sujeto y se enganchan 2 observadores con attach()")
    report.step("Quien detecta el evento solo llama notify(evento): no sabe quién escucha")
    event_subject.notify(event)