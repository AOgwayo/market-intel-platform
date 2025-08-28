from datetime import datetime
from sqlalchemy.orm import Session
from ..strategies.registry import strategy_registry
from ..db.models.signal import Signal
from ..db.models.market_bar import MarketBar

class StrategyRunner:
    def __init__(self, db: Session):
        self.db = db

    def run_all(self, symbol: str):
        bars = (
            self.db.query(MarketBar)
            .filter(MarketBar.symbol == symbol)
            .order_by(MarketBar.ts.desc())
            .limit(50)
            .all()
        )
        bars = list(reversed(bars))
        created = []
        simple_bars = [
            type("Bar", (), {"symbol": b.symbol, "ts": b.ts, "close": float(b.close)})
            for b in bars
        ]
        for strat in strategy_registry.values():
            sig_dict = strat.generate_signal(simple_bars)
            if sig_dict:
                sig = Signal(
                    symbol=symbol,
                    ts=datetime.utcnow(),
                    strategy=sig_dict["strategy"],
                    direction=sig_dict["direction"],
                    strength=sig_dict["strength"],
                )
                self.db.add(sig)
                created.append(sig)
        if created:
            self.db.commit()
        return created
