from __future__ import annotations
import httpx
from datetime import datetime
from typing import AsyncIterator
from market_intel.ingestion.base import IngestionAdapter
from market_intel.models.bar import Bar
from market_intel.config import settings

class BinanceAdapter(IngestionAdapter):
    source = "binance"

    async def fetch_latest_bars(self, symbols: list[str], interval: str) -> AsyncIterator[Bar]:
        # Placeholder stub
        async with httpx.AsyncClient(base_url=settings.binance_base_url) as client:  # noqa: F841
            for s in symbols:
                yield Bar(
                    symbol=s,
                    interval=interval,
                    open=0,
                    high=0,
                    low=0,
                    close=0,
                    volume=0,
                    start=datetime.utcnow(),
                    end=datetime.utcnow(),
                    source=self.source,
                )

    async def backfill_bars(
        self, symbols: list[str], interval: str, start: datetime, end: datetime
    ) -> AsyncIterator[Bar]:
        async for bar in self.fetch_latest_bars(symbols, interval):
            yield bar
