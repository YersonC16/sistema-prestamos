# Instalación y ejecución

## Requisitos

- Docker Desktop (con Docker Compose v2)
- Git

## Instalación desde cero

1. Clonar el repositorio.
2. Copiar `.env.example` a `.env` en la raíz y ajustar los valores.
3. Levantar el sistema:

```
   docker compose up -d --build
```

4. Crear el primer administrador:

```
   docker exec -it prestamos_asset_service python -m app.seed_admin
```

5. Abrir http://localhost:5173 e iniciar sesión con
   `admin@concreto.com` / `Admin123!` (cambiar la contraseña cuanto antes).

## Uso diario

Con Docker Desktop abierto:

```
docker compose up -d
```

`--build` solo es necesario cuando cambió el código fuente:

```
docker compose up -d --build asset-service
```

## Apagar

```
docker compose down
```

Conserva los datos. `docker compose down -v` borra también la base de datos.

## Desarrollo local sin Docker para los servicios

PostgreSQL y RabbitMQ siguen en Docker:

```
docker compose up -d postgres rabbitmq
```

Cada servicio con su propio entorno virtual y su propio `.env` (con
`localhost` en lugar de nombres de contenedor):

```
cd services/asset-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Repetir en `services/loan-service` con el puerto 8002, y en `frontend/`
con `npm install` y `npm run dev`.

## Problemas frecuentes

| Síntoma                                         | Causa                                | Solución                            |
| ----------------------------------------------- | ------------------------------------ | ----------------------------------- |
| `docker compose` falla al conectar con el motor | Docker Desktop no está abierto       | Abrirlo y esperar a que cargue      |
| Puerto 5432 ocupado                             | Otro Postgres local                  | Este proyecto usa 5433 externamente |
| Un cambio de código no se refleja               | La imagen conserva la copia anterior | Reconstruir con `--build`           |
| `ModuleNotFoundError` en desarrollo local       | Entorno virtual sin activar          | `venv\Scripts\activate`             |
