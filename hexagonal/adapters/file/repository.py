import csv
import fcntl
import os
from contextlib import contextmanager
from pathlib import Path
from core.domain import Order

class CsvOrderRepository:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.locked():
            if not self.path.exists() or self.path.stat().st_size == 0:
                with self.path.open('w', newline='', encoding='utf-8') as out:
                    csv.writer(out).writerow(['id','sku','qty'])

    @contextmanager
    def locked(self):
        with self.path.with_suffix(self.path.suffix + '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def create(self, order: Order) -> str:
        with self.locked():
            with self.path.open('a', newline='', encoding='utf-8') as out:
                csv.writer(out).writerow([order.id,order.sku,order.qty])
                out.flush()
                os.fsync(out.fileno())
        return order.id

    def get_by_id(self, id: str) -> Order | None:
        with self.locked():
            with self.path.open(newline='', encoding='utf-8') as data:
                for row in csv.DictReader(data):
                    if row['id'] == id:
                        return Order.create(row['sku'], int(row['qty']), row['id'])
        return None

    def ping(self):
        with self.locked():
            with self.path.open(encoding='utf-8') as data:
                if data.readline().strip() != 'id,sku,qty':
                    raise RuntimeError('invalid CSV header')
