import json
import os
import urllib.request
import urllib.error

def request(method, path, body=None):
    payload = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE+path,data=payload,method=method,
                                 headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=10) as response:
            return response.status,json.load(response)
    except urllib.error.HTTPError as error:
        return error.code,json.load(error)

BASE = os.getenv('BASE_URL','http://localhost:8080')
assert request('GET','/health') == (200,{'status':'ok'})
assert request('GET','/catalog/items')[0] == 200
assert request('GET','/users/1') == (200,{'id':1,'email':'student@example.com'})
status,saved = request('POST','/orders',{'userId':1,'itemId':1,'qty':1})
assert status == 201
assert request('GET','/orders/'+str(saved['id']))[1]['qty'] == 1
assert request('POST','/orders',{'userId':1,'itemId':1,'qty':0})[0] == 422
for path in ['/catalog/openapi.json','/users/openapi.json','/orders/openapi.json']:
    assert request('GET',path)[0] == 200
print('PASS: gateway, catalog, users, orders, validation, OpenAPI')
