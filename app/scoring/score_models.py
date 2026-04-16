from pydantic import BaseModel

from app.enums import ScoreClass


class ScoreBreakdown(BaseModel):
    regime: float
    location: float
    trigger: float
    execution: float
    risk_fit: float

    @property
    def total(self) -> float:
        return self.regime + self.location + self.trigger + self.execution + self.risk_fit


class ScoredSignal(BaseModel):
    score: float
    score_class: ScoreClass
    breakdown: ScoreBreakdown
