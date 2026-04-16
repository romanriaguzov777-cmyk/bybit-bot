from app.campaign.addon_manager import AddonManager
from app.campaign.basket_manager import Basket, Leg
from app.enums import Phase


def test_addon_eligibility() -> None:
    b = Basket(symbol="SOLUSDT", legs=[Leg(1, 100, 99)])
    ok = AddonManager().can_addon(Phase.IGNITION, b, {"IGNITION": 1, "EXPANSION": 2, "PRESS": 2}, True, True)
    assert ok
