from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.trading.order_router import OrderRouter


router = APIRouter(prefix="/trading", tags=["trading"])


class OrderRequest(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    order_type: str = "MARKET"  # MARKET or LIMIT
    quantity: float
    price: Optional[float] = None


@router.post("/orders")
def place_order(
    order_request: OrderRequest,
    db: Session = Depends(get_db)
):
    """Place a trading order."""
    order_router = OrderRouter(db)
    
    result = order_router.place_order(
        symbol=order_request.symbol,
        side=order_request.side,
        order_type=order_request.order_type,
        quantity=order_request.quantity,
        price=order_request.price
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": "Order placed successfully",
        "order_id": result["order_id"],
        "broker_order_id": result.get("broker_order_id"),
        "success": True
    }


@router.delete("/orders/{order_id}")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Cancel a trading order."""
    order_router = OrderRouter(db)
    result = order_router.cancel_order(order_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": "Order cancelled successfully",
        "success": True
    }


@router.get("/positions")
def get_positions(db: Session = Depends(get_db)):
    """Get current trading positions."""
    # TODO: Implement position retrieval
    return {
        "positions": [],
        "total_value": 0.0,
        "message": "Position tracking not yet implemented"
    }