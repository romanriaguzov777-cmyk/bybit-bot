from app.enums import Phase
from app.risk.daily_governor import DailyGovernor, DailyState


def test_daily_lock_by_loss() -> None:
    g = DailyGovernor({Phase.IGNITION: 0.18, Phase.EXPANSION: 0.14, Phase.PRESS: 0.1})
    s = DailyState(day_key="2025-01-01", start_equity=100, pnl=-19)
    assert g.check_lock(Phase.IGNITION, s)
