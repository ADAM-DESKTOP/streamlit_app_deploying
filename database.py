"""
Improved database layer for Prayer Tracker / Task app.

- Uses a single SQLite file stored in ./data/app_data.db
- Thread-safe writes via a lock; check_same_thread=False for concurrency
- Uses sqlite3.Row for dict-like results
- Centralized tables: tasks, prayers
- All methods return Python dict/list structures suitable for UI consumption
"""

import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Optional
import datetime

DEFAULT_DB_DIR = Path(__file__).parent / "data"
DEFAULT_DB_FILE = DEFAULT_DB_DIR / "app_data.db"


def _normalize_username(username: str) -> str:
    if username is None:
        return "anonymous"
    return username.strip().lower().replace(" ", "_")


class DBManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_FILE
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._connect()
        self._create_tables()

    def _connect(self):
        # check_same_thread=False to allow usage across threads (Streamlit callbacks etc.)
        self.con = sqlite3.connect(str(self.db_path), check_same_thread=False, timeout=30)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        # Recommended pragmas for better durability (SQLite)
        with self._lock:
            self.cur.execute("PRAGMA foreign_keys = ON;")
            self.cur.execute("PRAGMA journal_mode = WAL;")
            self.cur.execute("PRAGMA synchronous = NORMAL;")

    def _create_tables(self):
        with self._lock:
            # tasks table (per user)
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                task TEXT NOT NULL,
                due_date TEXT,
                completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0,1)),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """)
            self.cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user);")
            self.cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);")

            # prayers table (per user, per date, per prayer unique)
            self.cur.execute("""
            CREATE TABLE IF NOT EXISTS prayers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                date TEXT NOT NULL,
                prayer TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0,1)),
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(user, date, prayer)
            );
            """)
            self.cur.execute("CREATE INDEX IF NOT EXISTS idx_prayers_user_date ON prayers(user, date);")
            self.con.commit()

    # ----------------------
    # Task API
    # ----------------------
    def add_task(self, username: str, task: str, due_date: Optional[str] = None) -> Dict:
        """
        Add a task for a user. Returns the created task as a dict.
        """
        user = _normalize_username(username)
        if not task or not task.strip():
            raise ValueError("Task text must be non-empty.")
        with self._lock:
            self.cur.execute(
                "INSERT INTO tasks (user, task, due_date, completed) VALUES (?, ?, ?, 0)",
                (user, task.strip(), due_date)
            )
            self.con.commit()
            task_id = self.cur.lastrowid
            return self.get_task(user, task_id)

    def get_task(self, username: str, task_id: int) -> Dict:
        user = _normalize_username(username)
        row = self.cur.execute(
            "SELECT id, user, task, due_date, completed, created_at FROM tasks WHERE id=? AND user=?",
            (task_id, user)
        ).fetchone()
        return dict(row) if row else {}

    def get_tasks(self, username: str) -> Dict[str, List[Dict]]:
        """
        Returns { "incomplete": [...], "completed": [...] }
        each task is a dict with id, task, due_date, completed, created_at
        """
        user = _normalize_username(username)
        with self._lock:
            incompleted = self.cur.execute(
                "SELECT id, task, due_date, completed, created_at FROM tasks WHERE user=? AND completed=0 ORDER BY created_at DESC",
                (user,)
            ).fetchall()
            completed = self.cur.execute(
                "SELECT id, task, due_date, completed, created_at FROM tasks WHERE user=? AND completed=1 ORDER BY created_at DESC",
                (user,)
            ).fetchall()
        return {
            "incomplete": [dict(r) for r in incompleted],
            "completed": [dict(r) for r in completed]
        }

    def set_task_completed(self, username: str, task_id: int, completed: bool = True) -> bool:
        user = _normalize_username(username)
        with self._lock:
            self.cur.execute(
                "UPDATE tasks SET completed=? WHERE id=? AND user=?",
                (1 if completed else 0, task_id, user)
            )
            self.con.commit()
            return self.cur.rowcount > 0

    def delete_task(self, username: str, task_id: int) -> bool:
        user = _normalize_username(username)
        with self._lock:
            self.cur.execute("DELETE FROM tasks WHERE id=? AND user=?", (task_id, user))
            self.con.commit()
            return self.cur.rowcount > 0

    # ----------------------
    # Prayer API
    # ----------------------
    def get_prayers_for_date(self, username: str, date: str) -> Dict[str, bool]:
        """
        Return a dict { prayer_text: completed_bool } for the given user and date.
        date is a string like 'YYYY-MM-DD' (the UI should pass date.isoformat()).
        """
        user = _normalize_username(username)
        with self._lock:
            rows = self.cur.execute(
                "SELECT prayer, completed FROM prayers WHERE user=? AND date=? ORDER BY id",
                (user, date)
            ).fetchall()
        return {row["prayer"]: bool(row["completed"]) for row in rows}

    def set_prayer_status_for_date(self, username: str, date: str, status: Dict[str, bool]) -> None:
        """
        Given a mapping of prayer->bool, insert or update rows for that date and user.
        """
        user = _normalize_username(username)
        with self._lock:
            for prayer, completed in status.items():
                prayer_text = prayer.strip()
                self.cur.execute("""
                    INSERT INTO prayers (user, date, prayer, completed)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user, date, prayer) DO UPDATE SET completed=excluded.completed
                """, (user, date, prayer_text, 1 if completed else 0))
            self.con.commit()

    def ensure_prayers_exist_for_date(self, username: str, date: str, prayers: List[str]) -> None:
        """
        Ensures the given list of prayer texts exist for the user/date.
        Useful for initializing the day's prayer checklist.
        """
        user = _normalize_username(username)
        with self._lock:
            for prayer in prayers:
                prayer_text = prayer.strip()
                # INSERT OR IGNORE to avoid changing completed state if already exists
                self.cur.execute("""
                    INSERT OR IGNORE INTO prayers (user, date, prayer, completed)
                    VALUES (?, ?, ?, 0)
                """, (user, date, prayer_text))
            self.con.commit()

    # ----------------------
    # Utilities
    # ----------------------
    def close(self):
        try:
            self.con.close()
        except Exception:
            pass

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
