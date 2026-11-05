from app.services.notifications.inapp_observer import InAppNotificationObserver
from app.services.notifications.observers import PlantManagerEmailObserver
from app.services.notifications.subject import get_event_subject


def configure_notifications() -> None:
    """Se llama una vez al arrancar: engancha los observadores reales al sujeto.
    Cada reacción nueva es un observador y una línea attach() aquí."""
    subject = get_event_subject()
    subject.attach(PlantManagerEmailObserver())  # correo al jefe de planta
    subject.attach(InAppNotificationObserver())  # campanita dentro del sistema