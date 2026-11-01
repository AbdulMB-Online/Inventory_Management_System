"""Manage inventory stock changes and sales transactions."""

from datetime import UTC, datetime


def restock_product(connection, product_id, quantity, timestamp=None):
    if quantity <= 0:
        raise ValueError("Restock quantity must be greater than zero")
    if timestamp is None:
        timestamp = datetime.now(UTC).isoformat()

    with connection:
        cursor = connection.execute("UPDATE products SET stock_quantity = stock_quantity + ? "
                                    "WHERE product_id = ?", (quantity, product_id))
        if cursor.rowcount == 0:
            raise ValueError("Product not found")
        connection.execute("INSERT INTO stock_movements (product_id, quantity_change, reason, time_stamp) "
                           "VALUES (?, ?, ?, ?)", (product_id, quantity, "restock", timestamp))
    return True


def adjust_stock(connection, product_id, quantity_change, timestamp=None):
    if quantity_change == 0:
        raise ValueError("Adjustment quantity cannot be zero")

    if timestamp is None:
        timestamp = datetime.now(UTC).isoformat()

    with connection:
        product = connection.execute("SELECT stock_quantity FROM products "
                                     "WHERE product_id = ?", (product_id,)).fetchone()
        if product is None:
            raise ValueError("Product not found")
        if product[0] + quantity_change < 0:
            raise ValueError("Adjustment would result in negative stock")
        connection.execute("UPDATE products SET stock_quantity = stock_quantity + ? "
                           "WHERE product_id = ?", (quantity_change, product_id))
        connection.execute("INSERT INTO stock_movements (product_id, quantity_change, reason, time_stamp) "
                           "VALUES (?, ?, ?, ?)", (product_id, quantity_change, "adjustment", timestamp))
    return True


def record_sale(connection, items, timestamp=None):
    if not items:
        raise ValueError("Sale must contain at least one product")

    if timestamp is None:
        timestamp = datetime.now(UTC).isoformat()

    seen_products = set()

    with connection:
        cursor = connection.execute("INSERT INTO sales (sale_date) VALUES (?)", (timestamp,))
        sale_id = cursor.lastrowid

        for product_id, quantity in items:
            if product_id in seen_products:
                raise ValueError("Duplicate product in sale")

            seen_products.add(product_id)
            if quantity <= 0:
                raise ValueError("Sale quantity must be greater than zero")
            product = connection.execute("SELECT price_cents, stock_quantity FROM products "
                                         "WHERE product_id = ?", (product_id,)).fetchone()
            if product is None:
                raise ValueError("Product not found")
            price_cents, stock_quantity = product
            if stock_quantity < quantity:
                raise ValueError("Insufficient stock")

            connection.execute("INSERT INTO sale_items (sale_id, product_id, sale_quantity, unit_price_cents) "
                               "VALUES (?, ?, ?, ?)", (sale_id, product_id, quantity, price_cents))
            connection.execute("UPDATE products SET stock_quantity = stock_quantity - ? "
                               "WHERE product_id = ?", (quantity, product_id))
            connection.execute("INSERT INTO stock_movements (product_id, quantity_change, reason, time_stamp) "
                               "VALUES (?, ?, ?, ?)", (product_id, -quantity, "sale", timestamp))
    return sale_id
