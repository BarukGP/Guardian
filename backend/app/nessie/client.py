"""Cliente pequeño y seguro para la API de Capital One Nessie."""

from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings, get_settings


class NessieError(RuntimeError):
    """Error de comunicación con Nessie sin incluir la API key."""


class NessieClient:
    """Encapsula las llamadas a Nessie y adjunta la clave sólo como query param."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = httpx.Client(
            base_url=self._settings.nessie_base_url,
            timeout=self._settings.nessie_timeout_seconds,
        )

    def __enter__(self) -> "NessieClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def healthcheck(self) -> bool:
        """Comprueba credenciales y disponibilidad con un endpoint autenticado."""
        self.list_customers()
        return True

    def list_customers(self) -> list[dict[str, Any]]:
        data = self._request("GET", "/customers")
        if not isinstance(data, list):
            raise NessieError("Nessie devolvió una respuesta de clientes inesperada.")
        return data

    def create_customer(self, customer: dict[str, Any]) -> dict[str, Any]:
        return self._created_object(self._request("POST", "/customers", json=customer))

    def list_customer_accounts(self, customer_id: str) -> list[dict[str, Any]]:
        data = self._request("GET", f"/customers/{customer_id}/accounts")
        if not isinstance(data, list):
            raise NessieError("Nessie devolvió una respuesta de cuentas inesperada.")
        return data

    def create_account(self, customer_id: str, account: dict[str, Any]) -> dict[str, Any]:
        return self._created_object(
            self._request("POST", f"/customers/{customer_id}/accounts", json=account)
        )

    def create_deposit(self, account_id: str, deposit: dict[str, Any]) -> dict[str, Any]:
        return self._created_object(
            self._request("POST", f"/accounts/{account_id}/deposits", json=deposit)
        )

    @staticmethod
    def _created_object(data: Any) -> dict[str, Any]:
        """Extrae el recurso de la envoltura de creación de Nessie."""
        if isinstance(data, dict) and isinstance(data.get("objectCreated"), dict):
            return data["objectCreated"]
        if isinstance(data, dict) and isinstance(data.get("_id"), str):
            return data
        raise NessieError("Nessie no devolvió el recurso creado.")

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self._client.request(
                method, path, params={"key": self._settings.nessie_api_key}, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise NessieError(
                f"Nessie respondió con estado HTTP {exc.response.status_code}."
            ) from exc
        except httpx.HTTPError as exc:
            raise NessieError("No se pudo conectar con Nessie.") from exc
        except ValueError as exc:
            raise NessieError("Nessie devolvió JSON inválido.") from exc
