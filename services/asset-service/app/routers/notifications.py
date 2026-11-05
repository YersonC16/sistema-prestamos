from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.sites import sees_all_sites
from app.models.notification_log import NotificationLog
from app.models.user import User, UserRole
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notificaciones"])

readers = require_roles(UserRole.ADMINISTRADOR, UserRole.GERENTE, UserRole.JEFE_DE_PLANTA)


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(readers),
):
    query = db.query(NotificationLog)
    if not sees_all_sites(user):  # el jefe de planta solo ve su sede
        query = query.filter(NotificationLog.site == user.site)
    if status:
        query = query.filter(NotificationLog.status == status)
    return query.order_by(NotificationLog.id.desc()).limit(limit).all()