import time
import psycopg
from alembic import command
from alembic.config import Config
from .database import connect

def migrate():
    for attempt in range(30):
        try:
            with connect() as conn:
                conn.execute('SELECT 1')
            break
        except psycopg.OperationalError:
            if attempt == 29:
                raise
            time.sleep(1)
    command.upgrade(Config('alembic.ini'), 'head')

if __name__ == '__main__':
    migrate()
