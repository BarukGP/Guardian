"""Endpoints para ejecutar la demostración de riesgo sin usar Nessie."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.models.schemas import RiskAlert, RiskAssessment, SimulationResult
from app.risk_engine.state import AlertEvent, alert_store
from scripts.simulate_stream import DEMO_ACCOUNT_ID, run_simulation


router = APIRouter(prefix="/simulate", tags=["simulation"])


def _to_risk_alert(alert: AlertEvent) -> RiskAlert:
    return RiskAlert(
        account_id=alert.account_id,
        amount=alert.amount,
        risk=RiskAssessment(
            score=alert.score, level=alert.level, reasons=list(alert.reasons)
        ),
        created_at=alert.created_at,
    )


@router.post("/run", response_model=SimulationResult)
def run_demo_simulation(
    account_id: Annotated[str, Query(min_length=1, max_length=100)] = DEMO_ACCOUNT_ID,
) -> SimulationResult:
    """Ejecuta movimientos de demostración y registra sus alertas."""
    return run_simulation(account_id=account_id)


@router.get("/alerts", response_model=list[RiskAlert])
def list_alerts(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[RiskAlert]:
    """Devuelve las alertas más recientes, primero las de mayor recencia."""
    return [_to_risk_alert(alert) for alert in alert_store.recent(limit)]
