from app.utils.rounding import round_price, round_to_step


def test_round_to_step() -> None:
    assert round_to_step(1.234, 0.01) == 1.23


def test_round_price_buy() -> None:
    assert round_price(100.127, 0.05, "Buy") == 100.1
