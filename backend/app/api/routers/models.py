from fastapi import APIRouter
from ....app.strategies.registry import strategy_registry

router = APIRouter(tags=["models"])

@router.get("/models/strategies")
def list_strategies():
    return {"strategies": list(strategy_registry.keys())}
