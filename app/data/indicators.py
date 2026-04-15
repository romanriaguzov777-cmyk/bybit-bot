import numpy as np
import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    h_l = df["high"] - df["low"]
    h_pc = (df["high"] - df["close"].shift()).abs()
    l_pc = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def intraday_vwap(df: pd.DataFrame) -> pd.Series:
    pxv = (df["close"] * df["volume"]).cumsum()
    vol = df["volume"].cumsum().replace(0, np.nan)
    return pxv / vol


def overlap_ratio(df: pd.DataFrame, window: int = 10) -> pd.Series:
    prev_high = df["high"].shift(1)
    prev_low = df["low"].shift(1)
    overlap = ((df["low"] <= prev_high) & (df["high"] >= prev_low)).astype(float)
    return overlap.rolling(window).mean()


def relative_volume(df: pd.DataFrame, window: int = 20) -> pd.Series:
    return df["volume"] / df["volume"].rolling(window).mean()
