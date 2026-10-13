import sys
from uuid import uuid4
from shared.events import event
from shared.kafka_bus import producer, publish

if __name__ == '__main__':
    order_id = sys.argv[1] if len(sys.argv) > 1 else str(uuid4())
    message = event('OrderCreated', orderId=order_id, userId=1, itemId=2, qty=1)
    client = producer()
    try:
        publish(client, message)
        publish(client, message)
        print('Published the same event twice, orderId='+order_id)
    finally:
        client.close()
