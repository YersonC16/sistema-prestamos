from app.core.config import settings
from app.core.database import SessionLocal
from app.models.inapp_notification import InAppNotification
from app.models.user import User, UserRole
from app.services.notifications.events import DomainEvent
from app.services.notifications.messages import build_short_message
from app.services.notifications.subject import Observer


class InAppNotificationObserver(Observer):
    """Deja el aviso en la campanita del jefe de planta de la sede del evento.
    Se agregó con un attach(), sin tocar a quien emite los eventos ni al observador de correo."""

    def update(self, event: DomainEvent) -> None:
        if not settings.notifications_enabled:
            return

        title, message = build_short_message(event)
        db = SessionLocal()
        try:
            manager_ids = [
                row[0]
                for row in db.query(User.id)
                .filter(User.role == UserRole.JEFE_DE_PLANTA, User.site == event.site, User.is_active.is_(True))
                .all()
            ]
            for user_id in manager_ids:
                db.add(
                    InAppNotification(
                        user_id=user_id,
                        event_type=event.type,
                        site=event.site,
                        asset_id=event.asset_id,
                        title=title,
                        message=message,
                    )
                )
            if manager_ids:
                db.commit()
        finally:
            db.close()