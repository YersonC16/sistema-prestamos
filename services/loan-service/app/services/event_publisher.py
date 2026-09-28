import json
import pika
from app.core.rabbitmq import get_rabbitmq_connection

EXCHANGE_NAME = "prestamos_events"

def publish_event(routing_key: str, payload: dict) -> None:
    """Publica un evento en el exchange de préstamos. Si RabbitMQ no está
    disponible, no interrumpe la operación principal (el préstamo ya se
    guardó en la base de datos); solo se pierde la notificación async."""
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
        connection.close()
        print(f"[broker] Evento publicado: {routing_key} -> {payload}")
    except Exception as e:
        print(f"[broker] ERROR al publicar evento: {e}")