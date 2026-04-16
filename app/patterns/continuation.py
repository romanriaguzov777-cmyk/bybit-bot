from dataclasses import dataclass

import pandas as pd

from app.enums import TradeSide


@dataclass(slots=True)
class ContinuationSignal:
    valid: bool
    side: TradeSide | None
    pullback_depth: float
    score: float


def detect_continuation(m5: pd.DataFrame) -> ContinuationSignal:
    if len(m5) < 12:
        return ContinuationSignal(False, None, 0.0, 0.0)
    last = m5.tail(8)
    impulse = float((last["close"].iloc[2] - last["open"].iloc[0]) / max(last["open"].iloc[0], 1e-9))
    peak = last["high"].iloc[:4].max()
    trough = last["low"].iloc[:4].min()
    pb_low = last["low"].iloc[4:7].min()
    pb_high = last["high"].iloc[4:7].max()
    depth_long = (peak - pb_low) / max(peak - trough, 1e-9)
    depth_short = (pb_high - trough) / max(peak - trough, 1e-9)
    long_ok = impulse > 0.003 and 0.25 <= depth_long <= 0.45 and last["close"].iloc[-1] > last["high"].iloc[-2]
    short_ok = impulse < -0.003 and 0.25 <= depth_short <= 0.45 and last["close"].iloc[-1] < last["low"].iloc[-2]
    if long_ok:
        return ContinuationSignal(True, TradeSide.BUY, depth_long, 82.0)
    if short_ok:
        return ContinuationSignal(True, TradeSide.SELL, depth_short, 82.0)
    return ContinuationSignal(False, None, max(depth_long, depth_short), 40.0)
