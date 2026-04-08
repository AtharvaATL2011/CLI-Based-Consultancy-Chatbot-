"""
memory.py — stores conversation history using SQLite.
"""

import sqlite3
import uuid
from datetime import datetime
from chatbot.config import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                user        TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                domain      TEXT,
                timestamp   TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        conn.commit()


class Memory:
    def __init__(self, user: str = "default", resume: bool = True):
        self.user = user
        self.session_id = self._load_or_create_session(user, resume)
        self._messages: list[dict] = self._load_messages()

    def add(self, role: str, content: str, domain: str = "general") -> None:
        self._messages.append({"role": role, "content": content})
        with _connect() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, domain, timestamp) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.session_id, role, content, domain, datetime.utcnow().isoformat()),
            )
            conn.commit()

    def get_messages(self) -> list[dict]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()
        with _connect() as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (self.session_id,))
            conn.commit()

    def message_count(self) -> int:
        return len(self._messages)

    def _load_or_create_session(self, user: str, resume: bool) -> str:
        with _connect() as conn:
            if resume:
                row = conn.execute(
                    "SELECT id FROM sessions WHERE user = ? ORDER BY created_at DESC LIMIT 1",
                    (user,),
                ).fetchone()
                if row:
                    return row["id"]
            session_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO sessions (id, user, created_at) VALUES (?, ?, ?)",
                (session_id, user, datetime.utcnow().isoformat()),
            )
            conn.commit()
            return session_id

    def _load_messages(self) -> list[dict]:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
                (self.session_id,),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]