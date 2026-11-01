# Inventory Management System

## Overview

A Python-based inventory management system for a hardware store using SQLite.

The system supports:
- Adding, retrieving, updating, and deleting products.
- Searching products by name, SKU, or supplier with optional filters.
- Preventing deletion of products with sales history.
- Generating inventory and sales reports.

## Database

The SQLite database contains five related tables:

- `suppliers`
- `products`
- `sales`
- `sale_items`
- `stock_movements`

The database enforces unique SKUs, required fields, foreign key relationships, valid stock movement reasons, and non-negative prices and stock quantities.

Tables use SQLite STRICT mode.

## How to Initialize the Database

Run the following command from the project root:

```bash
python3 database/seed_db.py
```

This creates the database tables and populates them with sample suppliers, products, sales, and sale items.

## How to Run Tests

Run all automated tests:

```bash
python3 -m pytest -v
```

Run Ruff checks:

```bash
python3 -m ruff check .
```
## Expected Report Results

The following reports use the sample data loaded by seed_db.py. All monetary values are stored as integer cents and displayed in dollars with two decimal places.
### 1. Stock Value by Supplier

Returns each supplier's total inventory value, ordered from highest to lowest.

### 2. Low Stock

Returns products at or below their reorder levels, including the number of units short.

### 3. Sales by Product

Returns the total units sold and revenue for each sold product, ordered by revenue.

### 4. Never Sold

Returns products that have no sales history.

## Failed Sale and Transaction Rollback

A sale was attempted for two products:
- Hammer: 2 units requested, 10 available.
- Drill: 5 units requested, 3 available.

The Hammer could be sold, but the Drill had insufficient stock. The entire transaction was rolled back.

### Verification Output

```text
BEFORE STOCK: [('Hammer', 10), ('Drill', 3)]
BEFORE COUNTS: (0, 0, 0)

ATTEMPTED SALE: [(1, 2), (2, 5)]
ERROR: Insufficient stock

AFTER STOCK: [('Hammer', 10), ('Drill', 3)]
AFTER COUNTS: (0, 0, 0)

PASSED
```

The counts represent records in `sales`, `sale_items`, and `stock_movements`, respectively.

The unchanged stock quantities and record counts demonstrate that the failed sale did not save any partial changes.