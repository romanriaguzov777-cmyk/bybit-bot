from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.enums import Mode


class ScoreThresholds(BaseModel):
    a: int = 68
    a_plus: int = 80
    axx: int = 90


class RiskBand(BaseModel):
    a: tuple[float, float]
    a_plus: tuple[float, float]
    axx: tuple[float, float]


class DailyLimits(BaseModel):
    ignition: float = 0.18
    expansion: float = 0.14
    press: float = 0.10
    consecutive_losses_ignition: int = 2


class AppConfig(BaseModel):
    mode: Mode = Mode.DEMO
    symbols: list[str] = Field(default_factory=lambda: ["SOLUSDT", "ETHUSDT"])
    btc_filter_symbol: str = "BTCUSDT"
    sqlite_path: str = "bot.db"
    risk_ladder: dict[str, RiskBand]
    daily_limits: DailyLimits = DailyLimits()
    score_thresholds: ScoreThresholds = ScoreThresholds()
    funding_lock_minutes: int = 20
    max_open_campaigns: int = 1
    addon_max: dict[str, int] = Field(default_factory=lambda: {"IGNITION": 1, "EXPANSION": 2, "PRESS": 2})
    execution_preference: list[str] = Field(default_factory=lambda: ["POST_ONLY", "LIMIT", "MARKET"])
    log_level: str = "INFO"
    heartbeat_seconds: int = 20


class SecretSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BYBIT_")
    api_key: str = ""
    api_secret: str = ""
    recv_window: int = 5000
    app_config_path: str = Field(default="config/demo.yaml", alias="APP_CONFIG_PATH")


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        payload: dict[str, Any] = yaml.safe_load(f)
    return AppConfig.model_validate(payload)
