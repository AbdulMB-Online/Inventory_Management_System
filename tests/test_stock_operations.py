
"""Test stock updates, sale recording, and transaction rollback."""

import pytest

from inventory_db import add_product
from stock_changes import adjust_stock, record_sale, restock_product


def test_restock_product(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    product_id = add_product(db_connection, "FAN-001", "Ceiling Fan", "Electrical", 1, 7999, 10, 5)

    result = restock_product(db_connection, product_id, 5, "2026-11-01")

    assert result is True
    stock = db_connection.execute("SELECT stock_quantity FROM products "
                                  "WHERE product_id = ?", (product_id,)).fetchone()[0]
    assert stock == 15

    movement = db_connection.execute("SELECT quantity_change, reason FROM stock_movements "
                                     "WHERE product_id = ?", (product_id,)).fetchone()
    assert movement == (5, "restock")

    with pytest.raises(ValueError):
        restock_product(db_connection, product_id, 0)

    with pytest.raises(ValueError):
        restock_product(db_connection, product_id, -5)

    assert db_connection.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 1


def test_adjust_stock(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))
    product_id = add_product(db_connection, "FAN-001", "Ceiling Fan", "Electrical", 1, 7999, 10, 5)

    adjust_stock(db_connection, product_id, -3, "2026-11-01")
    adjust_stock(db_connection, product_id, 2, "2026-11-01")

    stock = db_connection.execute("SELECT stock_quantity FROM products "
                                  "WHERE product_id = ?", (product_id,)).fetchone()[0]
    assert stock == 9

    movements = db_connection.execute("SELECT quantity_change, reason FROM stock_movements "
                                      "ORDER BY movement_id").fetchall()
    assert movements == [(-3, "adjustment"), (2, "adjustment")]

    with pytest.raises(ValueError):
        adjust_stock(db_connection, product_id, -20)

    stock = db_connection.execute("SELECT stock_quantity FROM products WHERE product_id = ?", (product_id,)).fetchone()[0]
    assert stock == 9
    assert db_connection.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 2


def test_record_sale(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))

    hammer_id = add_product(db_connection, "HAM-001", "Hammer", "Tools", 1, 2000, 10, 3)
    drill_id = add_product(db_connection, "DRILL-001", "Drill", "Tools", 1, 5000, 5, 2)

    sale_id = record_sale(db_connection, [(hammer_id, 2), (drill_id, 1)], "2026-11-01")

    assert sale_id == 1

    items = db_connection.execute("SELECT product_id, sale_quantity, unit_price_cents "
                                  "FROM sale_items ORDER BY product_id").fetchall()
    assert items == [(hammer_id, 2, 2000), (drill_id, 1, 5000)]

    stocks = db_connection.execute("SELECT stock_quantity FROM products ORDER BY product_id").fetchall()
    assert stocks == [(8,), (4,)]

    movements = db_connection.execute("SELECT product_id, quantity_change, reason FROM stock_movements "
                                      "ORDER BY product_id").fetchall()
    assert movements == [(hammer_id, -2, "sale"), (drill_id, -1, "sale")]



def test_failed_sale_rollback(db_connection):
    db_connection.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)", (1, "Havells Inc"))

    hammer_id = add_product(db_connection, "HAM-001", "Hammer", "Tools", 1, 2000, 10, 3)
    drill_id = add_product(db_connection, "DRILL-001", "Drill", "Tools", 1, 5000, 3, 2)

    print("BEFORE STOCK:", db_connection.execute("SELECT product_name, stock_quantity FROM products "
                                                 "ORDER BY product_id").fetchall())
    print("BEFORE COUNTS:", db_connection.execute("SELECT (SELECT COUNT(*) FROM sales), "
                                                  "(SELECT COUNT(*) FROM sale_items), "
                                                  "(SELECT COUNT(*) FROM stock_movements)").fetchone())
    print("ATTEMPTED SALE:", [(hammer_id, 2), (drill_id, 5)])
    with pytest.raises(ValueError, match="Insufficient stock") as error:
        record_sale(db_connection, [(hammer_id, 2), (drill_id, 5)], "2026-11-01")
    print("ERROR:", error.value)
    print("AFTER STOCK:", db_connection.execute("SELECT product_name, stock_quantity FROM products "
                                                "ORDER BY product_id").fetchall())
    print("AFTER COUNTS:", db_connection.execute("SELECT (SELECT COUNT(*) FROM sales), "
                                                 "(SELECT COUNT(*) FROM sale_items), "
                                                 "(SELECT COUNT(*) FROM stock_movements)").fetchone())

    stocks = db_connection.execute("SELECT stock_quantity FROM products ORDER BY product_id").fetchall()
    assert stocks == [(10,), (3,)]

    assert db_connection.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0
    assert db_connection.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0] == 0
    assert db_connection.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 0



def test_sale_unknown_product(db_connection):
    with pytest.raises(ValueError, match="Product not found"):
        record_sale(db_connection, [(999, 1)], "2026-11-01")

    assert db_connection.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0
    assert db_connection.execute("SELECT COUNT(*) FROM sale_items").fetchone()[0] == 0
    assert db_connection.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0] == 0
