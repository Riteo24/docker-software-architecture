from unittest.mock import Mock
from redis import RedisError
from app.domain.product import Product
from app.infrastructure.cache import CachedProductRepository

def test_cache_ttl_and_invalidation():
    repository = Mock()
    product = Product.create('Desk',100,1)
    repository.list.return_value = [product]
    repository.create.return_value = product
    cached = CachedProductRepository(repository,'redis://localhost')
    cached.cache = Mock()
    cached.cache.get.side_effect = [b'3',None,b'4',b'[{"id":1,"name":"Desk","price":"100"}]']
    assert cached.list() == [product]
    assert cached.cache.setex.call_args.args[:2] == ('products:list:3',30)
    cached.create(product)
    cached.cache.incr.assert_called_once_with('products:version')
    assert cached.list() == [product]
    repository.list.assert_called_once()

def test_cache_outage_falls_back_to_database():
    repository = Mock()
    repository.list.return_value = []
    cached = CachedProductRepository(repository,'redis://localhost')
    cached.cache = Mock()
    cached.cache.get.side_effect = RedisError('offline')
    assert cached.list() == []
