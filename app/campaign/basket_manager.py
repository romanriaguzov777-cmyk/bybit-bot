from dataclasses import dataclass, field


@dataclass(slots=True)
class Leg:
    qty: float
    entry: float
    stop: float


@dataclass(slots=True)
class Basket:
    symbol: str
    legs: list[Leg] = field(default_factory=list)

    def total_qty(self) -> float:
        return sum(l.qty for l in self.legs)

    def avg_entry(self) -> float:
        q = self.total_qty()
        return sum(l.qty * l.entry for l in self.legs) / q if q else 0.0
