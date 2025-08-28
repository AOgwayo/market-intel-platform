from typing import Dict, Any, Optional
from datetime import datetime
import logging

from sqlalchemy.orm import Session

from app.models.database import Order, Position
from app.trading.alpaca_adapter import AlpacaBrokerAdapter
from app.trading.risk_checks import RiskCheck


class OrderRouter:
    """Routes and manages order execution."""
    
    def __init__(self, db: Session):
        self.db = db
        self.broker_adapter = AlpacaBrokerAdapter()
        self.risk_check = RiskCheck()
        
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Place an order through the routing system."""
        
        # Create order object
        order = Order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            status="PENDING"
        )
        
        # Get current positions for risk check
        positions = self._get_current_positions()
        
        # Risk check
        risk_result = self.risk_check.validate_order(order, positions)
        if not risk_result["passed"]:
            return {
                "success": False,
                "error": f"Risk check failed: {', '.join(risk_result['reasons'])}",
                "order_id": None
            }
        
        # Save order to database
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        # Send to broker
        order_data = {
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "quantity": quantity,
            "price": price
        }
        
        broker_result = self.broker_adapter.place_order(order_data)
        
        # Update order with broker response
        if broker_result["success"]:
            order.broker_order_id = broker_result["broker_order_id"]
            order.status = "SUBMITTED"
            logging.info(f"Order {order.id} successfully submitted to broker")
        else:
            order.status = "FAILED"
            logging.error(f"Failed to submit order {order.id}: {broker_result['error']}")
        
        self.db.commit()
        
        return {
            "success": broker_result["success"],
            "error": broker_result.get("error"),
            "order_id": order.id,
            "broker_order_id": broker_result.get("broker_order_id")
        }
    
    def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """Cancel an order."""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {"success": False, "error": "Order not found"}
        
        if order.status in ["FILLED", "CANCELLED"]:
            return {"success": False, "error": f"Cannot cancel order with status {order.status}"}
        
        if not order.broker_order_id:
            return {"success": False, "error": "No broker order ID found"}
        
        # Cancel with broker
        broker_result = self.broker_adapter.cancel_order(order.broker_order_id)
        
        if broker_result["success"]:
            order.status = "CANCELLED"
            order.updated_at = datetime.utcnow()
            self.db.commit()
        
        return broker_result
    
    def _get_current_positions(self) -> Dict[str, Position]:
        """Get current positions for risk management."""
        positions = (
            self.db.query(Position)
            .filter(Position.is_active == True)
            .all()
        )
        
        return {pos.symbol: pos for pos in positions}