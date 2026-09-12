"""Endpoints para movimientos financieros de las cuentas."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import DepositCreate, DepositWithRisk
from app.nessie.client import NessieClient, NessieError
from app.nessie.dependencies import get_nessie_client
from app.risk_engine.rules import assess_deposit
from app.storage import guardian_store


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/accounts/{account_id}/deposits")
def list_deposits(
    account_id: str, client: NessieClient = Depends(get_nessie_client)
) -> list[dict[str, Any]]:
    """Consulta los abonos de una cuenta."""
    try:
        return client.list_deposits(account_id)
    except NessieError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible consultar los movimientos en Nessie.",
        ) from exc


@router.post(
    "/accounts/{account_id}/deposits", status_code=status.HTTP_201_CREATED
)
def create_deposit(
    account_id: str,
    deposit: DepositCreate,
    client: NessieClient = Depends(get_nessie_client),
) -> DepositWithRisk:
    """Registra un abono y devuelve su evaluación de riesgo."""
    try:
        created_deposit = client.create_deposit(account_id, deposit.model_dump(mode="json"))
    except NessieError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible registrar el movimiento en Nessie.",
        ) from exc

    from datetime import datetime, timezone

    occurred_at = datetime.now(timezone.utc)
    assessment = assess_deposit(
        deposit.amount, guardian_store.events_for(account_id, occurred_at), occurred_at
    )
    guardian_store.record_transaction(account_id, deposit.amount, occurred_at)
    if assessment.level != "low":
        guardian_store.record_alert(
            account_id=account_id,
            amount=deposit.amount,
            score=assessment.score,
            level=assessment.level,
            reasons=assessment.reasons,
            created_at=occurred_at,
        )
    return DepositWithRisk(deposit=created_deposit, risk=assessment)
