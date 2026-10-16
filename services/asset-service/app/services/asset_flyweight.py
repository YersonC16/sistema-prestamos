import threading

from app.models.asset import AssetStatus, AssetType

SharedKey = tuple[str, AssetType, str | None]


class AssetModelFlyweight:
    """Flyweight: guarda el estado INTRÍNSECO (compartido) de un modelo de
    activo. Es inmutable porque lo comparten muchos activos a la vez."""

    __slots__ = ("name", "asset_type", "description")

    def __init__(self, name: str, asset_type: AssetType, description: str | None):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "asset_type", asset_type)
        object.__setattr__(self, "description", description)

    def __setattr__(self, key, value):
        raise AttributeError("Un flyweight es inmutable: se comparte entre muchos activos")

    def describe(self, asset_id: int, code: str | None, status: AssetStatus) -> dict:
        """Operación del flyweight: recibe el estado EXTRÍNSECO por parámetro
        y lo combina con el estado compartido."""
        return {
            "id": asset_id,
            "name": self.name,
            "code": code,
            "asset_type": self.asset_type,
            "status": status,
            "description": self.description,
        }


class AssetModelFactory:
    """Fábrica flyweight: decide si reutiliza un flyweight existente o crea uno.
    Usa un Lock porque FastAPI atiende peticiones en varios hilos."""

    def __init__(self):
        self._models: dict[SharedKey, AssetModelFlyweight] = {}
        self._lock = threading.Lock()

    def get_model(self, name: str, asset_type: AssetType, description: str | None) -> AssetModelFlyweight:
        key: SharedKey = (name, asset_type, description)
        model = self._models.get(key)
        if model is None:
            with self._lock:
                model = self._models.get(key)  # otro hilo pudo crearlo mientras esperábamos
                if model is None:
                    model = AssetModelFlyweight(name, asset_type, description)
                    self._models[key] = model
        return model

    def count(self) -> int:
        return len(self._models)


class AssetItem:
    """Objeto contextual: solo el estado EXTRÍNSECO (único de cada activo)
    más una referencia al flyweight compartido."""

    __slots__ = ("id", "code", "status", "model")

    def __init__(self, asset_id: int, code: str | None, status: AssetStatus, model: AssetModelFlyweight):
        self.id = asset_id
        self.code = code
        self.status = status
        self.model = model

    def summary(self) -> dict:
        return self.model.describe(self.id, self.code, self.status)


class AssetCatalog:
    """Cliente del flyweight: arma la colección de activos pidiendo los
    modelos a la fábrica."""

    def __init__(self, factory: AssetModelFactory | None = None):
        self._factory = factory or AssetModelFactory()
        self._items: list[AssetItem] = []

    @classmethod
    def from_rows(cls, rows, factory: AssetModelFactory | None = None) -> "AssetCatalog":
        catalog = cls(factory)
        for row in rows:
            catalog.add(row.id, row.code, row.status, row.name, row.asset_type, row.description)
        return catalog

    def add(
        self,
        asset_id: int,
        code: str | None,
        status: AssetStatus,
        name: str,
        asset_type: AssetType,
        description: str | None,
    ) -> AssetItem:
        model = self._factory.get_model(name, asset_type, description)
        item = AssetItem(asset_id, code, status, model)
        self._items.append(item)
        return item

    def summaries(self) -> list[dict]:
        return [item.summary() for item in self._items]

    @property
    def items(self) -> list[AssetItem]:
        return self._items

    @property
    def total_items(self) -> int:
        return len(self._items)

    @property
    def shared_models(self) -> int:
        return self._factory.count()