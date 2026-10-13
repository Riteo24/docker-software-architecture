from decimal import Decimal
from shared.events import event, validate_event

class BillingHandler:
    def __init__(self, publish):
        self.publish = publish
        self.processed_event_ids = set()
        self.processed_order_ids = set()
        self.payments = {}

    def handle(self, value):
        if value.get('type') != 'OrderCreated':
            return False
        validate_event(value)
        event_id, order_id = value['eventId'], value['orderId']
        if event_id in self.processed_event_ids or order_id in self.processed_order_ids:
            return False
        # A deterministic teaching tariff; this is a simulated payment, no external charge.
        amount = Decimal('100.00') * value['qty']
        # Retain one payment event even if publication needs to be retried.
        payment = self.payments.setdefault(order_id, event(
            'PaymentCaptured', orderId=order_id, amount=float(amount)))
        self.publish(payment)
        self.processed_event_ids.add(event_id)
        self.processed_order_ids.add(order_id)
        return True
