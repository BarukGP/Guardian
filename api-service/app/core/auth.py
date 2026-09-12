"""Sesiones opacas para el piloto local de Guardián.

El token es aleatorio, se guarda sólo como hash y expira. Esta capa permite
demostrar aislamiento de datos sin enviar una clave de servidor al navegador.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.infrastructure.database import guardian_store


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class Principal:
    id: str
    display_name: str
    role: str


def require_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión requerida.")
    user = guardian_store.session_user(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o expirada.")
    return Principal(id=user["id"], display_name=user["display_name"], role=user["role"])


def require_customer(principal: Principal = Depends(require_principal)) -> Principal:
    """Restringe decisiones financieras a la persona dueña de la cuenta demo."""
    if principal.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La vista de analista es únicamente de lectura.",
        )
    return principal
