from app.enums import BotState
from app.state.machine import StateMachine


def test_transition_flow() -> None:
    m = StateMachine()
    m.transition(BotState.SCAN)
    m.transition(BotState.ARMED)
    assert m.state == BotState.ARMED
