from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.models.database import MarketBar


router = APIRouter(prefix="/market", tags=["market"])


@router.get("/bars/{symbol}")
def get_market_bars(
    symbol: str,
    timeframe: str = "1d",
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """Get market bars for a symbol."""
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    bars = (
        db.query(MarketBar)
        .filter(
            MarketBar.symbol == symbol,
            MarketBar.timeframe == timeframe,
            MarketBar.timestamp >= cutoff_date
        )
        .order_by(MarketBar.timestamp.asc())
        .all()
    )
    
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "bars": [
            {
                "timestamp": bar.timestamp.isoformat(),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume
            }
            for bar in bars
        ],
        "count": len(bars)
    }


@router.get("/symbols")
def get_available_symbols(db: Session = Depends(get_db)):
    """Get list of available symbols with market data."""
    symbols = (
        db.query(MarketBar.symbol)
        .distinct()
        .all()
    )
    
    return {
        "symbols": [symbol[0] for symbol in symbols],
        "count": len(symbols)
    }