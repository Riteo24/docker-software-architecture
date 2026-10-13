from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from shared.events import event
from shared.kafka_bus import producer, publish, TOPIC

class OrderRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    userId: int = Field(strict=True, gt=0)
    itemId: int = Field(strict=True, gt=0)
    qty: int = Field(strict=True, gt=0)

def create_app(publisher=None):
    @asynccontextmanager
    async def lifespan(app):
        if publisher is None:
            app.state.producer = producer()
        yield
        if publisher is None:
            app.state.producer.close()

    app = FastAPI(title='Event-driven Orders', lifespan=lifespan)

    @app.get('/health')
    def health():
        if publisher is None and app.state.producer.partitions_for(TOPIC) is None:
            raise HTTPException(503, 'Kafka topic unavailable')
        return {'status':'ok'}

    @app.post('/orders', status_code=201)
    def create_order(body: OrderRequest):
        order_id = str(uuid4())
        message = event('OrderCreated', orderId=order_id, **body.model_dump())
        try:
            if publisher is None:
                publish(app.state.producer, message)
            else:
                publisher(message)
        except Exception:
            raise HTTPException(503, 'event publication failed') from None
        return {'id':order_id}

    return app

app = create_app()
