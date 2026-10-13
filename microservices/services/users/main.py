from fastapi import FastAPI, HTTPException

app = FastAPI(title='Users Service')
USERS = {1:{'id':1,'email':'student@example.com'}}

@app.get('/health')
def health():
    return {'status':'ok'}

@app.get('/users/{id}')
def get_user(id: int):
    if id not in USERS:
        raise HTTPException(404, 'user not found')
    return USERS[id]
