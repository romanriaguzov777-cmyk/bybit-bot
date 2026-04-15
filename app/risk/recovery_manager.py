class RecoveryManager:
    def __init__(self, on_threshold: float = 0.15, off_threshold: float = 0.07) -> None:
        self.on_threshold = on_threshold
        self.off_threshold = off_threshold
        self.enabled = False

    def update(self, equity: float, local_high: float) -> bool:
        drawdown = (local_high - equity) / max(local_high, 1e-9)
        if not self.enabled and drawdown > self.on_threshold:
            self.enabled = True
        elif self.enabled and drawdown < self.off_threshold:
            self.enabled = False
        return self.enabled
