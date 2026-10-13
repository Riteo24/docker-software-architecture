from threading import Lock
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title='Orders Service')
ORDERS = {}
LOCK = Lock()

class OrderRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    userId: int = Field(strict=True, gt=0)
    itemId: int = Field(strict=True, gt=0)
    qty: int = Field(strict=True, gt=0)

@app.get('/health')
def health():
    return {'status':'ok'}

@app.post('/orders', status_code=201)
def create_order(body: OrderRequest):
    with LOCK:
        id = len(ORDERS) + 1
        ORDERS[id] = {'id':id, **body.model_dump()}
    return {'id':id}

@app.get('/orders/{id}')
def get_order(id: int):
    if id not in ORDERS:
        raise HTTPException(404, 'order not found')
    return ORDERS[id]
