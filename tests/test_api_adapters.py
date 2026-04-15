from app.api.adapters import WsExecutionEvent


def test_ws_payload_parse() -> None:
    evt = WsExecutionEvent.model_validate({"symbol": "SOLUSDT", "side": "Buy", "execQty": "1", "execPrice": "120"})
    assert evt.symbol == "SOLUSDT"
