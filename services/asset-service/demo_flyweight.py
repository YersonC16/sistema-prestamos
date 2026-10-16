"""
Demo temporal: memoria de N activos SIN Flyweight vs CON Flyweight.
No forma parte de la aplicación: se puede borrar sin afectar nada.

Ejecutar: python demo_flyweight.py
"""
import gc
import tracemalloc

from app.models.asset import AssetStatus, AssetType
from app.services.asset_flyweight import AssetCatalog

N = 100_000
BRANDS = ("Dewalt", "Makita", "Bosch", "Stanley", "Milwaukee", "Hilti")
TOOLS = ("Taladro percutor", "Pulidora angular", "Sierra circular", "Rotomartillo", "Atornillador", "Llave de impacto")
MODEL_COUNT = len(BRANDS) * len(TOOLS)


def fake_row(i: int):
    """Simula una fila de la BD. Los f-strings crean un texto NUEVO por fila,
    igual que lo haría el driver de la base de datos."""
    brand = BRANDS[i % len(BRANDS)]
    tool = TOOLS[(i // len(BRANDS)) % len(TOOLS)]
    name = f"{tool} {brand}"
    description = f"{tool} marca {brand}. Uso en planta de concreto; revisión preventiva cada 6 meses y entrega con kit completo."
    status = AssetStatus.DISPONIBLE if i % 5 else AssetStatus.PRESTADO
    return i, f"ACT-{i:06d}", status, name, AssetType.HERRAMIENTA, description


# ---------------- SIN patrón ----------------
class AssetWithoutFlyweight:
    """Cada activo guarda su PROPIA copia de nombre, tipo y descripción."""

    __slots__ = ("id", "code", "status", "name", "asset_type", "description")

    def __init__(self, asset_id, code, status, name, asset_type, description):
        self.id = asset_id
        self.code = code
        self.status = status
        self.name = name
        self.asset_type = asset_type
        self.description = description

    def summary(self) -> dict:
        return {
            "id": self.id, "name": self.name, "code": self.code,
            "asset_type": self.asset_type, "status": self.status, "description": self.description,
        }


def build_without(n: int) -> list[AssetWithoutFlyweight]:
    return [AssetWithoutFlyweight(*fake_row(i)) for i in range(n)]


# ---------------- CON patrón ----------------
def build_with(n: int) -> AssetCatalog:
    catalog = AssetCatalog()
    for i in range(n):
        catalog.add(*fake_row(i))
    return catalog


def measure(builder, n: int):
    gc.collect()
    tracemalloc.start()
    result = builder(n)
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, result


if __name__ == "__main__":
    print(f"Creando {N:,} activos de {MODEL_COUNT} modelos distintos por cada enfoque...\n")

    memory_without, plain = measure(build_without, N)
    memory_with, catalog = measure(build_with, N)

    # El patrón no cambia el comportamiento: ambos producen el mismo resultado
    assert all(plain[k].summary() == catalog.items[k].summary() for k in range(1000))

    saving = (1 - memory_with / memory_without) * 100
    print(f"SIN Flyweight: {memory_without / 1_048_576:7.1f} MB  ({N:,} copias del texto de cada modelo)")
    print(f"CON Flyweight: {memory_with / 1_048_576:7.1f} MB  ({catalog.shared_models} flyweights compartidos)")
    print(f"\nAhorro de memoria: {saving:.0f}%")
    print("Resultado idéntico en ambos enfoques (verificado con los primeros 1.000 activos).")
    print("\nNota: el ahorro es grande con muchos activos y pocos modelos. Con cientos de")
    print("activos casi no se nota; el patrón se justifica por la escalabilidad.")