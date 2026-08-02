"""
CivicTrace - Database helpers
Simple SQLite persistence for reports and uploaded minutes.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent / "civictrace.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_date TEXT NOT NULL,
            meeting_title TEXT NOT NULL,
            motion_title TEXT NOT NULL,
            description TEXT,
            mover TEXT,
            seconder TEXT,
            outcome TEXT NOT NULL,
            votes_json TEXT NOT NULL DEFAULT '{}',
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS minutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_date TEXT NOT NULL,
            meeting_title TEXT NOT NULL,
            filename TEXT,
            content_text TEXT,
            uploaded_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_report(
    meeting_date: str,
    meeting_title: str,
    motion_title: str,
    description: str,
    mover: str,
    seconder: str,
    outcome: str,
    votes: Dict[str, str],
    notes: str = ""
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO reports (
            meeting_date, meeting_title, motion_title, description,
            mover, seconder, outcome, votes_json, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            meeting_date,
            meeting_title,
            motion_title,
            description,
            mover,
            seconder,
            outcome,
            json.dumps(votes),
            notes,
            datetime.now().isoformat(timespec="seconds")
        )
    )
    report_id = cur.lastrowid
    conn.commit()
    conn.close()
    return report_id


def get_all_reports() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports ORDER BY meeting_date DESC, id DESC")
    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        d = dict(row)
        d["votes"] = json.loads(d.pop("votes_json") or "{}")
        results.append(d)
    return results


def get_report(report_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["votes"] = json.loads(d.pop("votes_json") or "{}")
    return d


def delete_report(report_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def add_minutes(
    meeting_date: str,
    meeting_title: str,
    filename: str,
    content_text: str
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO minutes (meeting_date, meeting_title, filename, content_text, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            meeting_date,
            meeting_title,
            filename,
            content_text,
            datetime.now().isoformat(timespec="seconds")
        )
    )
    minutes_id = cur.lastrowid
    conn.commit()
    conn.close()
    return minutes_id


def get_all_minutes() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM minutes ORDER BY meeting_date DESC, id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_minutes(minutes_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM minutes WHERE id = ?", (minutes_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def search_content(query: str) -> Dict[str, List]:
    """Simple case-insensitive search across reports and minutes."""
    q = f"%{query.lower()}%"
    conn = get_connection()
    cur = conn.cursor()

    # Reports
    cur.execute(
        """
        SELECT * FROM reports
        WHERE lower(motion_title) LIKE ?
           OR lower(description) LIKE ?
           OR lower(meeting_title) LIKE ?
           OR lower(mover) LIKE ?
           OR lower(seconder) LIKE ?
           OR lower(notes) LIKE ?
        ORDER BY meeting_date DESC
        """,
        (q, q, q, q, q, q)
    )
    report_rows = cur.fetchall()
    reports = []
    for row in report_rows:
        d = dict(row)
        d["votes"] = json.loads(d.pop("votes_json") or "{}")
        reports.append(d)

    # Minutes
    cur.execute(
        """
        SELECT * FROM minutes
        WHERE lower(meeting_title) LIKE ?
           OR lower(content_text) LIKE ?
           OR lower(filename) LIKE ?
        ORDER BY meeting_date DESC
        """,
        (q, q, q)
    )
    minutes = [dict(row) for row in cur.fetchall()]

    conn.close()
    return {"reports": reports, "minutes": minutes}


# Initialise on import
init_db()
