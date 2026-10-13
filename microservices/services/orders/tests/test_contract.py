from fastapi.testclient import TestClient
from main import app

def test_contract():
    client = TestClient(app)
    assert client.get("/health").json() == {"status":"ok"}
    response = client.post('/orders',json={'userId':1,'itemId':1,'qty':2})
    assert response.status_code == 201
    id = response.json()['id']
    assert client.get('/orders/'+str(id)).json() == {'id':id,'userId':1,'itemId':1,'qty':2}
    assert client.post('/orders',json={'userId':1,'itemId':1,'qty':0}).status_code == 422
