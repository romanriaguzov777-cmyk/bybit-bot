import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS signals (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  symbol TEXT NOT NULL,
  setup TEXT NOT NULL,
  side TEXT NOT NULL,
  score REAL NOT NULL,
  score_class TEXT NOT NULL,
  regime TEXT NOT NULL,
  breakdown TEXT NOT NULL,
  decision TEXT NOT NULL,
  reason TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  order_link_id TEXT UNIQUE NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL,
  qty REAL NOT NULL,
  price REAL,
  status TEXT NOT NULL,
  payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fills (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  order_link_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL,
  qty REAL NOT NULL,
  price REAL NOT NULL,
  fee REAL NOT NULL,
  payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS campaigns (
  id TEXT PRIMARY KEY,
  ts_open TEXT NOT NULL,
  ts_close TEXT,
  symbol TEXT NOT NULL,
  setup TEXT NOT NULL,
  score_class TEXT NOT NULL,
  status TEXT NOT NULL,
  pnl REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS equity_snapshots (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  equity REAL NOT NULL,
  daily_pnl REAL NOT NULL,
  local_high REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS state_transitions (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  from_state TEXT NOT NULL,
  to_state TEXT NOT NULL,
  reason TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS errors (
  id INTEGER PRIMARY KEY,
  ts TEXT NOT NULL,
  source TEXT NOT NULL,
  message TEXT NOT NULL,
  payload TEXT
);
"""


def connect(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn
