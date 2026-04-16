import asyncio
import hashlib
import hmac
import json
import time
from collections.abc import AsyncIterator

import websockets

from app.enums import Mode


class PrivateWS:
    def __init__(self, api_key: str, api_secret: str, mode: Mode) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.url = "wss://stream-demo.bybit.com/v5/private" if mode == Mode.DEMO else "wss://stream.bybit.com/v5/private"

    def _sign(self, expires: int) -> str:
        payload = f"GET/realtime{expires}"
        return hmac.new(self.api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    async def stream_private(self) -> AsyncIterator[dict]:
        while True:
            async with websockets.connect(self.url, ping_interval=20, ping_timeout=10) as ws:
                expires = int((time.time() + 10) * 1000)
                await ws.send(json.dumps({"op": "auth", "args": [self.api_key, expires, self._sign(expires)]}))
                await ws.send(json.dumps({"op": "subscribe", "args": ["order", "position", "execution"]}))
                async for msg in ws:
                    yield json.loads(msg)
            await asyncio.sleep(1)
