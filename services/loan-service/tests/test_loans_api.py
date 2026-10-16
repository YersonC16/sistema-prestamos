from datetime import datetime, timedelta, timezone

import pytest

from app.services.asset_client import AssetServiceClient


@pytest.fixture(autouse=True)
def fake_external_services(monkeypatch):
    """Simula asset-service y RabbitMQ: las pruebas no salen del proceso."""
    published = []
    monkeypatch.setattr(
        AssetServiceClient,
        "get_available_assets",
        lambda self: [{"id": 1, "name": "Taladro"}, {"id": 2, "name": "Pulidora"}],
    )
    monkeypatch.setattr(
        "app.services.decorators.publish_event", lambda key, payload: published.append((key, payload))
    )
    return published


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def responsible_id(client, make_token):
    response = client.post(
        "/responsibles/",
        json={"full_name": "Juan Pérez", "document_type": "CC", "document_number": "123456", "phone": "3001234567"},
        headers=_auth(make_token()),
    )
    assert response.status_code == 200
    return response.json()["id"]


def _payload(responsible_id, asset_id=1, days=3):
    due = datetime.now(timezone.utc) + timedelta(days=days)
    return {"asset_id": asset_id, "responsible_id": responsible_id, "expected_return_date": due.isoformat()}


def _create_loan(client, token, responsible_id):
    response = client.post("/loans/", json=_payload(responsible_id), headers=_auth(token))
    assert response.status_code == 200
    return response.json()


# ---------- Crear préstamos ----------

def test_almacenista_registra_prestamo_y_queda_trazado(client, make_token, responsible_id, fake_external_services):
    token = make_token()
    response = client.post("/loans/", json=_payload(responsible_id), headers=_auth(token))
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "activo"
    assert body["asset_name"] == "Taladro"
    assert body["responsible_name"] == "Juan Pérez"
    assert body["responsible_document"] == "CC 123456"
    assert body["registered_by_name"] == "Ana Almacén"
    assert fake_external_services[0][0] == "prestamo.creado"

    history = client.get(f"/loans/{body['id']}/history", headers=_auth(token)).json()
    assert history[0]["action"] == "prestamo_creado"
    assert history[0]["performed_by"] == "Ana Almacén"


def test_personal_autorizado_no_puede_registrar_prestamos(client, make_token, responsible_id, fake_external_services):
    token = make_token(role="personal_autorizado", name="Luis")
    response = client.post("/loans/", json=_payload(responsible_id), headers=_auth(token))
    assert response.status_code == 403
    assert fake_external_services == []


def test_no_permite_dos_prestamos_abiertos_del_mismo_activo(client, make_token, responsible_id):
    token = make_token()
    assert client.post("/loans/", json=_payload(responsible_id), headers=_auth(token)).status_code == 200
    assert client.post("/loans/", json=_payload(responsible_id), headers=_auth(token)).status_code == 409


def test_fecha_de_devolucion_en_el_pasado_se_rechaza(client, make_token, responsible_id):
    response = client.post("/loans/", json=_payload(responsible_id, days=-1), headers=_auth(make_token()))
    assert response.status_code == 400


def test_responsable_inexistente_se_rechaza(client, make_token):
    response = client.post("/loans/", json=_payload(9999), headers=_auth(make_token()))
    assert response.status_code == 400


def test_responsable_desactivado_se_rechaza(client, make_token, responsible_id):
    token = make_token()
    patched = client.patch(f"/responsibles/{responsible_id}", json={"is_active": False}, headers=_auth(token))
    assert patched.status_code == 200

    response = client.post("/loans/", json=_payload(responsible_id), headers=_auth(token))
    assert response.status_code == 400


# ---------- Devoluciones ----------

def test_devolucion_con_novedad_exige_descripcion(client, make_token, responsible_id):
    token = make_token()
    loan = _create_loan(client, token, responsible_id)
    response = client.put(f"/loans/{loan['id']}/return", json={"condition": "con_novedad"}, headers=_auth(token))
    assert response.status_code == 422


def test_devolucion_con_novedad_exige_destino_de_mantenimiento(client, make_token, responsible_id):
    token = make_token()
    loan = _create_loan(client, token, responsible_id)
    response = client.put(
        f"/loans/{loan['id']}/return",
        json={"condition": "con_novedad", "notes": "Cable pelado"},
        headers=_auth(token),
    )
    assert response.status_code == 422


def test_devolucion_en_buen_estado(client, make_token, responsible_id, fake_external_services):
    token = make_token()
    loan = _create_loan(client, token, responsible_id)

    returned = client.put(f"/loans/{loan['id']}/return", json={"condition": "bueno"}, headers=_auth(token))
    assert returned.status_code == 200
    assert returned.json()["status"] == "devuelto"
    assert returned.json()["returned_by_name"] == "Ana Almacén"
    assert returned.json()["return_condition"] == "bueno"

    key, payload = fake_external_services[-1]
    assert key == "prestamo.devuelto"
    assert payload["condition"] == "bueno"
    assert payload["maintenance_location"] is None


def test_devolucion_con_novedad_a_proveedor_externo_y_no_se_repite(client, make_token, responsible_id, fake_external_services):
    token = make_token()
    loan = _create_loan(client, token, responsible_id)

    returned = client.put(
        f"/loans/{loan['id']}/return",
        json={
            "condition": "con_novedad",
            "notes": "Cable pelado",
            "maintenance_location": "externo",
            "maintenance_provider": "Taller Hilti",
        },
        headers=_auth(token),
    )
    assert returned.status_code == 200
    assert returned.json()["status"] == "devuelto"
    assert returned.json()["return_condition"] == "con_novedad"

    key, payload = fake_external_services[-1]
    assert key == "prestamo.devuelto"
    assert payload["condition"] == "con_novedad"
    assert payload["notes"] == "Cable pelado"
    assert payload["maintenance_location"] == "externo"
    assert payload["maintenance_provider"] == "Taller Hilti"
    assert payload["maintenance_assigned_to"] is None

    again = client.put(f"/loans/{loan['id']}/return", json={"condition": "bueno"}, headers=_auth(token))
    assert again.status_code == 409


def test_devolucion_con_novedad_a_mantenimiento_interno(client, make_token, responsible_id, fake_external_services):
    token = make_token()
    loan = _create_loan(client, token, responsible_id)

    returned = client.put(
        f"/loans/{loan['id']}/return",
        json={
            "condition": "con_novedad",
            "notes": "Mandril flojo",
            "maintenance_location": "interno",
            "maintenance_assigned_to": "Carlos Ruiz",
        },
        headers=_auth(token),
    )
    assert returned.status_code == 200

    key, payload = fake_external_services[-1]
    assert key == "prestamo.devuelto"
    assert payload["maintenance_location"] == "interno"
    assert payload["maintenance_assigned_to"] == "Carlos Ruiz"
    assert payload["maintenance_provider"] is None