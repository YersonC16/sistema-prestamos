import json
import threading
import time
from datetime import datetime

import pika

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.asset import Asset, AssetStatus
from app.models.maintenance import Maintenance
from app.services.audit_service import record_audit

EXCHANGE_NAME = "prestamos_events"
QUEUE_NAME = "asset_status_queue"


def _format_date(value: str | None) -> str:
    if not value:
        return "sin fecha"
    try:
        return datetime.fromisoformat(value).strftime("%d/%m/%Y")
    except ValueError:
        return value


def _create_maintenance_from_return(db, asset: Asset, data: dict) -> None:
    location = data.get("maintenance_location") or "interno"
    maintenance = Maintenance(
        asset_id=asset.id,
        asset_name=asset.name,
        location=location,
        assigned_to=data.get("maintenance_assigned_to") if location == "interno" else None,
        provider_name=data.get("maintenance_provider") if location == "externo" else None,
        maintenance_type="correctivo",
        reason=data.get("notes") or "Novedad reportada al devolver el préstamo",
        source="devolucion_con_novedad",
        source_loan_id=data.get("loan_id"),
        created_by=data.get("returned_by") or "Sistema",
    )
    db.add(maintenance)


def _apply_event(routing_key: str, data: dict) -> None:
    db = SessionLocal()
    try:
        asset = db.query(Asset).filter(Asset.id == data.get("asset_id")).first()
        if asset is None:
            print(f"[broker] Evento {routing_key} ignorado: el activo {data.get('asset_id')} no existe")
            return

        actor = data.get("registered_by") or data.get("returned_by") or "Sistema"

        if routing_key == "prestamo.creado":
            asset.status = AssetStatus.PRESTADO
            action = "prestamo_creado"
            detail = (
                f"Prestado a {data.get('responsible_name')}. "
                f"Devolución prevista: {_format_date(data.get('expected_return_date'))}"
            )
        elif routing_key == "prestamo.devuelto":
            late = " (fuera de plazo)" if data.get("was_late") else ""
            if data.get("condition") == "con_novedad":
                asset.status = AssetStatus.MANTENIMIENTO
                action = "devolucion_con_novedad"
                destino = data.get("maintenance_assigned_to") or data.get("maintenance_provider") or "revisión"
                detail = f"Devuelto por {data.get('responsible_name')}{late} con novedad: {data.get('notes')} (enviado a {destino})"
                _create_maintenance_from_return(db, asset, data)
            else:
                asset.status = AssetStatus.DISPONIBLE
                action = "prestamo_devuelto"
                detail = f"Devuelto por {data.get('responsible_name')}{late} en buen estado"
        elif routing_key == "prestamo.atrasado":
            action = "prestamo_atrasado"
            detail = (
                f"Préstamo de {data.get('responsible_name')} vencido el "
                f"{_format_date(data.get('expected_return_date'))} sin devolución"
            )
            actor = "Sistema"
        else:
            return

        db.commit()
        record_audit(db, "asset", asset.id, action, detail, actor, None)
        print(f"[broker] Activo {asset.id}: {action}")
    finally:
        db.close()


def _handle_message(ch, method, properties, body):
    try:
        _apply_event(method.routing_key, json.loads(body))
    except Exception as exc:
        print(f"[broker] Error procesando {method.routing_key}: {exc}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def _connect_and_consume():
    connection = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="prestamo.*")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=_handle_message)
    print("[broker] asset-service escuchando eventos de préstamos...")
    channel.start_consuming()


def start_consumer():
    while True:
        try:
            _connect_and_consume()
        except pika.exceptions.AMQPConnectionError as exc:
            print(f"[broker] No se pudo conectar a RabbitMQ, reintentando en 5s: {exc}")
            time.sleep(5)
        except Exception as exc:
            print(f"[broker] Error inesperado en el consumidor, reintentando en 5s: {exc}")
            time.sleep(5)


def start_consumer_thread():
    threading.Thread(target=start_consumer, daemon=True).start()