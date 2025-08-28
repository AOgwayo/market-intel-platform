from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from ...db.session import Base

class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    qty: Mapped[float] = mapped_column(Numeric(18, 8))
    avg_price: Mapped[float] = mapped_column(Numeric(18, 8))
