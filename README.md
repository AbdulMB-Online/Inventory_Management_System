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

### Self-Reflection
What I learned:	SQLite transactions, Foreign keys, Multiple operation management, pytest, Docker persistence, and release rollback
What I would improve: Design test cases earlier and try to reduce redundant cases which are already addressed by the schema
What I was Uncertain about: Designing menu for an application of this nature, how do I simplify the menu for maximum usecase coverage with a small learning curve


## Docker Build Verification

The following command completed successfully:

```bash
docker build -t inventory-management:dev .
```

Actual build output:

```text
#0 building with "desktop-linux" instance using docker driver

#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 227B done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 0.2s

#3 [internal] load .dockerignore
#3 transferring context: 179B done
#3 DONE 0.0s

#4 [1/4] FROM docker.io/library/python:3.12-slim@sha256:b18b261e1b4974b4f321451ad5251ded85abb22c2b8b262da527dda1d031ab30
#4 resolve docker.io/library/python:3.12-slim@sha256:b18b261e1b4974b4f321451ad5251ded85abb22c2b8b262da527dda1d031ab30 0.0s done
#4 DONE 0.0s

#5 [internal] load build context
#5 transferring context: 7.84kB done
#5 DONE 0.0s

#6 [2/4] WORKDIR /app
#6 CACHED

#7 [3/4] COPY . .
#7 DONE 0.0s

#8 [4/4] RUN mkdir -p /data
#8 DONE 0.1s

#9 exporting to image
#9 exporting layers 0.0s done
#9 exporting manifest sha256:dc5729fc87f9a7f3ab5b5b299a33e5b1e3e2ae64cfc7835df33a56045791224d done
#9 exporting config sha256:6e0d8bff9fd7fd671357789361ef42a441614654ccea8219e3be73a828582466 done
#9 exporting attestation manifest sha256:b760c8e9e3db13aff7570fa82bf7bcd78444ddb1d2019e52242435f253616dad done
#9 exporting manifest list sha256:227a03b22ec0e12f1fe0faee6931f81e317b4b8f38f3fdd3cbf0d9872c948dae done
#9 naming to docker.io/library/inventory-management:dev done
#9 unpacking to docker.io/library/inventory-management:dev done
#9 DONE 0.0s
```

## Docker Persistence Verification Output

This check used an isolated database loaded from `database/sample_data.py` in a temporary host directory.
Product 1 started with 20 units. In the first container, 5 units were added through Stock Management → Restock Product.
The application then exited, removing that container because of `--rm`. A new container started with the same database mount.

The following command was run once for each container:

```bash
docker run --rm -it --network none --mount type=bind,source=/private/tmp/inventory-persistence-evidence-gq0o7je8,target=/data inventory-management:dev
```

Actual output excerpts from the first container (repeated menus omitted):

```text
product_id: 1
product_sku: FAN-CEIL-48
product_name: Ceiling Fan 48 Inch
product_category: Electrical
supplier_id: 1
price_cents: $79.99
stock_quantity: 20
reorder_level: 5
supplier_name: Havells Inc

Choose an option: Product ID: Quantity to restock: Product restocked successfully.

Thank You!
```

Actual product lookup output from the second container:

```text
product_id: 1
product_sku: FAN-CEIL-48
product_name: Ceiling Fan 48 Inch
product_category: Electrical
supplier_id: 1
price_cents: $79.99
stock_quantity: 25
reorder_level: 5
supplier_name: Havells Inc
```

The new container showed `stock_quantity: 25`, confirming that the restock persisted after the first container was removed.
The database also passed `PRAGMA integrity_check`:

```text
PRAGMA integrity_check: ok
```

## Version Rollback Verification

Verified rollback from Docker image `1.1.0` to `1.0.0` using the same persistent SQLite database.

### Commands

Run version 1.1.0:

```bash
docker run --rm -it -v "$(pwd)/database/rollback-test:/data" inventory-management:1.1.0
```

Roll back to version 1.0.0:

```bash
docker run --rm -it -v "$(pwd)/database/rollback-test:/data" inventory-management:1.0.0
```

### Verification Results

- Version 1.1.0 displayed the low-stock banner.
- Product ID 1 initially had 25 units.
- Adjusted stock by +2 units in version 1.1.0.
- Version 1.0.0 started successfully without the low-stock banner.
- Product ID 1 retained 27 units after rollback.

Database verification output:

```text
Integrity: ok
suppliers 4
products 12
sales 8
sale_items 20
stock_movements 3
```

**Result:** Application rollback preserved inventory changes and database integrity.
