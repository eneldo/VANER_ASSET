# Última sesión

Fecha: 2026-08-26

## Objetivo trabajado

Completar implementación de política de contraseñas (OWASP/NIST) + Rediseño de login.

## Cambios realizados

### Backend — Política de contraseñas (nuevo servicio)
- **`backend/app/services/password_policy.py`** — Servicio centralizado:
  - Mínimo 15 caracteres (sin MFA) / 12 con MFA
  - Máximo 128 caracteres
  - Validación de contraseñas comunes (NIST 10k list)
  - Prohibición de términos tenant (vaner, asset, sistema, datos, empresa, etc.)
  - No incluir username ni email local part
  - Historial de 5 contraseñas (no repetir)
  - Verificación de contraseña actual en cambios
  - Mensajes genéricos de error (sin revelar criterios)
  - Nunca loggear contraseñas

### Backend — Modelo password_history
- **`backend/app/models/password_history.py`** — Tabla `password_history` con `usuario_id`, `password_hash`, `created_at`
- **Migración** `o85d3e860001_password_history_policy.py` — Crea tabla + agrega campos a `usuarios`:
  - `debe_cambiar_password` (boolean, default False)
  - `password_changed_at` (timestamp, nullable)
  - `temp_password_expires_at` (timestamp, nullable)

### Backend — Security.py mejorado
- **`backend/app/security.py`** — Argon2id para contraseñas nuevas, pbkdf2 backward compat
  - `hash_password()` usa Argon2id por defecto
  - `verify_password()` acepta Argon2id y pbkdf2
  - `needs_upgrade()` detecta si hash necesita migración

### Backend — Integración en endpoints
- **`routers/usuarios.py`** — Política integrada en crear, reset, nuevo endpoint `POST /cambio-password`
- **`routers/auth.py`** — Verificación temp expirada, auto-upgrade hash pbkdf2→argon2, flag `debe_cambiar_password`
- **`routers/password_recovery.py`** — Política integrada en reset de contraseña

### Backend — Config y schemas
- **`config.py`** — Variables: `PASSWORD_MIN_LENGTH`, `ARGON2_TIME_COST`, `ARGON2_MEMORY_COST`, etc.
- **`schemas/usuario.py`** — `CambioPasswordRequest`, `UsuarioOut` con `debe_cambiar_password`
- **`schemas/auth.py`** — `TokenResponse` con `debe_cambiar_password`

### Backend — Tests (31 pruebas)
- **`tests/test_password_policy.py`** — 31 tests cubriendo:
  - Longitud mínima/máxima, passphrase, contraseñas comunes
  - Términos tenant, username, email
  - Historial, expiración temp password
  - Compatibilidad pbkdf2/argon2, upgrade de hash
  - Sin logs de contraseñas, mensajes seguros

### Frontend — Cambio forzado
- **`ForcedPasswordChange.jsx`** — Formulario con:
  - Indicador de fuerza (barra coloreada + reglas visuales)
  - 8 reglas mostradas en tiempo real
  - Confirmación de contraseña
  - Redirect automático si `debe_cambiar_password=true`

### Frontend — AuthContext
- **`AuthContext.jsx`** — Manejo de `debe_cambiar_password` en login, redirect a `/cambiar-password`

### Archivos actualizados
- `requirements.txt` — `argon2-cffi==25.1.0`
- `.env.example` — Variables de política
- `scripts/create_initial_admin.py` — Usa política centralizada

## Validación

- **Backend**: 316 pruebas aprobadas (31 nuevas de política).
- **Frontend**: Build exitoso, ESLint sin errores.
- **Migración**: Aplicada (`alembic upgrade head`), tabla `password_history` verificada.

## Estado actual

Fase de política de contraseñas completada y validada. Próximo: Fase 12 — Despliegue.

## Próximo paso recomendado

Continuar con Fase 12 — Despliegue (Docker, CI/CD, dominio).
