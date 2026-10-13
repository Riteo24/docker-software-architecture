from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.domain.product import Product
from app.application.usecases import CreateProduct, ListProducts, CheckHealth
from app.presentation.http import create_app

def test_http_contracts_and_invalid_input():
    repo = Mock()
    repo.create.return_value = Product.create('Desk',199.9,1)
    repo.list.return_value = [repo.create.return_value]
    client = TestClient(create_app(CreateProduct(repo),ListProducts(repo),CheckHealth(repo)))
    assert client.get('/health').json() == {'status':'ok'}
    response = client.post('/products',json={'name':'Desk','price':199.9})
    assert response.status_code == 201
    assert response.json() == {'id':1}
    assert client.get('/products').json() == [{'id':1,'name':'Desk','price':199.9}]
    for body in [{'name':'','price':1},{'name':'   ','price':1},{'name':'Desk','price':0},
                 {'name':'Desk','price':-1},{'name':'x'*101,'price':1}, {'name':'Desk','price':True}]:
        assert client.post('/products',json=body).status_code == 422
    repo.create.assert_called_once()

def test_health_failure_is_503():
    repo = Mock()
    repo.ping.side_effect = RuntimeError('offline')
    client = TestClient(create_app(CreateProduct(repo),ListProducts(repo),CheckHealth(repo)))
    assert client.get('/health').status_code == 503
