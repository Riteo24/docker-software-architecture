from pathlib import Path
import psycopg
from core.domain import Order

class PostgresOrderRepository:
    def __init__(self, options):
        self.options = options

    def connect(self):
        return psycopg.connect(**self.options)

    def migrate(self):
        sql = Path(__file__).with_name('001_orders.sql').read_text()
        with self.connect() as conn:
            conn.execute(sql)

    def create(self, order: Order) -> str:
        with self.connect() as conn:
            row = conn.execute('INSERT INTO orders(id,sku,qty) VALUES (%s,%s,%s) RETURNING id',
                               (order.id, order.sku, order.qty)).fetchone()
        return str(row[0])

    def get_by_id(self, id: str) -> Order | None:
        # Comparing text also makes an arbitrary unknown HTTP id yield 404, not SQL 500.
        with self.connect() as conn:
            row = conn.execute('SELECT id,sku,qty FROM orders WHERE id::text=%s', (id,)).fetchone()
        return Order.create(row[1], row[2], str(row[0])) if row else None

    def ping(self):
        with self.connect() as conn:
            conn.execute('SELECT 1 FROM orders LIMIT 1')
