from fastapi import APIRouter, HTTPException, Query
from app.database import get_connection
import math

router = APIRouter()


def linear_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_xx = sum(xi ** 2 for xi in x)

    denom = n * sum_xx - sum_x ** 2
    if denom == 0:
        return 0, sum_y / n

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


def r_squared(y_actual, y_predicted):
    mean_y = sum(y_actual) / len(y_actual)
    ss_tot = sum((y - mean_y) ** 2 for y in y_actual)
    ss_res = sum((y_actual[i] - y_predicted[i]) ** 2 for i in range(len(y_actual)))
    if ss_tot == 0:
        return 1.0
    return round(1 - ss_res / ss_tot, 4)


@router.get("/predict/{symbol}")
def predict_price(
    symbol: str,
    horizon_days: int = Query(7, ge=1, le=30, description="Days ahead to forecast")
):
    symbol = symbol.upper()
    conn = get_connection()

    company = conn.execute("SELECT name FROM companies WHERE symbol = ?", (symbol,)).fetchone()
    if not company:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")

    rows = conn.execute("""
        SELECT date, close
        FROM stock_prices
        WHERE symbol = ?
        ORDER BY date ASC
    """, (symbol,)).fetchall()
    conn.close()

    if len(rows) < 30:
        raise HTTPException(status_code=400, detail="Not enough historical data for prediction.")

    closes = [r["close"] for r in rows]
    dates = [r["date"] for r in rows]
    x = list(range(len(closes)))

    slope, intercept = linear_regression(x, closes)
    y_pred = [intercept + slope * xi for xi in x]
    r2 = r_squared(closes, y_pred)

    future_preds = []
    last_idx = x[-1]
    last_date = dates[-1]

    from datetime import datetime, timedelta
    last_dt = datetime.strptime(last_date, "%Y-%m-%d")

    for i in range(1, horizon_days + 1):
        future_x = last_idx + i
        predicted_price = round(intercept + slope * future_x, 2)
        future_date = (last_dt + timedelta(days=i)).strftime("%Y-%m-%d")
        future_preds.append({"date": future_date, "predicted_close": predicted_price})

    current_price = closes[-1]
    final_pred = future_preds[-1]["predicted_close"]
    direction = "UP" if final_pred > current_price else "DOWN"
    change_pct = round(((final_pred - current_price) / current_price) * 100, 2)

    confidence = "High" if r2 > 0.8 else "Medium" if r2 > 0.5 else "Low"

    return {
        "symbol": symbol,
        "company": company["name"],
        "model": "Linear Regression (trend-based)",
        "current_price": current_price,
        "horizon_days": horizon_days,
        "predicted_prices": future_preds,
        "expected_direction": direction,
        "expected_change_pct": change_pct,
        "model_r2_score": r2,
        "confidence": confidence,
        "disclaimer": "This is a simplified trend model for educational purposes only. Not financial advice."
    }
