import asyncio
from typing import Any

import pandas as pd
import structlog

from app.api.bybit_http import BybitHTTP
from app.api.bybit_ws_public import PublicWS
from app.campaign.campaign_manager import Campaign, CampaignManager
from app.data.market_state import build_market_features
from app.enums import BotState, Regime, SetupType
from app.patterns.compression_breakout import detect_compression_breakout
from app.patterns.continuation import detect_continuation
from app.patterns.sweep_reclaim import detect_sweep_reclaim
from app.regime.regime_engine import RegimeEngine
from app.risk.phase_manager import detect_phase
from app.risk.recovery_manager import RecoveryManager
from app.risk.risk_engine import RiskEngine
from app.scoring.scoring_engine import ScoringEngine
from app.state.machine import StateMachine
from app.storage.repositories import Repository
from app.types import Signal
from app.utils.ids import order_link_id
from app.utils.time import utc_date_key


class BotRunner:
    def __init__(self, config: Any, secrets: Any, repo: Repository) -> None:
        self.config = config
        self.secrets = secrets
        self.repo = repo
        self.log = structlog.get_logger("runner")
        self.state = StateMachine()
        self.http = BybitHTTP(secrets.api_key, secrets.api_secret, secrets.recv_window, config.mode)
        self.ws = PublicWS(config.mode)
        self.regime_engine = RegimeEngine()
        self.scoring = ScoringEngine()
        self.risk = RiskEngine({k: v.model_dump() for k, v in config.risk_ladder.items()})
        self.campaigns = CampaignManager()
        self.recovery = RecoveryManager()
        self.m1_data: dict[str, pd.DataFrame] = {}
        self.day = utc_date_key()

    def _to_df(self, symbol: str, rows: list[list[str]]) -> pd.DataFrame:
        df = pd.DataFrame(rows, columns=["start", "open", "high", "low", "close", "volume", "turnover"])
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        df["ts"] = pd.to_datetime(df["start"].astype(int), unit="ms", utc=True)
        return df.set_index("ts")[["open", "high", "low", "close", "volume"]].sort_index()

    async def bootstrap(self) -> None:
        for symbol in [*self.config.symbols, self.config.btc_filter_symbol]:
            kl = await self.http.get_kline(symbol, "1", 500)
            self.m1_data[symbol] = self._to_df(symbol, kl["result"]["list"])

    async def step(self) -> None:
        prev, now = self.state.transition(BotState.SCAN)
        self.repo.insert_state_transition(prev.value, now.value, "scan_start")
        for symbol in self.config.symbols:
            features = build_market_features(self.m1_data[symbol].copy())
            btc_features = build_market_features(self.m1_data[self.config.btc_filter_symbol].copy())
            regime = self.regime_engine.classify(features.m30, features.m15, btc_features.m15)
            if regime.regime in {Regime.CHOP, Regime.NO_TRADE}:
                continue
            cont = detect_continuation(features.m5)
            sweep = detect_sweep_reclaim(features.m5)
            brk = detect_compression_breakout(features.m5)
            candidates = [
                (SetupType.IMPULSE_PULLBACK, cont.valid, cont.side, cont.score),
                (SetupType.SWEEP_RECLAIM, sweep.valid, sweep.side, sweep.score),
                (SetupType.COMPRESSION_BREAKOUT, brk.valid, brk.side, brk.score),
            ]
            for setup, valid, side, loc_score in candidates:
                if not valid or side is None:
                    continue
                scored = self.scoring.score(regime_score=min(regime.score / 3, 30), location_score=min(loc_score / 4, 25), trigger_score=16, execution_score=12, risk_fit=8)
                signal = Signal(
                    symbol=symbol,
                    setup=setup,
                    side=side,
                    regime=regime.regime,
                    score=scored.score,
                    score_class=scored.score_class,
                    entry_price=float(features.m1["close"].iloc[-1]),
                    stop_price=float(features.m5["low"].iloc[-2] if side.value == "Buy" else features.m5["high"].iloc[-2]),
                    reason="pattern_and_regime_match",
                )
                self.repo.insert_signal({
                    "symbol": signal.symbol,
                    "setup": signal.setup.value,
                    "side": signal.side.value,
                    "score": signal.score,
                    "score_class": signal.score_class.value,
                    "regime": signal.regime.value,
                    "breakdown": scored.breakdown.model_dump(),
                    "decision": "candidate",
                    "reason": signal.reason,
                })
                if scored.score_class.value == "NO_TRADE" or self.campaigns.has_open():
                    continue
                phase = detect_phase(100.0)
                r = self.risk.size_position(100.0, signal.entry_price, signal.stop_price, phase, signal.score_class, 0.1, 0.1, 5)
                if not r.valid:
                    continue
                self.campaigns.open_campaign(Campaign(id=order_link_id("cmp"), symbol=symbol, setup=setup))
                return

    async def run(self) -> None:
        await self.bootstrap()
        while True:
            await self.step()
            await asyncio.sleep(5)
