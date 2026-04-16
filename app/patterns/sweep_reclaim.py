from dataclasses import dataclass

import pandas as pd

from app.enums import TradeSide


@dataclass(slots=True)
class SweepSignal:
    valid: bool
    side: TradeSide | None
    score: float


def detect_sweep_reclaim(m5: pd.DataFrame) -> SweepSignal:
    if len(m5) < 10:
        return SweepSignal(False, None, 0.0)
    c = m5.tail(4)
    prev_high = m5["high"].tail(10).iloc[:-4].max()
    prev_low = m5["low"].tail(10).iloc[:-4].min()
    sweep_hi = c["high"].iloc[0] > prev_high and c["close"].iloc[1] < prev_high and c["close"].iloc[-1] < c["open"].iloc[-1]
    sweep_lo = c["low"].iloc[0] < prev_low and c["close"].iloc[1] > prev_low and c["close"].iloc[-1] > c["open"].iloc[-1]
    if sweep_lo:
        return SweepSignal(True, TradeSide.BUY, 86.0)
    if sweep_hi:
        return SweepSignal(True, TradeSide.SELL, 86.0)
    return SweepSignal(False, None, 35.0)
