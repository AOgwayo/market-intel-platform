from datetime import datetime
from .base import Strategy, Bar

class MeanReversionV1(Strategy):
    name = "mean_reversion_v1"

    def generate_signal(self, bars: list[Bar]):
        if len(bars) < 2:
            return None
        prices = [b.close for b in bars]
        mean_price = sum(prices) / len(prices)
        last = prices[-1]
        strength = (mean_price - last) / mean_price if mean_price else 0
        direction = "BUY" if last < mean_price else "SELL"
        return {
            "strategy": self.name,
            "direction": direction,
            "strength": strength,
            "generated_at": datetime.utcnow().isoformat(),
        }
