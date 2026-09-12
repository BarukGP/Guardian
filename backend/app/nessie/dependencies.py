"""Dependencias de FastAPI para acceder a Nessie de forma segura."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import HTTPException, status

from app.config import ConfigurationError
from app.nessie.client import NessieClient


def get_nessie_client() -> Generator[NessieClient, None, None]:
    """Proporciona un cliente por petición y cierra su conexión al terminar."""
    try:
        client = NessieClient()
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La integración con Nessie no está configurada.",
        ) from exc

    try:
        yield client
    finally:
        client.close()
