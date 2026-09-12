"""Modelos de entrada para la API de Guardián."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    """Datos necesarios para abrir una cuenta en Nessie."""

    type: Literal["Checking", "Savings", "Credit Card"]
    nickname: str = Field(min_length=1, max_length=80)
    rewards: int = Field(default=0, ge=0)
    balance: float = Field(default=0, ge=0)
    account_number: str = Field(min_length=4, max_length=32)


class DepositCreate(BaseModel):
    """Movimiento de abono para una cuenta."""

    medium: Literal["balance", "cash", "check", "transfer"]
    status: Literal["pending", "completed", "cancelled"] = "completed"
    transaction_date: date
    amount: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=255)


class RiskAssessment(BaseModel):
    """Resultado explicable de la evaluación de fraude."""

    score: int = Field(ge=0, le=100)
    level: Literal["low", "medium", "high"]
    reasons: list[str]


class DepositWithRisk(BaseModel):
    """Depósito creado y la evaluación de riesgo asociada."""

    deposit: dict[str, Any]
    risk: RiskAssessment


class TransferCreate(BaseModel):
    """Transferencia entre cuentas (caso APP Fraud: Rosa Elena -> estafador)."""

    medium: Literal["balance", "rewards"] = "balance"
    payee_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    transaction_date: date | None = None
    description: str | None = Field(default=None, min_length=1, max_length=255)
    new_device: bool = False
    unusual_hour: bool = False
    beneficiary_flagged: bool = False


class TransferWithRisk(BaseModel):
    """Transferencia creada y la evaluación de riesgo asociada."""

    transfer: dict[str, Any]
    risk: RiskAssessment


class ReviewDecision(BaseModel):
    """Decisión explícita tomada después de la pausa de seguridad."""

    decision: Literal["confirmed", "cancelled", "reported_pressure"]


class TimelineOperation(BaseModel):
    """Operación evaluada que el frontend puede mostrar en su feed."""

    id: int
    account_id: str
    kind: Literal["deposit", "transfer"]
    description: str
    payee_name: str | None = None
    amount: float
    risk: RiskAssessment
    status: Literal["completed", "pending_review", "confirmed", "cancelled", "reported_pressure"]
    occurred_at: datetime
    resolved_at: datetime | None = None


class RiskAlert(BaseModel):
    """Alerta persistida en memoria para mostrar actividad sospechosa."""

    id: int
    account_id: str
    amount: float
    risk: RiskAssessment
    created_at: datetime


class SimulatedTransaction(BaseModel):
    """Movimiento generado durante una ejecución de demostración."""

    amount: float
    description: str
    occurred_at: datetime
    risk: RiskAssessment
    kind: Literal["deposit", "transfer"] = "deposit"
    payee_name: str | None = None
    status: Literal["completed", "pending_review"] = "completed"


class SimulationResult(BaseModel):
    """Resumen de una ejecución del simulador."""

    account_id: str
    processed: int
    alerts_generated: int
    transactions: list[SimulatedTransaction]


class LoginRequest(BaseModel):
    """Credenciales locales para el piloto, nunca enviadas por query string."""

    user_id: Literal["rosa-elena", "analyst-demo"]
    password: str = Field(min_length=8, max_length=128)


class SessionUser(BaseModel):
    id: str
    display_name: str
    role: Literal["customer", "analyst"]


class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_at: datetime
    user: SessionUser


class FraudCase(BaseModel):
    id: int
    user_id: str
    user_display_name: str | None = None
    operation_id: int
    status: Literal["open", "resolved"]
    created_at: datetime


class AuditEvent(BaseModel):
    id: int
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    occurred_at: datetime
