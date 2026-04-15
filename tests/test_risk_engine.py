from app.enums import Phase, ScoreClass
from app.risk.risk_engine import RiskEngine


def test_risk_qty() -> None:
    engine = RiskEngine({
        "IGNITION": {"a": (0.06, 0.08), "a_plus": (0.1, 0.12), "axx": (0.12, 0.15)},
        "EXPANSION": {"a": (0.05, 0.06), "a_plus": (0.08, 0.1), "axx": (0.1, 0.12)},
        "PRESS": {"a": (0.04, 0.05), "a_plus": (0.06, 0.08), "axx": (0.08, 0.1)},
    })
    result = engine.size_position(100, 150, 148, Phase.IGNITION, ScoreClass.A_PLUS, 0.1, 0.1, 5)
    assert result.valid
    assert result.qty > 0
