# Guardian — Contexto y avances del proyecto

> Documento de continuidad para el equipo y para agentes de IA que colaboren en el repositorio.
> Mantener este archivo actualizado cuando se complete una parte importante del proyecto.

## 1. Contexto general

Guardian es un proyecto de hackathon orientado a la **detección de fraude financiero**.

La prioridad del equipo es tener una demo:
- funcional,
- estable,
- fácil de explicar,
- y con suficiente profundidad técnica para defender el proyecto frente a jueces.

La estrategia acordada es evitar complejidad innecesaria y concentrar el esfuerzo en el **motor de riesgo**, la integración con la fuente de transacciones y una demo clara.

## 2. Objetivo del MVP

El flujo esperado de Guardian es:

1. Recibir u obtener transacciones financieras.
2. Analizar cada transacción con un motor de riesgo.
3. Calcular un **Risk Score de 0 a 100**.
4. Explicar por qué la transacción fue marcada como normal, sospechosa o de alto riesgo.
5. Mostrar el resultado en un dashboard.
6. Permitir disparar una transacción fraudulenta durante la demo para mostrar la detección en tiempo real.

Ejemplo de salida esperada:

- Risk Score: 82/100
- Nivel: alto
- Razones:
  - monto muy superior al comportamiento habitual,
  - beneficiario nuevo,
  - patrón de actividad inusual.

## 3. Stack actual

### Backend
- Python
- FastAPI
- Uvicorn
- httpx
- Pandas
- python-dotenv

### Frontend
- React
- Vite
- Axios
- Recharts
- Tailwind CSS previsto en la arquitectura

### Datos
- Integración prevista con Nessie.
- Estado temporal en memoria para el MVP.
- SQLite solo si realmente hace falta.

## 4. Estructura actual del repositorio

```text
Guardian/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── config.py
│       ├── models/
│       │   └── schemas.py
│       ├── nessie/
│       │   └── client.py
│       ├── risk_engine/
│       │   ├── rules.py
│       │   ├── stats.py
│       │   └── state.py
│       └── routers/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       └── styles.css
│
├── docs/
│   ├── GUARDIAN_stack_y_estructura.md
│   └── CONTEXTO_Y_AVANCES.md
│
├── pitch/
│   └── guion_demo.md
│
├── .gitignore
└── README.md
```

## 5. Avances completados

### Repositorio
- Se creó la rama `feature/project-scaffold`.
- La rama `main` se dejó sin tocar para mantenerla estable.
- Se creó la estructura base del monorepo.

### Backend
- FastAPI ya arranca correctamente.
- Existen los endpoints básicos:
  - `GET /`
  - `GET /health`
- CORS básico configurado.
- Variables de entorno configuradas mediante `.env`.
- Se creó un cliente base para Nessie.
- Se crearon modelos Pydantic iniciales.
- Se creó la estructura del motor de riesgo.
- Existe una primera regla temporal de prueba para validar el flujo del motor.

### Prueba local realizada
El backend fue probado localmente y respondió correctamente:

```json
{
  "name": "Guardian",
  "status": "running"
}
```

También está disponible Swagger en:

```text
http://127.0.0.1:8000/docs
```

### Frontend
- Se creó la base con React + Vite.
- Existe una pantalla inicial de Guardian.
- El frontend todavía necesita terminar de conectarse al backend y desarrollar el dashboard final.

## 6. Lo que sigue

Prioridad inmediata:

1. Terminar el motor de riesgo real.
2. Crear los endpoints:
   - `GET /transactions`
   - `GET /accounts/{id}/score`
   - `POST /simulate-fraud`
3. Crear datos simulados para desarrollar sin depender de Nessie.
4. Conectar React al backend.
5. Construir:
   - feed de transacciones,
   - alertas,
   - score de riesgo,
   - explicación de razones,
   - gráfica de historial.
6. Integrar Nessie cuando el flujo local ya funcione.
7. Preparar el escenario exacto del pitch y la demo.

## 7. Motor de riesgo — dirección propuesta

El motor no debe limitarse a decir "fraude/no fraude".

Debe devolver:
- score numérico,
- nivel de riesgo,
- lista de razones.

Reglas candidatas para el hackathon:
- monto mucho mayor al promedio histórico,
- beneficiario nuevo,
- varias transacciones en poco tiempo,
- horario atípico,
- cambio brusco en el patrón del usuario,
- operación muy distinta al comportamiento reciente.

Las reglas deben ser ponderadas para formar un score de 0 a 100.

## 8. Estrategia de demo

Una posible demo:

1. Mostrar transacciones normales de una cuenta.
2. Mostrar que el score se mantiene bajo.
3. Pulsar un botón de "Simular fraude".
4. Insertar una operación claramente anómala.
5. Guardian actualiza el score.
6. El dashboard muestra una alerta roja.
7. Se explican las razones concretas de la detección.

La demo debe seguir funcionando incluso si una API externa falla. Por eso primero se desarrollará con datos simulados y después se conectará Nessie.

## 9. Cómo levantar el backend

Desde la raíz del repositorio:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## 10. Cómo levantar el frontend

Se necesita Node.js y npm.

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Por defecto Vite debería levantar en:

```text
http://localhost:5173
```

## 11. Reglas de colaboración

- No trabajar directamente sobre `main` mientras el MVP está en construcción.
- Usar ramas `feature/`.
- Hacer cambios pequeños y fáciles de revisar.
- No subir archivos `.env` con claves reales.
- Mantener `.env.example` actualizado.
- No introducir una tecnología nueva si no mejora claramente la demo.
- Antes de integrar una parte a `main`, comprobar que corre localmente.
- Actualizar este documento cuando cambie de forma importante el estado del proyecto.

## 12. Instrucción para otros agentes de IA

Si un agente de IA recibe este repositorio:

1. Leer primero este archivo.
2. Leer `docs/GUARDIAN_stack_y_estructura.md`.
3. Revisar el estado actual de la rama antes de crear código.
4. Mantener la separación entre:
   - `nessie/` para integración externa,
   - `risk_engine/` para lógica de riesgo,
   - `routers/` para API,
   - frontend para visualización.
5. Priorizar un MVP demostrable antes que una arquitectura compleja.
6. No reemplazar decisiones del equipo sin justificar claramente por qué.
7. Documentar los avances relevantes en este archivo.

---

## Estado resumido

**Estado actual:** scaffolding funcional + backend levantando correctamente.

**Siguiente objetivo técnico:** motor de riesgo + endpoints de transacciones y simulación de fraude.

**Rama de trabajo actual:** `feature/project-scaffold`.
