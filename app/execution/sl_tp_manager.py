from dataclasses import dataclass


@dataclass(slots=True)
class ManageDecision:
    action: str
    new_stop: float | None = None
    reduce_ratio: float | None = None


class SLTPManager:
    def decision(self, r_multiple: float, bars_open: int, strong_trend: bool) -> ManageDecision:
        if bars_open >= 5 and r_multiple < 0.3:
            return ManageDecision("scratch")
        if r_multiple >= 1.0:
            return ManageDecision("move_stop_be_plus", new_stop=0.05)
        if 1.2 <= r_multiple <= 1.5 and not strong_trend:
            return ManageDecision("partial", reduce_ratio=0.25)
        if r_multiple >= 2.0:
            return ManageDecision("trail")
        return ManageDecision("hold")
