import sqlite3
import json
from datetime import datetime, timezone

DB = "newsletter.db"


def init():
    with sqlite3.connect(DB) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)


def save(data: dict) -> int:
    with sqlite3.connect(DB) as con:
        cur = con.execute(
            "INSERT INTO issues (created_at, data) VALUES (?, ?)",
            (datetime.now(tz=timezone.utc).isoformat(), json.dumps(data)),
        )
        return cur.lastrowid


def list_issues() -> list:
    with sqlite3.connect(DB) as con:
        rows = con.execute(
            "SELECT id, created_at, data FROM issues ORDER BY id DESC"
        ).fetchall()
    return [{"id": r[0], "created_at": r[1], **json.loads(r[2])} for r in rows]


def get_issue(issue_id: int) -> dict | None:
    with sqlite3.connect(DB) as con:
        row = con.execute(
            "SELECT id, created_at, data FROM issues WHERE id = ?", (issue_id,)
        ).fetchone()
    if not row:
        return None
    return {"id": row[0], "created_at": row[1], **json.loads(row[2])}
