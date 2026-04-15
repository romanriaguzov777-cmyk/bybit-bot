from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.enums import Regime, ScoreClass, SetupType, TradeSide


@dataclass(slots=True)
class Candle:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class Signal:
    symbol: str
    setup: SetupType
    side: TradeSide
    regime: Regime
    score: float
    score_class: ScoreClass
    stop_price: float
    entry_price: float
    reason: str


@dataclass(slots=True)
class Position:
    symbol: str
    side: TradeSide
    qty: float
    entry_price: float
    stop_price: float
    unrealized_pnl: float
    opened_at: datetime
    campaign_id: Optional[str] = None
