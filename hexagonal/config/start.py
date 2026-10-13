import os
import time
import psycopg
import uvicorn
from config.settings import Settings

if __name__ == '__main__':
    settings = Settings.from_env()
    if settings.adapter == 'db':
        from adapters.db.repository import PostgresOrderRepository
        for attempt in range(30):
            try:
                PostgresOrderRepository(settings.db).migrate()
                break
            except psycopg.OperationalError:
                if attempt == 29:
                    raise
                time.sleep(1)
    uvicorn.run('config.wiring:app', host='0.0.0.0', port=int(os.getenv('PORT','8081')))
