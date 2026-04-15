import pandas as pd


def aggregate(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    out = (
        df.resample(timeframe)
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
    )
    return out
