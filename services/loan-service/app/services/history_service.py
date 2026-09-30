from sqlalchemy.orm import Session

from app.models.loan_history import LoanHistory


def record_history(
    db: Session,
    loan_id: int,
    asset_id: int,
    action: str,
    detail: str,
    performed_by: str,
    role: str | None = None,
    commit: bool = True,
) -> LoanHistory:
    entry = LoanHistory(
        loan_id=loan_id,
        asset_id=asset_id,
        action=action,
        detail=(detail or "")[:500],
        performed_by=performed_by,
        performed_by_role=role,
    )
    db.add(entry)
    if commit:
        db.commit()
    return entry