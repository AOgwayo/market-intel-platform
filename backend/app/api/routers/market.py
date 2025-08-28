from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ....app.db.session import get_db
from ....app.db.models.market_bar import MarketBar

router = APIRouter(tags=["market"])

@router.get("/market/latest")
def latest_market(symbol: str, db: Session = Depends(get_db)):
    bar = (
        db.query(MarketBar)
        .filter(MarketBar.symbol == symbol)
        .order_by(MarketBar.ts.desc())
        .first()
    )
    if not bar:
        return {"symbol": symbol, "data": None}
    return {"symbol": symbol, "close": float(bar.close), "ts": bar.ts.isoformat()}
