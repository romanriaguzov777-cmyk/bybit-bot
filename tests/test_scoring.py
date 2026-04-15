from app.enums import ScoreClass
from app.scoring.scoring_engine import ScoringEngine


def test_score_classification() -> None:
    s = ScoringEngine().score(30, 25, 20, 15, 10)
    assert s.score == 100
    assert s.score_class == ScoreClass.AXX
