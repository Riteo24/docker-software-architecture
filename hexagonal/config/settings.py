from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    adapter: str
    csv_path: str
    db: dict

    @classmethod
    def from_env(cls):
        adapter = os.getenv('REPO_ADAPTER', 'db')
        if adapter not in {'db', 'file'}:
            raise ValueError('REPO_ADAPTER must be db or file')
        return cls(adapter, os.getenv('CSV_PATH', '/data/orders.csv'), {
            'host':os.getenv('DB_HOST','db'), 'port':int(os.getenv('DB_PORT','5432')),
            'dbname':os.getenv('DB_NAME','shop'), 'user':os.getenv('DB_USER','shop'),
            'password':os.getenv('DB_PASS','shop'), 'connect_timeout':3})
