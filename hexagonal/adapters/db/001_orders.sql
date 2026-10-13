CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    sku TEXT NOT NULL CHECK (length(btrim(sku)) > 0),
    qty INTEGER NOT NULL CHECK (qty > 0)
);
