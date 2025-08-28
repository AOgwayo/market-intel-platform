from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ....app.db.session import get_db
from ....app.db.models.signal import Signal

router = APIRouter(tags=["signals"])

@router.get("/signals/latest")
def latest_signal(symbol: str, strategy: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Signal).filter(Signal.symbol == symbol)
    if strategy:
        q = q.filter(Signal.strategy == strategy)
    sig = q.order_by(Signal.ts.desc()).first()
    if not sig:
        return {"symbol": symbol, "signal": None}
    return {
        "symbol": symbol,
        "strategy": sig.strategy,
        "direction": sig.direction,
        "strength": float(sig.strength),
        "ts": sig.ts.isoformat(),
    }
