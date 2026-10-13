from dataclasses import dataclass
from uuid import uuid4

class ValidationError(ValueError):
    pass

class OrderNotFound(LookupError):
    pass

@dataclass(frozen=True)
class Order:
    id: str
    sku: str
    qty: int

    @classmethod
    def create(cls, sku: str, qty: int, id: str | None = None):
        if not isinstance(sku, str) or not sku.strip():
            raise ValidationError('sku cannot be empty')
        if type(qty) is not int or qty <= 0:
            raise ValidationError('qty must be a positive integer')
        return cls(id or str(uuid4()), sku.strip(), qty)
