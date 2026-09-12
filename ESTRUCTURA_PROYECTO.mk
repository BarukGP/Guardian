# Estructura técnica — Guardián

Raíz del proyecto: `C:\Users\smyoi\Documents\Guardian\Guardian`

## Servicio API

Ubicación: `C:\Users\smyoi\Documents\Guardian\Guardian\api-service`

```text
api-service/
├── main.py                              # Arranque FastAPI
├── app/
│   ├── api/
│   │   ├── router.py                     # Registro de rutas
│   │   └── routes/                       # Auth, cuentas, transacciones y simulación
│   ├── core/                             # Configuración, sesiones y permisos
│   ├── domain/                           # Esquemas Pydantic
│   ├── infrastructure/
│   │   ├── database.py                   # Persistencia SQLite
│   │   └── nessie/                       # Cliente e inicialización Nessie
│   └── services/
│       ├── simulation.py                 # Caso de uso de la demo
│       └── risk_engine/                  # Reglas, estado y estadísticas
├── tests/                                # Pruebas automatizadas
├── .env.example                          # Plantilla de entorno
└── requirements.txt                      # Dependencias Python
```

Acciones actualizadas:

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\api-service
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\api-service
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\api-service
.\venv\Scripts\python.exe -m app.services.simulation
```

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\api-service
.\venv\Scripts\python.exe -m app.infrastructure.nessie.seed
```

## Cliente web

Ubicación: `C:\Users\smyoi\Documents\Guardian\Guardian\web-client`

```text
web-client/
├── public/                               # Ícono y recursos públicos
├── src/
│   ├── app/                              # Bootstrap React y estilos globales
│   ├── features/
│   │   ├── auth/                         # Inicio de sesión
│   │   ├── dashboard/                    # Cabecera y resumen de riesgo
│   │   ├── simulation/                   # Pausa y botón de simulación
│   │   ├── timeline/                     # Feed y consulta periódica
│   │   └── cases/                        # Casos de protección
│   └── shared/
│       ├── api/                          # Cliente HTTP único
│       └── lib/                          # Formateadores y utilidades
├── index.html
├── package.json
└── vite.config.js
```

Acciones actualizadas:

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\web-client
npm run dev
```

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\web-client
npm run build
```

## Reglas de ubicación

- Una ruta HTTP nueva va en `api-service/app/api/routes/` y se registra en `api-service/app/api/router.py`.
- Una regla de fraude va en `api-service/app/services/risk_engine/`.
- Una integración externa va en `api-service/app/infrastructure/`.
- Un contrato de request o response va en `api-service/app/domain/schemas.py`.
- Una pantalla o componente va dentro del módulo correspondiente de `web-client/src/features/`.
- Código reutilizable sin dependencia de una feature va en `web-client/src/shared/`.
