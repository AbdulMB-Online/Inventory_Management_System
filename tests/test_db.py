import sqlite3
from pathlib import Path

import pytest

from inventory_db import (
    add_product,
    delete_product,
    get_product,
    search_products,
    update_product_price,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


@pytest.fixture
def db_connection():
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        yield connection
    finally:
        connection.close()

def test_expected_tables_exist(db_connection):
    rows = db_connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ").fetchall()
    actual_tables = {row[0] for row in rows}
    expected_tables = {"suppliers","products","sales","sale_items","stock_movements",}
    missing_tables = expected_tables - actual_tables
    assert not missing_tables, (f"Missing tables: {sorted(missing_tables)}")


def test_schema_rerun_preserves_supplier(db_connection):
    supplier = (1, "Schema rerun test supplier")
    db_connection.execute( """ INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?) """,supplier,)
    db_connection.commit()
    before = db_connection.execute(" SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_id").fetchall()
    assert supplier in before
    db_connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
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

def test_add_new_product(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)",(1, "Havells Inc"),)
    new_id = add_product(db_connection, "FAN-CEIL-48", "Ceiling Fan 48 Inch","Electrical", 1, 7999, 20, 5)
    assert new_id == 1
    product = db_connection.execute( "SELECT product_id, product_sku, product_name FROM products WHERE product_id = ?",(new_id,),).fetchone()
    assert product == (1, "FAN-CEIL-48", "Ceiling Fan 48 Inch")

def test_get_existing_product(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    product_id = add_product(db_connection, "FAN-CEIL-48", "Ceiling Fan 48 Inch", "Electrical", 1, 7999, 20, 5)
    product = get_product(db_connection, product_id)
    assert product is not None
    assert product[0] == product_id
    assert product[2] == "Ceiling Fan 48 Inch"
    assert product[8] == "Havells Inc"

def test_update_product_price(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    product_id = add_product(db_connection, "FAN-CEIL-48", "Ceiling Fan 48 Inch", "Electrical", 1, 7999, 20, 5)
    result = update_product_price(db_connection, product_id, 9999)
    assert result is True
    price = db_connection.execute("SELECT price_cents FROM products WHERE product_id = ?", (product_id,)).fetchone()[0]
    assert price == 9999

def test_delete_unsold_product(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    product_id = add_product(db_connection, "FAN-001", "Ceiling Fan", "Electrical", 1, 7999, 20, 5)
    result = delete_product(db_connection, product_id)
    assert result is True
    product = db_connection.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    assert product is None

def test_delete_sold_product(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    product_id = add_product(db_connection, "FAN-001", "Ceiling Fan", "Electrical", 1, 7999, 20, 5)
    db_connection.execute("INSERT INTO sales (sale_id, sale_date) VALUES (?, ?)", (1, "2026-10-31"))
    db_connection.execute("INSERT INTO sale_items (sale_id, product_id, sale_quantity, unit_price_cents) VALUES (?, ?, ?, ?)", (1, product_id, 2, 7999))
    result = delete_product(db_connection, product_id)
    assert result is False
    product = db_connection.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    assert product is not None

def test_search_text(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    add_product(db_connection, "FAN-001", "Ceiling Fan", "Electrical", 1, 7999, 20, 5)
    assert len(search_products(db_connection, search_text="CEILING")) == 1
    assert len(search_products(db_connection, search_text="fan-001")) == 1
    assert len(search_products(db_connection, search_text="hAvElLs")) == 1
    assert len(search_products(db_connection, search_text="xyz")) == 0

def test_search_sql_injection(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    add_product(db_connection, "FAN-001", "Ceiling Fan", "Electrical", 1, 7999, 20, 5)
    results = search_products(db_connection, search_text="'; DROP TABLE products; --")
    assert results == []
    count = db_connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    assert count == 1

def test_search_filters(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    add_product(db_connection, "FAN-001", "Table Fan", "Electrical", 1, 3999, 3, 5)
    add_product(db_connection, "BULB-001", "LED Bulb", "Electrical", 1, 999, 0, 5)
    add_product(db_connection, "HAM-001", "Hammer", "Tools", 1, 1999, 20, 5)

    assert len(search_products(db_connection, category="Electrical")) == 2
    assert len(search_products(db_connection, max_price=2000)) == 2
    assert len(search_products(db_connection, in_stock_only=True)) == 2
    assert len(search_products(db_connection, low_stock_only=True)) == 2

    results = search_products(db_connection, category="Electrical", max_price=5000, in_stock_only=True, low_stock_only=True)

    assert len(results) == 1
    assert results[0][2] == "Table Fan"

    all_products = search_products(db_connection)
    assert [product[2] for product in all_products] == ["Hammer", "LED Bulb", "Table Fan"]