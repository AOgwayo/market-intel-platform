from sqlalchemy.orm import Session
from ..db.models.signal import Signal

class SignalService:
    def __init__(self, db: Session):
        self.db = db

    def latest_signal(self, symbol: str, strategy: str | None = None):
        q = self.db.query(Signal).filter(Signal.symbol == symbol)
        if strategy:
            q = q.filter(Signal.strategy == strategy)
        return q.order_by(Signal.ts.desc()).first()
