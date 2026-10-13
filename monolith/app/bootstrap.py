import os
from app.application.usecases import CreateProduct, ListProducts, CheckHealth
from app.infrastructure.repository import PostgresProductRepository
from app.infrastructure.cache import CachedProductRepository
from app.presentation.http import create_app

repository = PostgresProductRepository()
if os.getenv('REDIS_URL'):
    repository = CachedProductRepository(repository, os.environ['REDIS_URL'])
app = create_app(CreateProduct(repository), ListProducts(repository), CheckHealth(repository))
