from dataclasses import dataclass

import pandas as pd

from app.enums import Regime


@dataclass(slots=True)
class RegimeResult:
    regime: Regime
    score: float
    details: dict[str, float]


class RegimeEngine:
    def classify(self, m30: pd.DataFrame, m15: pd.DataFrame, btc_m15: pd.DataFrame) -> RegimeResult:
        r30 = m30.iloc[-1]
        r15 = m15.iloc[-1]
        slope = float(m15["ema20"].diff().tail(5).mean())
        trend_up = r15["ema20"] > r15["ema50"] and r30["ema20"] > r30["ema50"] and slope > 0
        trend_dn = r15["ema20"] < r15["ema50"] and r30["ema20"] < r30["ema50"] and slope < 0
        atr_exp = float(r15["atr"] / (m15["atr"].rolling(30).mean().iloc[-1] or 1))
        overlap = float(r15["overlap"])
        vwap_bias = float((r15["close"] - r15["vwap"]) / max(r15["vwap"], 1e-9))
        btc_bias = float((btc_m15["close"].iloc[-1] - btc_m15["ema20"].iloc[-1]) / btc_m15["ema20"].iloc[-1])
        if overlap > 0.78:
            return RegimeResult(Regime.CHOP, 20.0, {"overlap": overlap, "atr_exp": atr_exp, "btc_bias": btc_bias})
        if atr_exp < 0.65:
            return RegimeResult(Regime.NO_TRADE, 10.0, {"overlap": overlap, "atr_exp": atr_exp, "btc_bias": btc_bias})
        if trend_up and atr_exp > 1.15:
            reg = Regime.HOT_TREND_UP if abs(vwap_bias) > 0.001 else Regime.EXPANSION_UP
            return RegimeResult(reg, 90.0 if reg == Regime.HOT_TREND_UP else 80.0, {"overlap": overlap, "atr_exp": atr_exp, "btc_bias": btc_bias})
        if trend_dn and atr_exp > 1.15:
            reg = Regime.HOT_TREND_DOWN if abs(vwap_bias) > 0.001 else Regime.EXPANSION_DOWN
            return RegimeResult(reg, 90.0 if reg == Regime.HOT_TREND_DOWN else 80.0, {"overlap": overlap, "atr_exp": atr_exp, "btc_bias": btc_bias})
        return RegimeResult(Regime.NEUTRAL, 55.0, {"overlap": overlap, "atr_exp": atr_exp, "btc_bias": btc_bias})
