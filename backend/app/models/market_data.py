from sqlalchemy import Column, String, DateTime, Float, Integer, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from backend.app.models.database import Base


class MarketBar(Base):
    """Market bar data model for OHLCV data."""
    __tablename__ = "market_bars"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    timeframe = Column(String, nullable=False, default="1m")  # 1m, 5m, 1h, 1d, etc.
    
    # OHLCV data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Additional fields
    num_trades = Column(Integer, nullable=True)
    source = Column(String, nullable=False)  # polygon, binance, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite unique index on symbol and timestamp
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp', unique=True),
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )