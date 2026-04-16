import asyncio
from typing import Any

import pandas as pd
import structlog

from app.api.bybit_http import BybitHTTP
from app.api.bybit_ws_private import PrivateWS
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
        self.private_ws = PrivateWS(secrets.api_key, secrets.api_secret, config.mode)
        self.regime_engine = RegimeEngine()
        self.scoring = ScoringEngine()
        self.risk = RiskEngine({k: v.model_dump() for k, v in config.risk_ladder.items()})
        self.campaigns = CampaignManager()
        self.recovery = RecoveryManager()
        self.m1_data: dict[str, pd.DataFrame] = {}
        self.day = utc_date_key()
        self.active_symbol: str | None = None
        self.last_regime: str | None = None
        self.last_score: float | None = None
        self.next_action: str = "bootstrap"
        self._shutdown = asyncio.Event()

    def _to_df(self, symbol: str, rows: list[list[str]]) -> pd.DataFrame:
        df = pd.DataFrame(rows, columns=["start", "open", "high", "low", "close", "volume", "turnover"])
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        df["ts"] = pd.to_datetime(df["start"].astype(int), unit="ms", utc=True)
        return df.set_index("ts")[["open", "high", "low", "close", "volume"]].sort_index()

    async def bootstrap(self) -> None:
        self.log.info("bootstrap_started", symbols=[*self.config.symbols, self.config.btc_filter_symbol])
        for symbol in [*self.config.symbols, self.config.btc_filter_symbol]:
            kl = await self.http.get_kline(symbol, "1", 500)
            self.m1_data[symbol] = self._to_df(symbol, kl["result"]["list"])
        self.log.info("bootstrap_finished", loaded_symbols=list(self.m1_data.keys()))

    async def _heartbeat_loop(self) -> None:
        while not self._shutdown.is_set():
            self.log.info(
                "heartbeat",
                current_state=self.state.state.value,
                active_symbol=self.active_symbol,
                open_campaign=self.campaigns.has_open(),
                last_regime=self.last_regime,
                last_score=self.last_score,
                next_action=self.next_action,
            )
            try:
                await asyncio.wait_for(self._shutdown.wait(), timeout=10)
            except TimeoutError:
                continue

    async def _public_ws_probe(self) -> None:
        self.log.info("ws_public_started")

    async def _private_ws_probe(self) -> None:
        self.log.info("ws_private_started")

    async def step(self) -> None:
        self.log.info("entering_state_scan")
        prev, now = self.state.transition(BotState.SCAN)
        self.repo.insert_state_transition(prev.value, now.value, "scan_start")
        self.next_action = "scan_symbols"
        for symbol in self.config.symbols:
            self.active_symbol = symbol
            features = build_market_features(self.m1_data[symbol].copy())
            btc_features = build_market_features(self.m1_data[self.config.btc_filter_symbol].copy())
            regime = self.regime_engine.classify(features.m30, features.m15, btc_features.m15)
            self.last_regime = regime.regime.value
            self.log.info("regime_result", symbol=symbol, regime=regime.regime.value, regime_score=regime.score, details=regime.details)
            if regime.regime in {Regime.CHOP, Regime.NO_TRADE}:
                self.next_action = "continue_scan"
                self.log.info("no_trade_reason", symbol=symbol, reason=f"regime_gate:{regime.regime.value}")
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
                    self.log.info("no_trade_reason", symbol=symbol, setup=setup.value, reason="pattern_not_valid")
                    continue
                scored = self.scoring.score(
                    regime_score=min(regime.score / 3, 30),
                    location_score=min(loc_score / 4, 25),
                    trigger_score=16,
                    execution_score=12,
                    risk_fit=8,
                )
                self.last_score = scored.score
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
                self.repo.insert_signal(
                    {
                        "symbol": signal.symbol,
                        "setup": signal.setup.value,
                        "side": signal.side.value,
                        "score": signal.score,
                        "score_class": signal.score_class.value,
                        "regime": signal.regime.value,
                        "breakdown": scored.breakdown.model_dump(),
                        "decision": "candidate",
                        "reason": signal.reason,
                    }
                )
                if scored.score_class.value == "NO_TRADE":
                    self.log.info("no_trade_reason", symbol=symbol, setup=setup.value, reason="score_below_threshold", score=scored.score)
                    continue
                if self.campaigns.has_open():
                    self.log.info("no_trade_reason", symbol=symbol, setup=setup.value, reason="campaign_already_open")
                    continue
                phase = detect_phase(100.0)
                r = self.risk.size_position(100.0, signal.entry_price, signal.stop_price, phase, signal.score_class, 0.1, 0.1, 5)
                if not r.valid:
                    self.log.info(
                        "order_decision_summary",
                        symbol=symbol,
                        setup=setup.value,
                        score=scored.score,
                        score_class=scored.score_class.value,
                        decision="reject",
                        reason=r.reason,
                        qty=r.qty,
                    )
                    continue
                campaign_id = order_link_id("cmp")
                self.campaigns.open_campaign(Campaign(id=campaign_id, symbol=symbol, setup=setup))
                self.next_action = "manage_open_campaign"
                self.log.info(
                    "order_decision_summary",
                    symbol=symbol,
                    setup=setup.value,
                    score=scored.score,
                    score_class=scored.score_class.value,
                    decision="accepted",
                    qty=r.qty,
                    risk_value=r.risk_value,
                    campaign_id=campaign_id,
                )
                return
        self.next_action = "sleep"

    async def run(self) -> None:
        ws_public_task: asyncio.Task[None] | None = None
        ws_private_task: asyncio.Task[None] | None = None
        heartbeat_task: asyncio.Task[None] | None = None
        exit_reason = "unknown"
        try:
            await self.bootstrap()
            ws_public_task = asyncio.create_task(self._public_ws_probe(), name="ws_public_probe")
            ws_private_task = asyncio.create_task(self._private_ws_probe(), name="ws_private_probe")
            heartbeat_task = asyncio.create_task(self._heartbeat_loop(), name="heartbeat")
            while True:
                await self.step()
                self.log.info("sleeping_next_cycle", sleep_seconds=5)
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            exit_reason = "cancelled"
            self.log.info("runner_cancelled")
            raise
        except KeyboardInterrupt:
            exit_reason = "keyboard_interrupt"
            self.log.info("runner_keyboard_interrupt")
            raise
        except Exception as exc:
            exit_reason = f"exception:{exc.__class__.__name__}"
            self.log.exception("runner_exception", error=str(exc))
            raise
        finally:
            self._shutdown.set()
            for task in (ws_public_task, ws_private_task, heartbeat_task):
                if task is not None and not task.done():
                    task.cancel()
            self.log.info("shutdown", reason=exit_reason, final_state=self.state.state.value)
