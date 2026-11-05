import time

from sqlalchemy.orm import Session

from app.services.notifications.events import DomainEvent
from app.services.notifications.lab.report import LabReport
from app.services.notifications.lab.with_observer import run_with_observer
from app.services.notifications.lab.with_observer_strategy import run_with_observer_and_strategy
from app.services.notifications.lab.with_strategy_only import run_with_strategy_only
from app.services.notifications.lab.without_pattern import notify_without_pattern

# (clave, nombre, ruta que sigue el código hasta enviar el correo)
MODES = (
    ("sin_patron", "Sin patrones", "función directa → if/else de canal → envío"),
    ("observer", "Solo Observer", "EventSubject.notify() → observador → if/else de canal → envío"),
    ("strategy", "Solo Strategy", "función directa → estrategia.deliver() → envío"),
    ("observer_strategy", "Observer + Strategy", "EventSubject.notify() → observador → estrategia.deliver() → envío"),
)


def run_all(db: Session, event_type: str, site: str, channel: str, actor: str) -> list[LabReport]:
    reports: list[LabReport] = []
    for mode, label, route in MODES:
        event = DomainEvent(
            type=event_type,
            site=site,
            asset_name="Taladro de prueba",
            actor=actor,
            detail=f"Evento simulado. Ruta del código: {route}",
            label=label,
        )
        report = LabReport(mode)
        started = time.perf_counter()
        if mode == "sin_patron":
            notify_without_pattern(db, event, channel, report)
        elif mode == "observer":
            run_with_observer(event, channel, report)
        elif mode == "strategy":
            run_with_strategy_only(db, event, channel, report)
        else:
            run_with_observer_and_strategy(event, channel, report)
        report.elapsed_ms = (time.perf_counter() - started) * 1000
        reports.append(report)
    return reports