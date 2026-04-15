from dataclasses import dataclass

from app.enums import SetupType


@dataclass(slots=True)
class Campaign:
    id: str
    symbol: str
    setup: SetupType
    open: bool = True
    addons_used: int = 0


class CampaignManager:
    def __init__(self) -> None:
        self.current: Campaign | None = None

    def has_open(self) -> bool:
        return self.current is not None and self.current.open

    def open_campaign(self, campaign: Campaign) -> None:
        if self.has_open():
            raise RuntimeError("campaign_already_open")
        self.current = campaign

    def close_campaign(self) -> None:
        if self.current:
            self.current.open = False
