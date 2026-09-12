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

La documentación interactiva queda disponible en `http://127.0.0.1:8000/docs`.

## Endpoints disponibles

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/` | Estado del backend. |
| `GET` | `/accounts/customers/{customer_id}` | Lista las cuentas de una cliente. |
| `POST` | `/accounts/customers/{customer_id}` | Crea una cuenta. |
| `GET` | `/transactions/accounts/{account_id}/deposits` | Lista los abonos de una cuenta. |
| `POST` | `/transactions/accounts/{account_id}/deposits` | Registra un abono y devuelve su riesgo. |

Las rutas de Nessie devuelven `502` si el servicio externo no está disponible
y `503` si falta la configuración local.

## Motor de riesgo inicial

Cada depósito creado pasa por reglas explicables y devuelve un puntaje de 0 a
100, nivel (`low`, `medium` o `high`) y motivos. Las señales actuales son:

- monto individual alto (10,000 o más);
- actividad rápida (tres o más movimientos previos en 10 minutos);
- volumen acumulado alto en 10 minutos; y
- monto que excede tres veces el promedio de los últimos 30 días.

El historial se conserva en memoria por proceso y hasta 30 días; es apropiado
para el MVP, pero debe sustituirse por persistencia compartida antes de escalar.

## Comprobar Nessie y cargar datos demo

Con las dependencias instaladas y el `.env` configurado, ejecuta:

```powershell
python -m app.nessie.seed
```

El seeder busca primero la cliente `Guardian Demo` y la cuenta
`Guardian Demo Checking`; sólo las crea si no existen. De esta manera puede
ejecutarse de nuevo sin duplicar esos recursos.

## Estado de verificación

Se verificó una conexión autenticada mediante `NessieClient.healthcheck()` y se
ejecutó el seeder correctamente. La instancia configurada responde mediante
HTTPS; usa `https://api.nessieisreal.com` como `NESSIE_BASE_URL`.
