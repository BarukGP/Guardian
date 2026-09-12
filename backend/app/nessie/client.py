"""Cliente HTTP para Nessie.

Se completa cuando el equipo confirme los endpoints y credenciales del hackathon.
"""

import httpx

from app.config import settings


class NessieClient:
    def __init__(self):
        self.base_url = settings.nessie_base_url.rstrip("/")
        self.api_key = settings.nessie_api_key

    async def get(self, path: str):
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{self.base_url}/{path.lstrip('/')}", headers=headers)
            response.raise_for_status()
            return response.json()
