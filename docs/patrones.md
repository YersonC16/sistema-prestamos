# Patrones de diseño

## Factory Method: asset-service

**Ubicación:** `app/services/asset_factory.py`

**Problema:** crear distintos tipos de activo (equipo, herramienta, otro)
sin condicionales repetidos por el código.

**Cómo funciona:** cada tipo tiene su propio creador (`EquipoCreator`,
`HerramientaCreator`, `OtroCreator`) que hereda de `AssetCreator`.
`AssetFactory` elige el creador mediante un diccionario y le delega la
creación. Agregar un tipo nuevo es una clase nueva y una línea en el
diccionario.

**Abstracción manual:** `AssetCreator` no usa el módulo `abc`. Su método
`create()` lanza `NotImplementedError`, así que toda subclase debe
sobrescribirlo.

| Rol GoF               | En este proyecto                                     |
| --------------------- | ---------------------------------------------------- |
| Creator               | `AssetCreator`                                       |
| Método fábrica        | `create()`                                           |
| Concrete Creators     | `EquipoCreator`, `HerramientaCreator`, `OtroCreator` |
| Selección del creador | `AssetFactory.create_asset()`                        |

**Variación respecto al patrón clásico:** no hay jerarquía de productos
(como `WindowsButton`/`HTMLButton`), porque todos los activos son la
misma clase `Asset` y solo cambian sus datos.

## Builder: loan-service

**Ubicación:** `app/services/loan_builder.py`

**Problema:** construir un préstamo con varios campos y reglas cruzadas
(la fecha de devolución debe ser posterior a la de préstamo) sin un
constructor de muchos parámetros.

**Cómo funciona:** cada método `with_*` valida y guarda un dato, y
devuelve el mismo builder para poder encadenar llamadas. `build()`
verifica que estén todos los campos y crea el `Loan` con estado `activo`.

| Rol GoF               | En este proyecto                                                                   |
| --------------------- | ---------------------------------------------------------------------------------- |
| Builder concreto      | `LoanBuilder`                                                                      |
| `reset()`             | `__init__()`                                                                       |
| Pasos de construcción | `with_asset()`, `with_responsible()`, `with_loan_date()`, `with_expected_return()` |
| `getProduct()`        | `build()`                                                                          |
| Director              | No existe: lo cumple el router de FastAPI                                          |

## Por qué estos dos patrones

Factory Method encaja con los activos porque hay tipos con creación
diferenciada y extensible. Builder encaja con los préstamos por sus
validaciones entre campos. Singleton, Prototype y Abstract Factory no
respondían a ninguna necesidad del alcance.
