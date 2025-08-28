from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd

from app.models.database import Signal


class BaseStrategy(ABC):
    """Base strategy class."""
    
    def __init__(self, name: str, version: str = "v1"):
        self.name = name
        self.version = version
        self.full_name = f"{name}_{version}"
        
    @abstractmethod
    def generate_signal(
        self, 
        symbol: str, 
        bars: pd.DataFrame, 
        current_price: float
    ) -> Optional[Signal]:
        """Generate a trading signal based on market data.
        
        Args:
            symbol: Trading symbol
            bars: Historical market data as DataFrame
            current_price: Current market price
            
        Returns:
            Signal object or None if no signal
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters."""
        pass
    
    def validate_data(self, bars: pd.DataFrame) -> bool:
        """Validate input data."""
        required_cols = ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        return all(col in bars.columns for col in required_cols) and len(bars) > 0