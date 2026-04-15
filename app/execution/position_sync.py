from typing import Any


def normalize_position(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": raw.get("symbol"),
        "side": raw.get("side"),
        "qty": float(raw.get("size", 0)),
        "entry_price": float(raw.get("avgPrice", 0)),
    }
