import uuid
from .broker_alpaca import AlpacaBroker
from .risk import RiskEngine

class OrderRouter:
    def __init__(self):
        self.broker = AlpacaBroker()
        self.risk = RiskEngine()

    def place_order(self, symbol: str, side: str, qty: float, price: float | None = None) -> str:
        if not self.risk.check_order(symbol=symbol, side=side, qty=qty):
            raise ValueError("Risk check failed")
        client_order_id = str(uuid.uuid4())
        self.broker.submit_order(symbol=symbol, side=side, qty=qty, price=price, client_order_id=client_order_id)
        return client_order_id
