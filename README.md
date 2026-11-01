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

## How to Run the Application

Launch the interactive terminal menu using the seeded database:

```bash
INVENTORY_DB=database/hardwarestore.db python3 main.py
```

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

The following reports use the original sample data loaded by `seed_db.py`, before any manual stock changes. Monetary values are stored as integer cents and displayed in dollars.

### 1. Stock Value by Supplier

Shows the total inventory value for each supplier, ordered from highest to lowest.

| Supplier | Total Stock Value |
|---|---:|
| Havells Inc | $1,953.22 |
| Godrej | $939.40 |
| United Hardware | $754.20 |
| Shaik Systems | $749.67 |

### 2. Low Stock Report

Shows products with stock quantities at or below their reorder levels.

| Product ID | Product Name | Stock | Reorder Level | Units Short |
|---|---|---:|---:|---:|
| 12 | Cabinet Lock 25mm | 10 | 10 | 0 |
| 3 | Extension Board 6 Feet | 8 | 10 | 2 |
| 8 | Smart Door Sensor White | 6 | 10 | 4 |

### 3. Sales by Product

Shows total units sold and historical sales revenue per product, ordered by revenue.

| Product Name | Units Sold | Revenue |
|---|---:|---:|
| Ceiling Fan 48 Inch | 3 | $239.97 |
| PIR Motion Sensor | 3 | $74.97 |
| Padlock 40mm | 3 | $56.97 |
| Claw Hammer 16 Oz | 3 | $47.97 |
| Electrical Switch White | 9 | $44.91 |
| WiFi Relay Module 1 Channel | 2 | $43.98 |
| Stainless Steel Door Handle | 3 | $41.97 |
| Extension Board 6 Feet | 3 | $38.97 |
| Screwdriver Set 6 Piece | 3 | $38.97 |
| Steel Nails Pack 1 Lb | 8 | $31.92 |

### 4. Never Sold Products

Shows products without any sales history.

| Product ID | SKU | Product Name |
|---|---|---|
| 12 | CAB-LOCK-25MM | Cabinet Lock 25mm |
| 8 | DRS-SMART-WHT | Smart Door Sensor White |

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

## Docker

Build the Docker image:

```bash
docker build -t inventory-management:dev .
```

Run the interactive application with a persistent database:

```bash
docker run --rm -it -v "$(pwd)/database:/data" inventory-management:dev
```

### Database Persistence Verification

1. Started the application inside Docker.
2. Restocked product ID `1` by `5` units.
3. Exited the application, removing the container.
4. Started a new container using the same volume mount.
5. Retrieved product ID `1` and confirmed its stock quantity was `25`.

**Result:** Database changes persisted across container restarts.

## Database Backup and Restoration

The application uses SQLite's `connection.backup()` method to create database backups.

### Create a Backup

Run the application and select option `4` (Backup Database).

Enter the destination:

```text
database/hardwarestore_backup.db
```

### Restore a Backup

To restore into a separate database file:

```bash
cp database/hardwarestore_backup.db database/hardwarestore_restored.db
```

Run the application using the restored database:

```bash
INVENTORY_DB=database/hardwarestore_restored.db python3 main.py
```

### Backup Verification Results

Both the original and backup databases passed `PRAGMA integrity_check` with the result `ok`.

| Table | Original | Backup |
|---|---:|---:|
| suppliers | 4 | 4 |
| products | 12 | 12 |
| sales | 8 | 8 |
| sale_items | 20 | 20 |
| stock_movements | 2 | 2 |

All five tables had matching row counts, confirming that the backup preserved the database records.