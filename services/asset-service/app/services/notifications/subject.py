import threading

from app.core.config import settings
from app.services.notifications.events import DomainEvent


class Observer:
    """Contrato de todo observador: reacciona cuando el sujeto avisa de un evento."""

    def update(self, event: DomainEvent) -> None:
        raise NotImplementedError("Todo observador debe implementar update()")


class EventSubject:
    """Sujeto: guarda la lista de observadores y les avisa. No sabe qué hace cada uno."""

    def __init__(self):
        self._observers: list[Observer] = []
        self._lock = threading.Lock()

    def attach(self, observer: Observer) -> None:
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)

    def notify(self, event: DomainEvent) -> None:
        with self._lock:
            observers = list(self._observers)
        for observer in observers:
            try:
                observer.update(event)
            except Exception as exc:
                # Un observador que falla no debe romper a los demás ni a la operación original
                print(f"[observer] {type(observer).__name__} falló: {exc}")

    @property
    def observer_count(self) -> int:
        return len(self._observers)


_subject = EventSubject()


def get_event_subject() -> EventSubject:
    return _subject


def emit_event(
    event_type: str,
    *,
    asset_id: int | None = None,
    asset_name: str | None = None,
    actor: str = "Sistema",
    detail: str = "",
    site: str | None = None,
) -> None:
    """Atajo para quien detecta un cambio: arma el evento y avisa."""
    get_event_subject().notify(
        DomainEvent(
            type=event_type,
            site=site or settings.default_site,
            asset_id=asset_id,
            asset_name=asset_name,
            actor=actor,
            detail=detail,
        )
    )