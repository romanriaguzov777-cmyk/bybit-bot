from app.risk.recovery_manager import RecoveryManager


def test_recovery_switch() -> None:
    r = RecoveryManager(0.15, 0.07)
    assert r.update(80, 100)
    assert not r.update(95, 100)
