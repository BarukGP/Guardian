"""Simulador reproducible de movimientos normales y sospechosos.

Ejecutar desde ``backend``: ``python scripts/simulate_stream.py``.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.schemas import SimulatedTransaction, SimulationResult
from app.risk_engine.rules import assess_deposit
from app.risk_engine.state import RiskState
from app.storage import GuardianStore, guardian_store


DEMO_ACCOUNT_ID = "guardian-demo-simulation"
DEMO_EVENTS = (
    (timedelta(days=-29), 120.0, "Depósito histórico"),
    (timedelta(days=-15), 100.0, "Depósito histórico"),
    (timedelta(days=-1), 110.0, "Depósito habitual"),
    (timedelta(minutes=-4), 200.0, "Abono rápido 1"),
    (timedelta(minutes=-3), 200.0, "Abono rápido 2"),
    (timedelta(minutes=-2), 200.0, "Abono rápido 3"),
    (timedelta(minutes=-1), 5_000.0, "Abono de volumen elevado"),
    (timedelta(), 12_000.0, "Abono de monto alto"),
)


def run_simulation(
    account_id: str = DEMO_ACCOUNT_ID,
    now: datetime | None = None,
    state: RiskState | None = None,
    store: GuardianStore | None = None,
) -> SimulationResult:
    """Procesa una secuencia fija y devuelve todas sus evaluaciones."""
    reference_time = now or datetime.now(timezone.utc)
    simulation_state = state if state is not None else RiskState()
    persistence = store if store is not None else guardian_store
    transactions: list[SimulatedTransaction] = []
    alerts_generated = 0

    for offset, amount, description in DEMO_EVENTS:
        occurred_at = reference_time + offset
        assessment = assess_deposit(
            amount, simulation_state.events_for(account_id, occurred_at), occurred_at
        )
        simulation_state.record(account_id, amount, occurred_at)
        persistence.record_transaction(account_id, amount, occurred_at)
        transactions.append(
            SimulatedTransaction(
                amount=amount,
                description=description,
                occurred_at=occurred_at,
                risk=assessment,
            )
        )
        if assessment.level != "low":
            persistence.record_alert(
                account_id=account_id,
                amount=amount,
                score=assessment.score,
                level=assessment.level,
                reasons=assessment.reasons,
                created_at=occurred_at,
            )
            alerts_generated += 1

    return SimulationResult(
        account_id=account_id,
        processed=len(transactions),
        alerts_generated=alerts_generated,
        transactions=transactions,
    )


if __name__ == "__main__":
    result = run_simulation()
    print(f"Simulación lista: {result.processed} movimientos, {result.alerts_generated} alertas.")
