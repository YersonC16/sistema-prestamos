import os

# Deben fijarse ANTES de importar la aplicación
os.environ["TESTING"] = "true"
os.environ.setdefault("JWT_SECRET_KEY", "clave-solo-para-pruebas-1234")

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_token():
    def _make(role="almacenista", name="Ana Almacén", user_id=1):
        claims = {"sub": str(user_id), "role": role, "name": name}
        return jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    return _make