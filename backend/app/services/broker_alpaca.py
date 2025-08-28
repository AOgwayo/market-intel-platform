from ..core.config import settings

class AlpacaBroker:
    def submit_order(self, symbol: str, side: str, qty: float, price: float | None, client_order_id: str) -> None:
        if not settings.alpaca_api_key:
            print("[AlpacaBroker] No API keys set; simulating order", client_order_id)
            return
        print(
            f"[AlpacaBroker] Would submit order: {client_order_id} {side} {qty} {symbol} price={price} paper={settings.alpaca_paper}"
        )
