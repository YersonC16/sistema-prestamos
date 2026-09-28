# Microservicios

## asset-service (puerto 8001)

Ruta: `services/asset-service/`

```
app/
├── models/     asset.py, user.py
├── schemas/    asset.py, user.py
├── routers/    assets.py, auth.py
├── services/   asset_factory.py (Factory Method), event_consumer.py
├── core/       config.py, database.py, security.py, deps.py, rabbitmq.py
├── main.py
└── seed_admin.py
```

Variables de entorno: `DATABASE_URL`, `RABBITMQ_URL`, `JWT_SECRET_KEY`,
`JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`.

## loan-service (puerto 8002)

Ruta: `services/loan-service/`

```
app/
├── models/     loan.py
├── schemas/    loan.py
├── routers/    loans.py
├── services/   loan_builder.py (Builder), event_publisher.py
├── core/       config.py, database.py, deps.py, rabbitmq.py
└── main.py
```

Variables de entorno: `DATABASE_URL`, `RABBITMQ_URL`, `ASSET_SERVICE_URL`,
`JWT_SECRET_KEY`, `JWT_ALGORITHM`.

`JWT_SECRET_KEY` debe ser idéntica en ambos servicios; de lo contrario un
token válido en uno es rechazado por el otro.

## Reglas de convivencia

- Ningún servicio importa código del otro.
- Ningún servicio consulta el esquema del otro.
- Toda comunicación pasa por REST (consultas) o por el broker (eventos).
