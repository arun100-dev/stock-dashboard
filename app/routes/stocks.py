from fastapi import APIRouter, HTTPException, Query
from app.database import get_connection

router = APIRouter()


@router.get("/companies")
def list_companies():
    conn = get_connection()
    rows = conn.execute("SELECT symbol, name, sector, exchange FROM companies ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/data/{symbol}")
def get_stock_data(symbol: str, days: int = Query(30, ge=7, le=365)):
    symbol = symbol.upper()
    conn = get_connection()

    company = conn.execute("SELECT * FROM companies WHERE symbol = ?", (symbol,)).fetchone()
    if not company:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")

    rows = conn.execute("""
        SELECT date, open, high, low, close, volume, daily_return, ma7
        FROM stock_prices
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT ?
    """, (symbol, days)).fetchall()
    conn.close()

    return {
        "symbol": symbol,
        "company": company["name"],
        "sector": company["sector"],
        "days_requested": days,
        "records": len(rows),
        "data": [dict(r) for r in reversed(rows)]
    }


@router.get("/summary/{symbol}")
def get_stock_summary(symbol: str):
    symbol = symbol.upper()
    conn = get_connection()

    company = conn.execute("SELECT * FROM companies WHERE symbol = ?", (symbol,)).fetchone()
    if not company:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")

    stats = conn.execute("""
        SELECT
            MAX(high) as week52_high,
            MIN(low)  as week52_low,
            ROUND(AVG(close), 2) as avg_close,
            ROUND(AVG(volume), 0) as avg_volume,
            COUNT(*) as total_trading_days
        FROM stock_prices
        WHERE symbol = ?
        AND date >= DATE('now', '-365 days')
    """, (symbol,)).fetchone()

    latest = conn.execute("""
        SELECT close, daily_return, date
        FROM stock_prices
        WHERE symbol = ?
        ORDER BY date DESC LIMIT 1
    """, (symbol,)).fetchone()

    volatility = conn.execute("""
        SELECT ROUND(AVG(ABS(daily_return)), 6) as avg_daily_move
        FROM stock_prices
        WHERE symbol = ?
        AND date >= DATE('now', '-90 days')
    """, (symbol,)).fetchone()

    conn.close()

    return {
        "symbol": symbol,
        "company": company["name"],
        "sector": company["sector"],
        "latest_close": latest["close"] if latest else None,
        "latest_date": latest["date"] if latest else None,
        "latest_return": round(latest["daily_return"] * 100, 2) if latest else None,
        "week52_high": stats["week52_high"],
        "week52_low": stats["week52_low"],
        "avg_close": stats["avg_close"],
        "avg_daily_volume": int(stats["avg_volume"]) if stats["avg_volume"] else None,
        "trading_days_tracked": stats["total_trading_days"],
        "volatility_score": round(volatility["avg_daily_move"] * 100, 4) if volatility["avg_daily_move"] else None
    }
