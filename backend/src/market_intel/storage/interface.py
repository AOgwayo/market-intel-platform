from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable
from market_intel.models.bar import Bar

class BarStore(ABC):
    @abstractmethod
    def write_bars(self, bars: Iterable[Bar]) -> None:
        ...

    @abstractmethod
    def latest_bars(self, symbol: str, limit: int = 100):
        ...