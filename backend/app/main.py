from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.app.models.database import get_db, engine
from backend.app.models.market_data import MarketBar, Base
from backend.app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Market Intelligence Platform",
    description="Real-time market intelligence platform with data ingestion and strategy execution",
    version="0.1.0",
    debug=settings.debug
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Market Intelligence Platform is running"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Database health check."""
    try:
        # Simple query to test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.get("/bars/{symbol}")
async def get_bars(
    symbol: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get recent bars for a symbol."""
    bars = db.query(MarketBar).filter(
        MarketBar.symbol == symbol.upper()
    ).order_by(MarketBar.timestamp.desc()).limit(limit).all()
    
    return {
        "symbol": symbol.upper(),
        "count": len(bars),
        "bars": [
            {
                "timestamp": bar.timestamp,
                "timeframe": bar.timeframe,
                "open": bar.open_price,
                "high": bar.high_price,
                "low": bar.low_price,
                "close": bar.close_price,
                "volume": bar.volume,
                "source": bar.source
            }
            for bar in bars
        ]
    }


@app.get("/symbols")
async def get_symbols(db: Session = Depends(get_db)):
    """Get list of available symbols."""
    symbols = db.query(MarketBar.symbol).distinct().all()
    return {"symbols": [s[0] for s in symbols]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)