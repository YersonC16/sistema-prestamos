from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole


def _crear_usuario_y_token(db_session, role: UserRole) -> str:
    user = User(
        full_name="Usuario de Prueba",
        email=f"{role.value}@test.com",
        hashed_password=hash_password("Test123!"),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return create_access_token({"sub": str(user.id), "role": user.role.value})


def test_crear_activo_como_administrador(client, db_session):
    token = _crear_usuario_y_token(db_session, UserRole.ADMINISTRADOR)
    response = client.post(
        "/assets/",
        json={"name": "Taladro", "asset_type": "herramienta"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Taladro"
    assert response.json()["status"] == "disponible"


def test_crear_activo_sin_permiso_retorna_403(client, db_session):
    token = _crear_usuario_y_token(db_session, UserRole.PERSONAL_AUTORIZADO)
    response = client.post(
        "/assets/",
        json={"name": "Taladro", "asset_type": "herramienta"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_crear_activo_sin_token_retorna_401(client):
    response = client.post("/assets/", json={"name": "Taladro", "asset_type": "herramienta"})
    assert response.status_code == 401


def test_listar_activos_disponibles(client, db_session):
    token = _crear_usuario_y_token(db_session, UserRole.ALMACENISTA)
    client.post(
        "/assets/",
        json={"name": "Sierra", "asset_type": "herramienta"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get("/assets/available", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Sierra"