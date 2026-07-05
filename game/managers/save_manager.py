"""SQLite save/load manager."""

import json
import sqlite3
from pathlib import Path

from game.core.constants import DATABASE_DIR
from game.core.events import EVT_SAVE, EVT_LOAD


class SaveManager:
    """Persists game state to SQLite."""

    DB_PATH = DATABASE_DIR / "prairieville.db"

    def __init__(self, event_bus):
        self.events = event_bus
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.DB_PATH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saves (
                slot INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save(self, data: dict, slot: int = 0):
        conn = sqlite3.connect(str(self.DB_PATH))
        conn.execute(
            "INSERT OR REPLACE INTO saves (slot, data, updated_at) VALUES (?, ?, datetime('now'))",
            (slot, json.dumps(data)),
        )
        conn.commit()
        conn.close()
        self.events.emit(EVT_SAVE, slot=slot)

    def load(self, slot: int = 0) -> dict | None:
        conn = sqlite3.connect(str(self.DB_PATH))
        row = conn.execute("SELECT data FROM saves WHERE slot = ?", (slot,)).fetchone()
        conn.close()
        if row:
            data = json.loads(row[0])
            self.events.emit(EVT_LOAD, slot=slot)
            return data
        return None

    def has_save(self, slot: int = 0) -> bool:
        conn = sqlite3.connect(str(self.DB_PATH))
        row = conn.execute("SELECT 1 FROM saves WHERE slot = ?", (slot,)).fetchone()
        conn.close()
        return row is not None
