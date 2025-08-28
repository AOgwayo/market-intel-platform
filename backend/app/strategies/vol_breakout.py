from datetime import datetime
from .base import Strategy, Bar

class VolBreakoutStub(Strategy):
    name = "vol_breakout_stub"

    def generate_signal(self, bars: list[Bar]):
        if len(bars) < 2:
            return None
        return {
            "strategy": self.name,
            "direction": "BUY",
            "strength": 0.05,
            "generated_at": datetime.utcnow().isoformat(),
        }
