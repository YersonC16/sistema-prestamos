# Base de datos

## Motor

PostgreSQL 16 en Docker, con volumen persistente `postgres_data`. Los
datos sobreviven a `docker compose down`.

## Esquemas

Una sola base (`prestamos_db`) con un esquema por microservicio:

| Esquema  | Dueño         | Tablas            |
| -------- | ------------- | ----------------- |
| `assets` | asset-service | `assets`, `users` |
| `loans`  | loan-service  | `loans`           |

Cada servicio solo lee y escribe en su propio esquema.

## Tipos ENUM

Los enums viven dentro del esquema de su servicio y guardan los mismos
valores en minúscula que expone la API:

| Tipo                 | Valores                                         |
| -------------------- | ----------------------------------------------- |
| `assets.assettype`   | equipo, herramienta, otro                       |
| `assets.assetstatus` | disponible, prestado, mantenimiento             |
| `assets.userrole`    | administrador, almacenista, personal_autorizado |
| `loans.loanstatus`   | activo, devuelto, atrasado                      |

**Nota técnica:** SQLAlchemy crea los tipos ENUM en `public` si no se
indica el esquema. Por eso cada `Enum(...)` declara `schema=` y
`values_callable=` de forma explícita en los modelos.

## Creación de tablas

Las tablas se crean al arrancar cada servicio
(`Base.metadata.create_all`). No se usan migraciones: si cambia un modelo
existente, hay que recrear la tabla manualmente (aceptable en desarrollo).

## Consultas útiles

```
docker exec -it prestamos_postgres psql -U admin -d prestamos_db -c "\dt assets.*"
docker exec -it prestamos_postgres psql -U admin -d prestamos_db -c "SELECT id, name, status FROM assets.assets;"
docker exec -it prestamos_postgres psql -U admin -d prestamos_db -c "SELECT * FROM loans.loans;"
```

## Pruebas automatizadas

Usan SQLite en memoria. Con `TESTING=true` los modelos omiten los
esquemas, porque SQLite no los soporta.
