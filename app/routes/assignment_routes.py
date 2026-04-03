
from fastapi import APIRouter
import sqlite3

router = APIRouter()

def get_db():
    return sqlite3.connect("stocks.db")

@router.get("/companies")
def get_companies():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT symbol, name FROM companies")
    data = cur.fetchall()
    conn.close()
    return [{"symbol": d[0], "name": d[1]} for d in data]

@router.get("/data/{symbol}")
def get_data(symbol: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT date, close FROM stock_prices WHERE symbol=? ORDER BY date DESC LIMIT 30", (symbol,))
    data = cur.fetchall()
    conn.close()
    return [{"date": d[0], "close": d[1]} for d in data]

@router.get("/summary/{symbol}")
def get_summary(symbol: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT MAX(close), MIN(close), AVG(close) FROM stock_prices WHERE symbol=?", (symbol,))
    data = cur.fetchone()
    conn.close()
    return {"52_week_high": data[0], "52_week_low": data[1], "avg_close": data[2]}

@router.get("/compare")
def compare(symbol1: str, symbol2: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT AVG(close) FROM stock_prices WHERE symbol=?", (symbol1,))
    s1 = cur.fetchone()[0]
    cur.execute("SELECT AVG(close) FROM stock_prices WHERE symbol=?", (symbol2,))
    s2 = cur.fetchone()[0]
    conn.close()
    return {symbol1: s1, symbol2: s2}
