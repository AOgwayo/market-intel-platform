from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from backend.app.models.database import get_db
from backend.app.models.market_data import MarketBar
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BarWriter:
    """Utility class for writing market bar data to database with conflict handling."""
    
    def __init__(self, session: Session = None):
        self.session = session
        
    def upsert_bars(self, bars: List[Dict], source: str = "unknown") -> int:
        """
        Insert or update market bars with conflict resolution.
        
        Args:
            bars: List of bar dictionaries with OHLCV data
            source: Data source identifier (polygon, binance, etc.)
            
        Returns:
            Number of bars processed
        """
        if not bars:
            return 0
            
        session = self.session or next(get_db())
        
        try:
            # Convert bar dicts to MarketBar objects
            market_bars = []
            for bar in bars:
                market_bar = MarketBar(
                    symbol=bar["symbol"].upper(),
                    timestamp=bar["timestamp"],
                    timeframe=bar.get("timeframe", "1m"),
                    open_price=float(bar["open"]),
                    high_price=float(bar["high"]),
                    low_price=float(bar["low"]),
                    close_price=float(bar["close"]),
                    volume=float(bar["volume"]),
                    num_trades=bar.get("num_trades"),
                    source=source,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                market_bars.append(market_bar)
            
            # Use PostgreSQL's ON CONFLICT for upsert
            for bar in market_bars:
                stmt = insert(MarketBar).values(
                    symbol=bar.symbol,
                    timestamp=bar.timestamp,
                    timeframe=bar.timeframe,
                    open_price=bar.open_price,
                    high_price=bar.high_price,
                    low_price=bar.low_price,
                    close_price=bar.close_price,
                    volume=bar.volume,
                    num_trades=bar.num_trades,
                    source=bar.source,
                    created_at=bar.created_at,
                    updated_at=bar.updated_at
                )
                
                # On conflict, update OHLCV data (for partial bar re-aggregation)
                stmt = stmt.on_conflict_do_update(
                    constraint='idx_symbol_timestamp',
                    set_=dict(
                        open_price=stmt.excluded.open_price,
                        high_price=stmt.excluded.high_price,
                        low_price=stmt.excluded.low_price,
                        close_price=stmt.excluded.close_price,
                        volume=stmt.excluded.volume,
                        num_trades=stmt.excluded.num_trades,
                        updated_at=stmt.excluded.updated_at
                    )
                )
                
                session.execute(stmt)
            
            session.commit()
            logger.info(f"Successfully upserted {len(bars)} bars from {source}")
            return len(bars)
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error upserting bars: {e}")
            raise
        finally:
            if not self.session:  # Only close if we created the session
                session.close()


def write_bars_to_db(bars: List[Dict], source: str = "unknown") -> int:
    """Convenience function for writing bars to database."""
    writer = BarWriter()
    return writer.upsert_bars(bars, source)