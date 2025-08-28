from sqlalchemy import Integer, String, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from ...db.session import Base

class MarketBar(Base):
    __tablename__ = "market_bars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open: Mapped[float] = mapped_column(Numeric(18, 8))
    high: Mapped[float] = mapped_column(Numeric(18, 8))
    low: Mapped[float] = mapped_column(Numeric(18, 8))
    close: Mapped[float] = mapped_column(Numeric(18, 8))
    volume: Mapped[float] = mapped_column(Numeric(24, 8))