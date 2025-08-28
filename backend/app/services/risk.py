class RiskEngine:
    def check_order(self, symbol: str, side: str, qty: float) -> bool:
        if qty <= 0:
            return False
        return qty <= 1_000_000
