from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from core.domain import Order
from core.usecases import CreateOrder, GetOrder, CheckHealth
from adapters.file.repository import CsvOrderRepository
from adapters.http.routes import create_app

def test_file_adapter_contracts_and_persistence(tmp_path):
    path = str(tmp_path / 'orders.csv')
    repo = CsvOrderRepository(path)
    client = TestClient(create_app(CreateOrder(repo),GetOrder(repo),CheckHealth(repo)))
    assert client.get('/health').json() == {'status':'ok'}
    created = client.post('/orders',json={'sku':'ABC,"Special"','qty':2})
    assert created.status_code == 201
    id = created.json()['id']
    assert client.get('/orders/'+id).json() == {'id':id,'sku':'ABC,"Special"','qty':2}
    assert CsvOrderRepository(path).get_by_id(id).qty == 2
    assert client.get('/orders/missing').status_code == 404
    for qty in [0,-1,True,1.5]:
        assert client.post('/orders',json={'sku':'ABC','qty':qty}).status_code == 422
    assert client.post('/orders',json={'sku':'  ','qty':1}).status_code == 422

def test_concurrent_csv_writes_do_not_lose_rows(tmp_path):
    repo = CsvOrderRepository(str(tmp_path / 'orders.csv'))
    orders = [Order.create('ABC',1) for _ in range(24)]
    with ThreadPoolExecutor(max_workers=6) as pool:
        ids = list(pool.map(repo.create,orders))
    assert len(set(ids)) == 24
    assert all(repo.get_by_id(id) is not None for id in ids)
