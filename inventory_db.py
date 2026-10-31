"""Product management and search operations for the hardware store."""
def add_product(connection, product_sku, product_name, product_category, supplier_id, price_cents, stock_quantity, reorder_level):
    with connection:
        cursor = connection.execute("INSERT INTO products(product_sku, product_name, product_category, supplier_id, price_cents, stock_quantity, reorder_level) VALUES(?,?,?,?,?,?,?)",
            (product_sku, product_name, product_category, supplier_id, price_cents, stock_quantity, reorder_level),)
    return cursor.lastrowid

def get_product(connection, product_id):
    cursor = connection.execute(
        "SELECT p.*, s.supplier_name FROM products p JOIN suppliers s ON p.supplier_id = s.supplier_id WHERE p.product_id = ?", (product_id,),)
    return cursor.fetchone()

def update_product_price(connection, product_id, price_cents):
    with connection:
        cursor = connection.execute("UPDATE products SET price_cents = ? WHERE product_id = ?", (price_cents, product_id),)
    return cursor.rowcount > 0

def delete_product(connection, product_id):
    with connection:
        cursor = connection.execute("SELECT 1 FROM sale_items WHERE product_id = ? LIMIT 1", (product_id,))
        if cursor.fetchone() is not None:
            return False
        cursor = connection.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        return cursor.rowcount > 0

def search_products(connection, search_text=None, category=None, max_price=None, in_stock_only=False, low_stock_only=False):
    sql = "SELECT p.*, s.supplier_name FROM products p JOIN suppliers s ON p.supplier_id = s.supplier_id WHERE 1=1"
    params = []

    if search_text:
        sql += " AND (LOWER(p.product_name) LIKE LOWER(?) OR LOWER(p.product_sku) LIKE LOWER(?) OR LOWER(s.supplier_name) LIKE LOWER(?))"
        term = f"%{search_text}%"
        params.extend([term, term, term])

    if category:
        sql += " AND LOWER(p.product_category) = LOWER(?)"
        params.append(category)

    if max_price is not None:
        sql += " AND p.price_cents <= ?"
        params.append(max_price)

    if in_stock_only:
        sql += " AND p.stock_quantity > 0"

    if low_stock_only:
        sql += " AND p.stock_quantity <= p.reorder_level"

    sql += " ORDER BY p.product_name COLLATE NOCASE"

    return connection.execute(sql, params).fetchall()
