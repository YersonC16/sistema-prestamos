from app.models.asset import Asset, AssetStatus, AssetType


class AssetCreator:
    """Contrato de todo creador de activos. La abstracción se fuerza a mano:
    si una subclase no sobrescribe create(), falla al usarla."""

    def create(self, name: str, description: str | None, code: str | None = None) -> Asset:
        raise NotImplementedError("Toda subclase de AssetCreator debe implementar el método create()")


class EquipoCreator(AssetCreator):
    def create(self, name: str, description: str | None, code: str | None = None) -> Asset:
        return Asset(name=name, description=description, code=code, asset_type=AssetType.EQUIPO, status=AssetStatus.DISPONIBLE)


class HerramientaCreator(AssetCreator):
    def create(self, name: str, description: str | None, code: str | None = None) -> Asset:
        return Asset(name=name, description=description, code=code, asset_type=AssetType.HERRAMIENTA, status=AssetStatus.DISPONIBLE)


class OtroCreator(AssetCreator):
    def create(self, name: str, description: str | None, code: str | None = None) -> Asset:
        return Asset(name=name, description=description, code=code, asset_type=AssetType.OTRO, status=AssetStatus.DISPONIBLE)


class AssetFactory:
    """Punto único de entrada: decide qué Creator usar según el tipo pedido."""

    _creators: dict[AssetType, AssetCreator] = {
        AssetType.EQUIPO: EquipoCreator(),
        AssetType.HERRAMIENTA: HerramientaCreator(),
        AssetType.OTRO: OtroCreator(),
    }

    @classmethod
    def create_asset(
        cls, asset_type: AssetType, name: str, description: str | None = None, code: str | None = None
    ) -> Asset:
        creator = cls._creators.get(asset_type)
        if not creator:
            raise ValueError(f"Tipo de activo no soportado: {asset_type}")
        return creator.create(name, description, code)