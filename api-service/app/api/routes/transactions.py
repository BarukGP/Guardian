"""Endpoints para movimientos financieros de las cuentas."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import Principal, require_customer, require_principal
from app.domain.schemas import DepositCreate, DepositWithRisk, TransferCreate, TransferWithRisk
from app.infrastructure.database import guardian_store
from app.infrastructure.nessie.client import NessieClient, NessieError
from app.infrastructure.nessie.dependencies import get_nessie_client
from app.services.risk_engine.rules import assess_deposit, assess_transfer


router = APIRouter(
    prefix="/transactions", tags=["transactions"]
)


@router.get("/accounts/{account_id}/deposits")
def list_deposits(
    account_id: str, client: NessieClient = Depends(get_nessie_client), _: Principal = Depends(require_principal)
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
    principal: Principal = Depends(require_customer),
) -> DepositWithRisk:
    """Registra un abono y devuelve su evaluación de riesgo."""
    try:
        created_deposit = client.create_deposit(account_id, deposit.model_dump(mode="json"))
    except NessieError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible registrar el movimiento en Nessie.",
        ) from exc

    occurred_at = datetime.now(timezone.utc)
    assessment = assess_deposit(
        deposit.amount, guardian_store.events_for(account_id, occurred_at), occurred_at
    )
    guardian_store.record_transaction(account_id, deposit.amount, occurred_at)
    guardian_store.record_operation(
        account_id=account_id,
        kind="deposit",
        description=deposit.description,
        payee_name=None,
        amount=deposit.amount,
        score=assessment.score,
        level=assessment.level,
        reasons=assessment.reasons,
        status="completed",
        occurred_at=occurred_at,
        user_id=principal.id,
    )
    if assessment.level != "low":
        guardian_store.record_alert(
            account_id=account_id,
            amount=deposit.amount,
            score=assessment.score,
            level=assessment.level,
            reasons=assessment.reasons,
            created_at=occurred_at,
            user_id=principal.id,
        )
    return DepositWithRisk(deposit=created_deposit, risk=assessment)


@router.get("/accounts/{account_id}/transfers")
def list_transfers(
    account_id: str, client: NessieClient = Depends(get_nessie_client), _: Principal = Depends(require_principal)
) -> list[dict[str, Any]]:
    """Consulta las transferencias (caso APP Fraud) de una cuenta."""
    try:
        return client.list_transfers(account_id)
    except NessieError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible consultar las transferencias en Nessie.",
        ) from exc


@router.post(
    "/accounts/{account_id}/transfers", status_code=status.HTTP_201_CREATED
)
def create_transfer(
    account_id: str,
    transfer: TransferCreate,
    client: NessieClient = Depends(get_nessie_client),
    principal: Principal = Depends(require_customer),
) -> TransferWithRisk:
    """Registra una transferencia y devuelve su evaluación APP Fraud.

    Nessie sandbox rechaza la creación de transfers en esta versión
    (400 aun con schema válido), así que la persistencia en Nessie es
    best-effort: si falla, se devuelve evaluación local con 201 y
    ``nessie_persisted: False`` para no bloquear la demo.
    """
    from datetime import date as date_cls

    tx_date = transfer.transaction_date or date_cls.today()
    occurred_at = datetime.now(timezone.utc)
    priors = guardian_store.events_for(account_id, occurred_at)
    assessment = assess_transfer(
        transfer.amount,
        transfer.payee_id,
        priors,
        occurred_at,
        new_device=transfer.new_device,
        unusual_hour=transfer.unusual_hour,
        beneficiary_flagged=transfer.beneficiary_flagged,
    )

    # Una alerta alta se queda en pausa antes de intentar mover dinero. Es la
    # intervención de producto que diferencia Guardián de un simple monitor.
    if assessment.level == "high":
        created = {
            "_id": f"pending-{account_id[:8]}-{int(occurred_at.timestamp())}",
            "payer_id": account_id,
            "payee_id": transfer.payee_id,
            "medium": transfer.medium,
            "amount": transfer.amount,
            "transaction_date": tx_date.isoformat(),
            "status": "pending_review",
            "description": transfer.description or "Transferencia Guardian",
            "nessie_persisted": False,
        }
        operation_status = "pending_review"
    else:
        nessie_payload = {
            "medium": transfer.medium,
            "payee_id": transfer.payee_id,
            "amount": transfer.amount,
            "transaction_date": tx_date.isoformat(),
            "description": transfer.description or "Transferencia Guardian",
        }
        try:
            created = client.create_transfer(account_id, nessie_payload)
            created.setdefault("payee_id", transfer.payee_id)
            created["nessie_persisted"] = True
        except NessieError:
            created = {
                "_id": f"local-{account_id[:8]}-{int(occurred_at.timestamp())}",
                "payer_id": account_id,
                "payee_id": transfer.payee_id,
                "medium": transfer.medium,
                "amount": transfer.amount,
                "transaction_date": tx_date.isoformat(),
                "status": "completed",
                "description": transfer.description or "Transferencia Guardian",
                "created_at": occurred_at.isoformat(),
                "nessie_persisted": False,
            }
        operation_status = "completed"
        guardian_store.record_transaction(
            account_id, transfer.amount, occurred_at, payee_id=transfer.payee_id
        )

    guardian_store.record_operation(
        account_id=account_id,
        kind="transfer",
        description=transfer.description or "Transferencia Guardian",
        payee_name=transfer.payee_id,
        amount=transfer.amount,
        score=assessment.score,
        level=assessment.level,
        reasons=assessment.reasons,
        status=operation_status,
        occurred_at=occurred_at,
        user_id=principal.id,
    )
    if assessment.level != "low":
        guardian_store.record_alert(
            account_id=account_id,
            amount=transfer.amount,
            score=assessment.score,
            level=assessment.level,
            reasons=assessment.reasons,
            created_at=occurred_at,
            user_id=principal.id,
        )
    return TransferWithRisk(transfer=created, risk=assessment)
