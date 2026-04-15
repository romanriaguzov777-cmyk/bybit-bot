from dataclasses import dataclass

from app.enums import Phase, ScoreClass
from app.utils.rounding import round_to_step


@dataclass(slots=True)
class RiskResult:
    qty: float
    risk_value: float
    valid: bool
    reason: str


class RiskEngine:
    def __init__(self, ladder: dict[str, dict[str, tuple[float, float]]]) -> None:
        self.ladder = ladder

    def risk_pct(self, phase: Phase, score_class: ScoreClass, conservative: bool = False) -> float:
        key = "a" if score_class == ScoreClass.A else "a_plus" if score_class == ScoreClass.A_PLUS else "axx"
        lo, hi = self.ladder[phase.value][key]
        return lo if conservative else (lo + hi) / 2

    def size_position(
        self,
        equity: float,
        entry: float,
        stop: float,
        phase: Phase,
        score_class: ScoreClass,
        qty_step: float,
        min_qty: float,
        min_notional: float,
    ) -> RiskResult:
        if stop == entry:
            return RiskResult(0.0, 0.0, False, "zero_stop_distance")
        budget = equity * self.risk_pct(phase, score_class)
        distance = abs(entry - stop)
        raw_qty = budget / max(distance, 1e-9)
        qty = round_to_step(raw_qty, qty_step, down=True)
        if qty < min_qty:
            return RiskResult(qty, 0.0, False, "below_min_qty")
        notional = qty * entry
        if notional < min_notional:
            return RiskResult(qty, 0.0, False, "below_min_notional")
        risk = qty * distance
        if risk > budget * 1.02:
            return RiskResult(qty, risk, False, "risk_after_rounding_exceeds_budget")
        return RiskResult(qty, risk, True, "ok")
