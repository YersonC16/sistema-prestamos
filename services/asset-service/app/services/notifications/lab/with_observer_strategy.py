from app.services.notifications.events import DomainEvent
from app.services.notifications.lab.report import LabReport
from app.services.notifications.lab.with_observer import ExtraReactionObserver
from app.services.notifications.mailer import send_email
from app.services.notifications.observers import PlantManagerEmailObserver, SynchronousExecutor
from app.services.notifications.subject import EventSubject


class DeliveryStrategy:
    """Estrategia: UNA forma de entregar el mensaje. Todas se usan igual."""

    name = "base"

    def deliver(self, to: str, subject: str, body: str) -> str:
        raise NotImplementedError("Toda estrategia debe implementar deliver()")


class EmailStrategy(DeliveryStrategy):
    name = "correo"

    def deliver(self, to: str, subject: str, body: str) -> str:
        return send_email(to, subject, body)


class SimulatedStrategy(DeliveryStrategy):
    name = "simulado"

    def deliver(self, to: str, subject: str, body: str) -> str:
        print(f"[simulado] Para: {to} | Asunto: {subject}")
        return "simulado"


# Agregar WhatsApp sería: class WhatsAppStrategy(DeliveryStrategy) y una línea aquí
STRATEGIES = {"correo": EmailStrategy, "simulado": SimulatedStrategy}


class StrategyPlantManagerObserver(PlantManagerEmailObserver):
    """Observador + Strategy: el observador decide A QUIÉN y CUÁNDO; la estrategia decide CÓMO."""

    def __init__(self, strategy: DeliveryStrategy, report: LabReport):
        self._strategy = strategy
        self._report = report
        super().__init__(sender=self._send, executor=SynchronousExecutor())

    def set_strategy(self, strategy: DeliveryStrategy) -> None:
        self._strategy = strategy

    def _send(self, to: str, subject: str, body: str) -> str:
        try:
            used = self._strategy.deliver(to, subject, body)
        except Exception as exc:
            self._report.delivery(to, self._strategy.name, "fallido", str(exc))
            self._report.step(f"La estrategia '{self._strategy.name}' no pudo enviar a {to}")
            raise
        self._report.delivery(to, used, "enviado" if used == "correo" else "simulado")
        self._report.step(f"La estrategia '{self._strategy.name}' entrega a {to}")
        return used


def run_with_observer_and_strategy(event: DomainEvent, channel: str, report: LabReport) -> None:
    observer = StrategyPlantManagerObserver(SimulatedStrategy(), report)
    observer.set_strategy(STRATEGIES[channel]())  # se elige EN EJECUCIÓN
    report.step(f"Estrategia elegida en ejecución: '{channel}'")
    report.step("Agregar WhatsApp = una clase nueva con deliver(); el observador no cambia")

    event_subject = EventSubject()
    event_subject.attach(observer)
    event_subject.attach(ExtraReactionObserver(report))
    event_subject.notify(event)