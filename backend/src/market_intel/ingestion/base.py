from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable
from datetime import datetime
from market_intel.models.bar import Bar

class IngestionAdapter(ABC):
    source: str

    @abstractmethod
    async def fetch_latest_bars(self, symbols: list[str], interval: str) -> Iterable[Bar]:
        ...

    @abstractmethod
    async def backfill_bars(
        self, symbols: list[str], interval: str, start: datetime, end: datetime
    ) -> Iterable[Bar]:
        ...