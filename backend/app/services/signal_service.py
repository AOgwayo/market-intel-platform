from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import Signal


class SignalService:
    """Service for managing trading signals."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_latest_signal(self, symbol: str, strategy_name: Optional[str] = None) -> Optional[Signal]:
        """Get the latest signal for a symbol, optionally filtered by strategy."""
        query = self.db.query(Signal).filter(Signal.symbol == symbol)
        
        if strategy_name:
            query = query.filter(Signal.strategy_name == strategy_name)
        
        return query.order_by(desc(Signal.timestamp)).first()
    
    def get_signals(
        self, 
        symbol: Optional[str] = None,
        strategy_name: Optional[str] = None,
        signal_type: Optional[str] = None,
        hours_back: int = 24,
        limit: int = 100
    ) -> List[Signal]:
        """Get signals with optional filters."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = self.db.query(Signal).filter(Signal.timestamp >= cutoff_time)
        
        if symbol:
            query = query.filter(Signal.symbol == symbol)
        if strategy_name:
            query = query.filter(Signal.strategy_name == strategy_name)
        if signal_type:
            query = query.filter(Signal.signal_type == signal_type)
        
        return query.order_by(desc(Signal.timestamp)).limit(limit).all()
    
    def create_signal(
        self,
        symbol: str,
        strategy_name: str,
        signal_type: str,
        confidence: float,
        price: float,
        metadata: Optional[str] = None
    ) -> Signal:
        """Create a new signal."""
        signal = Signal(
            symbol=symbol,
            strategy_name=strategy_name,
            signal_type=signal_type,
            confidence=confidence,
            price=price,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)
        
        return signal