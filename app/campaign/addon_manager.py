from app.enums import Phase
from app.campaign.basket_manager import Basket


class AddonManager:
    def can_addon(self, phase: Phase, basket: Basket, max_units: dict[str, int], first_leg_protected: bool, regime_intact: bool) -> bool:
        if not first_leg_protected or not regime_intact:
            return False
        return len(basket.legs) < (1 + max_units[phase.value])
