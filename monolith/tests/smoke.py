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
status, saved = request('POST','/products',{'name':'Desk','price':199.9})
assert status == 201 and type(saved['id']) is int
status, products = request('GET','/products')
assert status == 200 and any(p == {'id':saved['id'],'name':'Desk','price':199.9} for p in products)
assert request('POST','/products',{'name':'','price':-1})[0] == 422
print('PASS: health, create, list, invalid product')
