from decimal import Decimal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from app.application.usecases import CreateProduct, CreateProductDTO, ListProducts, CheckHealth
from app.domain.product import ValidationError

class ProductRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(strict=True, min_length=1, max_length=100)
    price: Decimal = Field(gt=0, allow_inf_nan=False)

def create_app(create_product: CreateProduct, list_products: ListProducts, health: CheckHealth):
    api = FastAPI(title='Layered Monolith Products')

    @api.get('/health')
    def health_check():
        try:
            health()
        except Exception:
            raise HTTPException(503, 'database unavailable') from None
        return {'status':'ok'}

    @api.get('/products')
    def products():
        return [{'id':p.id, 'name':p.name, 'price':float(p.price)} for p in list_products()]

    @api.post('/products', status_code=201)
    def create_product_route(body: ProductRequest):
        try:
            saved = create_product(CreateProductDTO(body.name, body.price))
        except ValidationError as error:
            raise HTTPException(422, str(error)) from None
        return {'id':saved.id}

    return api
