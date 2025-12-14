import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[2] / "DATA"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database (creates file if missing).
    Returns a sqlite3.Connection object.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
