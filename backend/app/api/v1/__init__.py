from fastapi import APIRouter

from app.api.v1 import signals, market, trading, models, backtest

api_router = APIRouter()

api_router.include_router(signals.router)
api_router.include_router(market.router)
api_router.include_router(trading.router)
api_router.include_router(models.router)
api_router.include_router(backtest.router)