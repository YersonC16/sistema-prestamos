# Sistema de Gestión y Control de Préstamos de Activos y Herramientas

Sistema web para la sede de Concreto que permite registrar, prestar y
devolver equipos y herramientas, con seguimiento de cada movimiento.

## Tecnologías

- Backend: FastAPI (Python 3.12), 2 microservicios
- Frontend: React + TypeScript (Vite)
- Base de datos: PostgreSQL, con un esquema por servicio
- Broker: RabbitMQ
- Contenedores: Docker + Docker Compose

## Arquitectura

- `asset-service` (8001): activos, usuarios y autenticación. Patrón
  Factory Method.
- `loan-service` (8002): préstamos y devoluciones. Patrón Builder.
- Comunicación: REST para consultas y RabbitMQ para eventos.
- Organización interna: MVW (models, schemas, routers, services/core).

Detalle en `docs/arquitectura.md`.

## Requisitos

- Docker Desktop
- Git

## Instalación

```bash
git clone <url-del-repositorio>
cd sistema-prestamos
cp .env.example .env
docker compose up -d --build
docker exec -it prestamos_asset_service python -m app.seed_admin
```

En PowerShell, `cp` puede reemplazarse por `copy .env.example .env`.

Abrir http://localhost:5173. Primer administrador:
`admin@concreto.com` / `Admin123!` (cambiar la contraseña al ingresar).

## Uso diario

```bash
docker compose up -d
```

## Variables de entorno

Ver `.env.example`. `JWT_SECRET_KEY` debe cambiarse en cualquier entorno
real.

## Estructura del proyecto

```
sistema-prestamos/
├── frontend/              React + TypeScript
├── services/
│   ├── asset-service/     Activos, usuarios y autenticación
│   └── loan-service/      Préstamos
├── docs/                  Documentación detallada
├── docker-compose.yml
└── .env.example
```

## Usuarios y roles

| Rol                 | Permisos                            |
| ------------------- | ----------------------------------- |
| Administrador       | Todo: usuarios, activos y préstamos |
| Almacenista         | Registrar activos y préstamos       |
| Personal autorizado | Consultar y solicitar préstamos     |

## Pruebas

```bash
cd services/asset-service
venv\Scripts\activate
$env:TESTING="true"
pytest -v
```

Repetir en `loan-service`. Ver `docs/pruebas.md`.

## Documentación

- [Arquitectura](docs/arquitectura.md)
- [Instalación](docs/instalacion.md)
- [Base de datos](docs/base-datos.md)
- [Microservicios](docs/microservicios.md)
- [Broker](docs/broker.md)
- [Patrones de diseño](docs/patrones.md)
- [Frontend](docs/frontend.md)
- [Pruebas](docs/pruebas.md)
- [API](docs/api.md)

## Logo

Reemplazar `frontend/src/assets/logo/logo-placeholder.svg` por el logo
definitivo, sin tocar ningún componente.

## Alcance y escalabilidad

La primera versión se limita a la sede de Concreto. Está pensada para
incorporar más sedes (ver `docs/arquitectura.md`), pero eso no forma
parte de esta entrega. No incluye app móvil nativa, control financiero ni
integración con otros sistemas.
