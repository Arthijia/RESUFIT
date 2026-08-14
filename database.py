"""
RESUFIT — Persistent Storage

Uses SQLite so screening history survives page refreshes and
new browser sessions, instead of resetting every time (as with
st.session_state alone).

Note: On Streamlit Community Cloud's free tier, the underlying
filesystem is ephemeral and resets on redeploys/sleep-wake cycles.
This still meaningfully improves on session-only storage — history
persists across page refreshes and multiple users during the same
running instance.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "resufit.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            match_score INTEGER NOT NULL,
            ats_score INTEGER NOT NULL,
            matched_count INTEGER NOT NULL,
            missing_count INTEGER NOT NULL,
            matched_skills TEXT,
            missing_skills TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_screening(match_score, ats_score, matched_skills, missing_skills):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO screenings
           (timestamp, match_score, ats_score, matched_count, missing_count, matched_skills, missing_skills)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            match_score,
            ats_score,
            len(matched_skills),
            len(missing_skills),
            ", ".join(sorted(matched_skills)),
            ", ".join(sorted(missing_skills)),
        )
    )
    conn.commit()
    conn.close()


def get_recent_screenings(limit=5):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT timestamp, match_score, ats_score, matched_count, missing_count
           FROM screenings ORDER BY id DESC LIMIT ?""",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "time": r[0],
            "match_score": r[1],
            "ats_score": r[2],
            "matched_count": r[3],
            "missing_count": r[4],
        }
        for r in rows
    ]


def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), AVG(match_score), AVG(ats_score) FROM screenings")
    row = cur.fetchone()
    conn.close()
    total = row[0] or 0
    avg_match = round(row[1]) if row[1] is not None else 0
    avg_ats = round(row[2]) if row[2] is not None else 0
    return {"total": total, "avg_match": avg_match, "avg_ats": avg_ats}


def clear_history():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM screenings")
    conn.commit()
    conn.close()
