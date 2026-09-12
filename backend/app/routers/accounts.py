"""Endpoints para consultar y crear cuentas vinculadas a Nessie."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import AccountCreate
from app.nessie.client import NessieClient, NessieError
from app.nessie.dependencies import get_nessie_client
from app.security import require_api_key


router = APIRouter(
    prefix="/accounts", tags=["accounts"], dependencies=[Depends(require_api_key)]
)


@router.get("/customers/{customer_id}")
def list_accounts(
    customer_id: str, client: NessieClient = Depends(get_nessie_client)
) -> list[dict[str, Any]]:
    """Devuelve las cuentas de una cliente de Nessie."""
    try:
        return client.list_customer_accounts(customer_id)
    except NessieError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible consultar las cuentas en Nessie.",
        ) from exc


@router.post("/customers/{customer_id}", status_code=status.HTTP_201_CREATED)
def create_account(
    customer_id: str,
    account: AccountCreate,
    client: NessieClient = Depends(get_nessie_client),
) -> dict[str, Any]:
    """Crea una cuenta para la cliente indicada."""
    try:
        return client.create_account(customer_id, account.model_dump(mode="json"))
    except NessieError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible crear la cuenta en Nessie.",
        ) from exc
