"""Historial efímero y seguro por cuenta para el análisis de riesgo."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock


@dataclass(frozen=True, slots=True)
class TransactionEvent:
    account_id: str
    amount: float
    occurred_at: datetime
    payee_id: str | None = None


@dataclass(frozen=True, slots=True)
class AlertEvent:
    id: int
    account_id: str
    amount: float
    score: int
    level: str
    reasons: tuple[str, ...]
    created_at: datetime


class RiskState:
    """Mantiene un historial acotado en memoria; no reemplaza persistencia."""

    def __init__(self, retention: timedelta = timedelta(days=30)) -> None:
        self._retention = retention
        self._events: dict[str, deque[TransactionEvent]] = defaultdict(deque)
        self._lock = Lock()

    def events_for(self, account_id: str, now: datetime | None = None) -> list[TransactionEvent]:
        """Devuelve una instantánea del historial vigente de una cuenta."""
        current_time = now or datetime.now(timezone.utc)
        with self._lock:
            self._prune(account_id, current_time)
            return list(self._events[account_id])

    def record(
        self,
        account_id: str,
        amount: float,
        now: datetime | None = None,
        payee_id: str | None = None,
    ) -> None:
        """Registra un movimiento ya creado exitosamente en Nessie."""
        current_time = now or datetime.now(timezone.utc)
        with self._lock:
            self._prune(account_id, current_time)
            self._events[account_id].append(
                TransactionEvent(
                    account_id=account_id,
                    amount=amount,
                    occurred_at=current_time,
                    payee_id=payee_id,
                )
            )

    def clear(self) -> None:
        """Limpia el estado; útil para pruebas y reinicios controlados."""
        with self._lock:
            self._events.clear()

    def _prune(self, account_id: str, now: datetime) -> None:
        threshold = now - self._retention
        account_events = self._events[account_id]
        while account_events and account_events[0].occurred_at < threshold:
            account_events.popleft()
