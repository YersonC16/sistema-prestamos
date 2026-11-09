from app.models.asset import Asset, AssetStatus
from app.models.user import UserRole
from app.services.event_consumer import _apply_event
from tests.conftest import TestingSessionLocal


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create(client, token, **extra):
    body = {"name": "Taladro", "asset_type": "herramienta", **extra}
    return client.post("/assets/", json=body, headers=_auth(token))


def _decommission(client, token, asset_id, reason="Irreparable, el motor está quemado"):
    return client.post(f"/assets/{asset_id}/decommission", json={"reason": reason}, headers=_auth(token))


def test_un_activo_guarda_marca_y_numero_de_serie(client, make_user):
    _, token = make_user(UserRole.ALMACENISTA)
    created = _create(client, token, brand="Dewalt", serial_number="SN-0001")
    assert created.status_code == 200
    assert created.json()["brand"] == "Dewalt"
    assert created.json()["serial_number"] == "SN-0001"

    listing = client.get("/assets/", headers=_auth(token)).json()
    assert listing[0]["brand"] == "Dewalt"
    assert listing[0]["serial_number"] == "SN-0001"


def test_no_se_repite_marca_y_numero_de_serie(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    base = {"brand": "Dewalt", "serial_number": "SN-001"}

    assert _create(client, token, **base).status_code == 200
    assert _create(client, token, name="Otro", brand="dewalt", serial_number="sn-001").status_code == 409
    assert _create(client, token, brand="Makita", serial_number="SN-001").status_code == 200  # otra marca


def test_dar_de_baja_un_activo_disponible(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create(client, token).json()

    response = _decommission(client, token, asset["id"])
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "baja"
    assert body["decommission_reason"] == "Irreparable, el motor está quemado"
    assert body["decommissioned_by"] == "Usuario administrador"
    assert body["decommissioned_at"] is not None

    assert client.get("/assets/available", headers=_auth(token)).json() == []
    assert client.get("/assets/", headers=_auth(token)).json()[0]["status"] == "baja"
    detail = client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()
    assert detail["decommission_reason"] == "Irreparable, el motor está quemado"
    actions = [entry["action"] for entry in client.get(f"/assets/{asset['id']}/history", headers=_auth(token)).json()]
    assert "activo_dado_de_baja" in actions


def test_la_baja_exige_motivo_y_rol_autorizado(client, make_user):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, manager_token = make_user(UserRole.GERENTE)
    _, plant_token = make_user(UserRole.JEFE_DE_PLANTA)
    _, store_token = make_user(UserRole.ALMACENISTA)
    first = _create(client, admin_token).json()
    second = _create(client, admin_token, name="Pulidora").json()

    assert _decommission(client, manager_token, first["id"]).status_code == 403
    assert _decommission(client, plant_token, first["id"]).status_code == 403
    assert _decommission(client, admin_token, first["id"], reason="x").status_code == 422
    assert _decommission(client, store_token, second["id"]).status_code == 200


def test_no_se_da_de_baja_un_activo_prestado(client, make_user, db_session):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create(client, token).json()
    db_session.query(Asset).filter(Asset.id == asset["id"]).update({"status": AssetStatus.PRESTADO})
    db_session.commit()

    assert _decommission(client, token, asset["id"]).status_code == 400


def test_no_se_da_de_baja_dos_veces(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create(client, token).json()

    assert _decommission(client, token, asset["id"]).status_code == 200
    assert _decommission(client, token, asset["id"]).status_code == 409


def test_la_baja_cierra_el_mantenimiento_abierto(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create(client, token).json()
    started = client.post(
        "/maintenance/",
        json={
            "asset_id": asset["id"], "location": "interno", "assigned_to": "Carlos Ruiz",
            "maintenance_type": "correctivo", "reason": "Motor quemado",
        },
        headers=_auth(token),
    )
    assert started.status_code == 200

    assert _decommission(client, token, asset["id"]).status_code == 200

    record = client.get("/maintenance/", params={"asset_id": asset["id"]}, headers=_auth(token)).json()[0]
    assert record["status"] == "finalizado"
    assert "baja" in record["finish_notes"]
    assert client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()["status"] == "baja"


def test_un_activo_dado_de_baja_no_va_a_mantenimiento(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create(client, token).json()
    _decommission(client, token, asset["id"])

    response = client.post(
        "/maintenance/",
        json={
            "asset_id": asset["id"], "location": "externo", "provider_name": "Taller X",
            "maintenance_type": "preventivo", "reason": "Revisión",
        },
        headers=_auth(token),
    )
    assert response.status_code == 400


def test_el_resumen_no_cuenta_los_dados_de_baja_en_el_total(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    first = _create(client, token).json()
    _create(client, token, name="Pulidora")
    _decommission(client, token, first["id"])

    summary = client.get("/assets/summary", headers=_auth(token)).json()
    assert summary["total"] == 1
    assert summary["disponible"] == 1
    assert summary["baja"] == 1


def test_un_evento_tardio_no_revive_un_activo_dado_de_baja(client, make_user, monkeypatch):
    monkeypatch.setattr("app.services.event_consumer.SessionLocal", TestingSessionLocal)
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create(client, token).json()
    _decommission(client, token, asset["id"])

    _apply_event(
        "prestamo.creado",
        {
            "asset_id": asset["id"], "loan_id": 1, "responsible_name": "Juan Pérez",
            "expected_return_date": "2026-12-01T00:00:00", "registered_by": "Ana",
        },
    )

    assert client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()["status"] == "baja"