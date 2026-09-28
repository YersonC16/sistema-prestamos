"""
Script temporal de demostración: compara el tiempo de crear préstamos
CON Builder vs SIN Builder (constructor directo).

Esto es solo para fines ilustrativos/académicos — no forma parte de la
aplicación real. Se puede eliminar sin afectar el sistema.

Ejecutar: python benchmark_builder.py
"""
import time
from datetime import datetime, timedelta, timezone
from app.services.loan_builder import LoanBuilder
from app.models.loan import Loan, LoanStatus

N = 100_000

hoy = datetime.now(timezone.utc)
manana = hoy + timedelta(days=1)


def crear_con_builder():
    """Usa el patrón: construcción paso a paso con validación en cada paso."""
    return (
        LoanBuilder()
        .with_asset(1)
        .with_responsible("Juan Pérez")
        .with_loan_date(hoy)
        .with_expected_return(manana)
        .build()
    )


def crear_sin_builder():
    """Equivalente SIN el patrón: constructor directo con todos los
    parámetros de una vez, sin validación incremental por campo."""
    return Loan(
        asset_id=1,
        responsible_name="Juan Pérez",
        loan_date=hoy,
        expected_return_date=manana,
        status=LoanStatus.ACTIVO,
    )


def medir(func) -> float:
    inicio = time.perf_counter()
    for _ in range(N):
        func()
    fin = time.perf_counter()
    return fin - inicio


if __name__ == "__main__":
    print(f"Creando {N:,} préstamos en memoria por cada método...\n")

    tiempo_con_patron = medir(crear_con_builder)
    tiempo_sin_patron = medir(crear_sin_builder)

    print(f"CON Builder:  {tiempo_con_patron:.4f} s  ({(tiempo_con_patron / N) * 1_000_000:.3f} µs por objeto)")
    print(f"SIN Builder:  {tiempo_sin_patron:.4f} s  ({(tiempo_sin_patron / N) * 1_000_000:.3f} µs por objeto)")

    diferencia_pct = ((tiempo_con_patron - tiempo_sin_patron) / tiempo_sin_patron) * 100
    print(f"\nDiferencia: {diferencia_pct:+.2f}% (la indirección del patrón es prácticamente despreciable)")
    print("\nNota: el patrón no busca ser más rápido, sino evitar constructores con muchos")
    print("parámetros posicionales y permitir validar cada campo en el momento en que se agrega")
    print("(ej. que la fecha de devolución sea posterior a la de préstamo).")