from app.models.asset import Asset, AssetType, AssetStatus

"Clase creador, es decir la fabrica."
"aqui se define la interfaz que todos los creadores concretos deben implementar."
class AssetCreator:
    """Clase base que define el "contrato" que todo creador de activos
    debe cumplir. En vez de usar el módulo abc de Python, forzamos la
    abstracción manualmente: si una subclase no sobrescribe create(),
    lanzará un error en tiempo de ejecución al intentar usarla."""

    def create(self, name: str, description: str | None) -> Asset:
        raise NotImplementedError(
            "Toda subclase de AssetCreator debe implementar el método create()"
        )


"aqui se definen los creadores, cada uno con características específicas de cada tipo de activo."
class EquipoCreator(AssetCreator):
    def create(self, name: str, description: str | None) -> Asset:
        return Asset(
            name=name,
            description=description,
            asset_type=AssetType.EQUIPO,
            status=AssetStatus.DISPONIBLE,
        )

"Aqui se hereda del creador y se implementa el create() "
"para crear un activo de tipo herramienta."
class HerramientaCreator(AssetCreator):
    def create(self, name: str, description: str | None) -> Asset:
        return Asset(
            name=name,
            description=description,
            asset_type=AssetType.HERRAMIENTA,
            status=AssetStatus.DISPONIBLE,
        )

"aqui es lo mismo que el anterior, pero para el tipo de activo 'otro'."
class OtroCreator(AssetCreator):
    def create(self, name: str, description: str | None) -> Asset:
        return Asset(
            name=name,
            description=description,
            asset_type=AssetType.OTRO,
            status=AssetStatus.DISPONIBLE,
        )

"aqui se define , es la unica entrada para crear el activo"
class AssetFactory:
    """Punto único de entrada: decide qué Creator usar según el tipo pedido."""

    _creators: dict[AssetType, AssetCreator] = {
        AssetType.EQUIPO: EquipoCreator(),
        AssetType.HERRAMIENTA: HerramientaCreator(),
        AssetType.OTRO: OtroCreator(),
    }

    @classmethod
    def create_asset(cls, asset_type: AssetType, name: str, description: str | None = None) -> Asset:
        creator = cls._creators.get(asset_type)
        if not creator:
            raise ValueError(f"Tipo de activo no soportado: {asset_type}")
        return creator.create(name, description)