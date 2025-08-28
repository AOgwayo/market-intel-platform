from fastapi import APIRouter, Query
from ....app.backtest.engine import run_mean_reversion_backtest

router = APIRouter(tags=["backtest"])

@router.get("/backtest/mean_reversion")
def mean_reversion(symbol: str = Query("TEST"), lookback: int = 20):
    result = run_mean_reversion_backtest(symbol=symbol, lookback=lookback)
    return result
