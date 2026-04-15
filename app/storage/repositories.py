import json
import sqlite3
from typing import Any

from app.utils.time import utc_now


class Repository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def insert_signal(self, payload: dict[str, Any]) -> None:
        self.conn.execute(
            "INSERT INTO signals(ts,symbol,setup,side,score,score_class,regime,breakdown,decision,reason) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                utc_now().isoformat(),
                payload["symbol"],
                payload["setup"],
                payload["side"],
                payload["score"],
                payload["score_class"],
                payload["regime"],
                json.dumps(payload["breakdown"]),
                payload["decision"],
                payload["reason"],
            ),
        )
        self.conn.commit()

    def insert_state_transition(self, from_state: str, to_state: str, reason: str) -> None:
        self.conn.execute(
            "INSERT INTO state_transitions(ts,from_state,to_state,reason) VALUES(?,?,?,?)",
            (utc_now().isoformat(), from_state, to_state, reason),
        )
        self.conn.commit()

    def insert_error(self, source: str, message: str, payload: dict[str, Any] | None = None) -> None:
        self.conn.execute(
            "INSERT INTO errors(ts,source,message,payload) VALUES(?,?,?,?)",
            (utc_now().isoformat(), source, message, json.dumps(payload or {})),
        )
        self.conn.commit()
