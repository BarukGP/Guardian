"""Utilidades estadísticas para el motor de riesgo."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta

from app.risk_engine.state import TransactionEvent


def events_within(
    events: Iterable[TransactionEvent], now: datetime, window: timedelta
) -> list[TransactionEvent]:
    """Filtra eventos ocurridos dentro de una ventana temporal."""
    threshold = now - window
    return [event for event in events if event.occurred_at >= threshold]


def total_amount(events: Iterable[TransactionEvent]) -> float:
    """Calcula el importe acumulado de una colección de eventos."""
    return sum(event.amount for event in events)


def average_amount(events: Iterable[TransactionEvent]) -> float:
    """Calcula el importe medio, devolviendo cero cuando no hay historial."""
    values = list(events)
    return total_amount(values) / len(values) if values else 0.0


def known_payees(events: Iterable[TransactionEvent]) -> set[str]:
    """Devuelve los beneficiarios ya vistos en el historial."""
    return {event.payee_id for event in events if event.payee_id}
