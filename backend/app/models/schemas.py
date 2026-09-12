"""Modelos de entrada para la API de Guardián."""

from __future__ import annotations

from datetime import date
from typing import Literal

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
