"""Configuración del backend.

Las credenciales se cargan exclusivamente desde ``backend/.env`` (o desde el
entorno del proceso) y nunca se incluyen en mensajes, excepciones o logs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")


class ConfigurationError(RuntimeError):
    """Señala una configuración local incompleta sin revelar secretos."""


@dataclass(frozen=True, slots=True)
class Settings:
    nessie_api_key: str
    nessie_base_url: str = "https://api.nessieisreal.com"
    nessie_timeout_seconds: float = 10.0


def get_settings() -> Settings:
    """Construye la configuración y valida los valores requeridos."""
    api_key = os.getenv("NESSIE_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "Falta NESSIE_API_KEY. Defínela en backend/.env o en el entorno."
        )

    base_url = os.getenv("NESSIE_BASE_URL", "https://api.nessieisreal.com").strip()
    if not base_url.startswith(("http://", "https://")):
        raise ConfigurationError("NESSIE_BASE_URL debe ser una URL HTTP(S) válida.")

    return Settings(nessie_api_key=api_key, nessie_base_url=base_url.rstrip("/"))


def get_database_path() -> Path:
    """Devuelve la ruta local para la persistencia SQLite del MVP."""
    configured_path = os.getenv("GUARDIAN_DATABASE_PATH", "").strip()
    return Path(configured_path) if configured_path else BACKEND_DIR / "data" / "guardian.db"
