CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT UNIQUE NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_sku TEXT UNIQUE NOT NULL,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    supplier_id INTEGER NOT NULL,
    price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0),
    reorder_level INTEGER NOT NULL CHECK(reorder_level >= 0),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
) STRICT;

CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY,
    sale_date TEXT NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS sale_items (
    sale_item_id INTEGER PRIMARY KEY,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    sale_quantity INTEGER NOT NULL CHECK(sale_quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0),
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) STRICT ;

CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    quantity_change INTEGER NOT NULL CHECK(quantity_change != 0),
    reason TEXT NOT NULL,
    time_stamp TEXT NOT NULL,
    CHECK ((reason = 'restock' AND quantity_change > 0) OR (reason = 'sale' AND quantity_change < 0)
    OR (reason = 'adjustment' AND quantity_change != 0)),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) STRICT ;

CREATE INDEX IF NOT EXISTS idx_sale_items_product_id ON sale_items(product_id);
