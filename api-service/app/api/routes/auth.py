"""Autenticación local limitada al piloto de demostración."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.auth import Principal, bearer_scheme, require_principal
from app.core.config import get_settings
from app.domain.schemas import LoginRequest, LoginResponse, SessionUser
from app.infrastructure.database import guardian_store


router = APIRouter(prefix="/auth", tags=["auth"])
SESSION_DURATION = timedelta(hours=8)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    settings = get_settings()
    if not settings.guardian_demo_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Falta configurar GUARDIAN_DEMO_PASSWORD para el piloto local.",
        )
    guardian_store.ensure_demo_users(settings.guardian_demo_password)
    user = guardian_store.authenticate_demo_user(payload.user_id, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas.")
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + SESSION_DURATION
    guardian_store.create_session(token, user["id"], expires_at)
    return LoginResponse(
        access_token=token,
        expires_at=expires_at,
        user=SessionUser(**user),
    )


@router.get("/me", response_model=SessionUser)
def me(principal: Principal = Depends(require_principal)) -> SessionUser:
    return SessionUser(id=principal.id, display_name=principal.display_name, role=principal.role)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    _: Principal = Depends(require_principal),
) -> None:
    if credentials is not None:
        guardian_store.revoke_session(credentials.credentials)
