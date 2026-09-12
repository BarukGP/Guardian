"""Endpoints para ejecutar la demostración de riesgo sin usar Nessie."""

from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.models.schemas import RiskAlert, RiskAssessment, SimulationResult
from app.risk_engine.state import AlertEvent
from app.storage import guardian_store
from scripts.simulate_stream import DEMO_ACCOUNT_ID, run_simulation


router = APIRouter(prefix="/simulate", tags=["simulation"])


def _to_risk_alert(alert: AlertEvent) -> RiskAlert:
    return RiskAlert(
        id=alert.id,
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
    return [_to_risk_alert(alert) for alert in guardian_store.recent_alerts(limit)]


@router.websocket("/alerts/stream")
async def stream_alerts(websocket: WebSocket) -> None:
    """Envía alertas nuevas por WebSocket mientras la conexión esté activa."""
    await websocket.accept()
    last_alert_id = 0
    try:
        while True:
            new_alerts = guardian_store.recent_alerts(limit=100, after_id=last_alert_id)
            for alert in reversed(new_alerts):
                await websocket.send_json(_to_risk_alert(alert).model_dump(mode="json"))
                last_alert_id = alert.id
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=1)
            except TimeoutError:
                continue
    except WebSocketDisconnect:
        return
