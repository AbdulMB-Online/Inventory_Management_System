
from inventory_db import add_product
from reports import (
    low_stock_report,
    never_sold_products,
    sales_by_product,
    stock_value_by_supplier,
)


def test_stock_value_by_supplier(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    add_product(db_connection, "FAN-001", "Ceiling Fan", "Electrical", 1, 2000, 5, 2)
    add_product(db_connection, "BULB-001", "LED Bulb", "Electrical", 1, 1000, 10, 3)

    results = stock_value_by_supplier(db_connection)

    assert results == [("Havells Inc", 20000)]


def test_low_stock_report(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    add_product(db_connection, "FAN-001", "Table Fan", "Electrical", 1, 3999, 3, 5)
    add_product(db_connection, "BULB-001", "LED Bulb", "Electrical", 1, 999, 20, 5)

    results = low_stock_report(db_connection)

    assert len(results) == 1
    assert results[0][2] == "Table Fan"
    assert results[0][8] == 2


def test_sales_by_product(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    product_id = add_product(db_connection, "HAM-001", "Hammer", "Tools", 1, 2000, 10, 3)

    db_connection.execute("INSERT INTO sales (sale_id, sale_date) VALUES (?, ?)", (1, "2026-10-31"))
    db_connection.execute("INSERT INTO sale_items (sale_id, product_id, sale_quantity, unit_price_cents) VALUES (?, ?, ?, ?)", (1, product_id, 2, 1500))

    results = sales_by_product(db_connection)

    assert results == [(product_id, "Hammer", 2, 3000)]


def test_never_sold_products(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))

    sold_id = add_product(db_connection, "FAN-001", "Ceiling Fan", "Electrical", 1, 7999, 10, 3)
    add_product(db_connection, "DRILL-001", "Drill", "Tools", 1, 4999, 5, 2)

    db_connection.execute("INSERT INTO sales (sale_id, sale_date) VALUES (?, ?)", (1, "2026-10-31"))
    db_connection.execute("INSERT INTO sale_items (sale_id, product_id, sale_quantity, unit_price_cents) VALUES (?, ?, ?, ?)", (1, sold_id, 2, 7999))

    results = never_sold_products(db_connection)

    assert len(results) == 1
    assert results[0][2] == "Drill"
