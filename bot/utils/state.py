"""SQLite-backed bot state persistence."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional


SCHEMA = """
CREATE TABLE IF NOT EXISTS bot_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS task_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT,
    status TEXT,
    timestamp TEXT,
    details TEXT
);
CREATE TABLE IF NOT EXISTS error_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT,
    screenshot_path TEXT,
    timestamp TEXT,
    details TEXT
);
"""


class BotState:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    # ---------------------------------------------------------- key/value
    def get(self, key: str, default: Any = None) -> Any:
        cur = self._conn.execute("SELECT value FROM bot_state WHERE key=?", (key,))
        row = cur.fetchone()
        if row is None:
            return default
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return row[0]

    def set(self, key: str, value: Any) -> None:
        payload = json.dumps(value)
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            "INSERT INTO bot_state(key, value, updated_at) VALUES(?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (key, payload, now),
        )
        self._conn.commit()

    def all_state(self) -> dict:
        cur = self._conn.execute("SELECT key, value FROM bot_state")
        out = {}
        for k, v in cur.fetchall():
            try:
                out[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                out[k] = v
        return out

    # ------------------------------------------------------------- logging
    def log_task(self, task_name: str, status: str, details: str = "") -> None:
        self._conn.execute(
            "INSERT INTO task_log(task_name, status, timestamp, details) VALUES(?,?,?,?)",
            (task_name, status, datetime.utcnow().isoformat(), details),
        )
        self._conn.commit()

    def log_error(self, error_type: str, screenshot_path: str = "", details: str = "") -> None:
        self._conn.execute(
            "INSERT INTO error_log(error_type, screenshot_path, timestamp, details) VALUES(?,?,?,?)",
            (error_type, screenshot_path, datetime.utcnow().isoformat(), details),
        )
        self._conn.commit()

    def recent_tasks(self, limit: int = 20) -> Iterable[tuple]:
        cur = self._conn.execute(
            "SELECT task_name, status, timestamp, details FROM task_log "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()

    def close(self) -> None:
        self._conn.close()
