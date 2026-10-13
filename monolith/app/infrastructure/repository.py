from app.domain.product import Product
from .database import connect

class PostgresProductRepository:
    def create(self, product: Product) -> Product:
        with connect() as conn:
            row = conn.execute(
                'INSERT INTO products(name, price) VALUES (%s, %s) RETURNING id, name, price',
                (product.name, product.price)).fetchone()
        return Product.create(row[1], row[2], row[0])

    def list(self) -> list[Product]:
        with connect() as conn:
            rows = conn.execute('SELECT id, name, price FROM products ORDER BY id').fetchall()
        return [Product.create(row[1], row[2], row[0]) for row in rows]

    def ping(self):
        with connect() as conn:
            conn.execute('SELECT 1 FROM products LIMIT 1')
