# Guardián

Guardián es un piloto local para prevenir fraudes por ingeniería social antes de que una transferencia salga de la cuenta. Está pensado para un escenario frecuente: la persona hace la operación por voluntad propia, pero lo hace bajo presión o engaño de alguien que suplanta a su banco, a un familiar o a soporte técnico.

En lugar de bloquear sin explicación, el sistema identifica señales de riesgo, pone en pausa la operación y presenta una pregunta simple que ayuda a romper la urgencia creada por la estafa. La intención es proteger sin quitarle por completo el control a la persona.

## Qué demuestra el proyecto

- Evalúa transferencias con reglas claras: beneficiario nuevo, monto inusual, velocidad de movimientos, volumen acumulado, dispositivo nuevo y beneficiario previamente señalado.
- Explica por qué una operación recibió cierto riesgo; no usa una caja negra.
- Detiene una transferencia de alto riesgo en una pausa de seguridad.
- Permite cancelar, confirmar que se conoce el destino o reportar presión; cada decisión queda auditada.
- Mantiene separada la actividad de cada perfil demo y ofrece al analista una vista global de solo lectura.
- Incluye un simulador repetible para presentar el caso de fraude y una integración con Nessie de Capital One para cuentas y movimientos.

## Estructura del repositorio

```text
Guardian/
├── api-service/                         # Servicio FastAPI y lógica de negocio
│   ├── app/
│   │   ├── api/                         # Rutas HTTP y registro central
│   │   ├── core/                        # Configuración, sesiones y permisos
│   │   ├── domain/                      # Contratos de entrada y salida
│   │   ├── infrastructure/              # SQLite e integración Nessie
│   │   └── services/                    # Simulación y motor de riesgo
│   ├── tests/                           # Pruebas del flujo crítico
│   ├── .env.example                     # Variables de ejemplo, sin secretos
│   └── main.py                          # Punto de entrada de la API
├── web-client/                          # Aplicación React + Vite
│   └── src/
│       ├── app/                         # Arranque y estilos globales
│       ├── features/                    # Autenticación, feed, casos y demo
│       └── shared/                      # Cliente HTTP y utilidades reutilizables
├── PRUEBAS_PILOTO_GUARDIAN.mk           # Guía para validar la demo
└── ESTRUCTURA_PROYECTO.mk                # Detalle técnico de rutas y extensiones
```

## Antes de iniciar

Trabaja desde la raíz:

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian
```

Crea `C:\Users\smyoi\Documents\Guardian\Guardian\api-service\.env` a partir de `api-service\.env.example`. Para el piloto necesitas una contraseña local de al menos ocho caracteres:

```env
GUARDIAN_DEMO_PASSWORD=elige_una_contrasena_local_segura
```

Si vas a usar Nessie, agrega sus valores en ese mismo archivo. No subas `.env`, tokens ni contraseñas al repositorio.

## Ejecutar el piloto

Abre dos terminales.

Primera terminal — API:

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\api-service
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

La documentación interactiva queda disponible en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Segunda terminal — interfaz:

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\web-client
npm run dev
```

Abre la dirección que muestre Vite, normalmente [http://localhost:5173](http://localhost:5173). Selecciona un perfil demo, escribe la contraseña configurada y pulsa **Entrar al piloto**.

## Verificación antes de presentar

Con la API detenida o en otra terminal, ejecuta las pruebas del servicio:

```powershell
cd C:\Users\smyoi\Documents\Guardian\Guardian\api-service
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Debe mostrar cinco pruebas y terminar en `OK`. Para una validación guiada de inicio de sesión, simulación, decisiones, casos y auditoría, sigue [PRUEBAS_PILOTO_GUARDIAN.mk](PRUEBAS_PILOTO_GUARDIAN.mk).

## Criterios de organización

Las rutas HTTP nuevas se agregan en `api-service/app/api/routes/`; las reglas de fraude, en `api-service/app/services/risk_engine/`; las integraciones externas, en `api-service/app/infrastructure/`. En la interfaz, cada capacidad vive en `web-client/src/features/`, mientras que el código reutilizable y el único cliente HTTP viven en `web-client/src/shared/`.

Esta separación evita que la API, la lógica de fraude y la interfaz se mezclen, y permite que el proyecto crezca sin convertir una carpeta en un conjunto difícil de mantener.
