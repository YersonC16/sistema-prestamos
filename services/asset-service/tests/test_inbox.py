import pytest

from app.models.inapp_notification import InAppNotification
from app.models.user import UserRole
from app.services.notifications.inapp_observer import InAppNotificationObserver
from app.services.notifications.subject import get_event_subject
from tests.conftest import TestingSessionLocal


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_asset(client, token, name="Taladro"):
    response = client.post("/assets/", json={"name": name, "asset_type": "herramienta"}, headers=_auth(token))
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def bell(monkeypatch):
    """Engancha el observador REAL de la campanita a la base de pruebas."""
    monkeypatch.setattr("app.services.notifications.inapp_observer.SessionLocal", TestingSessionLocal)
    observer = InAppNotificationObserver()
    get_event_subject().attach(observer)
    yield observer
    get_event_subject().detach(observer)


def test_el_jefe_de_planta_ve_el_aviso_en_su_campanita(client, make_user, bell):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, jefe_token = make_user(UserRole.JEFE_DE_PLANTA, email="jefe@concreto.com")

    asset = _create_asset(client, admin_token)

    inbox = client.get("/inbox/", headers=_auth(jefe_token)).json()
    assert inbox["unread_count"] == 1
    assert inbox["items"][0]["title"] == "Nuevo activo registrado"
    assert "Taladro" in inbox["items"][0]["message"]
    assert inbox["items"][0]["asset_id"] == asset["id"]
    assert inbox["items"][0]["is_read"] is False


def test_los_otros_roles_no_reciben_avisos(client, make_user, bell, db_session):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, manager_token = make_user(UserRole.GERENTE)
    _, store_token = make_user(UserRole.ALMACENISTA)

    _create_asset(client, admin_token)

    for token in (admin_token, manager_token, store_token):
        assert client.get("/inbox/", headers=_auth(token)).json() == {"unread_count": 0, "items": []}
    assert db_session.query(InAppNotification).count() == 0


def test_cada_jefe_solo_recibe_los_avisos_de_su_sede(client, make_user, bell, db_session):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, concreto_token = make_user(UserRole.JEFE_DE_PLANTA, email="concreto@test.com")
    north, north_token = make_user(UserRole.JEFE_DE_PLANTA, email="norte@test.com")
    north.site = "norte"
    db_session.commit()

    _create_asset(client, admin_token)

    assert client.get("/inbox/", headers=_auth(concreto_token)).json()["unread_count"] == 1
    assert client.get("/inbox/", headers=_auth(north_token)).json()["unread_count"] == 0


def test_marcar_un_aviso_como_leido(client, make_user, bell):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, jefe_token = make_user(UserRole.JEFE_DE_PLANTA, email="jefe@concreto.com")
    _create_asset(client, admin_token)
    item_id = client.get("/inbox/", headers=_auth(jefe_token)).json()["items"][0]["id"]

    assert client.put(f"/inbox/{item_id}/read", headers=_auth(jefe_token)).status_code == 204

    inbox = client.get("/inbox/", headers=_auth(jefe_token)).json()
    assert inbox["unread_count"] == 0
    assert inbox["items"][0]["is_read"] is True


def test_marcar_todos_los_avisos_como_leidos(client, make_user, bell):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, jefe_token = make_user(UserRole.JEFE_DE_PLANTA, email="jefe@concreto.com")
    _create_asset(client, admin_token, name="Taladro")
    _create_asset(client, admin_token, name="Pulidora")
    assert client.get("/inbox/", headers=_auth(jefe_token)).json()["unread_count"] == 2

    assert client.put("/inbox/read-all", headers=_auth(jefe_token)).status_code == 204

    assert client.get("/inbox/", headers=_auth(jefe_token)).json()["unread_count"] == 0


def test_no_se_puede_marcar_el_aviso_de_otro_usuario(client, make_user, bell, db_session):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, owner_token = make_user(UserRole.JEFE_DE_PLANTA, email="dueno@test.com")
    north, north_token = make_user(UserRole.JEFE_DE_PLANTA, email="norte@test.com")
    north.site = "norte"
    db_session.commit()
    _create_asset(client, admin_token)
    item_id = client.get("/inbox/", headers=_auth(owner_token)).json()["items"][0]["id"]

    assert client.put(f"/inbox/{item_id}/read", headers=_auth(north_token)).status_code == 404
    assert client.get("/inbox/", headers=_auth(owner_token)).json()["unread_count"] == 1


def test_sin_sesion_no_hay_acceso(client):
    assert client.get("/inbox/").status_code == 401