import sqlite3
import json
from datetime import datetime

DB_PATH = "newsletter.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS newsletters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                week_label TEXT NOT NULL,
                stories TEXT NOT NULL,
                top_picks TEXT NOT NULL,
                raw_response TEXT NOT NULL
            )
        """)
        conn.commit()


def save_newsletter(week_label: str, stories: list, top_picks: dict, raw_response: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO newsletters (created_at, week_label, stories, top_picks, raw_response) VALUES (?, ?, ?, ?, ?)",
            (
                datetime.utcnow().isoformat(),
                week_label,
                json.dumps(stories),
                json.dumps(top_picks),
                raw_response,
            ),
        )
        conn.commit()


def get_latest():
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM newsletters ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if not row:
        return None
    return _deserialize(row)


def get_all():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM newsletters ORDER BY id DESC"
        ).fetchall()
    return [_deserialize(r) for r in rows]


def get_by_id(newsletter_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM newsletters WHERE id = ?", (newsletter_id,)
        ).fetchone()
    if not row:
        return None
    return _deserialize(row)


def _deserialize(row):
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "week_label": row["week_label"],
        "stories": json.loads(row["stories"]),
        "top_picks": json.loads(row["top_picks"]),
        "raw_response": row["raw_response"],
    }
