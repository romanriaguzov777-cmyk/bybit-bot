from dataclasses import dataclass

from app.enums import Phase


@dataclass(slots=True)
class DailyState:
    day_key: str
    start_equity: float
    pnl: float = 0.0
    consecutive_losses: int = 0
    axx_stopped: bool = False
    locked: bool = False


class DailyGovernor:
    def __init__(self, limits: dict[Phase, float], ignition_consecutive: int = 2) -> None:
        self.limits = limits
        self.ignition_consecutive = ignition_consecutive

    def check_lock(self, phase: Phase, state: DailyState) -> bool:
        if state.locked:
            return True
        if state.pnl <= -state.start_equity * self.limits[phase]:
            state.locked = True
        if phase == Phase.IGNITION and state.consecutive_losses >= self.ignition_consecutive:
            state.locked = True
        if phase == Phase.IGNITION and state.axx_stopped:
            state.locked = True
        return state.locked
