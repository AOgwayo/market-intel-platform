from datetime import datetime
from typing import Dict, Optional, Any

import pandas as pd
import numpy as np
import ta

from app.strategies.base import BaseStrategy
from app.models.database import Signal


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using Bollinger Bands."""
    
    def __init__(self, window: int = 20, num_std: float = 2.0):
        super().__init__("mean_reversion", "v1")
        self.window = window
        self.num_std = num_std
        
    def generate_signal(
        self, 
        symbol: str, 
        bars: pd.DataFrame, 
        current_price: float
    ) -> Optional[Signal]:
        """Generate mean reversion signal."""
        if not self.validate_data(bars) or len(bars) < self.window:
            return None
            
        # Calculate Bollinger Bands
        closes = bars['close'].values
        sma = ta.trend.sma_indicator(pd.Series(closes), window=self.window)
        std = pd.Series(closes).rolling(window=self.window).std()
        
        upper_band = sma + (self.num_std * std)
        lower_band = sma - (self.num_std * std)
        
        latest_sma = sma.iloc[-1]
        latest_upper = upper_band.iloc[-1]
        latest_lower = lower_band.iloc[-1]
        
        # Generate signal
        signal_type = "HOLD"
        confidence = 0.0
        
        if current_price <= latest_lower:
            # Price is below lower band - BUY signal
            signal_type = "BUY"
            confidence = min(0.9, (latest_lower - current_price) / latest_lower)
        elif current_price >= latest_upper:
            # Price is above upper band - SELL signal
            signal_type = "SELL"
            confidence = min(0.9, (current_price - latest_upper) / latest_upper)
        elif abs(current_price - latest_sma) / latest_sma < 0.01:
            # Price is near SMA - potential reversal
            signal_type = "HOLD"
            confidence = 0.3
            
        # Only generate signal if confidence is above threshold
        if confidence < 0.3:
            return None
            
        return Signal(
            symbol=symbol,
            strategy_name=self.full_name,
            signal_type=signal_type,
            confidence=confidence,
            price=current_price,
            timestamp=datetime.utcnow(),
            metadata=f'{{"sma": {latest_sma}, "upper_band": {latest_upper}, "lower_band": {latest_lower}}}'
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters."""
        return {
            "window": self.window,
            "num_std": self.num_std,
            "strategy_type": "mean_reversion"
        }