"""Registro centralizado de rutas HTTP."""

from fastapi import FastAPI

from app.api.routes import accounts, auth, simulation, transactions


def register_routers(app: FastAPI) -> None:
    """Monta los módulos HTTP sin acoplar el punto de entrada a cada ruta."""
    app.include_router(auth.router)
    app.include_router(accounts.router)
    app.include_router(transactions.router)
    app.include_router(simulation.router)
