
"""Terminal menu for the hardware store inventory management system."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

import inventory_db
import reports
import stock_changes


def connect():
    db_path = Path(os.environ.get("INVENTORY_DB") or Path(__file__).with_name("hardwarestore.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    schema_path = Path(__file__).parent / "database" / "schema.sql"
    connection.executescript(schema_path.read_text(encoding="utf-8"))
    return connection


def read_integer(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a whole number.")


def read_optional_integer(prompt):
    while True:
        value = input(prompt).strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            print("Invalid input. Please enter a whole number.")


def read_yes_no(prompt):
    while True:
        choice = input(prompt).strip().lower()
        if choice in ("y", "yes"):
            return True
        if choice in ("n", "no", ""):
            return False
        print("Please enter y or n.")


def display_rows(rows):
    if not rows:
        print("No records found.")
        return

    for row in rows:
        print("-" * 40)
        for key, value in dict(row).items():
            if key.endswith("_cents"):
                print(f"{key}: ${value / 100:.2f}")
            else:
                print(f"{key}: {value}")


def product_menu(connection):
    while True:
        print("\n===== PRODUCT MANAGEMENT =====")
        print("1. Add Product")
        print("2. Get Product")
        print("3. Search Products")
        print("4. Update Product Price")
        print("5. Delete Product")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            return

        try:
            if choice == "1":
                sku = input("SKU: ").strip()
                name = input("Product name: ").strip()
                category = input("Category: ").strip()
                supplier_id = read_integer("Supplier ID: ")
                price = read_integer("Price in cents: ")
                stock = read_integer("Stock quantity: ")
                reorder = read_integer("Reorder level: ")

                product_id = inventory_db.add_product(connection, sku, name, category, supplier_id, price, stock, reorder)
                print(f"Product added successfully. ID: {product_id}")

            elif choice == "2":
                product_id = read_integer("Product ID: ")
                product = inventory_db.get_product(connection, product_id)
                display_rows([product] if product else [])

            elif choice == "3":
                text = input("Search text (optional): ").strip()
                category = input("Category (optional): ").strip()
                max_price = read_optional_integer("Maximum price in cents (optional): ")
                in_stock = read_yes_no("In stock only? (y/n): ")
                low_stock = read_yes_no("Low stock only? (y/n): ")

                results = inventory_db.search_products(
                    connection, text or None, category or None,
                    max_price, in_stock, low_stock
                )
                display_rows(results)

            elif choice == "4":
                product_id = read_integer("Product ID: ")
                price = read_integer("New price in cents: ")
                updated = inventory_db.update_product_price(connection, product_id, price)
                print("Price updated." if updated else "Product not found.")

            elif choice == "5":
                product_id = read_integer("Product ID: ")
                deleted = inventory_db.delete_product(connection, product_id)
                print("Product deleted." if deleted else "Product not found or has sales history.")

            else:
                print("Invalid menu option.")

        except (ValueError, sqlite3.Error) as error:
            print(f"Operation failed: {error}")


def stock_menu(connection):
    while True:
        print("\n===== STOCK MANAGEMENT =====")
        print("1. Restock Product")
        print("2. Adjust Stock")
        print("3. Record Sale")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            return

        try:
            if choice == "1":
                product_id = read_integer("Product ID: ")
                quantity = read_integer("Quantity to restock: ")

                stock_changes.restock_product(connection, product_id, quantity)
                print("Product restocked successfully.")

            elif choice == "2":
                product_id = read_integer("Product ID: ")
                quantity = read_integer("Adjustment (+/-): ")

                stock_changes.adjust_stock(connection, product_id, quantity)
                print("Stock adjusted successfully.")

            elif choice == "3":
                count = read_integer("Number of different products: ")
                items = []

                for i in range(max(count, 0)):
                    print(f"\nProduct {i + 1}")
                    product_id = read_integer("Product ID: ")
                    quantity = read_integer("Quantity: ")
                    items.append((product_id, quantity))

                sale_id = stock_changes.record_sale(connection, items)
                print(f"Sale recorded successfully. Sale ID: {sale_id}")

            else:
                print("Invalid menu option.")

        except (ValueError, sqlite3.Error) as error:
            print(f"Operation failed: {error}")


def reports_menu(connection):
    while True:
        print("\n===== REPORTS =====")
        print("1. Stock Value by Supplier")
        print("2. Low Stock")
        print("3. Sales by Product")
        print("4. Never Sold Products")
        print("0. Back")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            return

        if choice == "1":
            display_rows(reports.stock_value_by_supplier(connection))
        elif choice == "2":
            display_rows(reports.low_stock_report(connection))
        elif choice == "3":
            display_rows(reports.sales_by_product(connection))
        elif choice == "4":
            display_rows(reports.never_sold_products(connection))
        else:
            print("Invalid menu option.")


def backup_database(connection):
    backup_path = Path(input("Backup file path (e.g., backup.db): ").strip())

    if str(backup_path) in ("", "."):
        raise ValueError("Backup path is required")

    source_path = Path(os.environ.get("INVENTORY_DB") or Path(__file__).with_name("hardwarestore.db"))

    if backup_path.resolve() == source_path.resolve():
        raise ValueError("Backup must have a different path from the database")

    backup_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(backup_path)) as backup_connection:
        connection.backup(backup_connection)

    print(f"Database backed up successfully to {backup_path}")


def main():
    with closing(connect()) as connection:
        while True:
            low_stock_count = reports.count_low_stock(connection)

            if low_stock_count > 0:
                print(f"\nLOW STOCK ALERT: {low_stock_count} products need restocking!")
            print("\n========== INVENTORY MANAGEMENT SYSTEM ==========")
            print("1. Product Management")
            print("2. Stock Management")
            print("3. Reports")
            print("4. Backup Database")
            print("0. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                product_menu(connection)
            elif choice == "2":
                stock_menu(connection)
            elif choice == "3":
                reports_menu(connection)
            elif choice == "4":
                try:
                    backup_database(connection)
                except (ValueError, sqlite3.Error, OSError) as error:
                    print(f"Backup failed: {error}")
            elif choice == "0":
                print("\nThank You!")
                break
            else:
                print("Invalid menu option.")



if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nThank You!")
