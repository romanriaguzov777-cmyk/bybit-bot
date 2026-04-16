from dataclasses import dataclass

import pandas as pd

from app.enums import TradeSide


@dataclass(slots=True)
class BreakoutSignal:
    valid: bool
    side: TradeSide | None
    width: float
    score: float


def detect_compression_breakout(m5: pd.DataFrame) -> BreakoutSignal:
    if len(m5) < 15:
        return BreakoutSignal(False, None, 0.0, 0.0)
    box = m5.tail(8)
    width = float((box["high"].max() - box["low"].min()) / max(box["close"].mean(), 1e-9))
    tails = ((box["high"] - box[["open", "close"]].max(axis=1)) + (box[["open", "close"]].min(axis=1) - box["low"]))
    noisy = float((tails / (box["high"] - box["low"]).replace(0, 1e-9)).mean()) > 0.55
    last = m5.iloc[-1]
    if width < 0.008 and not noisy:
        if last["close"] > box["high"].iloc[:-1].max():
            return BreakoutSignal(True, TradeSide.BUY, width, 80.0)
        if last["close"] < box["low"].iloc[:-1].min():
            return BreakoutSignal(True, TradeSide.SELL, width, 80.0)
    return BreakoutSignal(False, None, width, 45.0)
