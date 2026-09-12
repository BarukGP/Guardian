from fastapi import FastAPI

app = FastAPI(title="Guardián API")

@app.get("/")
def read_root():
    return {"status": "Guardián backend activo"}