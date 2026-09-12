"""Endpoints para consultar y crear cuentas vinculadas a Nessie."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import Principal, require_customer, require_principal
from app.domain.schemas import AccountCreate
from app.infrastructure.nessie.client import NessieClient, NessieError
from app.infrastructure.nessie.dependencies import get_nessie_client


router = APIRouter(
    prefix="/accounts", tags=["accounts"]
)


@router.get("/customers/{customer_id}")
def list_accounts(
    customer_id: str, client: NessieClient = Depends(get_nessie_client), _: Principal = Depends(require_principal)
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
    _: Principal = Depends(require_customer),
) -> dict[str, Any]:
    """Crea una cuenta para la cliente indicada."""
    try:
        return client.create_account(customer_id, account.model_dump(mode="json"))
    except NessieError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible crear la cuenta en Nessie.",
        ) from exc
