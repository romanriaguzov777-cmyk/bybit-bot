from dataclasses import dataclass

import pandas as pd

from app.data.aggregators import aggregate
from app.data.indicators import atr, ema, intraday_vwap, overlap_ratio, relative_volume


@dataclass(slots=True)
class MarketFeatures:
    m1: pd.DataFrame
    m5: pd.DataFrame
    m15: pd.DataFrame
    m30: pd.DataFrame


def build_market_features(df_m1: pd.DataFrame) -> MarketFeatures:
    m5 = aggregate(df_m1, "5min")
    m15 = aggregate(df_m1, "15min")
    m30 = aggregate(df_m1, "30min")
    for frame in (m1 := df_m1, m5, m15, m30):
        frame["ema20"] = ema(frame["close"], 20)
        frame["ema50"] = ema(frame["close"], 50)
        frame["atr"] = atr(frame)
        frame["vwap"] = intraday_vwap(frame)
        frame["overlap"] = overlap_ratio(frame)
        frame["rel_vol"] = relative_volume(frame)
    return MarketFeatures(m1=m1, m5=m5, m15=m15, m30=m30)
