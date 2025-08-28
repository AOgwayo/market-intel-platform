from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime

class Bar(BaseModel):
    symbol: str
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    start: datetime
    end: datetime
    source: str