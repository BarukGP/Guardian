"""Endpoints para ejecutar la demostración de riesgo sin usar Nessie."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import Principal, require_customer, require_principal
from app.domain.schemas import (
    FraudCase,
    AuditEvent,
    ReviewDecision,
    RiskAlert,
    RiskAssessment,
    SimulationResult,
    TimelineOperation,
)
from app.infrastructure.database import guardian_store
from app.services.risk_engine.state import AlertEvent, OperationEvent
from app.services.simulation import DEMO_ACCOUNT_ID, run_simulation


router = APIRouter(prefix="/simulate", tags=["simulation"])


def _scoped_demo_account(account_id: str, principal: Principal) -> str:
    """Evita que dos sesiones demo compartan un historial o borren datos ajenos."""
    return f"demo:{principal.id}:{account_id}"


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


def _to_timeline_operation(operation: OperationEvent) -> TimelineOperation:
    return TimelineOperation(
        id=operation.id,
        account_id=operation.account_id,
        kind=operation.kind,
        description=operation.description,
        payee_name=operation.payee_name,
        amount=operation.amount,
        risk=RiskAssessment(
            score=operation.score,
            level=operation.level,
            reasons=list(operation.reasons),
        ),
        status=operation.status,
        occurred_at=operation.occurred_at,
        resolved_at=operation.resolved_at,
    )


@router.post("/run", response_model=SimulationResult)
def run_demo_simulation(
    account_id: Annotated[str, Query(min_length=1, max_length=100)] = DEMO_ACCOUNT_ID,
    principal: Principal = Depends(require_customer),
) -> SimulationResult:
    """Ejecuta movimientos de demostración y registra sus alertas."""
    scoped_account_id = _scoped_demo_account(account_id, principal)
    guardian_store.reset_demo(scoped_account_id)
    return run_simulation(account_id=scoped_account_id, user_id=principal.id)


@router.get("/alerts", response_model=list[RiskAlert])
def list_alerts(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    principal: Principal = Depends(require_principal),
) -> list[RiskAlert]:
    """Devuelve alertas de la sesión actual, aisladas de otros usuarios."""
    user_scope = None if principal.role == "analyst" else principal.id
    return [_to_risk_alert(alert) for alert in guardian_store.recent_alerts(user_scope, limit)]


@router.get("/timeline", response_model=list[TimelineOperation])
def list_timeline(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    principal: Principal = Depends(require_principal),
) -> list[TimelineOperation]:
    """Devuelve actividad normal, alertas y decisiones en un mismo feed."""
    user_scope = None if principal.role == "analyst" else principal.id
    return [_to_timeline_operation(item) for item in guardian_store.recent_operations(user_scope, limit)]


@router.post("/operations/{operation_id}/decision", response_model=TimelineOperation)
def decide_operation(
    operation_id: int,
    review: ReviewDecision,
    principal: Principal = Depends(require_customer),
) -> TimelineOperation:
    """Registra la decisión de Rosa después de una pausa protectora."""
    operation = guardian_store.resolve_operation(operation_id, review.decision, principal.id)
    if operation is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La operación no existe o ya no requiere una decisión.",
        )
    return _to_timeline_operation(operation)


@router.delete("/demo")
def reset_demo(
    account_id: Annotated[str, Query(min_length=1, max_length=100)] = DEMO_ACCOUNT_ID,
    principal: Principal = Depends(require_customer),
) -> dict[str, str]:
    """Restablece sólo el historial local de la demostración seleccionada."""
    guardian_store.reset_demo(_scoped_demo_account(account_id, principal))
    return {"status": "ok", "message": "Escenario de demostración reiniciado."}


@router.get("/cases", response_model=list[FraudCase])
def list_cases(principal: Principal = Depends(require_principal)) -> list[FraudCase]:
    """Muestra los casos abiertos cuando la persona reporta presión externa."""
    user_scope = None if principal.role == "analyst" else principal.id
    return [FraudCase(**item) for item in guardian_store.recent_cases(user_scope)]


@router.get("/audit", response_model=list[AuditEvent])
def list_audit_events(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    principal: Principal = Depends(require_principal),
) -> list[AuditEvent]:
    """Evidencia auditable de las decisiones tomadas durante el piloto."""
    user_scope = None if principal.role == "analyst" else principal.id
    return [AuditEvent(**item) for item in guardian_store.recent_audit_events(user_scope, limit)]
