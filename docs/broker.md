# Patrón Broker — RabbitMQ

## Qué es

Un intermediario de mensajería que permite a los servicios comunicarse
sin conocerse directamente (bajo acoplamiento).

## Por qué se usa aquí

Al crear o devolver un préstamo, el activo debe cambiar de estado en
asset-service. En vez de que loan-service lo llame directamente, publica
un evento y asset-service se suscribe a él.

## Ubicación en el código

| Archivo                                                 | Rol                    |
| ------------------------------------------------------- | ---------------------- |
| `services/loan-service/app/services/event_publisher.py` | Publica eventos        |
| `services/asset-service/app/services/event_consumer.py` | Consume eventos        |
| `app/core/rabbitmq.py` (en ambos)                       | Conexión a RabbitMQ    |
| `docker-compose.yml` (servicio `rabbitmq`)              | El servidor del broker |

## Componentes

- **Exchange:** `prestamos_events` (tipo topic, durable)
- **Routing keys:** `prestamo.creado`, `prestamo.devuelto`
- **Cola:** `asset_status_queue`, ligada con el patrón `prestamo.*`

## Flujo

1. El usuario crea un préstamo y loan-service lo guarda.
2. loan-service publica `prestamo.creado`.
3. asset-service, escuchando en un hilo aparte, recibe el evento.
4. asset-service cambia el activo a `prestado`.

La devolución sigue el mismo camino con `prestamo.devuelto`.

## Manejo de errores

- Si RabbitMQ no responde al publicar, el préstamo igual se guarda y el
  error queda en el log.
- El consumidor reintenta la conexión cada 5 segundos si RabbitMQ no está
  disponible al arrancar o si la conexión se pierde.

## Ventajas y desventajas

Ventajas: bajo acoplamiento, y los mensajes esperan en la cola si el
consumidor está caído.

Desventajas: un componente más que operar, y consistencia eventual (el
estado del activo se actualiza unos milisegundos después de la petición).

## Verificación

Panel en http://localhost:15672 → Queues and Streams: la cola
`asset_status_queue` debe mostrar 1 consumidor mientras asset-service
esté corriendo. Logs en vivo:

```
docker logs -f prestamos_asset_service
```
