from decimal import Decimal
import pytest
from app.domain.product import Product, ValidationError

@pytest.mark.parametrize('name', ['', '   ', 'x'*101, None])
def test_invalid_name(name):
    with pytest.raises(ValidationError):
        Product.create(name, 100)

@pytest.mark.parametrize('price', [-1, 0, 'NaN', 'Infinity', '-Infinity', 'abc', True])
def test_invalid_price(price):
    with pytest.raises(ValidationError):
        Product.create('Desk', price)

def test_valid_product_normalizes_name_and_keeps_decimal():
    product = Product.create(' Desk ', 199.9)
    assert product.name == 'Desk'
    assert product.price == Decimal('199.9')
