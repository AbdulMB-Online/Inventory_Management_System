"""Inventory and sales reports for the hardware store."""

def stock_value_by_supplier(connection):
    return connection.execute("SELECT s.supplier_name, COALESCE(SUM(p.price_cents * p.stock_quantity), 0) AS stock_value_cents FROM suppliers s "
                              "LEFT JOIN products p ON s.supplier_id = p.supplier_id GROUP BY s.supplier_id, s.supplier_name "
                              "ORDER BY stock_value_cents DESC").fetchall()


def low_stock_report(connection):
    return connection.execute("SELECT p.*, (p.reorder_level - p.stock_quantity) AS units_short FROM products p "
                              "WHERE p.stock_quantity <= p.reorder_level ORDER BY p.product_name").fetchall()


def sales_by_product(connection):
    return connection.execute("SELECT p.product_id, p.product_name, SUM(si.sale_quantity) AS units_sold, "
                              "SUM(si.sale_quantity * si.unit_price_cents) AS revenue_cents "
                              "FROM products p JOIN sale_items si ON p.product_id = si.product_id "
                              "GROUP BY p.product_id, p.product_name ORDER BY revenue_cents DESC").fetchall()


def never_sold_products(connection):
    return connection.execute("SELECT p.* FROM products p "
                              "WHERE NOT EXISTS (SELECT 1 FROM sale_items si WHERE si.product_id = p.product_id) "
                              "ORDER BY p.product_name").fetchall()
def count_low_stock(connection):
    return connection.execute(
        "SELECT COUNT(*) FROM products WHERE stock_quantity <= reorder_level"
    ).fetchone()[0]