# Pruebas

## Ejecución

```
cd services/asset-service
venv\Scripts\activate
$env:TESTING="true"
pytest -v
```

Repetir en `services/loan-service`.

## Qué se prueba

| Servicio      | Archivo                       | Cubre                                        |
| ------------- | ----------------------------- | -------------------------------------------- |
| asset-service | `tests/test_asset_factory.py` | Factory Method: 3 tipos de activo            |
| asset-service | `tests/test_assets_api.py`    | Endpoints, autenticación (401) y roles (403) |
| loan-service  | `tests/test_loan_builder.py`  | Builder: caso válido y 3 casos de error      |

Total: 11 pruebas.

## Cómo funcionan

- Usan SQLite en memoria, sin necesidad de Docker.
- `TESTING=true` hace que los modelos omitan los esquemas de Postgres.
- Cada prueba parte de una base vacía.
- Los tokens de prueba se generan con la misma función que usa el sistema.

## Fuera de cobertura

No hay pruebas automáticas del broker, del frontend ni del flujo
completo entre servicios. Esas verificaciones se hicieron manualmente.
