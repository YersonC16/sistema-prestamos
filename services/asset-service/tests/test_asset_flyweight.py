import pytest

from app.models.asset import AssetStatus, AssetType
from app.models.user import UserRole
from app.services.asset_flyweight import AssetCatalog, AssetModelFactory


def test_la_fabrica_reutiliza_el_mismo_flyweight():
    factory = AssetModelFactory()
    first = factory.get_model("Taladro Dewalt", AssetType.HERRAMIENTA, "Percutor")
    second = factory.get_model("Taladro Dewalt", AssetType.HERRAMIENTA, "Percutor")
    assert first is second
    assert factory.count() == 1


def test_estados_distintos_crean_flyweights_distintos():
    factory = AssetModelFactory()
    factory.get_model("Taladro Dewalt", AssetType.HERRAMIENTA, "Percutor")
    factory.get_model("Pulidora", AssetType.HERRAMIENTA, None)
    assert factory.count() == 2


def test_el_catalogo_comparte_el_estado_intrinseco():
    catalog = AssetCatalog()
    for number in range(100):
        catalog.add(number, f"TAL-{number:03d}", AssetStatus.DISPONIBLE, "Taladro Dewalt", AssetType.HERRAMIENTA, "Percutor")
    catalog.add(1000, "PUL-001", AssetStatus.PRESTADO, "Pulidora", AssetType.HERRAMIENTA, None)

    assert catalog.total_items == 101
    assert catalog.shared_models == 2
    taladro_models = {id(item.model) for item in catalog.items if item.model.name == "Taladro Dewalt"}
    assert len(taladro_models) == 1  # los 100 taladros apuntan al MISMO objeto


def test_el_flyweight_es_inmutable():
    model = AssetModelFactory().get_model("Taladro", AssetType.HERRAMIENTA, None)
    with pytest.raises(AttributeError):
        model.name = "Otro nombre"


def test_describe_combina_estado_compartido_y_unico():
    model = AssetModelFactory().get_model("Taladro", AssetType.HERRAMIENTA, "Percutor")
    assert model.describe(7, "TAL-007", AssetStatus.PRESTADO) == {
        "id": 7,
        "name": "Taladro",
        "code": "TAL-007",
        "asset_type": AssetType.HERRAMIENTA,
        "status": AssetStatus.PRESTADO,
        "description": "Percutor",
    }


def test_listado_y_estadisticas_del_catalogo(client, make_user):
    _, token = make_user(UserRole.ADMINISTRADOR)
    headers = {"Authorization": f"Bearer {token}"}

    for number in range(3):
        response = client.post(
            "/assets/",
            json={"name": "Taladro Dewalt", "asset_type": "herramienta", "description": "Percutor", "code": f"TAL-00{number}"},
            headers=headers,
        )
        assert response.status_code == 200
    client.post("/assets/", json={"name": "Pulidora", "asset_type": "herramienta", "code": "PUL-001"}, headers=headers)

    listing = client.get("/assets/", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 4
    assert listing.json()[0]["code"] == "TAL-000"
    assert listing.json()[0]["status"] == "disponible"

    stats = client.get("/assets/catalog/stats", headers=headers).json()
    assert stats == {"assets": 4, "shared_models": 2, "duplicates_avoided": 2}