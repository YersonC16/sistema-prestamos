
"""
Implementación del patrón de diseño Flyweight para los activos.

Objetivo:
Reducir la duplicación de información compartiendo los datos
comunes de los modelos de herramientas y activos.

Estado intrínseco (compartido):
    - name
    - asset_type
    - description

Estado extrínseco (propio de cada activo):
    - id
    - code
    - status

La fábrica administra los modelos compartidos y el catálogo
organiza los activos que utilizan dichos modelos.
"""

import threading

# Importamos los tipos y estados definidos en el modelo de activos.
from app.models.asset import AssetStatus, AssetType


# Definimos el tipo de clave utilizado para identificar un modelo.
# Un modelo se identifica por su nombre, tipo y descripción.
# La descripción puede ser None.
SharedKey = tuple[str, AssetType, str | None]


# ============================================================
# 1. FLYWEIGHT: MODELO COMPARTIDO
# ============================================================

class AssetModelFlyweight:
    """
    Representa el estado intrínseco de un modelo de activo.

    Los atributos name, asset_type y description son compartidos
    por todos los activos que utilizan el mismo modelo.

    La clase es inmutable para evitar que una modificación afecte
    accidentalmente a muchos activos al mismo tiempo.
    """

    # __slots__ declara los atributos permitidos y evita que cada
    # instancia necesite un diccionario __dict__ para almacenarlos.
    __slots__ = ("name", "asset_type", "description")

    def __init__(
        self,
        name: str,
        asset_type: AssetType,
        description: str | None,
    ):
        # Utilizamos object.__setattr__ para asignar los valores
        # durante la construcción, evitando el __setattr__ propio.
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "asset_type", asset_type)
        object.__setattr__(self, "description", description)

    def __setattr__(self, key, value):
        """
        Impide cambiar los atributos después de la construcción.

        Como el modelo puede ser compartido, modificarlo podría
        alterar la información observada por varios activos.
        """
        raise AttributeError(
            "Un flyweight es inmutable: "
            "se comparte entre muchos activos"
        )

    def describe(
        self,
        asset_id: int,
        code: str | None,
        status: AssetStatus,
    ) -> dict:
        """
        Combina el estado intrínseco compartido con el estado
        extrínseco recibido desde un activo específico.

        Los datos particulares llegan como parámetros, por lo que
        no es necesario almacenarlos dentro del modelo compartido.
        """
        return {
            # Datos particulares del activo recibido.
            "id": asset_id,
            "code": code,
            "status": status,

            # Datos del modelo compartido.
            "name": self.name,
            "asset_type": self.asset_type,
            "description": self.description,
        }


# ============================================================
# 2. FACTORY: FÁBRICA DE MODELOS COMPARTIDOS
# ============================================================

class AssetModelFactory:
    """
    Administra los objetos AssetModelFlyweight.

    Antes de crear un modelo nuevo, comprueba si ya existe uno
    con la misma clave. Si existe, devuelve el objeto compartido.

    El diccionario _models mantiene las referencias a los modelos
    creados para poder reutilizarlos posteriormente.
    """

    def __init__(self):
        # Diccionario que relaciona cada clave con su modelo.
        # Ejemplo:
        # (nombre, tipo, descripción) -> objeto Flyweight.
        self._models: dict[SharedKey, AssetModelFlyweight] = {}

        # Lock para proteger la creación de modelos cuando varias
        # operaciones concurrentes acceden a la fábrica.
        self._lock = threading.Lock()

    def get_model(
        self,
        name: str,
        asset_type: AssetType,
        description: str | None,
    ) -> AssetModelFlyweight:
        """
        Busca un modelo existente o crea uno nuevo.

        Si dos activos tienen la misma clave, ambos reciben
        una referencia al mismo objeto AssetModelFlyweight.
        """

        # Construimos la clave a partir de los datos intrínsecos.
        key: SharedKey = (name, asset_type, description)

        # Primera consulta sin bloquear.
        # Si el modelo ya existe, no necesitamos adquirir el Lock.
        model = self._models.get(key)

        if model is None:
            # Protegemos la sección de creación frente al acceso
            # concurrente de otros hilos.
            with self._lock:

                # Comprobamos nuevamente el diccionario.
                # Otro hilo pudo crear el modelo mientras esperábamos.
                model = self._models.get(key)

                if model is None:
                    # Creamos el modelo únicamente si no existe.
                    model = AssetModelFlyweight(
                        name,
                        asset_type,
                        description,
                    )

                    # Guardamos la referencia para reutilizarla.
                    self._models[key] = model

        # Devolvemos el modelo existente o el recién creado.
        return model

    def count(self) -> int:
        """
        Devuelve la cantidad de modelos compartidos registrados.

        No cuenta los activos individuales, sino las entradas
        existentes en el diccionario de modelos.
        """
        return len(self._models)


# ============================================================
# 3. OBJETO CONTEXTUAL: ACTIVO INDIVIDUAL
# ============================================================

class AssetItem:
    """
    Representa un activo concreto de la empresa.

    Cada activo conserva su propio estado extrínseco y una
    referencia al modelo Flyweight que comparte con otros activos.

    Ejemplo:
    Dos taladros pueden compartir nombre, tipo y descripción,
    pero tener códigos, identificadores y estados diferentes.
    """

    # Limitamos los atributos almacenados en cada objeto.
    __slots__ = ("id", "code", "status", "model")

    def __init__(
        self,
        asset_id: int,
        code: str | None,
        status: AssetStatus,
        model: AssetModelFlyweight,
    ):
        # Información particular de este activo.
        self.id = asset_id
        self.code = code
        self.status = status

        # Referencia al modelo compartido.
        # Varios AssetItem pueden apuntar al mismo objeto.
        self.model = model

    def summary(self) -> dict:
        """
        Genera el resumen del activo.

        Delegamos en el modelo compartido la combinación de los
        datos intrínsecos y los datos extrínsecos de este activo.
        """
        return self.model.describe(
            self.id,
            self.code,
            self.status,
        )


# ============================================================
# 4. CATÁLOGO: ADMINISTRADOR DE ACTIVOS
# ============================================================

class AssetCatalog:
    """
    Organiza una colección de activos que utilizan Flyweight.

    El catálogo recibe los datos de cada activo, solicita el modelo
    correspondiente a la fábrica y almacena el objeto contextual.
    """

    def __init__(
        self,
        factory: AssetModelFactory | None = None,
    ):
        # Utilizamos la fábrica recibida o creamos una nueva.
        # La fábrica permite compartir modelos entre los activos
        # que se incorporan a este catálogo.
        self._factory = factory or AssetModelFactory()

        # Lista que contiene los objetos AssetItem individuales.
        self._items: list[AssetItem] = []

    @classmethod
    def from_rows(
        cls,
        rows,
        factory: AssetModelFactory | None = None,
    ) -> "AssetCatalog":
        """
        Construye un catálogo a partir de filas de datos.

        Se espera que cada fila tenga los atributos:
        id, code, status, name, asset_type y description.

        Este método facilita cargar registros provenientes
        de una consulta a la base de datos.
        """

        # Creamos el catálogo con la fábrica indicada, si existe.
        catalog = cls(factory)

        # Recorremos las filas y agregamos cada activo.
        for row in rows:
            catalog.add(
                row.id,
                row.code,
                row.status,
                row.name,
                row.asset_type,
                row.description,
            )

        # Devolvemos el catálogo con todos los activos procesados.
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
        """
        Agrega un activo a la colección.

        Primero obtiene el modelo compartido de la fábrica.
        Después crea un objeto AssetItem con los datos particulares
        y la referencia a dicho modelo.
        """

        # Reutilizamos el modelo si ya existe.
        # Solo se crea un Flyweight nuevo cuando la clave no existe.
        model = self._factory.get_model(
            name,
            asset_type,
            description,
        )

        # Creamos el objeto individual con su estado extrínseco.
        item = AssetItem(
            asset_id,
            code,
            status,
            model,
        )

        # Guardamos el activo en el catálogo.
        self._items.append(item)

        # Devolvemos el objeto creado.
        return item

    def summaries(self) -> list[dict]:
        """
        Devuelve los resúmenes de todos los activos del catálogo.

        Cada resumen combina la información individual del activo
        con la información del modelo compartido.
        """
        return [
            item.summary()
            for item in self._items
        ]

    @property
    def items(self) -> list[AssetItem]:
        """
        Permite consultar la lista de activos almacenados.

        Se devuelve la lista interna, no una copia.
        Por tanto, quien la recibe puede modificarla.
        """
        return self._items

    @property
    def total_items(self) -> int:
        """
        Devuelve el número total de activos individuales.

        Cada AssetItem cuenta como un activo, incluso cuando
        comparte su modelo con muchos otros objetos.
        """
        return len(self._items)

    @property
    def shared_models(self) -> int:
        """
        Devuelve la cantidad de modelos Flyweight registrados.

        Por ejemplo, el catálogo puede contener 100.000 activos
        y solamente 36 modelos compartidos.
        """
        return self._factory.count()
