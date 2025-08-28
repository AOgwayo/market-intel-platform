from datetime import datetime
import random

def run_mean_reversion_backtest(symbol: str, lookback: int = 20) -> dict:
    random.seed(42)
    days = 30
    prices = [100 + random.uniform(-1, 1) for _ in range(days)]
    pnl = 0.0
    trades = []
    for i in range(lookback, days):
        window = prices[i - lookback : i]
        mean_price = sum(window) / lookback
        last = prices[i - 1]
        direction = 1 if last < mean_price else -1
        ret = direction * (prices[i] - last)
        pnl += ret
        if abs(ret) > 0.2:
            trades.append({"day": i, "pnl": round(ret, 4), "direction": "LONG" if direction == 1 else "SHORT"})
    avg_daily = pnl / days
    return {
        "symbol": symbol,
        "final_pnl": round(pnl, 4),
        "avg_daily_pnl": round(avg_daily, 4),
        "trades": trades,
        "lookback": lookback,
    }
