from pydantic import BaseModel, Field


class BybitRestResp(BaseModel):
    retCode: int
    retMsg: str
    result: dict = Field(default_factory=dict)
    time: int | None = None


class WsOrderEvent(BaseModel):
    orderId: str | None = None
    orderLinkId: str | None = None
    symbol: str
    side: str
    orderStatus: str | None = None


class WsPositionEvent(BaseModel):
    symbol: str
    side: str
    size: str
    avgPrice: str


class WsExecutionEvent(BaseModel):
    symbol: str
    side: str
    execQty: str
    execPrice: str
    orderLinkId: str | None = None
