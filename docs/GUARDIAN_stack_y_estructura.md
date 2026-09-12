# Guardián — Stack Tecnológico y Estructura del Proyecto

Documento de arquitectura base definido por el equipo para el hackathon.

## Principio
Priorizar una demo funcional y estable, con pocas piezas móviles, para concentrar el esfuerzo en el motor de riesgo.

## Stack
- Backend: Python, FastAPI, Uvicorn, httpx, Pandas, python-dotenv.
- Frontend: React + Vite, Tailwind, Recharts, Axios.
- Estado inicial: en memoria; SQLite solo si hace falta.
- Demo: local o túnel, evitando despliegues innecesarios.

## Estructura
- `backend/app/nessie`: integración con Nessie.
- `backend/app/risk_engine`: reglas y estadísticas.
- `backend/app/routers`: endpoints HTTP.
- `backend/app/models`: modelos Pydantic.
- `frontend/src`: dashboard y componentes.
- `pitch`: guion y materiales de demo.
