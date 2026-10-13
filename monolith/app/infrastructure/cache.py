import json
import logging
from redis import Redis, RedisError
from app.domain.product import Product
from app.domain.ports import ProductRepository

class CachedProductRepository:
    # Separate keys per version prevent stale reads racing a successful create.
    def __init__(self, delegate: ProductRepository, url: str):
        self.delegate = delegate
        self.cache = Redis.from_url(url, socket_timeout=1, socket_connect_timeout=1)

    def create(self, product):
        saved = self.delegate.create(product)
        try:
            self.cache.incr('products:version')
        except RedisError:
            logging.warning('Redis unavailable; SQL remains the source of truth')
        return saved

    def list(self):
        try:
            version = self.cache.get('products:version') or b'0'
            key = 'products:list:' + version.decode()
            payload = self.cache.get(key)
            if payload is not None:
                return [Product.create(p['name'], p['price'], p['id']) for p in json.loads(payload)]
            products = self.delegate.list()
            self.cache.setex(key, 30, json.dumps([
                {'id':p.id, 'name':p.name, 'price':str(p.price)} for p in products]))
            return products
        except RedisError:
            return self.delegate.list()

    def ping(self):
        self.delegate.ping()
