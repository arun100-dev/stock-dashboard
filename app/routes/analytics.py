from fastapi import APIRouter, HTTPException, Query
from app.database import get_connection
import math

router = APIRouter()


@router.get("/compare")
def compare_stocks(
    symbol1: str = Query(..., description="First NSE symbol e.g. INFY"),
    symbol2: str = Query(..., description="Second NSE symbol e.g. TCS"),
    days: int = Query(30, ge=7, le=365)
):
    s1, s2 = symbol1.upper(), symbol2.upper()
    if s1 == s2:
        raise HTTPException(status_code=400, detail="Please provide two different symbols.")

    conn = get_connection()

    def fetch(sym):
        company = conn.execute("SELECT name FROM companies WHERE symbol = ?", (sym,)).fetchone()
        if not company:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Symbol '{sym}' not found.")

        rows = conn.execute("""
            SELECT date, close, daily_return
            FROM stock_prices
            WHERE symbol = ?
            ORDER BY date DESC LIMIT ?
        """, (sym, days)).fetchall()

        data = [dict(r) for r in reversed(rows)]
        if not data:
            return None

        closes = [r["close"] for r in data]
        returns = [r["daily_return"] for r in data if r["daily_return"] is not None]

        base = closes[0]
        normalized = [round((c / base) * 100, 2) for c in closes]

        total_return = round(((closes[-1] - closes[0]) / closes[0]) * 100, 2) if closes[0] else 0
        avg_return = round(sum(returns) / len(returns) * 100, 4) if returns else 0
        volatility = round(
            math.sqrt(sum((r - avg_return/100) ** 2 for r in returns) / len(returns)) * 100, 4
        ) if returns else 0

        return {
            "symbol": sym,
            "company": company["name"],
            "dates": [r["date"] for r in data],
            "closes": closes,
            "normalized": normalized,
            "period_return_pct": total_return,
            "avg_daily_return_pct": avg_return,
            "volatility_pct": volatility,
            "start_price": closes[0],
            "end_price": closes[-1]
        }

    d1 = fetch(s1)
    d2 = fetch(s2)
    conn.close()

    winner = s1 if d1["period_return_pct"] > d2["period_return_pct"] else s2

    return {
        "period_days": days,
        "winner": winner,
        "stock1": d1,
        "stock2": d2,
        "return_difference_pct": round(abs(d1["period_return_pct"] - d2["period_return_pct"]), 2)
    }


@router.get("/gainers-losers")
def top_movers(days: int = Query(7, ge=1, le=90)):
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            sp.symbol,
            c.name,
            c.sector,
            ROUND(((sp.close - sp2.close) / sp2.close) * 100, 2) as period_return,
            sp.close as latest_close,
            sp2.close as start_close
        FROM stock_prices sp
        JOIN companies c ON c.symbol = sp.symbol
        JOIN stock_prices sp2 ON sp2.symbol = sp.symbol
        WHERE sp.date = (SELECT MAX(date) FROM stock_prices WHERE symbol = sp.symbol)
        AND sp2.date = (
            SELECT date FROM stock_prices
            WHERE symbol = sp.symbol
            ORDER BY ABS(JULIANDAY(date) - JULIANDAY('now', ?))
            LIMIT 1
        )
    """, (f"-{days} days",)).fetchall()

    conn.close()

    results = sorted([dict(r) for r in rows], key=lambda x: x["period_return"] or 0, reverse=True)

    return {
        "period_days": days,
        "top_gainers": results[:3],
        "top_losers": results[-3:][::-1],
        "all": results
    }


@router.get("/correlation")
def stock_correlation(
    symbol1: str = Query(...),
    symbol2: str = Query(...),
    days: int = Query(90, ge=30, le=365)
):
    s1, s2 = symbol1.upper(), symbol2.upper()
    conn = get_connection()

    def get_returns(sym):
        rows = conn.execute("""
            SELECT daily_return FROM stock_prices
            WHERE symbol = ? AND daily_return IS NOT NULL
            ORDER BY date DESC LIMIT ?
        """, (sym, days)).fetchall()
        return [r["daily_return"] for r in rows]

    r1 = get_returns(s1)
    r2 = get_returns(s2)
    conn.close()

    n = min(len(r1), len(r2))
    if n < 10:
        raise HTTPException(status_code=400, detail="Not enough data to compute correlation.")

    r1, r2 = r1[:n], r2[:n]
    mean1 = sum(r1) / n
    mean2 = sum(r2) / n

    cov = sum((r1[i] - mean1) * (r2[i] - mean2) for i in range(n)) / n
    std1 = math.sqrt(sum((x - mean1) ** 2 for x in r1) / n)
    std2 = math.sqrt(sum((x - mean2) ** 2 for x in r2) / n)

    correlation = round(cov / (std1 * std2), 4) if std1 and std2 else 0

    if abs(correlation) > 0.7:
        interpretation = "Strongly correlated — tend to move together"
    elif abs(correlation) > 0.4:
        interpretation = "Moderately correlated"
    else:
        interpretation = "Weakly correlated — relatively independent movement"

    return {
        "symbol1": s1,
        "symbol2": s2,
        "days_analyzed": n,
        "pearson_correlation": correlation,
        "interpretation": interpretation
    }
