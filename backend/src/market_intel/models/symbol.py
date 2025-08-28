from __future__ import annotations
from pydantic import BaseModel

class Symbol(BaseModel):
    raw: str
    canonical: str
    asset_type: str  # equity, crypto, etc.
    exchange: str | None = None
    base: str | None = None
    quote: str | None = None