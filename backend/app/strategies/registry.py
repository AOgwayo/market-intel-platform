from typing import Dict, Type

from app.strategies.base import BaseStrategy
from app.strategies.mean_reversion import MeanReversionStrategy
from app.strategies.momentum import MomentumStrategy
from app.strategies.vol_breakout import VolatilityBreakoutStrategy
from app.strategies.regime_detection import RegimeDetectionStrategy


class StrategyRegistry:
    """Registry for trading strategies."""
    
    _strategies: Dict[str, Type[BaseStrategy]] = {}
    
    @classmethod
    def register(cls, strategy_class: Type[BaseStrategy], name: str = None) -> None:
        """Register a strategy class."""
        if name is None:
            # Create an instance to get the full name
            instance = strategy_class()
            name = instance.full_name
        cls._strategies[name] = strategy_class
    
    @classmethod
    def get_strategy(cls, name: str, **kwargs) -> BaseStrategy:
        """Get a strategy instance by name."""
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not found in registry")
        return cls._strategies[name](**kwargs)
    
    @classmethod
    def list_strategies(cls) -> Dict[str, Type[BaseStrategy]]:
        """List all registered strategies."""
        return cls._strategies.copy()
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a strategy is registered."""
        return name in cls._strategies


# Auto-register default strategies
StrategyRegistry.register(MeanReversionStrategy, "mean_reversion_v1")
StrategyRegistry.register(MomentumStrategy, "momentum_v1")  
StrategyRegistry.register(VolatilityBreakoutStrategy, "vol_breakout_v1")
StrategyRegistry.register(RegimeDetectionStrategy, "regime_detection_v1")