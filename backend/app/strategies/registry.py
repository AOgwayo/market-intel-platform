from .mean_reversion import MeanReversionV1
from .momentum import MomentumStub
from .vol_breakout import VolBreakoutStub
from .regime_detection import RegimeDetectionStub
from .base import Strategy

strategy_registry: dict[str, Strategy] = {
    "mean_reversion_v1": MeanReversionV1(),
    "momentum_stub": MomentumStub(),
    "vol_breakout_stub": VolBreakoutStub(),
    "regime_detection_stub": RegimeDetectionStub(),
}
