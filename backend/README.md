# Backend de Guardián

API inicial de Guardián para detección de fraude financiero, construida con
FastAPI e integrada con la API de Capital One Nessie.

## Lo que ya está disponible

- Aplicación FastAPI en `main.py`.
- Endpoint de comprobación: `GET /`, que devuelve el estado del backend.
- Estructura inicial para rutas, modelos y motor de riesgo en `app/`.
- Dependencias declaradas en `requirements.txt`.

## Integración con Nessie

La integración está organizada en `app/nessie/`:

- `app/config.py`: carga y valida la configuración local.
- `app/nessie/client.py`: cliente HTTP para clientes, cuentas y depósitos.
- `app/nessie/seed.py`: seeder idempotente de una cliente y cuenta demo.

La API key se lee exclusivamente de `backend/.env`. No se guarda en el
repositorio ni debe copiarse en código, logs o documentación.

### Configuración local

Crea `backend/.env` con estos valores:

```env
NESSIE_API_KEY=tu_clave_de_nessie
NESSIE_BASE_URL=https://api.nessieisreal.com
```

`NESSIE_BASE_URL` es opcional y, si se omite, usa esa misma URL por defecto.

## Ejecutar el backend

Desde la carpeta `backend`:

```powershell
python -m uvicorn main:app --reload
```

El endpoint inicial queda disponible en `http://127.0.0.1:8000/`.

## Comprobar Nessie y cargar datos demo

Con las dependencias instaladas y el `.env` configurado, ejecuta:

```powershell
python -m app.nessie.seed
```

El seeder busca primero la cliente `Guardian Demo` y la cuenta
`Guardian Demo Checking`; sólo las crea si no existen. De esta manera puede
ejecutarse de nuevo sin duplicar esos recursos.

## Estado de verificación

Se implementó una comprobación autenticada mediante `NessieClient.healthcheck()`.
Durante la última prueba de red, Nessie no respondió dentro del tiempo de espera.
Si persiste, confirma que la URL configurada y la disponibilidad del servicio de
Nessie sean correctas antes de ejecutar el seeder.
