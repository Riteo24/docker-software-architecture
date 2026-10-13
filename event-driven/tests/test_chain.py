from copy import deepcopy
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from jsonschema import ValidationError
from shared.events import event, validate_event
from services.orders.main import create_app
from services.billing.handler import BillingHandler
from services.notifications.handler import NotificationsHandler

def test_order_payment_email_chain_and_replayed_event():
    published = []
    billing = BillingHandler(published.append)
    notifications = NotificationsHandler(published.append)
    order = event('OrderCreated',orderId=str(uuid4()),userId=1,itemId=2,qty=2)
    assert billing.handle(order)
    assert not billing.handle(deepcopy(order))
    replay = deepcopy(order)
    replay['eventId'] = str(uuid4())
    assert not billing.handle(replay)
    assert len(published) == 1
    payment = published[0]
    assert payment['type'] == 'PaymentCaptured' and payment['amount'] == 200.0
    assert notifications.handle(payment)
    assert not notifications.handle(payment)
    assert len(published) == 2 and published[1]['type'] == 'EmailSent'
    for value in [order,*published]:
        validate_event(value)

def test_publication_failure_preserves_payment_event_id_for_retry():
    sent = []
    def publisher(value):
        sent.append(value)
        if len(sent) == 1:
            raise RuntimeError('broker temporarily offline')
    handler = BillingHandler(publisher)
    order = event('OrderCreated',orderId=str(uuid4()),userId=1,itemId=1,qty=1)
    with pytest.raises(RuntimeError):
        handler.handle(order)
    assert not handler.processed_event_ids
    assert handler.handle(order)
    assert sent[0]['eventId'] == sent[1]['eventId']
    assert len(handler.payments) == 1

def test_handlers_ignore_other_event_types():
    billing = BillingHandler(lambda _: None)
    notifications = NotificationsHandler(lambda _: None)
    assert not billing.handle({'type':'EmailSent'})
    assert not notifications.handle({'type':'OrderCreated'})

def test_schema_rejects_invalid_event():
    invalid = event('OrderCreated',orderId=str(uuid4()),userId=1,itemId=1,qty=0)
    with pytest.raises(ValidationError):
        validate_event(invalid)

def test_orders_http_publishes_order_created():
    sent = []
    with TestClient(create_app(sent.append)) as client:
        response = client.post('/orders',json={'userId':1,'itemId':2,'qty':1})
        assert response.status_code == 201
        assert response.json()['id'] == sent[0]['orderId']
        validate_event(sent[0])
        assert client.post('/orders',json={'userId':1,'itemId':2,'qty':0}).status_code == 422

def test_orders_http_returns_503_when_publication_fails():
    def offline(_):
        raise RuntimeError('offline')
    with TestClient(create_app(offline)) as client:
        assert client.post('/orders',json={'userId':1,'itemId':1,'qty':1}).status_code == 503
