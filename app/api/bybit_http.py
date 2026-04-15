import hashlib
import hmac
import json
import time
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.enums import Mode


class BybitHTTP:
    def __init__(self, api_key: str, api_secret: str, recv_window: int, mode: Mode) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.recv_window = recv_window
        self.base = "https://api-demo.bybit.com" if mode == Mode.DEMO else "https://api.bybit.com"
        self.client = httpx.AsyncClient(timeout=10)

    def _sign(self, ts: str, payload: str) -> str:
        raw = f"{ts}{self.api_key}{self.recv_window}{payload}"
        return hmac.new(self.api_secret.encode(), raw.encode(), hashlib.sha256).hexdigest()

    async def _request(self, method: str, path: str, params: dict[str, Any] | None = None, private: bool = False) -> dict[str, Any]:
        params = params or {}
        ts = str(int(time.time() * 1000))
        payload = json.dumps(params, separators=(",", ":")) if method != "GET" else "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        headers = {}
        if private:
            headers = {
                "X-BAPI-API-KEY": self.api_key,
                "X-BAPI-TIMESTAMP": ts,
                "X-BAPI-RECV-WINDOW": str(self.recv_window),
                "X-BAPI-SIGN": self._sign(ts, payload),
            }
        resp = await self.client.request(method, f"{self.base}{path}", params=params if method == "GET" else None, json=params if method != "GET" else None, headers=headers)
        resp.raise_for_status()
        return resp.json()

    @retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(4), reraise=True)
    async def get_instruments(self, symbol: str) -> dict[str, Any]:
        return await self._request("GET", "/v5/market/instruments-info", {"category": "linear", "symbol": symbol})

    async def get_kline(self, symbol: str, interval: str, limit: int = 200) -> dict[str, Any]:
        return await self._request("GET", "/v5/market/kline", {"category": "linear", "symbol": symbol, "interval": interval, "limit": limit})

    async def place_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/v5/order/create", payload, private=True)

    async def amend_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/v5/order/amend", payload, private=True)

    async def cancel_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/v5/order/cancel", payload, private=True)

    async def set_trading_stop(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/v5/position/trading-stop", payload, private=True)

    async def get_wallet(self) -> dict[str, Any]:
        return await self._request("GET", "/v5/account/wallet-balance", {"accountType": "UNIFIED", "coin": "USDT"}, private=True)

    async def get_positions(self, symbol: str) -> dict[str, Any]:
        return await self._request("GET", "/v5/position/list", {"category": "linear", "symbol": symbol}, private=True)
