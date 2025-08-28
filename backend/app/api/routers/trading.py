from fastapi import APIRouter
from pydantic import BaseModel
from ....app.services.order_router import OrderRouter

router = APIRouter(tags=["trading"])

class OrderRequest(BaseModel):
    symbol: str
    side: str
    qty: float
    price: float | None = None

@router.post("/trading/order")
def place_order(req: OrderRequest):
    router_service = OrderRouter()
    order_id = router_service.place_order(symbol=req.symbol, side=req.side, qty=req.qty, price=req.price)
    return {"status": "accepted", "client_order_id": order_id}
