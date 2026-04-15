from app.api.bybit_http import BybitHTTP
from app.execution.order_builder import InstrumentRules, OrderBuilder
from app.types import Signal
from app.utils.ids import order_link_id


class ExecutionEngine:
    def __init__(self, http: BybitHTTP) -> None:
        self.http = http
        self.builder = OrderBuilder()
        self.seen_order_links: set[str] = set()

    async def execute_entry(self, signal: Signal, qty: float, rules: InstrumentRules, preference: list[str]) -> dict:
        link_id = order_link_id(signal.symbol)
        if link_id in self.seen_order_links:
            raise RuntimeError("duplicate_order_link")
        self.seen_order_links.add(link_id)
        for kind in preference:
            payload = self.builder.build(signal.symbol, signal.side, qty, signal.entry_price, kind, rules, link_id)
            resp = await self.http.place_order(payload)
            if resp.get("retCode") == 0:
                return resp
        raise RuntimeError("entry_failed")
