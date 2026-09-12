"""Reglas explicables para detectar señales de fraude en depósitos."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.domain.schemas import RiskAssessment
from app.services.risk_engine.state import TransactionEvent
from app.services.risk_engine.stats import average_amount, events_within, known_payees, total_amount


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


def assess_transfer(
    amount: float,
    payee_id: str | None,
    prior_events: list[TransactionEvent],
    now: datetime | None = None,
    *,
    new_device: bool = False,
    unusual_hour: bool = False,
    beneficiary_flagged: bool = False,
) -> RiskAssessment:
    """Evalúa una transferencia tipo APP Fraud (Rosa Elena -> beneficiario).

    Reutiliza velocidad/volumen/promedio de deposits y suma la señal clave
    diferenciadora: beneficiario nuevo (+30).
    """
    current_time = now or datetime.now(timezone.utc)
    # Base: mismas reglas de velocidad/volumen/promedio que deposits.
    base = assess_deposit(amount, prior_events, current_time)
    score = base.score
    reasons = [r for r in base.reasons if "No se detectaron" not in r]

    payees = known_payees(prior_events)
    if payee_id and payee_id not in payees and len(prior_events) >= 1:
        score += 30
        reasons.append("Beneficiario nuevo: nunca se le había transferido antes.")
    if new_device:
        score += 15
        reasons.append("Dispositivo nuevo: el inicio de la transferencia no coincide con el dispositivo habitual.")
    if unusual_hour:
        score += 10
        reasons.append("Horario inusual: esta operación ocurre fuera del patrón habitual.")
    if beneficiary_flagged:
        score += 35
        reasons.append("Destino señalado: el beneficiario tiene señales previas de riesgo.")

    bounded_score = min(score, 100)
    level = "high" if bounded_score >= 60 else "medium" if bounded_score >= 25 else "low"
    if not reasons:
        reasons.append("No se detectaron señales de riesgo con las reglas actuales.")

    return RiskAssessment(score=bounded_score, level=level, reasons=reasons)
