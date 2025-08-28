from __future__ import annotations
from abc import ABC, abstractmethod
from typing import AsyncIterator
from datetime import datetime
from market_intel.models.bar import Bar

class IngestionAdapter(ABC):
    """Base class for ingestion adapters.

    Methods return AsyncIterator[Bar] so callers can stream results without
    buffering entire datasets in memory.
    """
    source: str

    @abstractmethod
    async def fetch_latest_bars(self, symbols: list[str], interval: str) -> AsyncIterator[Bar]:
        ...

    @abstractmethod
    async def backfill_bars(
        self, symbols: list[str], interval: str, start: datetime, end: datetime
    ) -> AsyncIterator[Bar]:
        ...
