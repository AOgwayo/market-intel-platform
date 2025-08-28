from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import numpy as np

from app.strategies.base import BaseStrategy
from app.models.database import MarketBar


class BacktestEngine:
    """Backtesting engine for trading strategies."""
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}  # {symbol: quantity}
        self.trades = []
        self.daily_pnl = []
        
    def run_backtest(
        self,
        strategy: BaseStrategy,
        market_data: pd.DataFrame,
        symbol: str = "SPY",
        commission_per_trade: float = 1.0
    ) -> Dict[str, Any]:
        """Run a backtest for a strategy."""
        
        if len(market_data) < 10:
            return {
                "error": "Insufficient market data for backtest",
                "final_pnl": 0.0,
                "trades": [],
                "avg_daily_pnl": 0.0
            }
        
        # Reset state
        self.capital = self.initial_capital
        self.positions = {symbol: 0}
        self.trades = []
        self.daily_pnl = []
        
        previous_portfolio_value = self.initial_capital
        
        # Sort data by timestamp
        market_data = market_data.sort_values('timestamp').reset_index(drop=True)
        
        for i in range(20, len(market_data)):  # Start after sufficient history
            current_row = market_data.iloc[i]
            current_price = current_row['close']
            
            # Get historical data up to current point
            historical_data = market_data.iloc[:i+1]
            
            # Generate signal
            signal = strategy.generate_signal(symbol, historical_data, current_price)
            
            if signal and signal.signal_type in ['BUY', 'SELL']:
                self._execute_signal(signal, current_price, current_row['timestamp'], commission_per_trade)
            
            # Calculate daily PnL
            current_position_value = self.positions[symbol] * current_price
            current_portfolio_value = self.capital + current_position_value
            
            daily_pnl = current_portfolio_value - previous_portfolio_value
            self.daily_pnl.append({
                'date': current_row['timestamp'],
                'pnl': daily_pnl,
                'portfolio_value': current_portfolio_value
            })
            
            previous_portfolio_value = current_portfolio_value
        
        # Calculate final metrics
        final_portfolio_value = self.capital + (self.positions[symbol] * market_data.iloc[-1]['close'])
        final_pnl = final_portfolio_value - self.initial_capital
        avg_daily_pnl = np.mean([d['pnl'] for d in self.daily_pnl]) if self.daily_pnl else 0.0
        
        return {
            "final_pnl": round(final_pnl, 2),
            "final_capital": round(self.capital, 2),
            "final_position": self.positions[symbol],
            "final_portfolio_value": round(final_portfolio_value, 2),
            "total_return_pct": round((final_pnl / self.initial_capital) * 100, 2),
            "trades": self.trades,
            "total_trades": len(self.trades),
            "avg_daily_pnl": round(avg_daily_pnl, 2),
            "daily_pnl": self.daily_pnl
        }
    
    def _execute_signal(
        self, 
        signal, 
        current_price: float, 
        timestamp: datetime, 
        commission: float
    ):
        """Execute a trading signal."""
        symbol = signal.symbol
        
        # Simple position sizing: use 10% of available capital
        position_size_pct = 0.1
        max_position_value = self.capital * position_size_pct
        shares_to_trade = int(max_position_value / current_price)
        
        if shares_to_trade <= 0:
            return
        
        if signal.signal_type == 'BUY' and self.positions[symbol] >= 0:
            # Buy signal - only if not already long
            cost = shares_to_trade * current_price + commission
            if self.capital >= cost:
                self.capital -= cost
                self.positions[symbol] += shares_to_trade
                
                self.trades.append({
                    'timestamp': timestamp,
                    'symbol': symbol,
                    'side': 'BUY',
                    'quantity': shares_to_trade,
                    'price': current_price,
                    'value': shares_to_trade * current_price,
                    'commission': commission,
                    'strategy': signal.strategy_name,
                    'confidence': signal.confidence
                })
        
        elif signal.signal_type == 'SELL' and self.positions[symbol] > 0:
            # Sell signal - close position
            shares_to_sell = min(shares_to_trade, self.positions[symbol])
            proceeds = shares_to_sell * current_price - commission
            
            self.capital += proceeds
            self.positions[symbol] -= shares_to_sell
            
            self.trades.append({
                'timestamp': timestamp,
                'symbol': symbol,
                'side': 'SELL',
                'quantity': shares_to_sell,
                'price': current_price,
                'value': shares_to_sell * current_price,
                'commission': commission,
                'strategy': signal.strategy_name,
                'confidence': signal.confidence
            })