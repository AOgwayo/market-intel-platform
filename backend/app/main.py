from fastapi import FastAPI
from .core.config import settings
from .api.routers import market, signals, trading, models, backtest

app = FastAPI(title="Market Intelligence Platform", version="0.1.0")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# Versioned API
app.include_router(market.router, prefix="/v1")
app.include_router(signals.router, prefix="/v1")
app.include_router(trading.router, prefix="/v1")
app.include_router(models.router, prefix="/v1")
app.include_router(backtest.router, prefix="/v1")

# Simple startup log
@app.on_event("startup")
async def startup_event() -> None:
    print("Starting Market Intelligence Platform (env=", settings.environment, ")")
