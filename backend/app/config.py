import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    nessie_api_key: str = os.getenv("NESSIE_API_KEY", "")
    nessie_base_url: str = os.getenv("NESSIE_BASE_URL", "")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
