import sqlite3
from pathlib import Path

import sample_data

folder = Path(__file__).parent
db_path = folder / "hardwarestore.db"
connection = sqlite3.connect(db_path)
connection.execute("PRAGMA foreign_keys = ON")
connection.executescript((folder / "schema.sql").read_text(encoding="utf-8"))
with connection:
    connection.executemany(
        "INSERT INTO suppliers(supplier_id, supplier_name) VALUES (?, ?)",
        sample_data.suppliers,
    )
    connection.executemany(
        "INSERT INTO products(product_id, product_sku, product_name, product_category, supplier_id, price_cents, stock_quantity, reorder_level) VALUES(?,?,?,?,?,?,?,?)",
        sample_data.products,
    )
    connection.executemany(
        "INSERT INTO sales(sale_id, sale_date) VALUES (?, ?)",
        sample_data.sales
    )
    connection.executemany(
        "INSERT INTO sale_items(sale_item_id, sale_id, product_id, sale_quantity, unit_price_cents) VALUES (?, ?, ?, ?, ?)",
        sample_data.sale_items
    )

tables = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
for (table,) in tables:
    count = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    print(f"{table}: {count} rows")
connection.close()

print(f"Created {db_path.name} with sample data")