from unittest.mock import Mock
from decimal import Decimal
import pytest
from app.domain.product import Product, ValidationError
from app.application.usecases import CreateProduct, CreateProductDTO, ListProducts

@pytest.mark.parametrize('dto', [CreateProductDTO('',100),CreateProductDTO('Desk',-1),CreateProductDTO('Desk',0)])
def test_invalid_input_does_not_call_repository(dto):
    repository = Mock()
    with pytest.raises(ValidationError):
        CreateProduct(repository)(dto)
    repository.create.assert_not_called()

def test_create_uses_repository():
    repository = Mock()
    repository.create.return_value = Product.create('Desk',199.9,7)
    result = CreateProduct(repository)(CreateProductDTO('Desk',199.9))
    repository.create.assert_called_once_with(Product.create('Desk',199.9))
    assert result.id == 7
    assert result.price == Decimal('199.9')

def test_list_uses_repository():
    repository = Mock()
    repository.list.return_value = [Product.create('Desk',199.9,7)]
    assert ListProducts(repository)() == repository.list.return_value
    repository.list.assert_called_once_with()
