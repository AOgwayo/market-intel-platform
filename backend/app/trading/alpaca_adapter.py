from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from app.core.config import settings

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logging.warning("Alpaca library not available")


class BrokerAdapter(ABC):
    """Abstract broker adapter."""
    
    @abstractmethod
    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order with the broker."""
        pass
    
    @abstractmethod
    def cancel_order(self, broker_order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        pass
    
    @abstractmethod
    def get_order_status(self, broker_order_id: str) -> Dict[str, Any]:
        """Get order status."""
        pass


class AlpacaBrokerAdapter(BrokerAdapter):
    """Alpaca broker adapter."""
    
    def __init__(self):
        if not ALPACA_AVAILABLE:
            raise ImportError("Alpaca library is required but not available")
        
        self.api_key = settings.alpaca_api_key
        self.secret_key = settings.alpaca_secret_key
        self.base_url = settings.alpaca_base_url
        
        if not self.api_key or not self.secret_key:
            logging.warning("Alpaca credentials not configured - trading will be disabled")
            self.client = None
        else:
            self.client = TradingClient(self.api_key, self.secret_key, paper=True)
    
    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order with Alpaca."""
        if not self.client:
            return {
                "success": False,
                "error": "Alpaca client not configured",
                "broker_order_id": None
            }
        
        try:
            symbol = order_data["symbol"]
            side = OrderSide.BUY if order_data["side"] == "BUY" else OrderSide.SELL
            quantity = order_data["quantity"]
            
            if order_data["order_type"] == "MARKET":
                request = MarketOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=side,
                    time_in_force=TimeInForce.DAY
                )
            else:  # LIMIT
                request = LimitOrderRequest(
                    symbol=symbol,
                    qty=quantity,
                    side=side,
                    time_in_force=TimeInForce.DAY,
                    limit_price=order_data["price"]
                )
            
            order = self.client.submit_order(request)
            
            return {
                "success": True,
                "broker_order_id": order.id,
                "status": order.status,
                "error": None
            }
            
        except Exception as e:
            logging.error(f"Error placing Alpaca order: {e}")
            return {
                "success": False,
                "error": str(e),
                "broker_order_id": None
            }
    
    def cancel_order(self, broker_order_id: str) -> Dict[str, Any]:
        """Cancel an Alpaca order."""
        if not self.client:
            return {"success": False, "error": "Alpaca client not configured"}
        
        try:
            self.client.cancel_order_by_id(broker_order_id)
            return {"success": True, "error": None}
        except Exception as e:
            logging.error(f"Error canceling Alpaca order: {e}")
            return {"success": False, "error": str(e)}
    
    def get_order_status(self, broker_order_id: str) -> Dict[str, Any]:
        """Get Alpaca order status."""
        if not self.client:
            return {"success": False, "error": "Alpaca client not configured"}
        
        try:
            order = self.client.get_order_by_id(broker_order_id)
            return {
                "success": True,
                "status": order.status,
                "filled_qty": order.filled_qty or 0,
                "error": None
            }
        except Exception as e:
            logging.error(f"Error getting Alpaca order status: {e}")
            return {"success": False, "error": str(e)}