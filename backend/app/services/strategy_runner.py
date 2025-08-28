from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.database import MarketBar, Signal
from app.strategies.registry import StrategyRegistry


class StrategyRunnerService:
    """Service for running trading strategies."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def load_bars(
        self, 
        symbol: str, 
        timeframe: str = "1d", 
        lookback_days: int = 30
    ) -> pd.DataFrame:
        """Load market bars for a symbol."""
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        
        bars = (
            self.db.query(MarketBar)
            .filter(
                MarketBar.symbol == symbol,
                MarketBar.timeframe == timeframe,
                MarketBar.timestamp >= cutoff_date
            )
            .order_by(MarketBar.timestamp.asc())
            .all()
        )
        
        if not bars:
            # Return empty DataFrame with correct structure
            return pd.DataFrame(columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])
        
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
        
        return pd.DataFrame(data)
    
    def run_strategy(
        self, 
        strategy_name: str, 
        symbol: str, 
        current_price: float,
        **strategy_kwargs
    ) -> Optional[Signal]:
        """Run a strategy for a symbol."""
        try:
            # Get strategy instance
            strategy = StrategyRegistry.get_strategy(strategy_name, **strategy_kwargs)
            
            # Load market data
            bars = self.load_bars(symbol)
            
            # Generate signal
            signal = strategy.generate_signal(symbol, bars, current_price)
            
            # Persist signal if generated
            if signal:
                self.db.add(signal)
                self.db.commit()
                self.db.refresh(signal)
            
            return signal
            
        except Exception as e:
            print(f"Error running strategy {strategy_name} for {symbol}: {e}")
            return None
    
    def run_all_strategies(
        self, 
        symbol: str, 
        current_price: float
    ) -> List[Signal]:
        """Run all registered strategies for a symbol."""
        signals = []
        
        for strategy_name in StrategyRegistry.list_strategies().keys():
            signal = self.run_strategy(strategy_name, symbol, current_price)
            if signal:
                signals.append(signal)
        
        return signals