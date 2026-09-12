"""Reglas explicables para detectar señales de fraude en depósitos."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.schemas import RiskAssessment
from app.risk_engine.state import TransactionEvent
from app.risk_engine.stats import average_amount, events_within, total_amount


HIGH_AMOUNT = 10_000.0
VELOCITY_WINDOW = timedelta(minutes=10)
RAPID_WINDOW = timedelta(minutes=5)
HISTORY_WINDOW = timedelta(days=30)


def assess_deposit(
    amount: float,
    prior_events: list[TransactionEvent],
    now: datetime | None = None,
) -> RiskAssessment:
    """Calcula un puntaje de 0 a 100 a partir de reglas auditables."""
    current_time = now or datetime.now(timezone.utc)
    score = 0
    reasons: list[str] = []

    if amount >= HIGH_AMOUNT:
        score += 60
        reasons.append("Monto alto: supera el umbral de 10,000.")

    recent_events = events_within(prior_events, current_time, VELOCITY_WINDOW)
    if len(recent_events) >= 3:
        score += 25
        reasons.append("Actividad rápida: hay al menos tres movimientos previos en 10 minutos.")

    if len(recent_events) >= 1 and total_amount(recent_events) + amount >= 5_000:
        score += 20
        reasons.append("Volumen elevado: el acumulado de 10 minutos supera 5,000.")

    history = events_within(prior_events, current_time, HISTORY_WINDOW)
    historical_average = average_amount(history)
    if len(history) >= 3 and amount >= historical_average * 3:
        score += 20
        reasons.append("Monto atípico: supera tres veces el promedio histórico.")

    bounded_score = min(score, 100)
    level = "high" if bounded_score >= 60 else "medium" if bounded_score >= 25 else "low"
    if not reasons:
        reasons.append("No se detectaron señales de riesgo con las reglas actuales.")

    return RiskAssessment(score=bounded_score, level=level, reasons=reasons)
