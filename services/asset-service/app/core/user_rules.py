from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


def ensure_single_plant_manager(db: Session, site: str, exclude_user_id: int | None = None) -> None:
    """Cada sede tiene un solo jefe de planta activo."""
    query = db.query(User).filter(
        User.role == UserRole.JEFE_DE_PLANTA,
        User.site == site,
        User.is_active.is_(True),
    )
    if exclude_user_id is not None:
        query = query.filter(User.id != exclude_user_id)
    if query.first() is not None:
        raise HTTPException(409, f"La sede '{site}' ya tiene un jefe de planta activo")