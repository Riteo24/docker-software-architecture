from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from core.domain import ValidationError, OrderNotFound
from core.usecases import CreateOrder, GetOrder, CheckHealth

class OrderRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    sku: str = Field(strict=True, min_length=1)
    qty: int = Field(strict=True, gt=0)

def create_app(create_order: CreateOrder, get_order: GetOrder, health: CheckHealth):
    app = FastAPI(title='Hexagonal Orders')

    @app.get('/health')
    def health_check():
        try:
            health()
        except Exception:
            raise HTTPException(503, 'repository unavailable') from None
        return {'status':'ok'}

    @app.post('/orders', status_code=201)
    def create(body: OrderRequest):
        try:
            return {'id':create_order(body.sku, body.qty)}
        except ValidationError as error:
            raise HTTPException(422, str(error)) from None

    @app.get('/orders/{id}')
    def get(id: str):
        try:
            return asdict(get_order(id))
        except OrderNotFound:
            raise HTTPException(404, 'order not found') from None

    return app
