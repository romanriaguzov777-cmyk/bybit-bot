import pandas as pd

from app.enums import Regime
from app.regime.regime_engine import RegimeEngine


def test_regime_notrade_on_low_atr() -> None:
    idx = pd.date_range("2025-01-01", periods=80, freq="15min", tz="UTC")
    base = pd.DataFrame({"open": 100, "high": 101, "low": 99.9, "close": 100.1, "volume": 10}, index=idx)
    base["ema20"] = 100
    base["ema50"] = 100
    base["atr"] = 0.1
    base["vwap"] = 100
    base["overlap"] = 0.2
    res = RegimeEngine().classify(base.resample("30min").last().dropna(), base, base)
    assert res.regime in {Regime.NO_TRADE, Regime.NEUTRAL, Regime.CHOP}
