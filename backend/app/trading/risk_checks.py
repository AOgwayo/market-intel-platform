from typing import Dict, Any
from decimal import Decimal

from app.models.database import Order, Position


class RiskCheck:
    """Risk management checks."""
    
    def __init__(self, max_position_size: float = 10000.0, max_daily_loss: float = 1000.0):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
    
    def validate_order(self, order: Order, current_positions: Dict[str, Position]) -> Dict[str, Any]:
        """Validate an order against risk parameters."""
        checks = {
            "passed": True,
            "reasons": []
        }
        
        # Check position size
        position_value = order.quantity * (order.price or 0)
        if position_value > self.max_position_size:
            checks["passed"] = False
            checks["reasons"].append(f"Position size ${position_value:.2f} exceeds maximum ${self.max_position_size:.2f}")
        
        # Check existing position
        existing_position = current_positions.get(order.symbol)
        if existing_position:
            new_quantity = existing_position.quantity
            if order.side == "BUY":
                new_quantity += order.quantity
            else:
                new_quantity -= order.quantity
            
            new_value = abs(new_quantity) * (order.price or 0)
            if new_value > self.max_position_size:
                checks["passed"] = False
                checks["reasons"].append(f"Total position would be ${new_value:.2f}, exceeding maximum")
        
        # Additional risk checks can be added here
        
        return checks