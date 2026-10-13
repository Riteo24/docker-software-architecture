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

BASE = os.getenv('BASE_URL','http://localhost:8081')
assert request('GET','/health') == (200,{'status':'ok'})
status, saved = request('POST','/orders',{'sku':'ABC','qty':2})
assert status == 201 and isinstance(saved['id'],str)
assert request('GET','/orders/'+saved['id']) == (200,{'id':saved['id'],'sku':'ABC','qty':2})
assert request('GET','/orders/not-found')[0] == 404
assert request('POST','/orders',{'sku':'ABC','qty':0})[0] == 422
print('PASS: health, create, get, 404, invalid qty')
