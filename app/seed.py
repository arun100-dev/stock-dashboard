import yfinance as yf
import pandas as pd
from app.database import get_connection
import logging

logger = logging.getLogger(__name__)

NSE_COMPANIES = {
    "INFY.NS":    ("Infosys Ltd", "IT"),
    "TCS.NS":     ("Tata Consultancy Services", "IT"),
    "RELIANCE.NS":("Reliance Industries", "Energy"),
    "HDFCBANK.NS":("HDFC Bank", "Banking"),
    "WIPRO.NS":   ("Wipro Ltd", "IT"),
    "ICICIBANK.NS":("ICICI Bank", "Banking"),
    "SBIN.NS":    ("State Bank of India", "Banking"),
    "BAJFINANCE.NS":("Bajaj Finance", "Finance"),
    "ASIANPAINT.NS":("Asian Paints", "Consumer"),
    "MARUTI.NS":  ("Maruti Suzuki", "Auto"),
}


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM companies")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    logger.info("Seeding stock data from yfinance...")

    for symbol, (name, sector) in NSE_COMPANIES.items():
        short_symbol = symbol.replace(".NS", "")
        cursor.execute(
            "INSERT OR IGNORE INTO companies (symbol, name, sector) VALUES (?, ?, ?)",
            (short_symbol, name, sector)
        )

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1y")

            if df.empty:
                continue

            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df["daily_return"] = ((df["close"] - df["open"]) / df["open"]).round(6)
            df["ma7"] = df["close"].rolling(7).mean().round(2)
            df = df.dropna(subset=["close"])

            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT OR IGNORE INTO stock_prices
                    (symbol, date, open, high, low, close, volume, daily_return, ma7)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    short_symbol,
                    row["date"],
                    round(row["open"], 2),
                    round(row["high"], 2),
                    round(row["low"], 2),
                    round(row["close"], 2),
                    int(row["volume"]),
                    row["daily_return"],
                    row["ma7"] if pd.notna(row["ma7"]) else None
                ))

            logger.info(f"Seeded {len(df)} rows for {short_symbol}")

        except Exception as e:
            logger.warning(f"Failed to fetch {symbol}: {e}")

    conn.commit()
    conn.close()
    logger.info("Seeding complete.")
