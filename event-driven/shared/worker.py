import logging
import os
import time
from pathlib import Path
from .kafka_bus import consumer, producer, publish

def run(handler_type, group):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    source = consumer(group)
    target = producer()
    handler = handler_type(lambda value: publish(target, value))
    heartbeat = Path('/tmp/worker-heartbeat')
    try:
        while True:
            batches = source.poll(timeout_ms=1000, max_records=1)
            for messages in batches.values():
                for message in messages:
                    value = message.value
                    try:
                        processed = handler.handle(value)
                    except Exception:
                        logging.exception('Processing failed; restarting without committing offset')
                        # Fail instead of committing a later offset past the unsuccessful record.
                        raise
                    source.commit()
                    if processed:
                        logging.info('PROCESSED type=%s orderId=%s eventId=%s',
                                     value['type'],value['orderId'],value['eventId'])
            heartbeat.write_text(str(time.time()))
    finally:
        source.close()
        target.close()
