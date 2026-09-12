"""Simulador reproducible de movimientos normales y sospechosos.

Ejecutar desde ``api-service``: ``python -m app.services.simulation``.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.domain.schemas import SimulatedTransaction, SimulationResult
from app.services.risk_engine.rules import assess_deposit, assess_transfer
from app.services.risk_engine.state import RiskState
from app.infrastructure.database import GuardianStore, guardian_store


DEMO_ACCOUNT_ID = "guardian-demo-simulation"
DEMO_EVENTS = (
    ("deposit", timedelta(days=-29), 120.0, "Depósito histórico", None),
    ("deposit", timedelta(days=-15), 100.0, "Depósito histórico", None),
    ("deposit", timedelta(days=-1), 110.0, "Depósito habitual", None),
    ("deposit", timedelta(minutes=-4), 200.0, "Abono rápido 1", None),
    ("deposit", timedelta(minutes=-3), 200.0, "Abono rápido 2", None),
    ("deposit", timedelta(minutes=-2), 200.0, "Abono rápido 3", None),
    ("deposit", timedelta(minutes=-1), 5_000.0, "Abono de volumen elevado", None),
    (
        "transfer",
        timedelta(),
        8_000.0,
        "Transferencia a Soporte Falso",
        "guardian-demo-fake-support",
    ),
)


def run_simulation(
    account_id: str = DEMO_ACCOUNT_ID,
    now: datetime | None = None,
    state: RiskState | None = None,
    store: GuardianStore | None = None,
    user_id: str = "rosa-elena",
) -> SimulationResult:
    """Procesa una secuencia fija y devuelve todas sus evaluaciones."""
    reference_time = now or datetime.now(timezone.utc)
    simulation_state = state if state is not None else RiskState()
    persistence = store if store is not None else guardian_store
    # Demo aislada y reproducible: parte de RiskState fresco cada corrida.
    # /transactions en cambio usa el historial persistido (SQLite + Nessie).
    transactions: list[SimulatedTransaction] = []
    alerts_generated = 0

    for kind, offset, amount, description, payee_id in DEMO_EVENTS:
        occurred_at = reference_time + offset
        prior_events = simulation_state.events_for(account_id, occurred_at)
        assessment = (
            assess_transfer(
                amount,
                payee_id,
                prior_events,
                occurred_at,
                new_device=True,
                unusual_hour=True,
            )
            if kind == "transfer"
            else assess_deposit(amount, prior_events, occurred_at)
        )
        status = "pending_review" if assessment.level == "high" and kind == "transfer" else "completed"
        simulation_state.record(account_id, amount, occurred_at, payee_id=payee_id)
        # Una transferencia retenida no forma parte del historial financiero hasta
        # que la persona la confirma; sólo existe como operación en revisión.
        if status != "pending_review":
            persistence.record_transaction(account_id, amount, occurred_at, payee_id=payee_id)
        persistence.record_operation(
            account_id=account_id,
            kind=kind,
            description=description,
            payee_name="Soporte Falso" if kind == "transfer" else None,
            amount=amount,
            score=assessment.score,
            level=assessment.level,
            reasons=assessment.reasons,
            status=status,
            occurred_at=occurred_at,
            user_id=user_id,
        )
        transactions.append(
            SimulatedTransaction(
                amount=amount,
                description=description,
                occurred_at=occurred_at,
                risk=assessment,
                kind=kind,
                payee_name="Soporte Falso" if kind == "transfer" else None,
                status=status,
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
                user_id=user_id,
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
