from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Task


class TaskStore:
    def __init__(self, db_path: Path | str):
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    run_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    last_error TEXT
                );

                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    timestamp TEXT NOT NULL,
                    event TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
                """
            )

    def add(self, task: Task) -> int:
        created_at = task.created_at or datetime.now()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO tasks(prompt, run_at, status, created_at, last_error) VALUES (?, ?, ?, ?, ?)",
                (task.prompt, task.run_at.isoformat(), task.status, created_at.isoformat(), task.last_error),
            )
            return int(cur.lastrowid)

    def list(self) -> list[Task]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY run_at, id").fetchall()
        return [self._row_to_task(row) for row in rows]

    def due(self, now: datetime) -> list[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status = 'pending' AND run_at <= ? ORDER BY run_at, id",
                (now.isoformat(),),
            ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def set_status(self, task_id: int, status: str, error: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE tasks SET status = ?, last_error = ? WHERE id = ?",
                (status, error, task_id),
            )

    def audit(self, task_id: int | None, event: str, details: str = "") -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audit_log(task_id, timestamp, event, details) VALUES (?, ?, ?, ?)",
                (task_id, datetime.now().isoformat(), event, details),
            )

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=int(row["id"]),
            prompt=str(row["prompt"]),
            run_at=datetime.fromisoformat(row["run_at"]),
            status=str(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_error=row["last_error"],
        )
