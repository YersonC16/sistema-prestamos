from app.services.asset_factory import AssetFactory
from app.models.asset import AssetType, AssetStatus


def test_factory_crea_equipo_con_estado_disponible():
    asset = AssetFactory.create_asset(AssetType.EQUIPO, "Taladro Bosch")
    assert asset.asset_type == AssetType.EQUIPO
    assert asset.status == AssetStatus.DISPONIBLE
    assert asset.name == "Taladro Bosch"


def test_factory_crea_herramienta():
    asset = AssetFactory.create_asset(AssetType.HERRAMIENTA, "Martillo")
    assert asset.asset_type == AssetType.HERRAMIENTA


def test_factory_crea_otro_tipo():
    asset = AssetFactory.create_asset(AssetType.OTRO, "Carretilla", "Uso general")
    assert asset.asset_type == AssetType.OTRO
    assert asset.description == "Uso general"