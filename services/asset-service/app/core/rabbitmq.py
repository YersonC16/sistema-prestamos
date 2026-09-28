import pika
from app.core.config import settings

def get_rabbitmq_connection():
    params = pika.URLParameters(settings.rabbitmq_url)
    return pika.BlockingConnection(params)