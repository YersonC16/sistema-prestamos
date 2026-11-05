from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.inapp_notification import InAppNotification
from app.models.user import User
from app.schemas.inbox import InboxItemResponse, InboxResponse

router = APIRouter(prefix="/inbox", tags=["Bandeja de entrada"])


@router.get("/", response_model=InboxResponse)
def my_inbox(
    limit: int = Query(default=15, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Los avisos del usuario que inició sesión y cuántos tiene sin leer."""
    mine = db.query(InAppNotification).filter(InAppNotification.user_id == user.id)
    unread = mine.filter(InAppNotification.is_read.is_(False)).count()
    rows = mine.order_by(InAppNotification.id.desc()).limit(limit).all()
    return InboxResponse(unread_count=unread, items=[InboxItemResponse.model_validate(row) for row in rows])


@router.put("/read-all", status_code=204)
def mark_all_read(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(InAppNotification).filter(
        InAppNotification.user_id == user.id, InAppNotification.is_read.is_(False)
    ).update({"is_read": True})
    db.commit()


@router.put("/{item_id}/read", status_code=204)
def mark_read(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(InAppNotification)
        .filter(InAppNotification.id == item_id, InAppNotification.user_id == user.id)
        .first()
    )
    if item is None:
        raise HTTPException(404, "Notificación no encontrada")
    if not item.is_read:
        item.is_read = True
        db.commit()