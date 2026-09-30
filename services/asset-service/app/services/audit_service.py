from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record_audit(
    db: Session,
    entity_type: str,
    entity_id: int | None,
    action: str,
    detail: str,
    performed_by: str,
    role: str | None = None,
    commit: bool = True,
) -> AuditLog:
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        detail=(detail or "")[:500],
        performed_by=performed_by,
        performed_by_role=role,
    )
    db.add(entry)
    if commit:
        db.commit()
    return entry