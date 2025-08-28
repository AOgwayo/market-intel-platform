from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd

from app.database.connection import get_db
from app.services.backtest_engine import BacktestEngine
from app.strategies.registry import StrategyRegistry
from app.models.database import MarketBar


router = APIRouter(prefix="/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    symbol: str = "SPY"
    strategy_name: str = "mean_reversion_v1"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: float = 100000.0


@router.post("/mean_reversion")
def run_mean_reversion_backtest(
    request: BacktestRequest = BacktestRequest(),
    db: Session = Depends(get_db)
):
    """Run a backtest for the mean reversion strategy."""
    
    # Set default date range if not provided
    if not request.end_date:
        end_date = datetime.utcnow()
    else:
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
    
    if not request.start_date:
        start_date = end_date - timedelta(days=365)  # 1 year back
    else:
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
    
    # Load market data
    bars = (
        db.query(MarketBar)
        .filter(
            MarketBar.symbol == request.symbol,
            MarketBar.timeframe == "1d",
            MarketBar.timestamp >= start_date,
            MarketBar.timestamp <= end_date
        )
        .order_by(MarketBar.timestamp.asc())
        .all()
    )
    
    if len(bars) < 30:
        # Generate synthetic data for demo purposes
        synthetic_data = _generate_synthetic_data(request.symbol, start_date, end_date)
        market_data = pd.DataFrame(synthetic_data)
    else:
        # Convert to DataFrame
        data = []
        for bar in bars:
            data.append({
                'timestamp': bar.timestamp,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume
            })
        market_data = pd.DataFrame(data)
    
    # Get strategy
    try:
        strategy = StrategyRegistry.get_strategy("mean_reversion_v1")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Run backtest
    backtest_engine = BacktestEngine(initial_capital=request.initial_capital)
    results = backtest_engine.run_backtest(strategy, market_data, request.symbol)
    
    # Add metadata
    results.update({
        "strategy_name": "mean_reversion_v1",
        "symbol": request.symbol,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "initial_capital": request.initial_capital,
        "data_points": len(market_data),
        "backtest_completed_at": datetime.utcnow().isoformat()
    })
    
    return results


def _generate_synthetic_data(symbol: str, start_date: datetime, end_date: datetime):
    """Generate synthetic market data for demo purposes."""
    import numpy as np
    
    # Generate daily dates
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate synthetic price data (random walk with trend)
    np.random.seed(42)  # For reproducible results
    initial_price = 100.0
    returns = np.random.normal(0.001, 0.02, len(dates))  # Daily returns
    prices = [initial_price]
    
    for i in range(1, len(dates)):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(new_price)
    
    # Generate OHLC data
    data = []
    for i, (date, close_price) in enumerate(zip(dates, prices)):
        # Generate realistic OHLC from close price
        volatility = 0.015
        high = close_price * (1 + np.random.uniform(0, volatility))
        low = close_price * (1 - np.random.uniform(0, volatility))
        
        if i == 0:
            open_price = close_price
        else:
            open_price = prices[i-1] * (1 + np.random.normal(0, 0.005))
        
        volume = np.random.uniform(1000000, 10000000)
        
        data.append({
            'timestamp': date,
            'open': round(open_price, 2),
            'high': round(max(open_price, high, close_price), 2),
            'low': round(min(open_price, low, close_price), 2),
            'close': round(close_price, 2),
            'volume': round(volume)
        })
    
    return data