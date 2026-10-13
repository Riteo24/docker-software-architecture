from alembic import op

revision = '001_products'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        CREATE TABLE products (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL CHECK (char_length(btrim(name)) BETWEEN 1 AND 100),
            price NUMERIC NOT NULL CHECK (price > 0 AND price <> 'NaN'::numeric
                AND price <> 'Infinity'::numeric AND price <> '-Infinity'::numeric)
        )
    """)

def downgrade():
    op.execute('DROP TABLE products')
