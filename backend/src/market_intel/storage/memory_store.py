from __future__ import annotations
from collections import defaultdict, deque
from typing import Iterable
from market_intel.storage.interface import BarStore
from market_intel.models.bar import Bar

class InMemoryBarStore(BarStore):
    def __init__(self, capacity: int = 10_000):
        self._data = defaultdict(lambda: deque(maxlen=capacity))

    def write_bars(self, bars: Iterable[Bar]) -> None:
        for b in bars:
            self._data[b.symbol].append(b)

    def latest_bars(self, symbol: str, limit: int = 100):
        d = self._data[symbol]
        return list(d)[-limit:]