import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import backoff
import logging
from backend.app.core.config import settings
from backend.app.ingestion.bar_writer import write_bars_to_db

logger = logging.getLogger(__name__)


class PolygonEquitiesClient:
    """Client for fetching equities data from Polygon.io API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.polygon_api_key
        self.base_url = "https://api.polygon.io"
        
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=30
    )
    async def _make_request(self, session: aiohttp.ClientSession, url: str, params: Dict) -> Dict:
        """Make HTTP request with retry logic."""
        params["apikey"] = self.api_key
        
        async with session.get(url, params=params) as response:
            if response.status == 429:  # Rate limit
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited, waiting {retry_after} seconds")
                await asyncio.sleep(retry_after)
                raise aiohttp.ClientError("Rate limited")
            
            response.raise_for_status()
            return await response.json()
    
    async def get_historical_minute_bars(
        self, 
        symbols: List[str], 
        start_date: datetime, 
        end_date: datetime = None
    ) -> List[Dict]:
        """
        Fetch historical minute bars for multiple symbols.
        
        Args:
            symbols: List of ticker symbols
            start_date: Start date for data retrieval
            end_date: End date for data retrieval (defaults to today)
            
        Returns:
            List of normalized bar dictionaries
        """
        if not self.api_key:
            logger.error("Polygon API key not configured")
            return []
            
        end_date = end_date or datetime.now()
        all_bars = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in symbols:
                task = self._fetch_symbol_bars(session, symbol, start_date, end_date)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error fetching data: {result}")
                else:
                    all_bars.extend(result)
        
        return all_bars
    
    async def _fetch_symbol_bars(
        self, 
        session: aiohttp.ClientSession, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """Fetch bars for a single symbol."""
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/minute/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": 50000
        }
        
        try:
            data = await self._make_request(session, url, params)
            return self._normalize_polygon_response(data, symbol)
        except Exception as e:
            logger.error(f"Error fetching bars for {symbol}: {e}")
            return []
    
    async def get_latest_daily_aggregate(self, symbols: List[str]) -> List[Dict]:
        """
        Fetch latest daily aggregate data for symbols.
        
        Args:
            symbols: List of ticker symbols
            
        Returns:
            List of normalized daily bar dictionaries
        """
        if not self.api_key:
            logger.error("Polygon API key not configured")
            return []
            
        all_bars = []
        yesterday = datetime.now() - timedelta(days=1)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for symbol in symbols:
                url = f"{self.base_url}/v2/aggs/ticker/{symbol}/prev"
                task = self._make_request(session, url, {})
                tasks.append((symbol, task))
            
            for symbol, task in tasks:
                try:
                    data = await task
                    bars = self._normalize_polygon_response(data, symbol, timeframe="1d")
                    all_bars.extend(bars)
                except Exception as e:
                    logger.error(f"Error fetching daily aggregate for {symbol}: {e}")
        
        return all_bars
    
    def _normalize_polygon_response(self, response: Dict, symbol: str, timeframe: str = "1m") -> List[Dict]:
        """
        Normalize Polygon API response to internal bar format.
        
        Args:
            response: Raw Polygon API response
            symbol: Ticker symbol
            timeframe: Bar timeframe (1m, 1d, etc.)
            
        Returns:
            List of normalized bar dictionaries
        """
        if response.get("status") != "OK" or not response.get("results"):
            return []
        
        normalized_bars = []
        
        for bar in response["results"]:
            # Polygon timestamps are in milliseconds
            timestamp = datetime.fromtimestamp(bar["t"] / 1000)
            
            normalized_bar = {
                "symbol": symbol.upper(),
                "timestamp": timestamp,
                "timeframe": timeframe,
                "open": bar["o"],
                "high": bar["h"],
                "low": bar["l"],
                "close": bar["c"],
                "volume": bar["v"],
                "num_trades": bar.get("n"),  # Number of trades
                "source": "polygon"
            }
            
            normalized_bars.append(normalized_bar)
        
        return normalized_bars


async def ingest_historical_minute_bars(
    symbols: List[str] = None, 
    start_date: datetime = None, 
    end_date: datetime = None
) -> int:
    """
    Ingest historical minute bars from Polygon.
    
    Args:
        symbols: List of symbols to ingest (defaults to config)
        start_date: Start date (defaults to 7 days ago)
        end_date: End date (defaults to now)
        
    Returns:
        Number of bars ingested
    """
    symbols = symbols or settings.equity_symbols_list
    start_date = start_date or (datetime.now() - timedelta(days=7))
    
    client = PolygonEquitiesClient()
    bars = await client.get_historical_minute_bars(symbols, start_date, end_date)
    
    if bars:
        count = write_bars_to_db(bars, source="polygon")
        logger.info(f"Ingested {count} minute bars for symbols: {symbols}")
        return count
    
    return 0


async def ingest_latest_daily_aggregates(symbols: List[str] = None) -> int:
    """
    Ingest latest daily aggregate data from Polygon.
    
    Args:
        symbols: List of symbols to ingest (defaults to config)
        
    Returns:
        Number of bars ingested
    """
    symbols = symbols or settings.equity_symbols_list
    
    client = PolygonEquitiesClient()
    bars = await client.get_latest_daily_aggregate(symbols)
    
    if bars:
        count = write_bars_to_db(bars, source="polygon")
        logger.info(f"Ingested {count} daily bars for symbols: {symbols}")
        return count
    
    return 0