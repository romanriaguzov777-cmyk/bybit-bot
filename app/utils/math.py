
def pct_change(a: float, b: float) -> float:
    if a == 0:
        return 0.0
    return (b - a) / a
