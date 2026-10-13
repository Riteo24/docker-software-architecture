import json
import os
import time
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from .events import validate_event

TOPIC = os.getenv('KAFKA_TOPIC', 'orders.events')
BROKERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')

def with_retry(factory):
    for attempt in range(40):
        try:
            return factory()
        except KafkaError:
            if attempt == 39:
                raise
            time.sleep(1)

def producer():
    return with_retry(lambda: KafkaProducer(
        bootstrap_servers=BROKERS, acks='all', retries=5, max_in_flight_requests_per_connection=1,
        value_serializer=lambda value: json.dumps(value).encode('utf-8')))

def consumer(group):
    return with_retry(lambda: KafkaConsumer(
        TOPIC, bootstrap_servers=BROKERS, group_id=group, auto_offset_reset='earliest',
        enable_auto_commit=False, max_poll_records=1,
        value_deserializer=lambda data: json.loads(data.decode('utf-8'))))

def publish(client, value):
    validate_event(value)
    client.send(TOPIC, key=value['orderId'].encode(), value=value).get(timeout=15)
