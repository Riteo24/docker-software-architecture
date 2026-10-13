import logging
from shared.events import event, validate_event

class NotificationsHandler:
    def __init__(self, publish):
        self.publish = publish
        self.processed_order_ids = set()
        self.emails = {}

    def handle(self, value):
        if value.get('type') != 'PaymentCaptured':
            return False
        validate_event(value)
        order_id = value['orderId']
        if order_id in self.processed_order_ids:
            return False
        notification = self.emails.setdefault(order_id, event(
            'EmailSent', orderId=order_id, to='customer@example.com'))
        self.publish(notification)
        logging.info('EMAIL_LOG orderId=%s to=%s', order_id, notification['to'])
        self.processed_order_ids.add(order_id)
        return True
