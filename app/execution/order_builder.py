from dataclasses import dataclass

from app.enums import TradeSide
from app.utils.rounding import round_price, round_to_step


@dataclass(slots=True)
class InstrumentRules:
    tick_size: float
    qty_step: float
    min_qty: float
    min_notional: float


class OrderBuilder:
    def build(
        self,
        symbol: str,
        side: TradeSide,
        qty: float,
        ref_price: float,
        order_type: str,
        rules: InstrumentRules,
        order_link_id: str,
    ) -> dict:
        qty = round_to_step(qty, rules.qty_step, down=True)
        payload = {
            "category": "linear",
            "symbol": symbol,
            "side": side.value,
            "orderType": "Limit" if order_type in {"POST_ONLY", "LIMIT"} else "Market",
            "qty": str(qty),
            "orderLinkId": order_link_id,
        }
        if payload["orderType"] == "Limit":
            payload["price"] = str(round_price(ref_price, rules.tick_size, side.value))
            if order_type == "POST_ONLY":
                payload["timeInForce"] = "PostOnly"
        return payload
