from app.enums import ScoreClass
from app.scoring.score_models import ScoreBreakdown, ScoredSignal


class ScoringEngine:
    def classify(self, score: float) -> ScoreClass:
        if score >= 90:
            return ScoreClass.AXX
        if score >= 80:
            return ScoreClass.A_PLUS
        if score >= 68:
            return ScoreClass.A
        return ScoreClass.NO_TRADE

    def score(self, regime_score: float, location_score: float, trigger_score: float, execution_score: float, risk_fit: float) -> ScoredSignal:
        breakdown = ScoreBreakdown(
            regime=min(regime_score, 30.0),
            location=min(location_score, 25.0),
            trigger=min(trigger_score, 20.0),
            execution=min(execution_score, 15.0),
            risk_fit=min(risk_fit, 10.0),
        )
        total = breakdown.total
        return ScoredSignal(score=total, score_class=self.classify(total), breakdown=breakdown)
