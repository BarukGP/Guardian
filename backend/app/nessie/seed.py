"""Datos de demostración reproducibles para Nessie.

Ejecutar desde la carpeta ``backend``: ``python -m app.nessie.seed``.
"""

from __future__ import annotations

from app.nessie.client import NessieClient


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


def seed_demo_data(client: NessieClient | None = None) -> dict[str, str]:
    """Crea (o reutiliza) una cliente y cuenta de demostración.

    La búsqueda por nombre y apodo evita duplicar los recursos al volver a
    ejecutar el seeder. No imprime credenciales ni respuestas sensibles.
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

        account = next(
            (
                item
                for item in nessie.list_customer_accounts(customer_id)
                if item.get("nickname") == DEMO_ACCOUNT["nickname"]
            ),
            None,
        )
        if account is None:
            account = nessie.create_account(customer_id, DEMO_ACCOUNT)

        account_id = account.get("_id")
        if not isinstance(account_id, str) or not account_id:
            raise RuntimeError("Nessie no devolvió un identificador de cuenta.")

        return {"customer_id": customer_id, "account_id": account_id}
    finally:
        if owns_client:
            nessie.close()


if __name__ == "__main__":
    resources = seed_demo_data()
    print(f"Datos demo listos (cliente: {resources['customer_id']}, cuenta: {resources['account_id']}).")
