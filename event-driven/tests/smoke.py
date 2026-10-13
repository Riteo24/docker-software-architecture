import json
import time
import os
import urllib.request
from uuid import uuid4
from kafka import KafkaConsumer
from shared.kafka_bus import producer, publish, TOPIC, BROKERS
from shared.events import validate_event

BASE = os.getenv('BASE_URL','http://orders:5002')
source = KafkaConsumer(TOPIC,bootstrap_servers=BROKERS,group_id='smoke-'+str(uuid4()),
    auto_offset_reset='earliest',enable_auto_commit=False,
    value_deserializer=lambda data:json.loads(data.decode()))
target = producer()
try:
    req = urllib.request.Request(BASE+'/orders',method='POST',
        data=json.dumps({'userId':1,'itemId':2,'qty':1}).encode(),
        headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as response:
        assert response.status == 201
        order_id = json.load(response)['id']
    seen = []
    deadline = time.monotonic()+60
    while time.monotonic() < deadline:
        for messages in source.poll(timeout_ms=1000).values():
            seen += [message.value for message in messages if message.value['orderId']==order_id]
        if any(v['type']=='EmailSent' for v in seen):
            break
    assert [v['type'] for v in seen] == ['OrderCreated','PaymentCaptured','EmailSent'], seen
    for value in seen:
        validate_event(value)
    # Replay exactly the original event twice after the first completed chain.
    publish(target,seen[0])
    publish(target,seen[0])
    deadline = time.monotonic()+10
    while time.monotonic()<deadline:
        for messages in source.poll(timeout_ms=1000).values():
            seen += [m.value for m in messages if m.value['orderId']==order_id]
    assert sum(v['type']=='OrderCreated' for v in seen)==3
    assert sum(v['type']=='PaymentCaptured' for v in seen)==1
    assert sum(v['type']=='EmailSent' for v in seen)==1
    print('PASS: OrderCreated -> PaymentCaptured -> EmailSent; duplicate does not duplicate payment')
finally:
    source.close()
    target.close()
