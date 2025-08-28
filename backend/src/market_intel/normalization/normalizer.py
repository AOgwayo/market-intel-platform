from __future__ import annotations
from market_intel.models.bar import Bar

def normalize_symbol(raw: str, source: str) -> str:
    # Very naive placeholder
    return raw.upper()

def normalize_bar(bar: Bar) -> Bar:
    # Placeholder — eventually adjust decimals, tz, symbol mapping
    return bar