import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def db_connection():
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        schema_path = Path(__file__).resolve().parent / "database" / "schema.sql"
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        yield connection
    finally:
        connection.close()