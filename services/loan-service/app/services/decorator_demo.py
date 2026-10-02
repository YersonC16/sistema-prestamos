"""
Demostración independiente del patrón Decorator.

IMPORTANTE:
Este archivo no modifica el funcionamiento real del sistema.
No utiliza RabbitMQ, base de datos ni los servicios reales.
"""

import time


# ============================================================
# COMPONENTE BASE
# ============================================================

class Operation:
    """Interfaz común de la operación y los decoradores."""

    name = "operacion"

    def execute(self, context):
        raise NotImplementedError


# ============================================================
# CONTEXTO
# ============================================================

class OperationContext:
    """Información que viaja por la cadena."""

    def __init__(self, user):
        self.user = user


# ============================================================
# OPERACIÓN CONCRETA
# ============================================================

class DemoLoanOperation(Operation):
    """
    Operación principal.

    Representa conceptualmente a CreateLoanOperation
    del sistema real.
    """

    name = "prestamo.crear"

    def execute(self, context):
        print("    [CORE] Ejecutando operación principal...")
        time.sleep(0.05)

        print("    [CORE] Creando préstamo...")
        time.sleep(0.05)

        print("    [CORE] Préstamo creado correctamente.")

        return {
            "id": 100,
            "asset_id": 25,
            "responsible": "Juan Pérez",
        }


# ============================================================
# DECORADOR BASE
# ============================================================

class OperationDecorator(Operation):
    """
    Decorador base.

    Contiene una operación y delega la ejecución
    hacia el objeto envuelto.
    """

    def __init__(self, wrapped):
        self._wrapped = wrapped
        self.name = wrapped.name

    def execute(self, context):
        return self._wrapped.execute(context)


# ============================================================
# DECORADOR DE PERMISOS
# ============================================================

class RoleGuardDecorator(OperationDecorator):

    def __init__(self, wrapped, allowed_roles):
        super().__init__(wrapped)
        self._allowed_roles = allowed_roles

    def execute(self, context):

        print("    [ROLE] Verificando permisos...")

        role = context.user["role"]

        if role not in self._allowed_roles:
            print(f"    [ROLE] Acceso rechazado: {role}")
            raise PermissionError(
                "El usuario no tiene permisos"
            )

        print(f"    [ROLE] Acceso permitido: {role}")

        return super().execute(context)


# ============================================================
# DECORADOR DE AUDITORÍA
# ============================================================

class AuditDecorator(OperationDecorator):

    def execute(self, context):

        loan = super().execute(context)

        print("    [AUDIT] Registrando operación...")
        print(
            f"            Usuario: {context.user['name']}"
        )
        print(
            f"            Acción: crear préstamo"
        )
        print(
            f"            Préstamo: {loan['id']}"
        )

        return loan


# ============================================================
# DECORADOR DE EVENTOS
# ============================================================

class EventPublisherDecorator(OperationDecorator):

    def execute(self, context):

        loan = super().execute(context)

        print("    [EVENT] Publicando evento...")
        print("            Evento: prestamo.creado")
        print(
            f"            Préstamo: {loan['id']}"
        )

        return loan


# ============================================================
# DECORADOR DE TIEMPO
# ============================================================

class TimingDecorator(OperationDecorator):

    def execute(self, context):

        start = time.perf_counter()

        try:
            return super().execute(context)

        finally:
            elapsed = (
                time.perf_counter() - start
            ) * 1000

            print(
                f"    [TIMING] Tiempo total: "
                f"{elapsed:.2f} ms"
            )


# ============================================================
# DEMOSTRACIÓN SIN DECORATOR
# ============================================================

def without_decorator():

    print()
    print("=" * 60)
    print("1. SIN DECORATOR")
    print("=" * 60)

    operation = DemoLoanOperation()

    context = OperationContext(
        {
            "id": 1,
            "name": "Administrador",
            "role": "administrador",
        }
    )

    print()
    print("[MAIN] Ejecutando operación directamente...")

    loan = operation.execute(context)

    print()
    print(
        f"[RESULTADO] Préstamo creado: {loan['id']}"
    )


# ============================================================
# DEMOSTRACIÓN CON DECORATOR
# ============================================================

def with_decorator():

    print()
    print("=" * 60)
    print("2. CON DECORATOR")
    print("=" * 60)

    core = DemoLoanOperation()

    # Capa 1
    operation = EventPublisherDecorator(core)

    # Capa 2
    operation = AuditDecorator(operation)

    # Capa 3
    operation = RoleGuardDecorator(
        operation,
        (
            "administrador",
            "almacenista",
        ),
    )

    # Capa 4
    operation = TimingDecorator(operation)

    context = OperationContext(
        {
            "id": 1,
            "name": "Administrador",
            "role": "administrador",
        }
    )

    print()
    print("[MAIN] Ejecutando cadena de Decorators...")
    print()

    loan = operation.execute(context)

    print()
    print(
        f"[RESULTADO] Préstamo creado: {loan['id']}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("#" * 60)
    print("#       DEMOSTRACIÓN PATRÓN DECORATOR")
    print("#       SISTEMA DE PRÉSTAMOS")
    print("#" * 60)

    without_decorator()

    with_decorator()

    print()
    print("=" * 60)
    print("FIN DE LA DEMOSTRACIÓN")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()