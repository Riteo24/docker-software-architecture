from fastapi import FastAPI

app = FastAPI(title='Catalog Service')
ITEMS = [{'id':1,'name':'Desk'},{'id':2,'name':'Chair'}]

@app.get('/health')
def health():
    return {'status':'ok'}

@app.get('/items')
def items():
    return ITEMS
