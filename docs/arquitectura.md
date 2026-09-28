# Arquitectura del sistema

## Visión general

El sistema tiene 2 microservicios independientes, un frontend React +
TypeScript, una base de datos PostgreSQL compartida (con un esquema por
servicio) y un broker RabbitMQ para la comunicación asíncrona. Todo se
ejecuta con Docker Compose.

## Microservicios

| Servicio      | Puerto | Responsabilidad                                | Patrón creacional |
| ------------- | ------ | ---------------------------------------------- | ----------------- |
| asset-service | 8001   | Activos, usuarios, autenticación (JWT + roles) | Factory Method    |
| loan-service  | 8002   | Préstamos, devoluciones, historial             | Builder           |

## Comunicación entre servicios

- **Síncrona (REST):** loan-service consulta a asset-service si un activo
  está disponible antes de crear un préstamo, reenviando el token JWT del
  usuario.
- **Asíncrona (Broker):** loan-service publica `prestamo.creado` y
  `prestamo.devuelto`; asset-service los consume y actualiza el estado
  del activo. Ver `broker.md`.

## Diagrama general

```
React + TypeScript (5173)
   |
   |--- REST + JWT ---> asset-service (8001) ---> schema "assets" (Postgres)
   |--- REST + JWT ---> loan-service (8002)  ---> schema "loans" (Postgres)
                              |
                              |--- eventos ---> RabbitMQ <--- consume --- asset-service
```

## Capas (patrón MVW) por microservicio

| Capa            | Rol MVW  | Carpeta                      | Contenido                                            |
| --------------- | -------- | ---------------------------- | ---------------------------------------------------- |
| Modelos         | Model    | `app/models/`                | Tablas SQLAlchemy y enums                            |
| Schemas         | Model    | `app/schemas/`               | Validación de entrada/salida (Pydantic)              |
| Routers         | View     | `app/routers/`               | Endpoints de la API                                  |
| Services + Core | Whatever | `app/services/`, `app/core/` | Patrones de diseño, broker, configuración, seguridad |

No existe una capa de repositorios separada: las consultas a la base de
datos viven en los routers, porque el tamaño del proyecto no justificaba
una capa adicional.

## Autenticación y roles

JWT firmado con una clave compartida entre ambos servicios. asset-service
emite el token y lo valida contra su tabla de usuarios; loan-service solo
lo decodifica para confirmar que la sesión es válida.

| Rol                 | Permisos                                      |
| ------------------- | --------------------------------------------- |
| Administrador       | Todo: registrar usuarios, activos y préstamos |
| Almacenista         | Registrar activos y préstamos                 |
| Personal autorizado | Consultar y solicitar préstamos               |

## Escalabilidad futura (fuera del alcance actual)

La primera versión se limita a la sede de Concreto. El diseño permite
sumar sedes sin rehacer la arquitectura:

- Agregar un campo `sede_id` a `Asset`, `Loan` y `User`, con filtrado por
  sede en cada consulta.
- El broker ya soporta múltiples colas y routing keys, por lo que los
  eventos por sede pueden enrutarse sin cambiar el patrón.
- Cada esquema (`assets`, `loans`) puede moverse a una base de datos
  independiente sin tocar el código, porque cada servicio solo accede al
  suyo.
- Si el número de servicios o sedes crece, se puede añadir un API Gateway
  para enrutamiento y autenticación centralizados.
- Un servicio de auditoría podría consumir los mismos eventos del broker
  para registrar la trazabilidad de operaciones.

Estas extensiones están documentadas como referencia y no se implementan
en esta versión.
