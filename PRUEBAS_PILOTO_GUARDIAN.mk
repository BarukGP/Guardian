# Protocolo de pruebas — Guardián

Este documento verifica el piloto local de punta a punta: autenticación, detección
de fraude APP, decisiones de la persona, creación de casos y aislamiento de sesiones.
No publiques contraseñas, tokens ni archivos `.env` al capturar evidencia.

## Preparación

En `api-service/.env` debe existir una contraseña local de al menos 8 caracteres:

```env
GUARDIAN_DEMO_PASSWORD=tu_contrasena_local
```

Inicia los servicios en dos terminales:

```powershell
# Terminal 1: servicio API
cd C:\Users\smyoi\Documents\Guardian\Guardian\api-service
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

```powershell
# Terminal 2: cliente web
cd C:\Users\smyoi\Documents\Guardian\Guardian\web-client
npm run dev
```

Abre `http://localhost:5173`.

---

## 1. Pruebas automatizadas

Ejecuta desde `api-service`:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Resultado esperado:

```text
Ran 5 tests
OK
```

Estas pruebas cubren: pausa por estafa APP, cancelación, confirmación única,
creación de caso por presión, aislamiento por usuario y señales de riesgo contextuales.

---

## 2. Inicio de sesión

1. En `http://localhost:5173`, elige **Rosa Elena · Cliente**.
2. Escribe la contraseña configurada en `api-service/.env`.
3. Pulsa **Entrar al piloto**.

Resultado esperado:

- Aparece el dashboard.
- El encabezado indica **Conectado**.
- Se muestra el nombre de Rosa Elena.
- No aparece ningún error de API key ni de sesión.

---

## 3. Escenario de fraude APP

1. Pulsa **Simular escenario de estafa**.
2. Revisa el feed de vigilancia.

Resultado esperado:

- Se registran ocho movimientos.
- Aparece una transferencia a **Soporte Falso**.
- La transferencia tiene riesgo alto y estado **En pausa**.
- Se muestra la tarjeta **Pausa de seguridad**.
- Las razones incluyen beneficiario nuevo, actividad o volumen inusual y señales de contexto.

---

## 4. Decisión: cancelar

1. En la pausa de seguridad, pulsa **Cancelar y revisar**.
2. Revisa el feed.

Resultado esperado:

- La tarjeta de pausa desaparece.
- La operación queda con estado **Cancelada**.
- No se crea un caso de protección.

Después pulsa **Reiniciar demo**.

Resultado esperado:

- El feed queda vacío.
- No hay operaciones ni alertas duplicadas.

---

## 5. Decisión: reportar presión

1. Ejecuta nuevamente **Simular escenario de estafa**.
2. Pulsa **Alguien me está presionando**.

Resultado esperado:

- La transferencia queda como **Presión reportada**.
- La pausa desaparece.
- Aparece un panel amarillo de **Caso de protección abierto**.
- El mensaje recomienda no responder al número que contactó a la persona.

---

## 6. Decisión: confirmar destino

1. Pulsa **Reiniciar demo**.
2. Simula nuevamente el escenario.
3. Pulsa **Confirmar que conozco el destino**.

Resultado esperado:

- La transferencia queda como **Confirmada**.
- No aparece un caso de protección.
- La operación deja de estar en pausa.

---

## 7. Aislamiento de sesiones

1. Con Rosa Elena, genera un escenario de fraude.
2. Pulsa el icono de cerrar sesión en el encabezado.
3. Inicia sesión como **Analista Guardián · Analista** con la misma contraseña local.

Resultado esperado:

- El analista entra en una **vista de solo lectura**.
- Puede ver la actividad, alertas, casos y auditoría globales para investigar.
- No ve botones para simular, reiniciar ni resolver transferencias.
- Si Rosa reportó presión antes de cerrar sesión, el analista ve ese caso y su
  auditoría, pero no puede modificarlo.

---

## 8. Auditoría mediante Swagger

Abre `http://127.0.0.1:8000/docs`.

1. Usa `POST /auth/login` con `rosa-elena` y la contraseña local.
2. Copia el `access_token` de la respuesta sin compartirlo.
3. Pulsa **Authorize** y registra el token como Bearer.
4. Ejecuta `GET /simulate/audit`.

Resultado esperado después de una decisión:

```text
review_cancelled
review_confirmed
review_reported_pressure
```

También puedes verificar `GET /simulate/cases` después de reportar presión.

---

## Evidencia recomendada para demo o presentación

- Terminal con las cinco pruebas en `OK`.
- Feed con transferencia a Soporte Falso en pausa.
- Estado final cancelado o confirmado.
- Caso de protección abierto al reportar presión.
- Endpoint `/simulate/audit` con el evento de decisión.

## Si algo falla

Comparte una captura de la pantalla y las últimas líneas de la terminal del servicio API.
Oculta siempre contraseñas, tokens, API keys y contenido de `.env`.
