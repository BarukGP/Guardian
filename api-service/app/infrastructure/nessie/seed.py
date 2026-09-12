"""Datos de demostración reproducibles para Nessie.

Ejecutar desde la carpeta ``api-service``: ``python -m app.infrastructure.nessie.seed``.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from app.infrastructure.nessie.client import NessieClient
from app.infrastructure.database import guardian_store


DEMO_CUSTOMER = {
    "first_name": "Guardian",
    "last_name": "Demo",
    "address": "100 Innovation Drive",
    "city": "Austin",
    "state": "TX",
    "zip": "78701",
}
DEMO_ACCOUNT = {
    "type": "Checking",
    "nickname": "Guardian Demo Checking",
    "rewards": 0,
    "balance": 2500.0,
    "account_number": "000112233445",
}
# Cuentas contraparte: 3 payees conocidos (baseline) + 1 estafador (demo en vivo).
KNOWN_PAYEES = (
    {"nickname": "Guardian Familiar", "account_number": "000100000001"},
    {"nickname": "Guardian Proveedor", "account_number": "000100000002"},
    {"nickname": "Guardian Ahorro", "account_number": "000100000003"},
)
SCAMMER_PAYEE = {"nickname": "Guardian Soporte Falso", "account_number": "000199999999"}


def _get_or_create_account(nessie: NessieClient, customer_id: str, spec: dict[str, object]) -> dict:
    existing = next(
        (
            item
            for item in nessie.list_customer_accounts(customer_id)
            if item.get("nickname") == spec["nickname"]
        ),
        None,
    )
    if existing is not None:
        return existing
    payload = {
        "type": "Checking",
        "nickname": spec["nickname"],
        "rewards": 0,
        "balance": 2500.0,
        "account_number": spec["account_number"],
    }
    return nessie.create_account(customer_id, payload)


def seed_demo_data(client: NessieClient | None = None) -> dict[str, str]:
    """Crea cliente, cuenta principal, payees y baseline local de 60 movimientos.

    - Cuentas en Nessie (idempotente, no duplica).
    - Historial de 60 transfers normales en SQLite local (no satura Nessie):
      3 payees conocidos, montos 80-350, últimos 21 días. Esto da baseline
      real para las reglas 3x-promedio y beneficiario-nuevo.
    - Intenta 3 transfers reales en Nessie como prueba (best-effort).
    """
    owns_client = client is None
    nessie = client or NessieClient()
    try:
        customer = next(
            (
                item
                for item in nessie.list_customers()
                if item.get("first_name") == DEMO_CUSTOMER["first_name"]
                and item.get("last_name") == DEMO_CUSTOMER["last_name"]
            ),
            None,
        )
        if customer is None:
            customer = nessie.create_customer(DEMO_CUSTOMER)

        customer_id = customer.get("_id")
        if not isinstance(customer_id, str) or not customer_id:
            raise RuntimeError("Nessie no devolvió un identificador de cliente.")

        account = _get_or_create_account(nessie, customer_id, DEMO_ACCOUNT)
        account_id = account.get("_id")
        if not isinstance(account_id, str) or not account_id:
            raise RuntimeError("Nessie no devolvió un identificador de cuenta.")

        payee_ids: dict[str, str] = {}
        for spec in (*KNOWN_PAYEES, SCAMMER_PAYEE):
            payee = _get_or_create_account(nessie, customer_id, spec)  # type: ignore[arg-type]
            pid = payee.get("_id")
            if isinstance(pid, str) and pid:
                payee_ids[str(spec["nickname"])] = pid

        # Baseline local: 60 movimientos normales a payees conocidos.
        rng = random.Random(42)
        now = datetime.now(timezone.utc)
        known_ids = [payee_ids[s["nickname"]] for s in KNOWN_PAYEES if s["nickname"] in payee_ids]
        fallback_payees = known_ids or ["payee-familiar", "payee-proveedor", "payee-ahorro"]
        for i in range(60):
            days_ago = rng.randint(0, 21)
            occurred = now - timedelta(days=days_ago, hours=rng.randint(0, 12))
            amount = round(rng.uniform(80.0, 350.0), 2)
            payee_id = fallback_payees[i % len(fallback_payees)]
            guardian_store.record_transaction(account_id, amount, occurred, payee_id=payee_id)

        # 3 transfers reales best-effort (si Nessie falla, el baseline local basta).
        for i in range(3):
            try:
                nessie.create_transfer(
                    account_id,
                    {
                        "medium": "balance",
                        "payee_id": fallback_payees[i % len(fallback_payees)],
                        "amount": 120.0,
                        "transaction_date": now.date().isoformat(),
                        "status": "completed",
                        "description": f"Baseline demo {i+1}",
                    },
                )
            except Exception:
                break

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "scammer_payee_id": payee_ids.get("Guardian Soporte Falso", ""),
        }
    finally:
        if owns_client:
            nessie.close()


if __name__ == "__main__":
    resources = seed_demo_data()
    print(f"Datos demo listos (cliente: {resources['customer_id']}, cuenta: {resources['account_id']}).")
