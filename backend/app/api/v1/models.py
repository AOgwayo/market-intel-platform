from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.strategies.registry import StrategyRegistry


router = APIRouter(prefix="/models", tags=["models"])


@router.get("/strategies")
def list_strategies():
    """List all available trading strategies."""
    strategies = StrategyRegistry.list_strategies()
    
    strategy_info = []
    for name, strategy_class in strategies.items():
        # Create instance to get parameters
        try:
            instance = strategy_class()
            parameters = instance.get_parameters()
        except Exception:
            parameters = {}
        
        strategy_info.append({
            "name": name,
            "class_name": strategy_class.__name__,
            "parameters": parameters,
            "description": strategy_class.__doc__ or "No description available"
        })
    
    return {
        "strategies": strategy_info,
        "total_count": len(strategy_info)
    }


@router.get("/strategies/{strategy_name}")
def get_strategy_info(strategy_name: str):
    """Get detailed information about a specific strategy."""
    if not StrategyRegistry.is_registered(strategy_name):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_name}' not found")
    
    strategy = StrategyRegistry.get_strategy(strategy_name)
    
    return {
        "name": strategy_name,
        "full_name": strategy.full_name,
        "class_name": strategy.__class__.__name__,
        "parameters": strategy.get_parameters(),
        "description": strategy.__class__.__doc__ or "No description available"
    }


@router.get("/versions")
def list_model_versions(db: Session = Depends(get_db)):
    """List all model versions in the database."""
    # TODO: Implement model version tracking
    return {
        "model_versions": [],
        "message": "Model version tracking not yet implemented"
    }