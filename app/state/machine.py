from app.enums import BotState
from app.state.transitions import ALLOWED


class StateMachine:
    def __init__(self) -> None:
        self.state = BotState.IDLE

    def transition(self, to_state: BotState) -> tuple[BotState, BotState]:
        if to_state not in ALLOWED.get(self.state, set()):
            raise ValueError(f"invalid_transition:{self.state}->{to_state}")
        prev = self.state
        self.state = to_state
        return prev, to_state
