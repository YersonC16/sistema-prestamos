"""
Script temporal de demostración: compara el tiempo de crear activos
CON Factory Method vs SIN Factory Method (creación directa).

Esto es solo para fines ilustrativos/académicos — no forma parte de la
aplicación real. Se puede eliminar sin afectar el sistema.

Ejecutar: python benchmark_factory.py
"""
import time
from app.services.asset_factory import AssetFactory
from app.models.asset import Asset, AssetType, AssetStatus

N = 100_000


def crear_con_factory_method():
    """Usa el patrón: AssetFactory decide qué Creator usar."""
    return AssetFactory.create_asset(AssetType.HERRAMIENTA, "Taladro", "Uso general")


def crear_sin_factory_method(tipo: str, nombre: str, descripcion: str | None):
    """Equivalente SIN el patrón: lógica condicional repetida inline,
    tal como se vería sin encapsular la creación en clases dedicadas."""
    if tipo == "equipo":
        return Asset(name=nombre, description=descripcion, asset_type=AssetType.EQUIPO, status=AssetStatus.DISPONIBLE)
    elif tipo == "herramienta":
        return Asset(name=nombre, description=descripcion, asset_type=AssetType.HERRAMIENTA, status=AssetStatus.DISPONIBLE)
    elif tipo == "otro":
        return Asset(name=nombre, description=descripcion, asset_type=AssetType.OTRO, status=AssetStatus.DISPONIBLE)
    else:
        raise ValueError(f"Tipo no soportado: {tipo}")


def medir(func, *args, **kwargs) -> float:
    inicio = time.perf_counter()
    for _ in range(N):
        func(*args, **kwargs)
    fin = time.perf_counter()
    return fin - inicio


if __name__ == "__main__":
    print(f"Creando {N:,} activos en memoria por cada método...\n")

    tiempo_con_patron = medir(crear_con_factory_method)
    tiempo_sin_patron = medir(crear_sin_factory_method, "herramienta", "Taladro", "Uso general")

    print(f"CON Factory Method:  {tiempo_con_patron:.4f} s  ({(tiempo_con_patron / N) * 1_000_000:.3f} µs por objeto)")
    print(f"SIN Factory Method:  {tiempo_sin_patron:.4f} s  ({(tiempo_sin_patron / N) * 1_000_000:.3f} µs por objeto)")

    diferencia_pct = ((tiempo_con_patron - tiempo_sin_patron) / tiempo_sin_patron) * 100
    print(f"\nDiferencia: {diferencia_pct:+.2f}% (la indirección del patrón es prácticamente despreciable)")
    print("\nNota: el patrón no busca ser más rápido, sino más mantenible y extensible.")
    print("Agregar un tipo de activo nuevo con Factory Method no requiere tocar código existente;")
    print("con el enfoque condicional (if/elif), cada tipo nuevo obliga a modificar la misma función.")