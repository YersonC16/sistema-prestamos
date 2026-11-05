from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://admin:admin123@localhost:5433/prestamos_db"
    schema_name: str = "assets"
    rabbitmq_url: str = "amqp://admin:admin123@localhost:5672/"
    jwt_secret_key: str  # obligatoria: no hay clave por defecto
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    cors_origins: str = "http://localhost:5173"
    login_max_attempts: int = 5
    login_lock_seconds: int = 300

    # Sedes y notificaciones
    default_site: str = "concreto"
    local_utc_offset_hours: int = -5  # Colombia
    notifications_enabled: bool = True
    smtp_host: str = ""  # vacío = los correos se simulan (no se envían)
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "notificaciones@concreto.local"
    smtp_starttls: bool = True

    @field_validator("jwt_secret_key")
    @classmethod
    def secret_must_be_long_enough(cls, value: str) -> str:
        if len(value) < 16:
            raise ValueError("JWT_SECRET_KEY debe tener al menos 16 caracteres")
        return value


settings = Settings()