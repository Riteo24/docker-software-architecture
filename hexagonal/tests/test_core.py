from unittest.mock import Mock
import pytest
from core.domain import Order, ValidationError, OrderNotFound
from core.usecases import CreateOrder, GetOrder

@pytest.mark.parametrize('sku,qty',[('',1),('  ',1),('ABC',0),('ABC',-2),('ABC',1.5),('ABC',True)])
def test_invalid_order_never_reaches_repository(sku,qty):
    repository = Mock()
    with pytest.raises(ValidationError):
        CreateOrder(repository)(sku,qty)
    repository.create.assert_not_called()

def test_create_uses_port():
    repository = Mock()
    repository.create.return_value = 'saved-id'
    assert CreateOrder(repository)('ABC',2) == 'saved-id'
    saved = repository.create.call_args.args[0]
    assert saved.sku == 'ABC' and saved.qty == 2 and saved.id

def test_get_uses_port():
    repository = Mock()
    repository.get_by_id.return_value = Order.create('ABC',2,'order-id')
    assert GetOrder(repository)('order-id').sku == 'ABC'
    repository.get_by_id.assert_called_once_with('order-id')

def test_missing_order():
    repository = Mock()
    repository.get_by_id.return_value = None
    with pytest.raises(OrderNotFound):
        GetOrder(repository)('missing')
