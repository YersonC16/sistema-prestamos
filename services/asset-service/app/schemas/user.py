from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints, field_validator

from app.models.user import UserRole

FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]


def check_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not any(c.isupper() for c in value):
        raise ValueError("La contraseña debe incluir una mayúscula")
    if not any(c.islower() for c in value):
        raise ValueError("La contraseña debe incluir una minúscula")
    if not any(c.isdigit() for c in value):
        raise ValueError("La contraseña debe incluir un número")
    return value


class UserCreate(BaseModel):
    full_name: FullName
    email: EmailStr
    password: str
    role: UserRole = UserRole.PERSONAL_AUTORIZADO

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return check_password_strength(value)


class UserUpdate(BaseModel):
    full_name: FullName | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return check_password_strength(value)


class PasswordReset(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return check_password_strength(value)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"