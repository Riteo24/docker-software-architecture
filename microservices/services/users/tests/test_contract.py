from fastapi.testclient import TestClient
from main import app

def test_contract():
    client = TestClient(app)
    assert client.get("/health").json() == {"status":"ok"}
    assert client.get('/users/1').json() == {'id':1,'email':'student@example.com'}
    assert client.get('/users/999').status_code == 404
