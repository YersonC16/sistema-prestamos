from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://admin:admin123@localhost:5433/prestamos_db"
    schema_name: str = "assets"
    rabbitmq_url: str = "amqp://admin:admin123@localhost:5672/"
    jwt_secret_key: str = "cambia-esta-clave-por-una-secreta-y-larga"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120

    class Config:
        env_file = ".env"

settings = Settings()