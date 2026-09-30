from app.models.user import UserRole


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_se_bloquea_tras_intentos_fallidos(client, make_user):
    make_user(UserRole.ALMACENISTA, email="ana@test.com")

    for _ in range(5):
        response = client.post("/auth/login", data={"username": "ana@test.com", "password": "incorrecta"})
        assert response.status_code == 401

    # Aun con la contraseña correcta, la cuenta queda bloqueada un rato
    response = client.post("/auth/login", data={"username": "ana@test.com", "password": "Test123!"})
    assert response.status_code == 429


def test_usuario_desactivado_no_puede_iniciar_sesion(client, make_user):
    make_user(UserRole.ALMACENISTA, email="baja@test.com", is_active=False)
    response = client.post("/auth/login", data={"username": "baja@test.com", "password": "Test123!"})
    assert response.status_code == 403


def test_administrador_no_puede_desactivarse_a_si_mismo(client, make_user):
    admin, token = make_user(UserRole.ADMINISTRADOR)
    response = client.patch(f"/users/{admin.id}", json={"is_active": False}, headers=_auth(token))
    assert response.status_code == 400


def test_registro_rechaza_contrasena_debil(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    response = client.post(
        "/auth/register",
        json={"full_name": "Nuevo Usuario", "email": "nuevo@test.com", "password": "abc"},
        headers=_auth(token),
    )
    assert response.status_code == 422