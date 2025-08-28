from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.services.signal_service import SignalService
from app.models.database import Signal


router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/{symbol}/latest")
def get_latest_signal(
    symbol: str,
    strategy_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get the latest signal for a symbol."""
    signal_service = SignalService(db)
    signal = signal_service.get_latest_signal(symbol, strategy_name)
    
    if not signal:
        raise HTTPException(status_code=404, detail="No signals found")
    
    return {
        "id": signal.id,
        "symbol": signal.symbol,
        "strategy_name": signal.strategy_name,
        "signal_type": signal.signal_type,
        "confidence": signal.confidence,
        "price": signal.price,
        "timestamp": signal.timestamp.isoformat(),
        "metadata": signal.metadata,
        "created_at": signal.created_at.isoformat()
    }


@router.get("/")
def get_signals(
    symbol: Optional[str] = None,
    strategy_name: Optional[str] = None,
    signal_type: Optional[str] = None,
    hours_back: int = 24,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get signals with optional filters."""
    signal_service = SignalService(db)
    signals = signal_service.get_signals(
        symbol=symbol,
        strategy_name=strategy_name,
        signal_type=signal_type,
        hours_back=hours_back,
        limit=limit
    )
    
    return {
        "signals": [
            {
                "id": signal.id,
                "symbol": signal.symbol,
                "strategy_name": signal.strategy_name,
                "signal_type": signal.signal_type,
                "confidence": signal.confidence,
                "price": signal.price,
                "timestamp": signal.timestamp.isoformat(),
                "metadata": signal.metadata,
                "created_at": signal.created_at.isoformat()
            }
            for signal in signals
        ],
        "count": len(signals)
    }