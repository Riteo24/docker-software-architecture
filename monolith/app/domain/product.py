from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

class ValidationError(ValueError):
    pass

@dataclass(frozen=True)
class Product:
    id: int | None
    name: str
    price: Decimal

    @classmethod
    def create(cls, name: str, price: object, id: int | None = None):
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
            raise ValidationError('name must contain 1..100 non-whitespace characters')
        if isinstance(price, bool):
            raise ValidationError('price must be a positive finite number')
        try:
            amount = Decimal(str(price))
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError('price must be a positive finite number') from None
        if not amount.is_finite() or amount <= 0:
            raise ValidationError('price must be greater than zero and finite')
        return cls(id=id, name=name.strip(), price=amount)
