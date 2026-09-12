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


@dataclass(frozen=True, slots=True)
class AlertEvent:
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

    def record(self, account_id: str, amount: float, now: datetime | None = None) -> None:
        """Registra un depósito ya creado exitosamente en Nessie."""
        current_time = now or datetime.now(timezone.utc)
        with self._lock:
            self._prune(account_id, current_time)
            self._events[account_id].append(
                TransactionEvent(account_id=account_id, amount=amount, occurred_at=current_time)
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


risk_state = RiskState()


class AlertStore:
    """Mantiene las alertas recientes para la demostración del MVP."""

    def __init__(self, max_alerts: int = 500) -> None:
        self._alerts: deque[AlertEvent] = deque(maxlen=max_alerts)
        self._lock = Lock()

    def record(
        self,
        account_id: str,
        amount: float,
        score: int,
        level: str,
        reasons: list[str],
        now: datetime | None = None,
    ) -> None:
        created_at = now or datetime.now(timezone.utc)
        alert = AlertEvent(
            account_id=account_id,
            amount=amount,
            score=score,
            level=level,
            reasons=tuple(reasons),
            created_at=created_at,
        )
        with self._lock:
            self._alerts.append(alert)

    def recent(self, limit: int = 50) -> list[AlertEvent]:
        with self._lock:
            return list(reversed(self._alerts))[:limit]

    def clear(self) -> None:
        with self._lock:
            self._alerts.clear()


alert_store = AlertStore()
