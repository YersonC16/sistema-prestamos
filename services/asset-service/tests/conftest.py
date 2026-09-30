import os

# Deben fijarse ANTES de importar la aplicación
os.environ["TESTING"] = "true"
os.environ.setdefault("JWT_SECRET_KEY", "clave-solo-para-pruebas-1234")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.login_guard import login_tracker
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_login_tracker():
    login_tracker.reset_all()
    yield


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
def make_user(db_session):
    """Crea un usuario y devuelve (usuario, token)."""

    def _make(role, email=None, password="Test123!", is_active=True):
        user = User(
            full_name=f"Usuario {role.value}",
            email=email or f"{role.value}@test.com",
            hashed_password=hash_password(password),
            role=role,
            is_active=is_active,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        token = create_access_token({"sub": str(user.id), "role": user.role.value, "name": user.full_name})
        return user, token

    return _make