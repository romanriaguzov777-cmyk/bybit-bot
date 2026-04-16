from app.enums import Phase


def detect_phase(equity: float) -> Phase:
    if equity < 120:
        return Phase.IGNITION
    if equity < 400:
        return Phase.EXPANSION
    return Phase.PRESS
