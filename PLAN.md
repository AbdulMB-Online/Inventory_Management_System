# GOAL:
This project aims to create a terminal based Inventory Management System for a small hardware store using Python and SQLite.

# REQUIREMENTS:
| **ID** | **Requirement** | **How to Verify** |
| --- | --- | ---|
| REQ 1 | Create five related SQLite tables with contraints. | Verify Schema, Foreign keys and constraints |
| REQ 2 | SEED 4 SUPPLOERS, 12 PRODUCTS, 5 SALES AND 12 SALE ITEMS | Check table row counts and sample data |
| REQ 3 | Add, retrieve and delete products | Test valid and invalid operations |
| REQ 4 | Search products using text and combined filters | Test case-insensitive searches and SQL injection safety |
| REQ 5 | Generate four inventory and sales reports | Compare results with sample data | 
| REQ 6 | Restock and adjust inventory with movement logs | Verify stock changes and reject invalid quantitites | 
| REQ 7 | Record sales as atomic transaction } Verify stock changes and reject invalid quantities |
| REQ 8 | Provide a terminal based menu with input validation | Test menu options and invalid inputs |
| REQ 9 | Run the applicaiton in Docker with persistent storage | Restart containers using the same volume |
| REQ 10 | Support backup, restoration and version rollback | Verify db integrity and preserved row counts |
| REQ 11 | Release 2 versions | Verify Git tags, Docker tags and low-stock banner |
| REQ 12 | Pass automated tests, ruff and CI | Run pytest,ruff and docker-based CI tests |

# COMPONENTS:
schema.sql

db.py

seed_db.py

products.py

reports.py

inventory.py

main.py

Dockerfile and CI

# Database Design

### Suppliers
Stores information about suppliers who provide products to the hardware store.

- **Columns:** supplier_id, name
- **Constraints:** supplier_id is the primary key; name is required.
- **Relationship:** One supplier can supply multiple products.

### Products
Stores product details, prices, and current stock quantities.

- **Columns:** product_id, sku, name, category, supplier_id, price_cents, quantity_in_stock, reorder_level
- **Constraints:** product_id is the primary key; SKU must be unique; all fields are required; price, stock quantity, and reorder level cannot be negative.
- **Relationship:** Each product belongs to one supplier and can appear in multiple sales and stock movements.

### Sales
Stores information about each sale made by the store.

- **Columns:** sale_id, sale_date
- **Constraints:** sale_id is the primary key; sale_date is required.
- **Relationship:** One sale can contain multiple sale items.

### Sale Items
Stores individual products included in each sale, along with their quantities and prices at the time of purchase.

- **Columns:** sale_item_id, sale_id, product_id, quantity, unit_price_cents
- **Constraints:** sale_item_id is the primary key; all fields are required; quantity must be positive; unit price cannot be negative; the combination of sale_id and product_id must be unique.
- **Relationship:** Each sale item references one sale and one product.

### Stock Movements
Tracks inventory changes caused by restocking, adjustments, or sales.

- **Columns:** movement_id, product_id, quantity_change, reason, timestamp
- **Constraints:** movement_id is the primary key; all fields are required; quantity_change must be nonzero; reason must be restock, adjustment, or sale.
- **Relationship:** Each stock movement belongs to one product.


# PUBLIC FUNCTIONS

| Function | Inputs | Return Value |
|---|---|---|
| connect | Database path | SQLite connection |
| initialize_database | Connection | None |
| seed_database | Connection | Row counts |
| add_product | Connection, product details | New product ID |
| get_product | Connection, product ID | Product details or None |
| update_price | Connection, product ID, new price | Boolean |
| delete_product | Connection, product ID | Boolean or error |
| search_products | Connection, search text, optional filters | Matching product rows |
| stock_value_by_supplier | Connection | Supplier stock value rows |
| low_stock_report | Connection | Low-stock product rows |
| sales_by_product | Connection | Product sales and revenue rows |
| never_sold_report | Connection | Never-sold product rows |
| restock_product | Connection, product ID, quantity, timestamp | None or error |
| adjust_stock | Connection, product ID, signed quantity, timestamp | None or error |
| record_sale | Connection, product-quantity pairs, timestamp | Sale ID |
| backup_database | Connection, destination path | None or error |
| count_low_stock | Connection | Number of low-stock products |

# TRANSACTION PLAN

### Restock

1. Validate the product and ensure the quantity is positive.
2. Increase the product's stock.
3. Record a restock movement.
4. Commit if successful.
5. If anything fails, roll back the stock increase and movement.

### Adjust Stock

1. Validate the product and adjustment amount.
2. Calculate the updated stock quantity.
3. Reject adjustments that would make stock negative.
4. Update stock and record an adjustment movement.
5. If anything fails, roll back both changes.

### Record Sale

1. Validate products, quantities, and duplicate entries.
2. Create a sale record.
3. Verify that each product exists and has sufficient stock.
4. Record each sale item at its current price.
5. Reduce the stock quantity for each product.
6. Record a sale movement for each item.
7. Commit only if all operations succeed.
8. If any step fails, roll back the sale, sale items,
   stock deductions, and movements.

# RELEASE PLAN

| PR | Branch | Feature |
|---|---|---|
| 1 | feature/database-and-seed | Schema and seed data |
| 2 | feature/products-and-search | Product CRUD and search |
| 3 | feature/reports | Four reports |
| 4 | feature/stock-and-sales | Stock transactions and sales |
| 5 | feature/menu-and-container | Terminal menu, Docker, backup, and CI |
| 6 | feature/low-stock-banner | Low-stock banner |

### Version 1.0.0

- Release the working inventory management application after PR 5.
- Create Git tag v1.0.0.
- Build Docker image tag 1.0.0.
- Document the release in CHANGELOG.md.

### Version 1.1.0

- Add a low-stock product count banner to the terminal menu.
- Implement the change on feature/low-stock-banner.
- Create Git tag v1.1.0.
- Build Docker image tag 1.1.0.
- Update CHANGELOG.md.

### Rollback Plan

- Run version 1.1.0 using a persistent Docker volume.
- Switch back to Docker image 1.0.0 using the same volume.
- Verify that products, sales, and stock quantities remain unchanged.

       