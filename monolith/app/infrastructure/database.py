import os
import psycopg
from sqlalchemy import URL

def db_options():
    return dict(host=os.getenv('DB_HOST', 'db'), port=int(os.getenv('DB_PORT', '5432')),
                dbname=os.getenv('DB_NAME', 'shop'), user=os.getenv('DB_USER', 'shop'),
                password=os.getenv('DB_PASS', 'shop'), connect_timeout=3)

def connect():
    return psycopg.connect(**db_options())

def sqlalchemy_url():
    p = db_options()
    return URL.create('postgresql+psycopg', username=p['user'], password=p['password'],
                      host=p['host'], port=p['port'], database=p['dbname'])
