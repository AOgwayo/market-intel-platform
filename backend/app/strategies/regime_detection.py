from datetime import datetime
from .base import Strategy, Bar

class RegimeDetectionStub(Strategy):
    name = "regime_detection_stub"

    def generate_signal(self, bars: list[Bar]):
        if not bars:
            return None
        return {
            "strategy": self.name,
            "direction": "FLAT",
            "strength": 0.0,
            "generated_at": datetime.utcnow().isoformat(),
        }
