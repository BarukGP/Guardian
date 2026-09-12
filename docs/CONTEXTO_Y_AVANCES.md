# Guardian — Contexto y avances

> Documento de continuidad para el equipo y para agentes de IA que trabajen con este repositorio.
> Actualizarlo cuando se complete una parte importante del proyecto.

## Contexto general

Guardian es un proyecto de hackathon orientado a la detección de fraude financiero.

La prioridad actual es tener una demo funcional, estable y fácil de explicar, evitando complejidad que no aporte directamente al MVP.

## Estado actual

### Backend

El backend ya fue integrado a `main` y está construido con FastAPI.

Actualmente incluye:

- integración con Capital One Nessie;
- configuración mediante `backend/.env`;
- persistencia local con SQLite;
- motor de riesgo explicable con score de 0 a 100;
- rutas de cuentas y depósitos;
- simulación local de fraude;
- almacenamiento y consulta de alertas;
- stream de alertas por WebSocket.

La raíz pública del backend es:

```text
GET /
```

y devuelve el estado de la API.

Las rutas operativas requieren:

```text
X-Guardian-API-Key: <GUARDIAN_API_KEY>
```

Endpoints relevantes ya disponibles:

```text
GET  /accounts/customers/{customer_id}
POST /accounts/customers/{customer_id}

GET  /transactions/accounts/{account_id}/deposits
POST /transactions/accounts/{account_id}/deposits

POST /simulate/run
GET  /simulate/alerts
WS   /simulate/alerts/stream
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Motor de riesgo actual

Las reglas iniciales del backend incluyen señales como:

- monto individual alto;
- actividad rápida;
- volumen acumulado alto en pocos minutos;
- monto muy superior al promedio reciente.

El motor devuelve:

- score de 0 a 100;
- nivel de riesgo;
- razones explicables.

## Frontend

La rama de integración de frontend es:

```text
feature/frontend-integration
```

El frontend está construido con:

- React;
- Vite;
- Axios.

Actualmente incluye una pantalla inicial de Guardian y un indicador visual del estado del backend:

- amarillo: comprobando;
- verde: conectado;
- rojo: desconectado.

## Conexión frontend ↔ backend

La conexión local ya fue probada correctamente.

El frontend usa Axios desde:

```text
frontend/src/services/api.js
```

y durante desarrollo usa un proxy de Vite configurado en:

```text
frontend/vite.config.js
```

El flujo actual es:

```text
React
  |
  v
/api
  |
  v
Vite proxy
  |
  v
http://127.0.0.1:8000
  |
  v
FastAPI
```

Esto evita depender de CORS durante desarrollo local.

Por ahora la comprobación de conexión consulta únicamente:

```text
GET /
```

porque esa ruta es pública.

## Cómo levantar el backend

Desde `backend/`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

## Cómo levantar el frontend

Desde `frontend/`:

```bash
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Para comprobar la integración local deben estar ejecutándose backend y frontend al mismo tiempo.

## Git y ramas

Estado de integración actual:

- `main`: contiene el backend integrado.
- `feature/frontend-integration`: contiene el frontend construido encima del `main` actualizado.
- El Pull Request del frontend debe apuntar de `feature/frontend-integration` hacia `main`.

La rama de integración del frontend fue creada desde el `main` que ya contenía el backend para evitar sobrescribir o reemplazar el trabajo del backend.

## Siguiente objetivo

Una vez integrado el frontend a `main`, el siguiente trabajo recomendado es conectar el dashboard con las rutas reales del backend.

Prioridades:

1. crear componentes para transacciones, score y alertas;
2. consumir `POST /simulate/run`;
3. mostrar las alertas obtenidas desde `GET /simulate/alerts`;
4. decidir cómo presentar las alertas en tiempo real usando `/simulate/alerts/stream`;
5. agregar el encabezado `X-Guardian-API-Key` a las llamadas protegidas;
6. construir el flujo visual de la demo del hackathon;
7. probar el flujo completo con Nessie cuando corresponda.

## Demo objetivo

Una demo posible:

1. abrir el dashboard;
2. mostrar estado normal;
3. ejecutar la simulación de fraude;
4. visualizar nuevas operaciones;
5. mostrar el aumento del risk score;
6. mostrar una alerta de riesgo;
7. explicar las razones de la detección.

## Reglas de colaboración

- No subir archivos `.env` con secretos.
- No subir `node_modules/`.
- No subir entornos virtuales.
- Trabajar en ramas antes de tocar `main`.
- Revisar `git status` antes de hacer commit.
- Evitar modificar archivos de otra área sin coordinarlo con la persona responsable.
- Mantener este archivo actualizado cuando cambie de forma importante el estado del proyecto.

## Para otros agentes de IA

Antes de modificar el proyecto:

1. leer este archivo;
2. leer `backend/README.md`;
3. revisar la rama actual y el estado de Git;
4. respetar la separación entre frontend y backend;
5. no asumir endpoints que no existan;
6. usar los contratos reales del backend;
7. priorizar un MVP demostrable para el hackathon.

---

**Estado resumido:** backend integrado en `main`, frontend funcional en rama de integración y conexión frontend ↔ backend verificada localmente.

**Siguiente paso:** fusionar el frontend a `main` y comenzar el dashboard conectado a los endpoints protegidos del backend.
