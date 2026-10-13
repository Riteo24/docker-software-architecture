from .domain import Order, OrderNotFound
from .ports import OrderRepository

class CreateOrder:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def __call__(self, sku: str, qty: int) -> str:
        return self.repository.create(Order.create(sku, qty))

class GetOrder:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def __call__(self, id: str) -> Order:
        order = self.repository.get_by_id(id)
        if order is None:
            raise OrderNotFound(id)
        return order

class CheckHealth:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def __call__(self):
        self.repository.ping()
