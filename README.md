# Guardián

Guardián es un piloto de protección contra fraude por ingeniería social. Nace de un problema muy concreto: muchas transferencias fraudulentas no parecen fraudulentas para un banco porque quien las autoriza es la propia víctima. Alguien la convenció de que hablaba con soporte, con un familiar o con su banco, creó urgencia y logró que enviara el dinero.

En esos casos no basta con detectar una tarjeta robada o un cargo duplicado. Guardián busca intervenir justo antes de que la transferencia salga: explica por qué parece riesgosa, la deja en pausa y hace una pregunta sencilla que ayuda a la persona a detenerse y pensar. La persona conserva la decisión final, pero ya no decide bajo la misma presión.

El piloto usa a Rosa Elena, una clienta ficticia, para contar esa historia. También incluye un perfil de analista para revisar los eventos y casos generados durante la demostración.

## Objetivo

Demostrar que un banco puede reducir el fraude APP (*Authorized Push Payment*) con una experiencia clara y explicable:

- detectar señales de riesgo en una transferencia;
- mostrar el motivo de la alerta en lenguaje entendible;
- poner en pausa únicamente las operaciones de riesgo alto;
- permitir cancelar, confirmar el destino o reportar presión;
- dejar una auditoría que ayude a investigar lo ocurrido.

No pretende ser un sistema bancario productivo todavía. Es un MVP funcional, local y repetible, diseñado para enseñar el flujo de prevención y servir como base técnica para una siguiente etapa.

## Qué está implementado

### Prevención y respuesta

- Motor de riesgo explicable con puntuación de `0` a `100`.
- Pausa de seguridad para transferencias con riesgo alto (`60` o más).
- Tres decisiones para una operación en pausa: **cancelar**, **confirmar que se conoce el destino** o **reportar presión**.
- Creación automática de un caso de protección cuando la persona reporta presión.
- Línea de tiempo de operaciones, alertas, casos y eventos de auditoría.
- Simulador local de un escenario de estafa que genera ocho movimientos y una transferencia sospechosa.

### Seguridad y perfiles

- Inicio de sesión local con contraseña configurada únicamente en el servicio API.
- Sesiones Bearer temporales de ocho horas; el navegador nunca recibe una clave de Nessie ni una contraseña de servidor.
- Perfil **Cliente**: puede simular, reiniciar y resolver sus propias operaciones en pausa.
- Perfil **Analista**: consulta la actividad, alertas, casos y auditoría globales en modo de solo lectura.
- Aislamiento de información por usuario para el perfil cliente.

### Integración y persistencia

- Cliente HTTP para la API de Nessie de Capital One: consulta y creación de cuentas, depósitos y transferencias.
- Base SQLite local para sesiones, operaciones, alertas, casos y auditoría.
- La demo no necesita conexión a Nessie: el simulador funciona completamente en local.
- Cuando Nessie no acepta una transferencia en el sandbox, el sistema conserva la evaluación local para no interrumpir la demostración.

## Cómo calcula el riesgo

Las reglas están en `api-service/app/services/risk_engine/`. Son intencionalmente visibles y auditables; cada regla agrega una razón al resultado.

| Señal | Puntos |
| --- | ---: |
| Monto igual o mayor a 10,000 | +60 |
| Beneficiario nuevo | +30 |
| Tres o más movimientos en diez minutos | +25 |
| Volumen acumulado mayor a 5,000 en diez minutos | +20 |
| Monto tres veces mayor al promedio histórico | +20 |
| Dispositivo nuevo | +15 |
| Horario fuera del patrón | +10 |
| Beneficiario con señales previas de riesgo | +35 |

El puntaje se limita a 100. De `0` a `24` es bajo, de `25` a `59` es medio y desde `60` es alto. Una alerta alta no ejecuta la transferencia de inmediato: queda como `pending_review` hasta que la persona tome una decisión.

## Arquitectura

```text
Guardian/
├── api-service/                         # Servicio FastAPI y lógica de negocio
│   ├── app/
│   │   ├── api/                         # Endpoints HTTP y registro de rutas
│   │   ├── core/                        # Configuración, autenticación y permisos
│   │   ├── domain/                      # Esquemas Pydantic
│   │   ├── infrastructure/              # SQLite y cliente Nessie
│   │   └── services/                    # Simulación y motor de riesgo
│   ├── tests/                           # Pruebas del flujo crítico
│   ├── .env.example                     # Plantilla de variables de entorno
│   ├── requirements.txt                 # Dependencias de Python
│   └── main.py                          # Punto de entrada FastAPI
├── web-client/                          # Interfaz React + Vite
│   ├── public/                          # Recursos públicos
│   ├── src/
│   │   ├── app/                         # Bootstrap y estilos globales
│   │   ├── features/                    # Login, feed, casos y simulación
│   │   └── shared/                      # Cliente HTTP y utilidades
│   └── package.json
└── README.md
```

La separación es deliberada: las rutas HTTP viven en `api/`, las reglas de fraude en `services/risk_engine/`, las integraciones externas en `infrastructure/` y los contratos de datos en `domain/`. En el cliente web, cada capacidad se agrupa dentro de `features/` para evitar una carpeta única de componentes difíciles de mantener.

## Tecnologías

| Capa | Tecnologías |
| --- | --- |
| API | Python 3.12, FastAPI, Pydantic, Uvicorn, HTTPX y python-dotenv |
| Persistencia | SQLite estándar de Python |
| Cliente web | React 19, Vite 8, Axios, Tailwind CSS y Lucide |
| Integración externa | API Nessie de Capital One |
| Pruebas | `unittest` y build/lint de Vite |

## Requisitos previos

- Git.
- Python 3.12 o compatible.
- Node.js 20 o superior con npm.
- Una API key de Nessie solo si se desean probar los endpoints reales de cuentas y movimientos. No es necesaria para la demo local.

## Instalación

Después de clonar el repositorio, abre una terminal en su carpeta raíz.

### 1. Preparar el servicio API

En PowerShell:

```powershell
cd api-service
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

En macOS o Linux, cambia las rutas de Windows por `./venv/bin/python` y usa `cp .env.example .env`.

Edita `api-service/.env` y define, como mínimo, una contraseña local de ocho caracteres o más:

```env
GUARDIAN_DEMO_PASSWORD=elige_una_contrasena_local_segura
```

Para usar Nessie agrega también:

```env
NESSIE_API_KEY=tu_api_key_de_nessie
NESSIE_BASE_URL=https://api.nessieisreal.com
```

`GUARDIAN_DATABASE_PATH` es opcional. Si se deja vacío, la base local se crea en `api-service/data/guardian.db`.

Nunca subas `.env`, tokens, contraseñas ni la base de datos local al repositorio.

### 2. Preparar el cliente web

Desde la raíz del repositorio, abre otra terminal:

```powershell
cd web-client
npm install
```

El cliente usa por defecto `http://127.0.0.1:8000`. Si la API se ejecuta en otra dirección, crea `web-client/.env` a partir de `.env.example` y ajusta:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Ejecutar el piloto

Abre dos terminales desde la raíz del repositorio.

Primera terminal — servicio API:

```powershell
cd api-service
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000` y la documentación Swagger en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Segunda terminal — cliente web:

```powershell
cd web-client
npm run dev
```

Abre la dirección que imprima Vite, normalmente [http://localhost:5173](http://localhost:5173). Selecciona **Rosa Elena · Cliente**, escribe la contraseña definida en `api-service/.env` y pulsa **Entrar al piloto**.

La sesión se conserva durante ocho horas. Para regresar al login, usa el botón de cerrar sesión del encabezado.

## Recorrido recomendado para la demo

1. Inicia sesión como **Rosa Elena · Cliente**.
2. Pulsa **Simular escenario de estafa**.
3. Observa el feed: aparece una transferencia a un beneficiario nuevo con riesgo alto.
4. Revisa la tarjeta de **Pausa de seguridad** y sus razones.
5. Prueba una de estas respuestas:
   - **Cancelar y revisar**: la operación se cancela y no se genera un caso.
   - **Confirmar que conozco el destino**: se confirma la operación y desaparece la pausa.
   - **Alguien me está presionando**: se cancela el flujo y se abre un caso de protección.
6. Cierra sesión e inicia como **Analista Guardián · Analista** para ver la actividad y auditoría en modo lectura.
7. Usa **Reiniciar demo** cuando quieras comenzar de nuevo con el perfil cliente.

## API disponible

Todas las rutas operativas requieren una sesión Bearer, excepto `POST /auth/login` y `GET /`.

| Grupo | Rutas principales | Uso |
| --- | --- | --- |
| Autenticación | `POST /auth/login`, `GET /auth/me`, `POST /auth/logout` | Inicio, consulta y cierre de sesión. |
| Simulación | `POST /simulate/run`, `GET /simulate/timeline`, `GET /simulate/alerts` | Ejecutar la demo y consultar el feed. |
| Decisiones | `POST /simulate/operations/{id}/decision`, `DELETE /simulate/demo` | Resolver una pausa o reiniciar el historial demo. |
| Protección | `GET /simulate/cases`, `GET /simulate/audit` | Consultar casos y evidencia de decisiones. |
| Nessie | `/accounts/*`, `/transactions/*` | Consultar o crear cuentas, depósitos y transferencias. |

La interfaz usa polling cada 2.5 segundos para actualizar el feed. No depende de WebSockets, lo que mantiene el piloto más sencillo de ejecutar localmente.

## Pruebas y verificación

Ejecuta las pruebas del servicio:

```powershell
cd api-service
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Se esperan cinco pruebas y un resultado final `OK`. Cubren la pausa por fraude APP, cancelación, confirmación única, caso por presión, aislamiento por perfil y señales contextuales de riesgo.

Para validar el cliente web:

```powershell
cd web-client
npm run build
npm run lint
```

El build debe terminar correctamente. El linter puede reportar advertencias de React sobre actualizaciones de estado dentro de efectos; no bloquean la compilación ni el flujo del piloto, pero conviene resolverlas antes de una versión productiva.

## Límites actuales y siguiente etapa

Guardián funciona como piloto local, no como plataforma bancaria lista para producción. Para una siguiente etapa sería importante incorporar una base de datos gestionada, cifrado de secretos, cuentas reales, roles administrables, límites por usuario, auditoría inmutable, monitoreo, pruebas de carga y reglas calibradas con datos reales.

Lo valioso del MVP ya está en su flujo central: detectar una transferencia sospechosa, explicar el riesgo, dar una pausa útil y registrar la decisión sin quitarle a la persona el control de su dinero.
