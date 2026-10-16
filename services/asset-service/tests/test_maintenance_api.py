import pytest

from app.models.asset import Asset, AssetStatus
from app.models.user import UserRole
from app.services.event_consumer import _apply_event


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_asset(client, token, name="Taladro", code="TAL-001"):
    response = client.post(
        "/assets/",
        json={"name": name, "asset_type": "herramienta", "code": code},
        headers=_auth(token),
    )
    assert response.status_code == 200
    return response.json()


def _start_internal(client, token, asset_id, assigned_to="Carlos Ruiz"):
    return client.post(
        "/maintenance/",
        json={
            "asset_id": asset_id,
            "location": "interno",
            "assigned_to": assigned_to,
            "maintenance_type": "correctivo",
            "reason": "Cambio de carbones",
        },
        headers=_auth(token),
    )


@pytest.fixture
def consumer_uses_test_db(monkeypatch, db_session):
    """Hace que el consumidor del broker use la base de pruebas, sin RabbitMQ."""
    monkeypatch.setattr("app.services.event_consumer.SessionLocal", lambda: db_session)


# ---------- Mantenimiento interno (el caso del mandril) ----------

def test_mantenimiento_interno_cambia_estado_y_guarda_responsable(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create_asset(client, token)

    started = _start_internal(client, token, asset["id"])
    assert started.status_code == 200
    assert started.json()["location"] == "interno"
    assert started.json()["assigned_to"] == "Carlos Ruiz"
    assert started.json()["provider_name"] is None
    assert client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()["status"] == "mantenimiento"

    finished = client.put(
        f"/maintenance/{started.json()['id']}/finish", json={"notes": "Listo"}, headers=_auth(token)
    )
    assert finished.status_code == 200
    assert client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()["status"] == "disponible"

    actions = [e["action"] for e in client.get(f"/assets/{asset['id']}/history", headers=_auth(token)).json()]
    assert "activo_registrado" in actions
    assert "mantenimiento_iniciado" in actions
    assert "mantenimiento_finalizado" in actions


# ---------- Mantenimiento externo directo (el caso del portafusil) ----------

def test_mantenimiento_externo_directo_guarda_proveedor(client, make_user):
    _, token = make_user(UserRole.ALMACENISTA)
    asset = _create_asset(client, token, name="Portafusil")

    response = client.post(
        "/maintenance/",
        json={
            "asset_id": asset["id"],
            "location": "externo",
            "provider_name": "Taller Autorizado Hilti",
            "maintenance_type": "correctivo",
            "reason": "Portafusil dañado",
        },
        headers=_auth(token),
    )
    assert response.status_code == 200
    assert response.json()["location"] == "externo"
    assert response.json()["provider_name"] == "Taller Autorizado Hilti"
    assert response.json()["assigned_to"] is None


# ---------- Escalar de interno a externo (el caso de la escobilla) ----------

def test_escalar_interno_a_externo_conserva_el_mismo_registro(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create_asset(client, token, name="Pulidora")
    started = _start_internal(client, token, asset["id"]).json()

    escalated = client.put(
        f"/maintenance/{started['id']}/escalate",
        json={"provider_name": "Servicio Técnico Makita", "notes": "No se consiguió la escobilla"},
        headers=_auth(token),
    )
    assert escalated.status_code == 200
    assert escalated.json()["id"] == started["id"]  # el MISMO registro, no uno nuevo
    assert escalated.json()["location"] == "externo"
    assert escalated.json()["provider_name"] == "Servicio Técnico Makita"
    assert escalated.json()["status"] == "en_proceso"

    all_records = client.get("/maintenance/", headers=_auth(token)).json()
    assert len(all_records) == 1

    actions = [e["action"] for e in client.get(f"/assets/{asset['id']}/history", headers=_auth(token)).json()]
    assert "mantenimiento_escalado_externo" in actions

    # Al terminar con el proveedor, el activo vuelve a estar disponible
    client.put(f"/maintenance/{started['id']}/finish", json={}, headers=_auth(token))
    assert client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()["status"] == "disponible"


def test_no_se_puede_escalar_un_mantenimiento_que_ya_es_externo(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create_asset(client, token)
    started = client.post(
        "/maintenance/",
        json={
            "asset_id": asset["id"],
            "location": "externo",
            "provider_name": "Taller X",
            "maintenance_type": "preventivo",
            "reason": "Calibración",
        },
        headers=_auth(token),
    ).json()

    response = client.put(
        f"/maintenance/{started['id']}/escalate", json={"provider_name": "Otro taller"}, headers=_auth(token)
    )
    assert response.status_code == 409


# ---------- Validaciones ----------

def test_el_destino_es_obligatorio_segun_el_tipo(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create_asset(client, token)
    base = {"asset_id": asset["id"], "maintenance_type": "preventivo", "reason": "Revisión"}

    interno_sin_persona = client.post("/maintenance/", json={**base, "location": "interno"}, headers=_auth(token))
    assert interno_sin_persona.status_code == 422

    externo_sin_proveedor = client.post("/maintenance/", json={**base, "location": "externo"}, headers=_auth(token))
    assert externo_sin_proveedor.status_code == 422


def test_no_se_envia_a_mantenimiento_un_activo_prestado(client, make_user, db_session):
    _, token = make_user(UserRole.ALMACENISTA)
    asset = _create_asset(client, token)

    db_session.query(Asset).filter(Asset.id == asset["id"]).update({"status": AssetStatus.PRESTADO})
    db_session.commit()

    response = _start_internal(client, token, asset["id"], assigned_to="Ana")
    assert response.status_code == 400


def test_personal_autorizado_no_puede_iniciar_mantenimiento(client, make_user):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, staff_token = make_user(UserRole.PERSONAL_AUTORIZADO)
    asset = _create_asset(client, admin_token)

    response = _start_internal(client, staff_token, asset["id"], assigned_to="Ana")
    assert response.status_code == 403


# ---------- Devolución con novedad: el mantenimiento se crea solo ----------

def test_devolucion_con_novedad_crea_mantenimiento_externo(client, make_user, consumer_uses_test_db):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create_asset(client, token, name="Portafusil")

    _apply_event(
        "prestamo.devuelto",
        {
            "asset_id": asset["id"],
            "loan_id": 5,
            "responsible_name": "Juan Pérez",
            "condition": "con_novedad",
            "notes": "Portafusil roto",
            "returned_by": "Ana Almacén",
            "maintenance_location": "externo",
            "maintenance_provider": "Taller Autorizado Hilti",
        },
    )

    assert client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()["status"] == "mantenimiento"

    records = client.get("/maintenance/", headers=_auth(token)).json()
    assert len(records) == 1
    assert records[0]["location"] == "externo"
    assert records[0]["provider_name"] == "Taller Autorizado Hilti"
    assert records[0]["source"] == "devolucion_con_novedad"
    assert records[0]["source_loan_id"] == 5
    assert records[0]["status"] == "en_proceso"


def test_devolucion_con_novedad_crea_mantenimiento_interno(client, make_user, consumer_uses_test_db):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create_asset(client, token, name="Mandril")

    _apply_event(
        "prestamo.devuelto",
        {
            "asset_id": asset["id"],
            "loan_id": 8,
            "responsible_name": "Juan Pérez",
            "condition": "con_novedad",
            "notes": "Mandril flojo",
            "returned_by": "Ana Almacén",
            "maintenance_location": "interno",
            "maintenance_assigned_to": "Carlos Ruiz",
        },
    )

    records = client.get("/maintenance/", headers=_auth(token)).json()
    assert len(records) == 1
    assert records[0]["location"] == "interno"
    assert records[0]["assigned_to"] == "Carlos Ruiz"
    assert records[0]["provider_name"] is None