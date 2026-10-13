from dataclasses import dataclass
from app.domain.ports import ProductRepository
from app.domain.product import Product

@dataclass(frozen=True)
class CreateProductDTO:
    name: str
    price: object

class CreateProduct:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def __call__(self, dto: CreateProductDTO) -> Product:
        product = Product.create(dto.name, dto.price)
        return self.repository.create(product)

class ListProducts:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def __call__(self) -> list[Product]:
        return self.repository.list()

class CheckHealth:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def __call__(self):
        self.repository.ping()
