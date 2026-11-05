
"""
Demo experimental: comparación de memoria SIN Flyweight vs. CON Flyweight.

El programa:
1. Genera activos simulados con datos repetidos.
2. Construye los activos sin compartir los modelos.
3. Construye los activos utilizando el patrón Flyweight.
4. Mide la memoria retenida y el pico de memoria de Python.
5. Repite las pruebas y calcula estadísticas.
6. Compara varias cantidades de activos.
7. Verifica que ambas implementaciones produzcan los mismos datos.

Ejecutar desde la carpeta raíz del proyecto:
    python demo_flyweight.py

Si el proyecto se ejecuta en Docker:
    docker exec -it prestamos_asset_service python demo_flyweight.py
"""

import gc
import statistics
import tracemalloc

from app.models.asset import AssetStatus, AssetType
from app.services.asset_flyweight import AssetCatalog


# ============================================================
# 1. CONFIGURACIÓN DEL EXPERIMENTO
# ============================================================

# Cantidades de activos que se construirán en cada escenario.
# Esto permite observar cómo cambia la memoria al crecer el inventario.
SIZES = [100, 1_000, 10_000, 50_000, 100_000]

# Número de repeticiones para cada cantidad de activos.
# Se utilizan varias pruebas para calcular promedios y variabilidad.
REPEATS = 3

# Cantidad de activos utilizados para verificar la equivalencia funcional.
VALIDATION_N = 1_000

# Marcas simuladas de herramientas.
BRANDS = (
    "Dewalt",
    "Makita",
    "Bosch",
    "Stanley",
    "Milwaukee",
    "Hilti",
)

# Tipos de herramientas simuladas.
TOOLS = (
    "Taladro percutor",
    "Pulidora angular",
    "Sierra circular",
    "Rotomartillo",
    "Atornillador",
    "Llave de impacto",
)

# Número de combinaciones distintas de marca y herramienta.
# 6 marcas x 6 herramientas = 36 modelos.
MODEL_COUNT = len(BRANDS) * len(TOOLS)

# Conversión de bytes a MiB.
MIB = 1_048_576


# ============================================================
# 2. GENERACIÓN DE DATOS
# ============================================================

def fake_row(i: int) -> tuple:
    """
    Genera los datos de un activo.

    Los modelos se repiten de forma determinista:
    - La marca depende del índice.
    - La herramienta depende del índice.
    - El código y el identificador son diferentes.
    - El estado cambia según el índice.

    Devuelve los seis campos esperados por las clases
    de las dos implementaciones.
    """

    # Selecciona una marca de la lista.
    brand = BRANDS[i % len(BRANDS)]

    # Selecciona una herramienta.
    tool = TOOLS[(i // len(BRANDS)) % len(TOOLS)]

    # Nombre compartible del modelo.
    name = f"{tool} {brand}"

    # Descripción compartible del modelo.
    description = (
        f"{tool} marca {brand}. "
        "Uso en planta de concreto; revisión preventiva "
        "cada 6 meses y entrega con kit completo."
    )

    # Cada quinto activo se encuentra prestado.
    status = (
        AssetStatus.DISPONIBLE
        if i % 5
        else AssetStatus.PRESTADO
    )

    # El código cambia para cada activo.
    code = f"ACT-{i:06d}"

    return (
        i,
        code,
        status,
        name,
        AssetType.HERRAMIENTA,
        description,
    )


# ============================================================
# 3. IMPLEMENTACIÓN SIN FLYWEIGHT
# ============================================================

class AssetWithoutFlyweight:
    """
    Representa un activo sin utilizar Flyweight.

    Cada instancia almacena sus propios campos de modelo:
    name, asset_type y description.

    Aunque varios activos tengan la misma marca y descripción,
    cada uno recibe sus propias cadenas generadas por fake_row().
    """

    __slots__ = (
        "id",
        "code",
        "status",
        "name",
        "asset_type",
        "description",
    )

    def __init__(
        self,
        asset_id,
        code,
        status,
        name,
        asset_type,
        description,
    ):
        # Datos particulares del activo.
        self.id = asset_id
        self.code = code
        self.status = status

        # Datos del modelo almacenados en cada instancia.
        self.name = name
        self.asset_type = asset_type
        self.description = description

    def summary(self) -> dict:
        """
        Devuelve la información del activo.

        Este método permite comparar los datos con la
        implementación que utiliza Flyweight.
        """

        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "asset_type": self.asset_type,
            "status": self.status,
            "description": self.description,
        }


def build_without(n: int) -> list:
    """
    Construye n activos sin compartir los objetos de modelo.

    La lista mantiene todas las instancias en memoria
    durante la medición.
    """

    return [
        AssetWithoutFlyweight(*fake_row(i))
        for i in range(n)
    ]


# ============================================================
# 4. IMPLEMENTACIÓN CON FLYWEIGHT
# ============================================================

def build_with(n: int) -> AssetCatalog:
    """
    Construye n activos utilizando AssetCatalog.

    La fábrica interna de AssetCatalog reutiliza los modelos
    que tengan la misma clave, en lugar de almacenar una
    copia del modelo en cada activo.

    El identificador, el código y el estado siguen siendo
    particulares de cada activo.
    """

    catalog = AssetCatalog()

    for i in range(n):
        # AssetCatalog se encarga de reutilizar el modelo.
        catalog.add(*fake_row(i))

    return catalog


# ============================================================
# 5. MEDICIÓN REAL DE MEMORIA
# ============================================================

def measure(builder, n: int) -> tuple:
    """
    Mide una construcción de activos utilizando tracemalloc.

    current:
        Memoria rastreada que permanece asignada al terminar
        la construcción.

    peak:
        Máximo de memoria rastreada durante la construcción.

    result:
        Objeto construido. Se devuelve para mantenerlo vivo
        hasta que la lectura de memoria haya terminado.

    Las mediciones no incluyen la memoria completa del
    contenedor Docker ni toda la memoria del proceso.
    """

    # Limpia objetos cíclicos pendientes antes de medir.
    gc.collect()

    # Inicia un seguimiento nuevo para esta prueba.
    tracemalloc.start()

    try:
        # Construye los activos de forma real.
        result = builder(n)

        # Consulta la memoria actual y el pico alcanzado.
        current, peak = tracemalloc.get_traced_memory()

    finally:
        # Detiene el seguimiento incluso si hay un error.
        tracemalloc.stop()

    return current, peak, result


# ============================================================
# 6. VALIDACIÓN DE RESULTADOS
# ============================================================

def validate_results() -> None:
    """
    Verifica que las dos implementaciones produzcan
    la misma información para una muestra de activos.

    La validación se ejecuta antes de las mediciones principales.
    """

    print("Verificando equivalencia funcional...")

    # Construye una muestra con cada implementación.
    plain = build_without(VALIDATION_N)
    catalog = build_with(VALIDATION_N)

    # Compara cada activo de ambas listas.
    for i in range(VALIDATION_N):

        summary_plain = plain[i].summary()
        summary_flyweight = catalog.items[i].summary()

        assert summary_plain == summary_flyweight, (
            f"Los resultados no coinciden en el activo {i}"
        )

    # Verifica el número de modelos compartidos.
    assert catalog.shared_models == MODEL_COUNT, (
        f"Se esperaban {MODEL_COUNT} modelos, "
        f"pero se encontraron {catalog.shared_models}"
    )

    print(
        f"Validación correcta: {VALIDATION_N:,} activos "
        f"coinciden y se comparten {catalog.shared_models} modelos.\n"
    )

    # Libera la memoria usada por la validación.
    del plain, catalog
    gc.collect()


# ============================================================
# 7. FUNCIONES ESTADÍSTICAS
# ============================================================

def summarize(values: list) -> dict:
    """
    Calcula estadísticas descriptivas de una lista de números.

    El promedio representa el valor central observado.
    La desviación estándar mide la dispersión entre pruebas.
    El mínimo y el máximo muestran el rango observado.
    """

    return {
        "mean": statistics.mean(values),
        "stdev": (
            statistics.stdev(values)
            if len(values) >= 2
            else 0.0
        ),
        "min": min(values),
        "max": max(values),
    }


def print_stats(
    label: str,
    values: list,
    unit: str = "MiB",
) -> None:
    """
    Imprime las estadísticas utilizando la unidad indicada.

    Para memoria, se utiliza MiB.
    Para porcentajes de ahorro, se utiliza %.
    """

    stats = summarize(values)

    print(f"\n{label}")
    print(f"  Promedio:             {stats['mean']:10.4f} {unit}")
    print(f"  Desviación estándar:  {stats['stdev']:10.4f} {unit}")
    print(f"  Mínimo:               {stats['min']:10.4f} {unit}")
    print(f"  Máximo:               {stats['max']:10.4f} {unit}")


# ============================================================
# 8. EJECUCIÓN DEL EXPERIMENTO
# ============================================================

if __name__ == "__main__":

    print("=" * 72)
    print("EXPERIMENTO DE MEMORIA: PATRÓN FLYWEIGHT")
    print("=" * 72)

    print(f"Cantidades de activos: {SIZES}")
    print(f"Repeticiones por escenario: {REPEATS}")
    print(f"Modelos diferentes: {MODEL_COUNT}")
    print(
        f"Construcciones medidas: {len(SIZES) * REPEATS * 2}\n"
    )

    # Comprueba que ambas versiones entreguen los mismos datos.
    validate_results()

    # Recorre los diferentes tamaños del inventario.
    for n in SIZES:

        # Listas donde se guardan las mediciones de cada repetición.
        without_current = []
        without_peak = []
        with_current = []
        with_peak = []

        savings_current = []
        savings_peak = []

        print("\n" + "=" * 72)
        print(f"ESCENARIO: {n:,} ACTIVOS")
        print("=" * 72)

        # Repite el escenario para poder calcular estadísticas.
        for trial in range(REPEATS):

            # Alterna el orden de ejecución para evitar medir
            # siempre primero la misma implementación.
            if trial % 2 == 0:
                order = ("without", "with")
            else:
                order = ("with", "without")

            # Aquí se guardan solamente los números medidos.
            results = {}

            for approach in order:

                # Selecciona la implementación que se medirá.
                if approach == "without":
                    builder = build_without
                else:
                    builder = build_with

                # Construye y mide los activos.
                current, peak, result = measure(builder, n)

                # Guarda las mediciones en bytes.
                results[approach] = (current, peak)

                # Libera los objetos antes de medir el otro enfoque.
                del result
                gc.collect()

            # Convierte los resultados de bytes a MiB.
            current_without = results["without"][0] / MIB
            peak_without_value = results["without"][1] / MIB

            current_with = results["with"][0] / MIB
            peak_with_value = results["with"][1] / MIB

            # Guarda los valores de esta repetición.
            without_current.append(current_without)
            without_peak.append(peak_without_value)

            with_current.append(current_with)
            with_peak.append(peak_with_value)

            # Calcula el ahorro de memoria retenida.
            # Un porcentaje positivo significa menos memoria
            # con Flyweight; uno negativo significa más memoria.
            if current_without > 0:
                saving_current = (
                    1 - current_with / current_without
                ) * 100
            else:
                saving_current = 0.0

            # Calcula el ahorro según el pico máximo.
            if peak_without_value > 0:
                saving_peak = (
                    1 - peak_with_value / peak_without_value
                ) * 100
            else:
                saving_peak = 0.0

            savings_current.append(saving_current)
            savings_peak.append(saving_peak)

            # Muestra los resultados reales de esta repetición.
            print(
                f"Repetición {trial + 1}/{REPEATS} | "
                f"Retenida sin: {current_without:9.4f} MiB | "
                f"Retenida con: {current_with:9.4f} MiB | "
                f"Ahorro: {saving_current:7.2f}%"
            )

            print(
                f"{'':22}"
                f"Pico sin: {peak_without_value:9.4f} MiB | "
                f"Pico con: {peak_with_value:9.4f} MiB | "
                f"Ahorro pico: {saving_peak:7.2f}%"
            )

        # ----------------------------------------------------
        # RESUMEN ESTADÍSTICO DEL ESCENARIO
        # ----------------------------------------------------

        print("\nRESUMEN ESTADÍSTICO")

        print_stats(
            "SIN FLYWEIGHT - Memoria retenida",
            without_current,
        )

        print_stats(
            "CON FLYWEIGHT - Memoria retenida",
            with_current,
        )

        print_stats(
            "SIN FLYWEIGHT - Pico de memoria",
            without_peak,
        )

        print_stats(
            "CON FLYWEIGHT - Pico de memoria",
            with_peak,
        )

        print_stats(
            "AHORRO - Memoria retenida",
            savings_current,
            "%",
        )

        print_stats(
            "AHORRO - Pico de memoria",
            savings_peak,
            "%",
        )

        # Calcula el ahorro a partir de las medias de memoria.
        mean_without = statistics.mean(without_current)
        mean_with = statistics.mean(with_current)

        if mean_without > 0:
            overall_saving = (
                1 - mean_with / mean_without
            ) * 100
        else:
            overall_saving = 0.0

        print(
            f"\nAhorro global sobre los promedios: "
            f"{overall_saving:.2f}%"
        )

    # ========================================================
    # 9. FINAL DEL EXPERIMENTO
    # ========================================================

    print("\n" + "=" * 72)
    print("EXPERIMENTO FINALIZADO")
    print("=" * 72)

    print(
        "\nInterpretación:"
        "\n- Un ahorro positivo indica menor memoria rastreada con Flyweight."
        "\n- Un ahorro negativo indica que Flyweight consumió más memoria."
        "\n- Las cantidades pequeñas pueden no justificar el costo del patrón."
        "\n- Las desviaciones estándar muestran la variación entre repeticiones."
    )

    print(
        "\nLimitación: tracemalloc mide asignaciones rastreadas por Python. "
        "No mide toda la RAM del proceso, el contenedor Docker ni otros "
        "servicios. Los resultados pueden repetirse si la construcción "
        "es determinista y el entorno es estable."
    )
