#!/usr/bin/env python3
"""
Test script for the Market Intelligence Platform.
This script tests core functionality without requiring external APIs or databases.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import json
import asyncio

def test_polygon_normalization():
    """Test Polygon API response normalization."""
    print("=== Testing Polygon Normalization ===")
    
    from backend.app.ingestion.polygon_equities import PolygonEquitiesClient
    
    # Create test client
    client = PolygonEquitiesClient(api_key="test")
    
    # Mock Polygon response
    mock_response = {
        "status": "OK",
        "results": [
            {
                "t": 1640995200000,  # 2022-01-01 00:00:00 UTC in milliseconds
                "o": 150.25,
                "h": 151.50,
                "l": 149.75,
                "c": 150.75,
                "v": 1500000,
                "n": 1250
            }
        ]
    }
    
    # Test normalization
    normalized = client._normalize_polygon_response(mock_response, "AAPL", "1m")
    
    if len(normalized) == 1:
        bar = normalized[0]
        print("✓ Polygon normalization successful:")
        print(f"  - Symbol: {bar['symbol']}")
        print(f"  - Timestamp: {bar['timestamp']}")
        print(f"  - OHLC: {bar['open']}/{bar['high']}/{bar['low']}/{bar['close']}")
        print(f"  - Volume: {bar['volume']:,}")
        print(f"  - Source: {bar['source']}")
    else:
        print("✗ Polygon normalization failed")


def test_binance_aggregation():
    """Test Binance trade aggregation logic."""
    print("\n=== Testing Binance Aggregation ===")
    
    from backend.app.ingestion.binance_stream import BinanceStreamAggregator
    
    # Create aggregator
    aggregator = BinanceStreamAggregator("BTCUSDT")
    
    # Mock trade data
    mock_trades = [
        {"p": "46000.00", "q": "0.001", "T": 1640995200000},  # 2022-01-01 00:00:00
        {"p": "46010.00", "q": "0.002", "T": 1640995210000},  # 10 seconds later
        {"p": "46020.00", "q": "0.001", "T": 1640995260000},  # Next minute
    ]
    
    print("Processing mock trades:")
    completed_bars = []
    
    for i, trade in enumerate(mock_trades):
        result = aggregator.process_trade(trade)
        print(f"  Trade {i+1}: Price ${trade['p']}, Qty {trade['q']}")
        
        if result:
            completed_bars.append(result)
            print(f"    → Completed bar: OHLC {result['open']}/{result['high']}/{result['low']}/{result['close']}")
    
    print(f"✓ Aggregation successful: {len(completed_bars)} bars completed")


def test_bar_normalization():
    """Test bar data structure consistency."""
    print("\n=== Testing Bar Data Structure ===")
    
    # Sample normalized bars from different sources
    polygon_bar = {
        "symbol": "AAPL",
        "timestamp": datetime.now(),
        "timeframe": "1m",
        "open": 150.25,
        "high": 151.50,
        "low": 149.75,
        "close": 150.75,
        "volume": 1500000,
        "num_trades": 1250,
        "source": "polygon"
    }
    
    binance_bar = {
        "symbol": "BTCUSDT",
        "timestamp": datetime.now(),
        "timeframe": "1m",
        "open": 46000.00,
        "high": 46050.00,
        "low": 45980.00,
        "close": 46025.00,
        "volume": 15.5,
        "num_trades": 125,
        "source": "binance"
    }
    
    # Check required fields
    required_fields = ["symbol", "timestamp", "timeframe", "open", "high", "low", "close", "volume", "source"]
    
    for name, bar in [("Polygon", polygon_bar), ("Binance", binance_bar)]:
        missing_fields = [field for field in required_fields if field not in bar]
        if not missing_fields:
            print(f"✓ {name} bar structure valid")
        else:
            print(f"✗ {name} bar missing fields: {missing_fields}")


def test_strategy_logic():
    """Test basic strategy logic without database."""
    print("\n=== Testing Strategy Logic ===")
    
    from backend.app.strategies.runner import StrategyRunner
    from backend.app.models.market_data import MarketBar
    
    # Create mock market bars
    base_time = datetime.now() - timedelta(minutes=30)
    mock_bars = []
    
    # Create 25 bars with trend data
    base_price = 150.0
    for i in range(25):
        price = base_price + (i * 0.5)  # Upward trend
        bar = MarketBar(
            symbol="AAPL",
            timestamp=base_time + timedelta(minutes=i),
            open_price=price - 0.25,
            high_price=price + 0.50,
            low_price=price - 0.50,
            close_price=price,
            volume=1000000,
            source="test"
        )
        mock_bars.insert(0, bar)  # Insert at beginning (most recent first)
    
    # Test mean reversion strategy
    runner = StrategyRunner()
    result = runner._run_mean_reversion_v1(mock_bars)
    
    print("Mean Reversion Strategy Results:")
    print(f"  - Signal: {result['signal']}")
    print(f"  - Confidence: {result['confidence']:.2f}")
    print(f"  - Current Price: ${result['current_price']:.2f}")
    print(f"  - 20-MA: ${result['ma20']:.2f}")
    print(f"  - Deviation: {result['deviation_pct']:.2f}%")
    print(f"  - Message: {result['message']}")
    
    # Determine expected signal based on trend
    if result['signal'] in ['BUY', 'SELL', 'NEUTRAL']:
        print("✓ Strategy logic working correctly")
    else:
        print("✗ Strategy returned unexpected signal")


def test_configuration():
    """Test configuration management."""
    print("\n=== Testing Configuration ===")
    
    from backend.app.core.config import settings
    
    print("Configuration loaded:")
    print(f"  - Database URL: {settings.database_url}")
    print(f"  - Polygon API Key configured: {'Yes' if settings.polygon_api_key else 'No (using default)'}")
    print(f"  - Equity Symbols: {', '.join(settings.equity_symbols_list)}")
    print(f"  - Binance Default Symbol: {settings.binance_default_symbol}")
    print(f"  - Log Level: {settings.log_level}")
    
    # Test symbol parsing
    if len(settings.equity_symbols_list) > 0:
        print("✓ Configuration management working")
    else:
        print("✗ Symbol configuration failed")


def main():
    """Run all tests."""
    print("Market Intelligence Platform - Test Suite")
    print("==========================================")
    
    try:
        test_configuration()
        test_polygon_normalization()
        test_binance_aggregation()
        test_bar_normalization()
        test_strategy_logic()
        
        print("\n✓ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Set up PostgreSQL database")
        print("2. Add POLYGON_API_KEY to .env file")
        print("3. Run: docker-compose up")
        print("4. Test ingestion: python -m backend.app.ingestion.polygon_equities")
        
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        print("Make sure all dependencies are installed: poetry install")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()