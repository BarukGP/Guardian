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
| `POST` | `/simulate/run` | Ejecuta la secuencia de demostración sin usar Nessie. |
| `GET` | `/simulate/alerts` | Consulta alertas persistidas en SQLite. |
| `WS` | `/simulate/alerts/stream` | Envía alertas nuevas en tiempo real. |

Las rutas de Nessie devuelven `502` si el servicio externo no está disponible
y `503` si falta la configuración local.

## Motor de riesgo inicial

Cada depósito creado pasa por reglas explicables y devuelve un puntaje de 0 a
100, nivel (`low`, `medium` o `high`) y motivos. Las señales actuales son:

- monto individual alto (10,000 o más);
- actividad rápida (tres o más movimientos previos en 10 minutos);
- volumen acumulado alto en 10 minutos; y
- monto que excede tres veces el promedio de los últimos 30 días.

Los movimientos y alertas se guardan localmente en `backend/data/guardian.db`.
La ruta se puede cambiar con `GUARDIAN_DATABASE_PATH`. SQLite es apropiado para
el MVP de una instancia; antes de escalar debe sustituirse por una base de datos
compartida.

## Simulación de fraude

`POST /simulate/run` procesa ocho movimientos predefinidos: historial normal,
actividad rápida, volumen alto y un monto alto. No crea recursos en Nessie y
devuelve cada evaluación junto con el total de alertas generadas.

Consulta las alertas con `GET /simulate/alerts` o ejecuta la simulación desde
la terminal, estando en `backend`:

```powershell
python scripts/simulate_stream.py
```

Para recibir alertas nuevas en tiempo real, conecta un cliente WebSocket a
`ws://127.0.0.1:8000/simulate/alerts/stream`.

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
