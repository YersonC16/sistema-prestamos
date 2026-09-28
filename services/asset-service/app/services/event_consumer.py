import json
import time
import threading
import pika
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.asset import Asset, AssetStatus

EXCHANGE_NAME = "prestamos_events"
QUEUE_NAME = "asset_status_queue"

def _handle_message(ch, method, properties, body):
    data = json.loads(body)
    asset_id = data.get("asset_id")
    routing_key = method.routing_key

    db = SessionLocal()
    try:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if asset:
            if routing_key == "prestamo.creado":
                asset.status = AssetStatus.PRESTADO
            elif routing_key == "prestamo.devuelto":
                asset.status = AssetStatus.DISPONIBLE
            db.commit()
            print(f"[broker] Activo {asset_id} actualizado a estado: {asset.status}")
    finally:
        db.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def _connect_and_consume():
    params = pika.URLParameters(settings.rabbitmq_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="prestamo.*")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=_handle_message)
    print("[broker] asset-service escuchando eventos de préstamos...")
    channel.start_consuming()

def start_consumer():
    """Bucle de reintento: si RabbitMQ no está listo o la conexión se cae,
    se reintenta cada 5 segundos en lugar de morir silenciosamente."""
    while True:
        try:
            _connect_and_consume()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[broker] No se pudo conectar a RabbitMQ, reintentando en 5s: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"[broker] Error inesperado en el consumidor, reintentando en 5s: {e}")
            time.sleep(5)

def start_consumer_thread():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()