from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class Bar:
    symbol: str
    ts: Any
    close: float

class Strategy(ABC):
    name: str

    @abstractmethod
    def generate_signal(self, bars: list[Bar]) -> dict | None:
        raise NotImplementedError
