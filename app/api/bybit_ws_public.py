import asyncio
import json
from collections.abc import AsyncIterator

import websockets

from app.enums import Mode


class PublicWS:
    def __init__(self, mode: Mode) -> None:
        self.url = "wss://stream-demo.bybit.com/v5/public/linear" if mode == Mode.DEMO else "wss://stream.bybit.com/v5/public/linear"

    async def stream_kline(self, symbols: list[str], interval: str = "1") -> AsyncIterator[dict]:
        topics = [f"kline.{interval}.{s}" for s in symbols]
        while True:
            async with websockets.connect(self.url, ping_interval=20, ping_timeout=10) as ws:
                await ws.send(json.dumps({"op": "subscribe", "args": topics}))
                async for msg in ws:
                    yield json.loads(msg)
            await asyncio.sleep(1)
