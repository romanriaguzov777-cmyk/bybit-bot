from pydantic import BaseModel


class SymbolMeta(BaseModel):
    symbol: str
    tick_size: float
    qty_step: float
    min_qty: float
    min_notional: float
