"""Endpoints para movimientos financieros de las cuentas."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import DepositCreate, DepositWithRisk
from app.nessie.client import NessieClient, NessieError
from app.nessie.dependencies import get_nessie_client
from app.risk_engine.rules import assess_deposit
from app.risk_engine.state import risk_state


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

    assessment = assess_deposit(deposit.amount, risk_state.events_for(account_id))
    risk_state.record(account_id, deposit.amount)
    return DepositWithRisk(deposit=created_deposit, risk=assessment)
