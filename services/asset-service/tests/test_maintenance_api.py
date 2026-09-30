from app.models.asset import Asset, AssetStatus
from app.models.user import UserRole


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_asset(client, token):
    response = client.post(
        "/assets/",
        json={"name": "Taladro", "asset_type": "herramienta", "code": "TAL-001"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    return response.json()


def test_mantenimiento_cambia_estado_y_guarda_responsable(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    asset = _create_asset(client, token)

    started = client.post(
        "/maintenance/",
        json={
            "asset_id": asset["id"],
            "assigned_to": "Carlos Ruiz",
            "maintenance_type": "correctivo",
            "reason": "Cambio de carbones",
        },
        headers=_auth(token),
    )
    assert started.status_code == 200
    assert started.json()["assigned_to"] == "Carlos Ruiz"
    assert client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()["status"] == "mantenimiento"

    finished = client.put(
        f"/maintenance/{started.json()['id']}/finish", json={"notes": "Listo"}, headers=_auth(token)
    )
    assert finished.status_code == 200
    assert client.get(f"/assets/{asset['id']}", headers=_auth(token)).json()["status"] == "disponible"

    history = client.get(f"/assets/{asset['id']}/history", headers=_auth(token)).json()
    actions = [entry["action"] for entry in history]
    assert "activo_registrado" in actions
    assert "mantenimiento_iniciado" in actions
    assert "mantenimiento_finalizado" in actions


def test_no_se_envia_a_mantenimiento_un_activo_prestado(client, make_user, db_session):
    _, token = make_user(UserRole.ALMACENISTA)
    asset = _create_asset(client, token)

    db_session.query(Asset).filter(Asset.id == asset["id"]).update({"status": AssetStatus.PRESTADO})
    db_session.commit()

    response = client.post(
        "/maintenance/",
        json={"asset_id": asset["id"], "assigned_to": "Ana", "maintenance_type": "preventivo", "reason": "Revisión"},
        headers=_auth(token),
    )
    assert response.status_code == 400


def test_personal_autorizado_no_puede_iniciar_mantenimiento(client, make_user):
    _, admin_token = make_user(UserRole.ADMINISTRADOR)
    _, staff_token = make_user(UserRole.PERSONAL_AUTORIZADO)
    asset = _create_asset(client, admin_token)

    response = client.post(
        "/maintenance/",
        json={"asset_id": asset["id"], "assigned_to": "Ana", "maintenance_type": "preventivo", "reason": "Revisión"},
        headers=_auth(staff_token),
    )
    assert response.status_code == 403