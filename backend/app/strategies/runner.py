from typing import List, Dict
from sqlalchemy.orm import Session
from backend.app.models.database import get_db
from backend.app.models.market_data import MarketBar
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StrategyRunner:
    """Basic strategy runner for demonstration purposes."""
    
    def __init__(self, session: Session = None):
        self.session = session or next(get_db())
    
    def run_strategies_for_symbol(self, symbol: str) -> Dict:
        """
        Run strategies for a specific symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with strategy results
        """
        logger.info(f"Running strategies for {symbol}")
        
        # Get recent bars for the symbol
        recent_bars = self.session.query(MarketBar).filter(
            MarketBar.symbol == symbol.upper()
        ).order_by(MarketBar.timestamp.desc()).limit(100).all()
        
        if len(recent_bars) < 20:
            logger.warning(f"Insufficient data for {symbol}: {len(recent_bars)} bars")
            return {"symbol": symbol, "strategies": [], "message": "Insufficient data"}
        
        results = {
            "symbol": symbol,
            "strategies": [],
            "timestamp": datetime.utcnow()
        }
        
        # Run mean reversion strategy
        mean_reversion_result = self._run_mean_reversion_v1(recent_bars)
        results["strategies"].append(mean_reversion_result)
        
        logger.info(f"Completed strategy run for {symbol}: {len(results['strategies'])} strategies")
        return results
    
    def _run_mean_reversion_v1(self, bars: List[MarketBar]) -> Dict:
        """
        Simple mean reversion strategy implementation.
        
        Args:
            bars: List of market bars (most recent first)
            
        Returns:
            Strategy result dictionary
        """
        if len(bars) < 20:
            return {
                "name": "mean_reversion_v1",
                "signal": "NEUTRAL",
                "confidence": 0.0,
                "message": "Insufficient data"
            }
        
        # Calculate 20-period moving average
        recent_prices = [bar.close_price for bar in bars[:20]]
        ma20 = sum(recent_prices) / len(recent_prices)
        
        current_price = bars[0].close_price
        deviation = (current_price - ma20) / ma20
        
        # Simple mean reversion logic
        if deviation > 0.02:  # 2% above MA
            signal = "SELL"
            confidence = min(abs(deviation) * 10, 1.0)
        elif deviation < -0.02:  # 2% below MA
            signal = "BUY"
            confidence = min(abs(deviation) * 10, 1.0)
        else:
            signal = "NEUTRAL"
            confidence = 0.0
        
        return {
            "name": "mean_reversion_v1",
            "signal": signal,
            "confidence": confidence,
            "current_price": current_price,
            "ma20": ma20,
            "deviation_pct": deviation * 100,
            "message": f"Price is {deviation*100:.2f}% from 20-MA"
        }


def run_strategies_for_symbols(symbols: List[str]) -> List[Dict]:
    """
    Run strategies for multiple symbols.
    
    Args:
        symbols: List of trading symbols
        
    Returns:
        List of strategy results
    """
    runner = StrategyRunner()
    results = []
    
    for symbol in symbols:
        try:
            result = runner.run_strategies_for_symbol(symbol)
            results.append(result)
        except Exception as e:
            logger.error(f"Error running strategies for {symbol}: {e}")
            results.append({
                "symbol": symbol,
                "strategies": [],
                "error": str(e)
            })
    
    return results