import threading
import time

from app.core.database import SessionLocal
from app.core.timeutils import utc_now_naive
from app.models.loan import Loan, LoanStatus
from app.services.event_publisher import publish_event
from app.services.history_service import record_history

CHECK_INTERVAL_SECONDS = 60


def mark_overdue_loans() -> int:
    db = SessionLocal()
    try:
        overdue = (
            db.query(Loan)
            .filter(Loan.status == LoanStatus.ACTIVO, Loan.expected_return_date < utc_now_naive())
            .all()
        )
        events = []
        for loan in overdue:
            loan.status = LoanStatus.ATRASADO
            record_history(
                db=db, loan_id=loan.id, asset_id=loan.asset_id, action="prestamo_atrasado",
                detail=f"Venció el {loan.expected_return_date:%d/%m/%Y} sin devolución",
                performed_by="Sistema", role="sistema", commit=False,
            )
            events.append({
                "asset_id": loan.asset_id,
                "loan_id": loan.id,
                "responsible_name": loan.responsible_name,
                "expected_return_date": loan.expected_return_date.isoformat(),
            })
        db.commit()
        for payload in events:
            publish_event("prestamo.atrasado", payload)
        return len(events)
    finally:
        db.close()


def _run_forever() -> None:
    while True:
        try:
            marked = mark_overdue_loans()
            if marked:
                print(f"[overdue] {marked} préstamo(s) marcados como atrasados")
        except Exception as exc:
            print(f"[overdue] Error revisando préstamos atrasados: {exc}")
        time.sleep(CHECK_INTERVAL_SECONDS)


def start_overdue_checker_thread() -> None:
    threading.Thread(target=_run_forever, daemon=True).start()