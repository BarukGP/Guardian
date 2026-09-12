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


class RiskAlert(BaseModel):
    """Alerta persistida en memoria para mostrar actividad sospechosa."""

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


class SimulationResult(BaseModel):
    """Resumen de una ejecución del simulador."""

    account_id: str
    processed: int
    alerts_generated: int
    transactions: list[SimulatedTransaction]
