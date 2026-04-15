from collections import defaultdict, deque
from datetime import datetime

from app.types import Candle


class CandleStore:
    def __init__(self, maxlen: int = 2000) -> None:
        self.data: dict[str, deque[Candle]] = defaultdict(lambda: deque(maxlen=maxlen))

    def append(self, symbol: str, candle: Candle) -> None:
        self.data[symbol].append(candle)

    def latest(self, symbol: str, n: int = 1) -> list[Candle]:
        return list(self.data[symbol])[-n:]

    @staticmethod
    def from_ws(payload: dict) -> Candle | None:
        if "data" not in payload:
            return None
        row = payload["data"][0]
        return Candle(
            ts=datetime.fromtimestamp(int(row["start"]) / 1000),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
        )
