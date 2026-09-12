from fastapi import FastAPI

from app.routers import accounts, transactions


app = FastAPI(title="Guardián API", version="0.1.0")

app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/")
def read_root():
    return {"status": "Guardián backend activo"}
