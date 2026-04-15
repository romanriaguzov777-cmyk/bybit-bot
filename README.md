# Bybit V5 Campaign Bot (USDT Perpetual)

Aggressive staged campaign bot for SOLUSDT/ETHUSDT with BTCUSDT regime filter.

## Features
- Bybit V5 REST wrappers: order create/amend/cancel, trading stop, instruments, wallet/position.
- Public/private websocket clients with reconnect.
- Data pipeline (M1->M5/M15/M30) with EMA20/EMA50, ATR, intraday VWAP, overlap, relative volume.
- Regime engine + 3 patterns: Sweep/Reclaim, Impulse Pullback Continuation, Compression Breakout.
- 5-gate scoring model (0-100) with A/A+/A++ classes.
- Risk ladder by phase (IGNITION/EXPANSION/PRESS), daily governor, recovery mode.
- Explicit state machine.
- SQLite logging for signals/transitions/errors.
- Unit tests for critical logic.

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Config
- Base defaults: `config/default.yaml`
- Demo profile: `config/demo.yaml`
- Live profile: `config/live.yaml`

Set in `.env`:
```env
BYBIT_API_KEY=...
BYBIT_API_SECRET=...
APP_CONFIG_PATH=config/demo.yaml
```

## Run (demo)
```bash
export APP_CONFIG_PATH=config/demo.yaml
python -m app.main
```

## Run (live)
```bash
export APP_CONFIG_PATH=config/live.yaml
python -m app.main
```

## Test
```bash
pytest -q
```

## Live checklist
1. API key has linear-perp trading permissions.
2. Account is one-way mode + isolated margin enabled.
3. Instrument constraints loaded (tick/step/min qty/min notional).
4. Funding lock window configured.
5. Risk ladder and daily stop match intended aggression.
6. Demo run logs state transitions/signals correctly before live switch.
