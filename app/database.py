import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "data/stocks.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            sector TEXT,
            exchange TEXT DEFAULT 'NSE'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            daily_return REAL,
            ma7 REAL,
            UNIQUE(symbol, date),
            FOREIGN KEY (symbol) REFERENCES companies(symbol)
        )
    """)

    conn.commit()
    conn.close()

    from app.seed import seed_data
    seed_data()
