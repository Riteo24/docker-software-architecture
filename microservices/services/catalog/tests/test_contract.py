from fastapi.testclient import TestClient
from main import app

def test_contract():
    client = TestClient(app)
    assert client.get("/health").json() == {"status":"ok"}
    assert client.get('/items').json() == [{'id':1,'name':'Desk'},{'id':2,'name':'Chair'}]
