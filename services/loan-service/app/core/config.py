from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://admin:admin123@localhost:5433/prestamos_db"
    schema_name: str = "loans"
    asset_service_url: str = "http://localhost:8001"
    rabbitmq_url: str = "amqp://admin:admin123@localhost:5672/"
    jwt_secret_key: str = "una-clave-larga-y-aleatoria-solo-para-desarrollo-12345"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()