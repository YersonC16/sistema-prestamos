from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import PasswordReset, UserResponse, UserUpdate
from app.services.audit_service import record_audit

router = APIRouter(prefix="/users", tags=["Usuarios"])
admin_only = require_roles(UserRole.ADMINISTRADOR)


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    return db.query(User).order_by(User.id).all()


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_only),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(404, "Usuario no encontrado")

    # Impide que el administrador se deje sin acceso a sí mismo
    if user.id == admin.id:
        if payload.role is not None and payload.role != user.role:
            raise HTTPException(400, "No puedes cambiar tu propio rol")
        if payload.is_active is False:
            raise HTTPException(400, "No puedes desactivar tu propia cuenta")

    changes = []
    if payload.full_name is not None and payload.full_name != user.full_name:
        changes.append(f"nombre: {user.full_name} → {payload.full_name}")
        user.full_name = payload.full_name
    if payload.role is not None and payload.role != user.role:
        changes.append(f"rol: {user.role.value} → {payload.role.value}")
        user.role = payload.role
    if payload.is_active is not None and payload.is_active != user.is_active:
        changes.append("usuario activado" if payload.is_active else "usuario desactivado")
        user.is_active = payload.is_active

    if changes:
        db.commit()
        record_audit(db, "user", user.id, "usuario_modificado", "; ".join(changes), admin.full_name, admin.role.value)
    db.refresh(user)
    return user


@router.post("/{user_id}/reset-password", status_code=204)
def reset_password(
    user_id: int,
    payload: PasswordReset,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_only),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(404, "Usuario no encontrado")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    record_audit(db, "user", user.id, "password_restablecida", user.email, admin.full_name, admin.role.value)