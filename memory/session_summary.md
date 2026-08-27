# Última sesión

Fecha: 2026-08-27

## Objetivo trabajado

Auditoría integral de seguridad del proyecto VANER ASSET.

## Cambios realizados

### Auditoría integral (Fases 1-6 completadas)
- **Secretos y seguridad**: 18 hallazgos (SEC-001 a SEC-018)
- **Multi-tenancy/RLS**: 37 tablas sin RLS, 20 tablas protegidas
- **Auth/permisos**: JWT + refresh rotación, 7 hallazgos
- **DB/migraciones**: 59 tablas, 18 migraciones, 15 hallazgos
- **Frontend/branding**: 62 referencias SGA, 10 hallazgos
- **Tests/build**: 316 tests OK, build limpio, 3 hallazgos

### Archivos creados
- **`AUDITORIA_INTEGRAL_VANER_ASSET_2026_08_27.md`** — Informe completo (990 líneas, 49 KB)
- **`PROMPT_MAESTRO_AUDITORIA_INTEGRAL_VANER_ASSET.md`** — Prompt de auditoría

### Resultado
- Calificación global: **4.3/10 — CRÍTICO — No apto para producción**
- Commit `5ba03d6` pushed a `product/vaner-asset`
- 10 condiciones para aprobar despliegue documentadas
- Plan de acción 30-60-90 días con 15 acciones priorizadas

## Cambios realizados

### Backend — Modelos (10 tablas nuevas)
- **`backend/app/models/repuestos.py`** — Modelos SQLAlchemy:
  - `CategoriaRepuesto` — Categorías de repuestos por empresa
  - `UnidadMedida` — Unidades de medida (UN, M, L, KG, JG, etc.)
  - `Repuesto` — Catálogo maestro (código, nombre, tipo, marca, referencia, stock min/max, costo promedio)
  - `Bodega` — Bodegas por sede
  - `Existencia` — Stock por repuesto por bodega (física, reservada, disponible)
  - `MovimientoRepuesto` — Movimientos inmutables (entrada, salida, reserva, transferencia, ajuste)
  - `SolicitudRepuesto` — Solicitudes con workflow SOLICITADO→APROBADO→RESERVADO→ENTREGADO→CONSUMIDO
  - `ProveedorRepuesto` — Proveedores
  - `RepuestoProveedor` — Relación N:N repuesto-proveedor
  - `RepuestoCompatibilidad` — Compatibilidad repuesto-equipo

### Backend — Schemas
- **`backend/app/schemas/repuestos.py`** — Schemas Pydantic para todos los modelos

### Backend — Migración
- **`r01a1b2c30001_repuestos_consumibles_modulo_completo.py`** — Crea 10 tablas + unidades de medida iniciales + FKs a ot_repuestos

### Backend — Router (31 endpoints)
- **`backend/app/routers/repuestos.py`** — Endpoints:
  - Dashboard con indicadores
  - CRUD categorías, unidades de medida
  - CRUD catálogo de repuestos
  - CRUD bodegas
  - Listar existencias por repuesto/bodega
  - Movimientos: entrada, ajuste, transferencia
  - Solicitudes: crear, aprobar, reservar, entregar, consumir, devolver
  - CRUD proveedores
  - Compatibilidad repuesto-equipo

### Frontend
- **`RepuestosPage.jsx`** — Página con 5 pestañas: Catálogo, Existencias, Movimientos, Solicitudes, Proveedores
- Dashboard con KPIs: activos, disponibles, stock bajo, agotados, valor inventario, solicitudes pendientes
- CRUD completo de repuestos con modal de edición
- Tabla de existencias con filtros por repuesto/bodega
- Historial de movimientos con filtros por tipo
- Workflow de solicitudes con acciones contextualizadas
- CRUD de proveedores

### Actualizaciones
- **`App.jsx`** — Ruta `/admin/repuestos` ahora carga `RepuestosPage`
- **`Sidebar.jsx`** — Renombrado a "Repuestos y Consumibles"
- **`models/__init__.py`** — Agregados 10 modelos nuevos
- **`main.py`** — Registrado router de repuestos
- **`l62a0d530001_privilegios_app_allowlist.py`** — Agregadas 10 tablas al allowlist

## Estado actual
- 316 tests OK
- Build OK
- Lint OK (2 warnings menores)
- Migración aplicada
- Commit `1be98ab` pushed

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

**OPTIMIZACIÓN DEL MÓDULO DE MANTENIMIENTOS COMPLETADA (Fases 0-5)**

### Archivos modificados/creados:
- `backend/app/routers/mantenimientos.py` — Reescrito: auth, aislamiento multi-tenant, soft-delete, paginación, conflictos, sugerencias, recurrencia, acceso-rápidos
- `backend/app/models/mantenimiento.py` — Campo `activo` para soft-delete
- `backend/alembic/versions/p91e4f720001_add_activo_mantenimientos.py` — Migración soft-delete
- `frontend/src/pages/admin/MaintenanceWizard.jsx` — Asistente 3 pasos con conflictos, sugerencias, borrador, recurrencia
- `frontend/src/pages/admin/MantenimientosPage.jsx` — Reescrito: filtros, paginación, toasts, integración wizard
- `frontend/src/pages/admin/MantenimientosPage.css` — Estilos de filtros
- `frontend/src/components/EquipmentSearch.jsx` — Búsqueda inteligente con dropdown
- `frontend/src/styles/maintenance-wizard.css` — Estilos del asistente
- `backend/tests/test_mantenimiento_fase8.py` — Mock actualizado para nueva firma

### Funcionalidades implementadas:
- **Fase 1**: Auth+roles, aislamiento tenant, UUID directo, soft-delete, paginación server-side
- **Fase 2**: Wizard 3 pasos, búsqueda inteligente, limpieza de alertas
- **Fase 3**: Detección de conflictos, sugerencia de técnico/prioridad, borrador automático
- **Fase 4**: Recurrencia (6 frecuencias), acceso rápido a equipo
- **Fase 5**: 316 tests OK, build OK, ESLint OK, migración aplicada

### Estado:
- **Pendiente**: Push a GitHub (esperando autorización del usuario)
- **Pendiente**: Verificación en navegador (requiere backend+frontend corriendo)

## Próximo paso recomendado

Priorizar las 5 acciones CRÍTICAS del plan 30-60-90 días:
1. Migración RLS completa (37 tablas)
2. Backup automatizado PostgreSQL
3. CI/CD pipeline mínimo
4. Branding completo (62 referencias SGA)
5. Secrets management (.env.docker)

## Sesión anterior (2026-08-26)

### Objetivo trabajado
Módulo completo de Repuestos y Consumibles — Fase 1 (Catálogo y existencias).
