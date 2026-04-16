from enum import Enum


class TradeSide(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


class Mode(str, Enum):
    DEMO = "demo"
    LIVE = "live"


class Regime(str, Enum):
    HOT_TREND_UP = "HOT_TREND_UP"
    HOT_TREND_DOWN = "HOT_TREND_DOWN"
    EXPANSION_UP = "EXPANSION_UP"
    EXPANSION_DOWN = "EXPANSION_DOWN"
    NEUTRAL = "NEUTRAL"
    CHOP = "CHOP"
    NO_TRADE = "NO_TRADE"


class SetupType(str, Enum):
    SWEEP_RECLAIM = "SWEEP_RECLAIM"
    IMPULSE_PULLBACK = "IMPULSE_PULLBACK"
    COMPRESSION_BREAKOUT = "COMPRESSION_BREAKOUT"


class ScoreClass(str, Enum):
    AXX = "A++ Prime"
    A_PLUS = "A+"
    A = "A"
    NO_TRADE = "NO_TRADE"


class Phase(str, Enum):
    IGNITION = "IGNITION"
    EXPANSION = "EXPANSION"
    PRESS = "PRESS"


class BotState(str, Enum):
    IDLE = "IDLE"
    SCAN = "SCAN"
    NO_TRADE = "NO_TRADE"
    ARMED = "ARMED"
    ENTRY_PENDING = "ENTRY_PENDING"
    POSITION_OPEN = "POSITION_OPEN"
    MANAGE = "MANAGE"
    ADDON_READY = "ADDON_READY"
    COOLDOWN = "COOLDOWN"
    DAILY_LOCK = "DAILY_LOCK"
    RECOVERY = "RECOVERY"
    AXX_PRIME_USED = "AXX_PRIME_USED"
