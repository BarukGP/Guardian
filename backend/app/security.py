"""Autenticación sencilla por clave API para el MVP."""

from __future__ import annotations

from hmac import compare_digest
from typing import Annotated

from fastapi import HTTPException, Security, WebSocket, status
from fastapi.security import APIKeyHeader

from app.config import ConfigurationError, get_settings


API_KEY_HEADER_NAME = "X-Guardian-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


def _is_valid_api_key(provided_key: str | None) -> bool:
    try:
        expected_key = get_settings().guardian_api_key
    except ConfigurationError:
        return False
    return bool(expected_key and provided_key and compare_digest(provided_key, expected_key))


def require_api_key(
    provided_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    """Restringe rutas HTTP a clientes que presenten la clave local correcta."""
    try:
        configured_key = get_settings().guardian_api_key
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La autenticación no está configurada.",
        ) from exc

    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Falta GUARDIAN_API_KEY en la configuración local.",
        )
    if not _is_valid_api_key(provided_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave API inválida o ausente.",
            headers={"WWW-Authenticate": "ApiKey"},
        )


async def authorize_websocket(websocket: WebSocket, api_key: str | None = None) -> bool:
    """Valida la misma clave API antes de aceptar una conexión WebSocket.

    Los browsers no pueden enviar headers custom en el handshake WS,
    por eso se acepta también ``?api_key=`` como fallback al header.
    """
    provided = (
        api_key
        or websocket.query_params.get("api_key")
        or websocket.headers.get(API_KEY_HEADER_NAME)
    )
    if _is_valid_api_key(provided):
        return True
    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return False
