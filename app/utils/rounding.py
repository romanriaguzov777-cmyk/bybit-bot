import math


def round_to_step(value: float, step: float, down: bool = True) -> float:
    if step <= 0:
        return value
    factor = value / step
    rounded = math.floor(factor) if down else math.ceil(factor)
    return round(rounded * step, 10)


def round_price(price: float, tick_size: float, side: str) -> float:
    return round_to_step(price, tick_size, down=side.lower() == "buy")
