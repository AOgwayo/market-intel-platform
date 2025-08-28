import asyncio
import websockets
import json
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import backoff
from backend.app.core.config import settings
from backend.app.ingestion.bar_writer import write_bars_to_db

logger = logging.getLogger(__name__)


class BinanceStreamAggregator:
    """Aggregates Binance trade stream data into 1-minute bars."""
    
    def __init__(self, symbol: str = None, flush_interval: int = 60):
        self.symbol = (symbol or settings.binance_default_symbol).lower()
        self.flush_interval = flush_interval  # seconds
        self.current_bar = {}
        self.trades_count = 0
        self.last_flush = datetime.utcnow()
        
        # Initialize current minute bar
        self._init_current_bar()
    
    def _init_current_bar(self):
        """Initialize the current minute bar."""
        now = datetime.utcnow()
        # Round down to current minute
        minute_start = now.replace(second=0, microsecond=0)
        
        self.current_bar = {
            "symbol": self.symbol.upper(),
            "timestamp": minute_start,
            "timeframe": "1m",
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": 0.0,
            "num_trades": 0
        }
    
    def process_trade(self, trade_data: Dict) -> Optional[Dict]:
        """
        Process a single trade and update current bar.
        
        Args:
            trade_data: Raw trade data from Binance websocket
            
        Returns:
            Complete bar dict if minute boundary crossed, None otherwise
        """
        try:
            price = float(trade_data["p"])
            quantity = float(trade_data["q"])
            trade_time = datetime.fromtimestamp(trade_data["T"] / 1000)
            
            # Check if we need to start a new bar (minute boundary crossed)
            current_minute = trade_time.replace(second=0, microsecond=0)
            bar_minute = self.current_bar["timestamp"]
            
            completed_bar = None
            
            if current_minute > bar_minute:
                # Minute boundary crossed, complete current bar
                if self.current_bar["open"] is not None:
                    completed_bar = self.current_bar.copy()
                    logger.debug(f"Completed 1m bar for {self.symbol}: {completed_bar}")
                
                # Start new bar
                self._init_current_bar()
                self.current_bar["timestamp"] = current_minute
            
            # Update current bar with trade data
            if self.current_bar["open"] is None:
                self.current_bar["open"] = price
                self.current_bar["high"] = price
                self.current_bar["low"] = price
            else:
                self.current_bar["high"] = max(self.current_bar["high"], price)
                self.current_bar["low"] = min(self.current_bar["low"], price)
            
            self.current_bar["close"] = price
            self.current_bar["volume"] += quantity
            self.current_bar["num_trades"] += 1
            
            return completed_bar
            
        except (KeyError, ValueError) as e:
            logger.error(f"Error processing trade data: {e}")
            return None
    
    def get_current_bar(self) -> Optional[Dict]:
        """Get the current incomplete bar."""
        if self.current_bar["open"] is not None:
            return self.current_bar.copy()
        return None


class BinanceStreamClient:
    """WebSocket client for Binance trade stream."""
    
    def __init__(self, symbol: str = None):
        self.symbol = (symbol or settings.binance_default_symbol).lower()
        self.aggregator = BinanceStreamAggregator(self.symbol)
        self.websocket = None
        self.running = False
        
    def get_stream_url(self) -> str:
        """Build WebSocket URL for trade stream."""
        return f"{settings.binance_base_url.rstrip('/')}/{self.symbol}@trade"
    
    @backoff.on_exception(
        backoff.expo,
        (websockets.ConnectionClosed, websockets.InvalidHandshake),
        max_tries=5,
        max_time=300
    )
    async def connect_and_stream(self, callback=None):
        """
        Connect to Binance WebSocket and stream trade data.
        
        Args:
            callback: Optional callback function for completed bars
        """
        url = self.get_stream_url()
        logger.info(f"Connecting to Binance stream: {url}")
        
        try:
            async with websockets.connect(url) as websocket:
                self.websocket = websocket
                self.running = True
                logger.info(f"Connected to Binance stream for {self.symbol.upper()}")
                
                # Track last flush time for periodic writes
                last_flush = datetime.utcnow()
                pending_bars = []
                
                async for message in websocket:
                    if not self.running:
                        break
                    
                    try:
                        data = json.loads(message)
                        completed_bar = self.aggregator.process_trade(data)
                        
                        if completed_bar:
                            pending_bars.append(completed_bar)
                            logger.info(f"Aggregated 1m bar: {completed_bar['symbol']} "
                                      f"O:{completed_bar['open']:.4f} H:{completed_bar['high']:.4f} "
                                      f"L:{completed_bar['low']:.4f} C:{completed_bar['close']:.4f} "
                                      f"V:{completed_bar['volume']:.2f} T:{completed_bar['num_trades']}")
                        
                        # Periodic flush to database
                        now = datetime.utcnow()
                        if (now - last_flush).seconds >= 60 and pending_bars:
                            await self._flush_bars_to_db(pending_bars)
                            pending_bars.clear()
                            last_flush = now
                            
                        # Call callback if provided
                        if callback and completed_bar:
                            await callback(completed_bar)
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing WebSocket message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                
                # Flush any remaining bars
                if pending_bars:
                    await self._flush_bars_to_db(pending_bars)
                
        except websockets.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            raise
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            raise
        finally:
            self.running = False
    
    async def _flush_bars_to_db(self, bars: list):
        """Flush completed bars to database."""
        try:
            count = write_bars_to_db(bars, source="binance")
            logger.info(f"Flushed {count} bars to database")
        except Exception as e:
            logger.error(f"Error flushing bars to database: {e}")
    
    async def stop(self):
        """Stop the stream."""
        self.running = False
        if self.websocket:
            await self.websocket.close()


async def run_binance_stream(symbol: str = None, duration: Optional[int] = None):
    """
    Run Binance trade stream for a specified duration.
    
    Args:
        symbol: Trading symbol (e.g., 'BTCUSDT')
        duration: Run duration in seconds (None for indefinite)
    """
    client = BinanceStreamClient(symbol)
    
    if duration:
        # Run for specified duration
        try:
            await asyncio.wait_for(
                client.connect_and_stream(),
                timeout=duration
            )
        except asyncio.TimeoutError:
            logger.info(f"Stream completed after {duration} seconds")
        finally:
            await client.stop()
    else:
        # Run indefinitely
        while True:
            try:
                await client.connect_and_stream()
            except Exception as e:
                logger.error(f"Stream error, reconnecting in 10 seconds: {e}")
                await asyncio.sleep(10)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the stream
    asyncio.run(run_binance_stream())