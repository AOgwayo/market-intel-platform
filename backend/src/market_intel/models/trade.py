from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime

class Trade(BaseModel):
    symbol: str
    price: float
    size: float
    ts: datetime
    source: str