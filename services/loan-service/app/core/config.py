from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://admin:admin123@localhost:5433/prestamos_db"
    schema_name: str = "loans"
    asset_service_url: str = "http://localhost:8001"
    rabbitmq_url: str = "amqp://admin:admin123@localhost:5672/"
    jwt_secret_key: str  # debe ser idéntica a la de asset-service
    jwt_algorithm: str = "HS256"
    cors_origins: str = "http://localhost:5173"

    @field_validator("jwt_secret_key")
    @classmethod
    def secret_must_be_long_enough(cls, value: str) -> str:
        if len(value) < 16:
            raise ValueError("JWT_SECRET_KEY debe tener al menos 16 caracteres")
        return value


settings = Settings()