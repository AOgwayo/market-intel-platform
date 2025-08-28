from datetime import datetime
from .base import Strategy, Bar

class MomentumStub(Strategy):
    name = "momentum_stub"

    def generate_signal(self, bars: list[Bar]):
        if len(bars) < 2:
            return None
        direction = "BUY" if bars[-1].close > bars[-2].close else "SELL"
        return {
            "strategy": self.name,
            "direction": direction,
            "strength": 0.1,
            "generated_at": datetime.utcnow().isoformat(),
        }
