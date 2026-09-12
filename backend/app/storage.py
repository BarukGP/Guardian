"""Persistencia SQLite local de movimientos y alertas del MVP."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import get_database_path
from app.risk_engine.state import AlertEvent, TransactionEvent


class GuardianStore:
    """Almacén ligero y seguro para una sola instancia de la aplicación."""

    def __init__(self, database_path: Path | None = None) -> None:
        self._database_path = database_path or get_database_path()
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def record_transaction(
        self,
        account_id: str,
        amount: float,
        occurred_at: datetime,
        payee_id: str | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO transactions (account_id, amount, occurred_at, payee_id)
                VALUES (?, ?, ?, ?)
                """,
                (account_id, amount, occurred_at.isoformat(), payee_id),
            )

    def events_for(
        self, account_id: str, now: datetime, retention: timedelta = timedelta(days=30)
    ) -> list[TransactionEvent]:
        threshold = (now - retention).isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT account_id, amount, occurred_at, payee_id
                FROM transactions
                WHERE account_id = ? AND occurred_at >= ?
                ORDER BY occurred_at ASC
                """,
                (account_id, threshold),
            ).fetchall()
        return [
            TransactionEvent(
                account_id=row["account_id"],
                amount=float(row["amount"]),
                occurred_at=datetime.fromisoformat(row["occurred_at"]),
                payee_id=row["payee_id"] if "payee_id" in row.keys() else None,
            )
            for row in rows
        ]

    def record_alert(
        self,
        account_id: str,
        amount: float,
        score: int,
        level: str,
        reasons: list[str],
        created_at: datetime,
    ) -> AlertEvent:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO alerts (account_id, amount, score, level, reasons, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    amount,
                    score,
                    level,
                    json.dumps(reasons),
                    created_at.isoformat(),
                ),
            )
            alert_id = int(cursor.lastrowid)
        return AlertEvent(
            id=alert_id,
            account_id=account_id,
            amount=amount,
            score=score,
            level=level,
            reasons=tuple(reasons),
            created_at=created_at,
        )

    def recent_alerts(self, limit: int = 50, after_id: int = 0) -> list[AlertEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, account_id, amount, score, level, reasons, created_at
                FROM alerts
                WHERE id > ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (after_id, limit),
            ).fetchall()
        return [self._to_alert_event(row) for row in rows]

    def clear(self) -> None:
        """Elimina datos locales; se usa exclusivamente en pruebas controladas."""
        with self._connect() as connection:
            connection.execute("DELETE FROM alerts")
            connection.execute("DELETE FROM transactions")

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    occurred_at TEXT NOT NULL,
                    payee_id TEXT
                );
                CREATE INDEX IF NOT EXISTS transactions_account_time
                    ON transactions (account_id, occurred_at);
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    score INTEGER NOT NULL,
                    level TEXT NOT NULL,
                    reasons TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS alerts_id ON alerts (id);
                """
            )
            # Migración ligera: DBs creadas antes no tienen payee_id.
            cols = [r[1] for r in connection.execute("PRAGMA table_info(transactions)").fetchall()]
            if "payee_id" not in cols:
                connection.execute("ALTER TABLE transactions ADD COLUMN payee_id TEXT")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _to_alert_event(row: sqlite3.Row) -> AlertEvent:
        return AlertEvent(
            id=int(row["id"]),
            account_id=row["account_id"],
            amount=float(row["amount"]),
            score=int(row["score"]),
            level=row["level"],
            reasons=tuple(json.loads(row["reasons"])),
            created_at=datetime.fromisoformat(row["created_at"]),
        )


guardian_store = GuardianStore()
