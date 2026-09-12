"""Persistencia SQLite local de movimientos y alertas del MVP."""

from __future__ import annotations

import json
import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from app.core.config import get_database_path
from app.services.risk_engine.state import AlertEvent, OperationEvent, TransactionEvent


def _as_utc(value: datetime) -> datetime:
    """Normaliza fechas de entrada para comparaciones SQLite consistentes."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


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
        occurred_at = _as_utc(occurred_at)
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
        threshold = (_as_utc(now) - retention).isoformat()
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
                occurred_at=_as_utc(datetime.fromisoformat(row["occurred_at"])),
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
        user_id: str = "rosa-elena",
    ) -> AlertEvent:
        created_at = _as_utc(created_at)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO alerts (account_id, user_id, amount, score, level, reasons, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    user_id,
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

    def record_operation(
        self,
        *,
        account_id: str,
        kind: str,
        description: str,
        payee_name: str | None,
        amount: float,
        score: int,
        level: str,
        reasons: list[str],
        status: str,
        occurred_at: datetime,
        user_id: str = "rosa-elena",
    ) -> OperationEvent:
        """Registra una operación evaluada para la línea de tiempo del producto."""
        occurred_at = _as_utc(occurred_at)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO operations (
                    account_id, user_id, kind, description, payee_name, amount, score,
                    level, reasons, status, occurred_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    user_id,
                    kind,
                    description,
                    payee_name,
                    amount,
                    score,
                    level,
                    json.dumps(reasons),
                    status,
                    occurred_at.isoformat(),
                ),
            )
            operation_id = int(cursor.lastrowid)
        return OperationEvent(
            id=operation_id,
            account_id=account_id,
            kind=kind,
            description=description,
            payee_name=payee_name,
            amount=amount,
            score=score,
            level=level,
            reasons=tuple(reasons),
            status=status,
            occurred_at=occurred_at,
        )

    def recent_operations(self, user_id: str | None = "rosa-elena", limit: int = 100) -> list[OperationEvent]:
        with self._connect() as connection:
            query = """
                SELECT id, account_id, kind, description, payee_name, amount, score,
                       level, reasons, status, occurred_at, resolved_at
                FROM operations
            """
            parameters: tuple[object, ...] = (limit,)
            if user_id is not None:
                query += " WHERE user_id = ?"
                parameters = (user_id, limit)
            rows = connection.execute(query + " ORDER BY id DESC LIMIT ?", parameters).fetchall()
        return [self._to_operation_event(row) for row in rows]

    def resolve_operation(
        self, operation_id: int, decision: str, user_id: str = "rosa-elena"
    ) -> OperationEvent | None:
        """Resuelve una pausa en una sola transacción local y deja auditoría."""
        resolved_at = datetime.now(timezone.utc)
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE operations
                SET status = ?, resolved_at = ?
                WHERE id = ? AND user_id = ? AND status = 'pending_review'
                """,
                (decision, resolved_at.isoformat(), operation_id, user_id),
            )
            if cursor.rowcount != 1:
                return None
            row = connection.execute(
                """
                SELECT id, account_id, kind, description, payee_name, amount, score,
                       level, reasons, status, occurred_at, resolved_at
                FROM operations
                WHERE id = ? AND user_id = ?
                """,
                (operation_id, user_id),
            ).fetchone()
            if row is None:
                return None
            if decision == "confirmed":
                connection.execute(
                    """
                    INSERT INTO transactions (account_id, amount, occurred_at, payee_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (row["account_id"], row["amount"], resolved_at.isoformat(), row["payee_name"]),
                )
            if decision == "reported_pressure":
                connection.execute(
                    """
                    INSERT INTO fraud_cases (user_id, operation_id, status, created_at)
                    VALUES (?, ?, 'open', ?)
                    """,
                    (user_id, operation_id, resolved_at.isoformat()),
                )
            connection.execute(
                """
                INSERT INTO audit_events (user_id, action, entity_type, entity_id, details, occurred_at)
                VALUES (?, ?, 'operation', ?, ?, ?)
                """,
                (user_id, f"review_{decision}", str(operation_id), json.dumps({"decision": decision}), resolved_at.isoformat()),
            )
        return self._to_operation_event(row) if row is not None else None

    def ensure_demo_users(self, password: str) -> None:
        """Crea identidades locales predecibles para el piloto sin exponer secretos al frontend."""
        password_hash = self._password_hash(password)
        users = (
            ("rosa-elena", "Rosa Elena", "customer"),
            ("analyst-demo", "Analista Guardián", "analyst"),
        )
        with self._connect() as connection:
            for user_id, display_name, role in users:
                connection.execute(
                    """
                    INSERT INTO users (id, display_name, role, password_hash)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        display_name = excluded.display_name,
                        role = excluded.role,
                        password_hash = excluded.password_hash
                    """,
                    (user_id, display_name, role, password_hash),
                )

    def authenticate_demo_user(self, user_id: str, password: str) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, display_name, role, password_hash FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        if row is None or not self._constant_time_equal(row["password_hash"], self._password_hash(password)):
            return None
        return {"id": row["id"], "display_name": row["display_name"], "role": row["role"]}

    def create_session(self, token: str, user_id: str, expires_at: datetime) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (datetime.now(timezone.utc).isoformat(),))
            connection.execute(
                "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
                (self._token_hash(token), user_id, expires_at.isoformat()),
            )

    def session_user(self, token: str) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT users.id, users.display_name, users.role
                FROM sessions JOIN users ON users.id = sessions.user_id
                WHERE sessions.token_hash = ? AND sessions.expires_at > ?
                """,
                (self._token_hash(token), datetime.now(timezone.utc).isoformat()),
            ).fetchone()
        return dict(row) if row is not None else None

    def revoke_session(self, token: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (self._token_hash(token),))

    def recent_cases(self, user_id: str | None = None) -> list[dict[str, object]]:
        with self._connect() as connection:
            query = """
                SELECT fraud_cases.id, fraud_cases.user_id, users.display_name AS user_display_name,
                       operation_id, status, created_at
                FROM fraud_cases LEFT JOIN users ON users.id = fraud_cases.user_id
            """
            parameters: tuple[object, ...] = ()
            if user_id is not None:
                query += " WHERE fraud_cases.user_id = ?"
                parameters = (user_id,)
            rows = connection.execute(query + " ORDER BY fraud_cases.id DESC LIMIT 20", parameters).fetchall()
        return [dict(row) for row in rows]

    def recent_audit_events(self, user_id: str | None, limit: int = 50) -> list[dict[str, object]]:
        with self._connect() as connection:
            query = "SELECT id, user_id, action, entity_type, entity_id, occurred_at FROM audit_events"
            parameters: tuple[object, ...] = (limit,)
            if user_id is not None:
                query += " WHERE user_id = ?"
                parameters = (user_id, limit)
            rows = connection.execute(query + " ORDER BY id DESC LIMIT ?", parameters).fetchall()
        return [dict(row) for row in rows]

    def reset_demo(self, account_id: str) -> None:
        """Elimina sólo el estado local del escenario de demo indicado."""
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM fraud_cases WHERE operation_id IN (SELECT id FROM operations WHERE account_id = ?)",
                (account_id,),
            )
            connection.execute(
                """
                DELETE FROM audit_events
                WHERE entity_type = 'operation'
                  AND entity_id IN (SELECT CAST(id AS TEXT) FROM operations WHERE account_id = ?)
                """,
                (account_id,),
            )
            connection.execute("DELETE FROM alerts WHERE account_id = ?", (account_id,))
            connection.execute("DELETE FROM transactions WHERE account_id = ?", (account_id,))
            connection.execute("DELETE FROM operations WHERE account_id = ?", (account_id,))

    def recent_alerts(
        self, user_id: str | None = "rosa-elena", limit: int = 50, after_id: int = 0
    ) -> list[AlertEvent]:
        with self._connect() as connection:
            query = """
                SELECT id, account_id, amount, score, level, reasons, created_at
                FROM alerts
            """
            parameters: tuple[object, ...] = (after_id, limit)
            if user_id is not None:
                query += " WHERE user_id = ? AND id > ?"
                parameters = (user_id, after_id, limit)
            else:
                query += " WHERE id > ?"
            rows = connection.execute(query + " ORDER BY id DESC LIMIT ?", parameters).fetchall()
        return [self._to_alert_event(row) for row in rows]

    def clear(self) -> None:
        """Elimina datos locales; se usa exclusivamente en pruebas controladas."""
        with self._connect() as connection:
            connection.execute("DELETE FROM audit_events")
            connection.execute("DELETE FROM fraud_cases")
            connection.execute("DELETE FROM sessions")
            connection.execute("DELETE FROM users")
            connection.execute("DELETE FROM alerts")
            connection.execute("DELETE FROM transactions")
            connection.execute("DELETE FROM operations")

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
                    user_id TEXT NOT NULL DEFAULT 'rosa-elena',
                    amount REAL NOT NULL,
                    score INTEGER NOT NULL,
                    level TEXT NOT NULL,
                    reasons TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS alerts_id ON alerts (id);
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    user_id TEXT NOT NULL DEFAULT 'rosa-elena',
                    kind TEXT NOT NULL,
                    description TEXT NOT NULL,
                    payee_name TEXT,
                    amount REAL NOT NULL,
                    score INTEGER NOT NULL,
                    level TEXT NOT NULL,
                    reasons TEXT NOT NULL,
                    status TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    resolved_at TEXT
                );
                CREATE INDEX IF NOT EXISTS operations_account_id
                    ON operations (account_id, id);
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    password_hash TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(id),
                    expires_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS sessions_user_id ON sessions (user_id);
                CREATE TABLE IF NOT EXISTS fraud_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL REFERENCES users(id),
                    operation_id INTEGER NOT NULL REFERENCES operations(id),
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    details TEXT NOT NULL,
                    occurred_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS audit_events_user_id
                    ON audit_events (user_id, id);
                """
            )
            # Migración ligera: DBs creadas antes no tienen payee_id.
            cols = [r[1] for r in connection.execute("PRAGMA table_info(transactions)").fetchall()]
            if "payee_id" not in cols:
                connection.execute("ALTER TABLE transactions ADD COLUMN payee_id TEXT")
            alert_columns = [r[1] for r in connection.execute("PRAGMA table_info(alerts)").fetchall()]
            if "user_id" not in alert_columns:
                connection.execute(
                    "ALTER TABLE alerts ADD COLUMN user_id TEXT NOT NULL DEFAULT 'rosa-elena'"
                )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS alerts_user_id ON alerts (user_id, id)"
            )
            operation_columns = [r[1] for r in connection.execute("PRAGMA table_info(operations)").fetchall()]
            if "user_id" not in operation_columns:
                connection.execute(
                    "ALTER TABLE operations ADD COLUMN user_id TEXT NOT NULL DEFAULT 'rosa-elena'"
                )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS operations_user_id ON operations (user_id, id)"
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        except Exception:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()

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

    @staticmethod
    def _to_operation_event(row: sqlite3.Row) -> OperationEvent:
        resolved_at = row["resolved_at"]
        return OperationEvent(
            id=int(row["id"]),
            account_id=row["account_id"],
            kind=row["kind"],
            description=row["description"],
            payee_name=row["payee_name"],
            amount=float(row["amount"]),
            score=int(row["score"]),
            level=row["level"],
            reasons=tuple(json.loads(row["reasons"])),
            status=row["status"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            resolved_at=datetime.fromisoformat(resolved_at) if resolved_at else None,
        )

    @staticmethod
    def _password_hash(password: str) -> str:
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), b"guardian-local-pilot-v1", 210_000
        ).hex()

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _constant_time_equal(left: str, right: str) -> bool:
        from hmac import compare_digest

        return compare_digest(left, right)


guardian_store = GuardianStore()
