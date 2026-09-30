from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.login_guard import login_tracker
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import PasswordChange, Token, UserCreate, UserResponse
from app.services.audit_service import record_audit

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponse)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMINISTRADOR)),
):
    email = payload.email.lower()
    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(400, "Ya existe un usuario con ese correo")

    user = User(
        full_name=payload.full_name,
        email=email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_audit(
        db, "user", user.id, "usuario_creado", f"{user.email} con rol {user.role.value}",
        current_user.full_name, current_user.role.value,
    )
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form_data.username.strip().lower()

    remaining = login_tracker.seconds_locked(email)
    if remaining > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Intenta de nuevo en {remaining} segundos.",
            headers={"Retry-After": str(remaining)},
        )

    user = db.query(User).filter(func.lower(User.email) == email).first()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        locked = login_tracker.register_failure(email)
        record_audit(db, "user", user.id if user else None, "login_fallido", f"Intento fallido para {email}", email)
        if locked:
            record_audit(db, "user", user.id if user else None, "usuario_bloqueado_temporalmente", email, "Sistema")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tu usuario está desactivado. Contacta al administrador")

    login_tracker.register_success(email)
    record_audit(db, "user", user.id, "login_exitoso", email, user.full_name, user.role.value)
    token = create_access_token({"sub": str(user.id), "role": user.role.value, "name": user.full_name})
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password", status_code=204)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(400, "La contraseña actual no es correcta")
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    record_audit(db, "user", current_user.id, "password_cambiada", current_user.email, current_user.full_name, current_user.role.value)