import sqlite3
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


@pytest.fixture
def db_connection():
    connection = sqlite3.connect(":memory:")

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            SCHEMA_PATH.read_text(encoding="utf-8")
        )
        yield connection
    finally:
        connection.close()

def test_expected_tables_exist(db_connection):
    rows = db_connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ").fetchall()

    actual_tables = {row[0] for row in rows}

    expected_tables = {
        "suppliers",
        "products",
        "sales",
        "sale_items",
        "stock_movements",
    }

    missing_tables = expected_tables - actual_tables

    assert not missing_tables, (
        f"Missing tables: {sorted(missing_tables)}"
    )


def test_schema_rerun_preserves_supplier(db_connection):
    supplier = (1, "Schema rerun test supplier")

    # Add data before running the schema a second time.
    db_connection.execute(
        """ INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?) """,supplier,)
    db_connection.commit()

    before = db_connection.execute(" SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_id").fetchall()

    assert supplier in before

    # The fixture ran it once; this is the second execution.
    db_connection.executescript(
        SCHEMA_PATH.read_text(encoding="utf-8")
    )

    after = db_connection.execute("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_id").fetchall()

    assert after == before, "Schema rerun changed or erased supplier data"


def test_duplicate_sku_is_refused(db_connection):
    supplier = (1, "Test supplier")
    product = (1, "FAN-CEIL-48", "Ceiling Fan 64 Inch", "Electrical", 1, 9999, 20, 4)
    duplicate_product = (2, "FAN-CEIL-48", "Another ceiling fan", "Electrical", 1, 10999, 10, 2)

    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", supplier)

    insert_product_sql = "INSERT INTO products (product_id, product_sku, product_name, product_category, supplier_id, price_cents, stock_quantity, reorder_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    db_connection.execute(insert_product_sql, product)
    db_connection.commit()

    with pytest.raises(sqlite3.IntegrityError, match=r"UNIQUE constraint failed: products\.product_sku"):
        db_connection.execute(insert_product_sql, duplicate_product)

    rows = db_connection.execute("SELECT product_id, product_sku FROM products WHERE product_sku = ?", ("FAN-CEIL-48",)).fetchall()
    assert rows == [(1, "FAN-CEIL-48")]

def test_product_with_unknown_supplier_is_refused(db_connection):
    product = (2, "FAN-CEIL-41", "Ceiling Fan 64 Inch", "Electrical", 999, 9999, 20, 4)
    insert_product_sql = "INSERT INTO products (product_id, product_sku, product_name, product_category, supplier_id, price_cents, stock_quantity, reorder_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    with pytest.raises(sqlite3.IntegrityError, match=r"FOREIGN KEY constraint failed"):
        db_connection.execute(insert_product_sql, product)

    rows = db_connection.execute("SELECT product_id, product_sku FROM products WHERE product_sku = ?", ("FAN-CEIL-41",)).fetchall()
    assert rows == []

