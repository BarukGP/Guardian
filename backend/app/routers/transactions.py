"""Endpoints para movimientos financieros de las cuentas."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import DepositCreate
from app.nessie.client import NessieClient, NessieError
from app.nessie.dependencies import get_nessie_client


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
) -> dict[str, Any]:
    """Registra un abono en Nessie."""
    try:
        return client.create_deposit(account_id, deposit.model_dump(mode="json"))
    except NessieError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible registrar el movimiento en Nessie.",
        ) from exc
