from __future__ import annotations
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from market_intel.logging_config import configure_logging
from market_intel.ingestion.polygon_adapter import PolygonAdapter
from market_intel.ingestion.binance_adapter import BinanceAdapter

scheduler = AsyncIOScheduler()
configure_logging()

polygon_adapter = PolygonAdapter()
binance_adapter = BinanceAdapter()

async def run_ingestion_cycle():
    # Placeholder cycle
    async for _ in polygon_adapter.fetch_latest_bars(["AAPL"], "1m"):
        pass
    async for _ in binance_adapter.fetch_latest_bars(["BTCUSDT"], "1m"):
        pass

def start_scheduler():
    scheduler.add_job(run_ingestion_cycle, "interval", seconds=60, id="ingestion_cycle")
    scheduler.start()