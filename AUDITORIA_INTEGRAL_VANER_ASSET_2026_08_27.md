# AUDITORÍA INTEGRAL DE SEGURIDAD — VANER ASSET

## Informe Ejecutivo — 27 de agosto de 2026

### Datos del Proyecto

| Campo | Valor |
|-------|-------|
| Producto | VANER ASSET — ERP modular enfocado en inventario, activos y mantenimiento, multiempresa |
| Stack | React 19 + Vite 6 (frontend), Python 3.12 + FastAPI 0.12 + SQLAlchemy 2 + Alembic (backend), PostgreSQL 17, Redis (deshabilitado en dev) |
| Versión analizada | Branch `product/vaner-asset`, commit `a4383fa` |
| Total tablas DB | 59 |
| Total migraciones Alembic | 18 |
| Total tests backend | 47 archivos (316 pruebas, todas aprobadas) |
| Total archivos fuente frontend | ~89 componentes/páginas (.jsx) |
| Total routers backend | 45 |
| Total modelos backend | 39 archivos |
| Auditor | opencode |

---

## 1. Calificación Global y Riesgos Críticos

### Calificación Global: 4.3/10

| Área | Calificación | Peso | Justificación |
|------|:---:|:---:|---|
| Autenticación (JWT + refresh + rotation) | 9/10 | 15% | Access en memoria, refresh HttpOnly, rotación implementada, recuperación por POST, revocación al cambiar password |
| Multi-tenancy (RLS) | 2/10 | 15% | RLS implementado en migración `g37c5e080001` para ~20 tablas; 37+ tablas operativas sin RLS (repuestos, existencias, movimientos, solicitudes, proveedores, notificaciones, categorías, etc.) |
| Secrets management | 4/10 | 10% | .env contiene passwords reales en texto plano; .env.example es correcto; backend/.env eliminado del repo; Redis deshabilitado |
| Database security | 3/10 | 10% | Allowlist implementada pero incompleta; privilegios de sga_app correctamente restringidos; sin BYPASSRLS; pero tablas nuevas sin RLS |
| Test coverage | 8/10 | 10% | 316 tests backend aprobados; 44 frontend; sin tests E2E; sin tests de integración RLS; sin tests de concurrencia |
| Frontend security | 7/10 | 10% | Token en memoria; localStorage limpio; guardas por rol; toast global; sin XSS evidente |
| Infrastructure/observability | 3/10 | 5% | Docker hardening parcial; sin health checks configurados; sin monitoreo en producción |
| CI/CD | 1/10 | 5% | Sin pipeline CI/CD configurado; sin GitHub Actions; sin Dependabot activo |
| Observabilidad | 3/10 | 5% | Logs estructurados en backend; sin Sentry; sin métricas; sin alertas |
| Backups | 4/10 | 5% | Cifrado AES-GCM implementado; retención S3 configurada; sin backup automatizado; sin restore drill |
| Cumplimiento normativo | 3/10 | 5% | Sin GDPR/LGPD; sin política de retención de datos; sin auditoría de consentimiento |
| Code quality | 8/10 | 5% | Arquitectura limpia; separación de responsabilidades; naming consistente; eslint limpio |

**Calificación ponderada: 4.3/10 — CRÍTICO — No apto para producción**

### Top 5 Riesgos Críticos (R1-R5)

| # | Riesgo | Severidad | Descripción | Impacto |
|---|--------|-----------|-------------|---------|
| R1 | **Sin RLS completo** | CRITICAL | 37+ tablas tenant-scoped sin proteger con RLS. Tablas de repuestos, existencias, movimientos, solicitudes, proveedores, notificaciones, categorías, y más no tienen aislamiento a nivel de BD. Un atacante con acceso SQL puede cruzar tenants. | Fuga de datos entre empresas, alteración de inventario |
| R2 | **Secrets hardcodeados** | MEDIUM | `.env` contiene passwords reales de PostgreSQL, Redis, SECRET_KEY y CONFIG_ENCRYPTION_KEY en texto plano. Aunque `.gitignore` lo excluye, el archivo existe en el repo local. | Compromiso de credenciales si el archivo se expone |
| R3 | **Sin backup automatizado** | HIGH | No hay cron job, script automatizado ni pipeline que ejecute `pg_dump` periódicamente. El backup manual se hizo una vez (229KB). | Pérdida total de datos sin posibilidad de recuperación |
| R4 | **Sin CI/CD pipeline** | MEDIUM | No hay GitHub Actions, ni pipeline de construcción. No se ejecutan tests automáticamente en PRs ni en pushes. | Código sin validar, regresiones no detectadas |
| R5 | **62 referencias SGA** | LOW | 62+ referencias a "SGA", "SGA SaaS", "SGAHolding", "sgaholding.online" en código, docs, configs y package-lock.json. | Riesgo de exposición del cliente anterior, incumplimiento contractual |

---

## 2. Autenticación

**Calificación: 9/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| AUTH-001 | LOW | Access token vive en memoria (Correcto). Refresh token en cookie HttpOnly (Correcto). No se exponen en localStorage/sessionStorage. | `frontend/src/AuthContext.jsx`, `frontend/src/App.jsx` |
| AUTH-002 | LOW | Rotación de refresh tokens implementada. Un solo refresh activo por sesión. | `backend/app/routers/auth.py` |
| AUTH-003 | LOW | Revocación global al cambiar contraseña. Se eliminan todos los refresh tokens activos. | `backend/app/routers/auth.py` |
| AUTH-004 | LOW | Recuperación de contraseña por POST con token en fragmento (no query string). | `backend/app/routers/password_recovery.py` |
| AUTH-005 | LOW | Login real verificado contra PostgreSQL: ADMIN y COORDINADOR retornan HTTP 200. | Auditoría v1.0.14 |
| AUTH-006 | INFORMATIONAL | No hay MFA implementado. Se recomienda como mejora futura. | No se encontró implementación |
| AUTH-007 | INFORMATIONAL | No hay bloqueo por intentos fallidos de login implementado a nivel de BD (solo rate limiting). | `login_intentos` table existe pero sin lógica de bloqueo |

### Recomendaciones

1. Implementar MFA (TOTP) para roles ADMIN y COORDINADOR
2. Agregar bloqueo temporal tras N intentos fallidos (5 intentos → bloqueo 15 min)
3. Implementar enumerate-user mitigation (respuesta genérica)

---

## 3. Contraseñas y Política de Seguridad

**Calificación: 9/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| PWD-001 | LOW | Longitud mínima 15 caracteres (sin MFA) / 12 con MFA. Correcto. | `backend/app/services/password_policy.py` |
| PWD-002 | LOW | Argon2id para hashes nuevos; pbkdf2 para backward compat. Auto-upgrade implementado. | `backend/app/security.py` |
| PWD-003 | LOW | Historial de 5 contraseñas. No repetir. | `backend/app/models/password_history.py` |
| PWD-004 | LOW | Validación de contraseñas comunes (NIST 10k list). | `backend/app/services/password_policy.py` |
| PWD-005 | LOW | Prohibición de términos tenant (vaner, asset, sistema, datos, empresa). | `backend/app/services/password_policy.py` |
| PWD-006 | LOW | Cambio forzado de contraseña temporal implementado en frontend. | `frontend/src/pages/ForcedPasswordChange.jsx` |
| PWD-007 | LOW | 31 tests de política de contraseñas aprobados. | `backend/tests/test_password_policy.py` |

### Recomendaciones

1. Documentar la política de contraseñas en `.env.example` y en la guía de usuario
2. Considerar reducir la longitud mínima a 12 para UX (con MFA obligatorio)

---

## 4. Gestión de Secretos y Credenciales

**Calificación: 4/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| SEC-001 | MEDIUM | `.env` contiene passwords reales en texto plano: `POSTGRES_PASSWORD`, `POSTGRES_APP_PASSWORD`, `POSTGRES_BACKUP_PASSWORD`, `REDIS_PASSWORD`, `SECRET_KEY`, `CONFIG_ENCRYPTION_KEY`. | `.env` línea 17-29 |
| SEC-002 | LOW | `.env.example` usa placeholders correctos (`CAMBIAR_*`). | `.env.example` |
| SEC-003 | LOW | `backend/.env` fue eliminado del repositorio (correcto). | Auditoría v1.0.14 |
| SEC-004 | MEDIUM | `SECRET_KEY` y `CONFIG_ENCRYPTION_KEY` son iguales a `REDIS_PASSWORD`. Riesgo de reutilización de secretos. | `.env` línea 20, 28 |
| SEC-005 | LOW | Nombres de usuarios DB: `sga_app`, `sga_backup`, `postgres`. El rol `sga_app` no tiene BYPASSRLS. | `.env`, `l62a0d530001_privilegios_app_allowlist.py` |
| SEC-006 | INFORMATIONAL | No se encontraron API keys de servicios externos expuestas. | Búsqueda de archivos |

### Recomendaciones

1. **Inmediato**: Rotar todas las contraseñas de `.env` y generar valores únicos para `SECRET_KEY` y `CONFIG_ENCRYPTION_KEY`
2. **Corto plazo**: Migrar a Docker secrets o vault para producción
3. **Inmediato**: Asegurar que `.gitignore` excluye `.env` (verificar que no se versionó previamente)

---

## 5. Inventario Técnico del Proyecto

### Backend Stack

| Componente | Versión/Detalle |
|------------|-----------------|
| Python | 3.12 |
| FastAPI | 0.12 |
| SQLAlchemy | 2.x |
| Alembic | 18 migraciones |
| Pydantic | v2 (schemas) |
| JWT | PyJWT |
| Password hashing | passlib + bcrypt + Argon2id |
| PostgreSQL driver | psycopg2-binary |
| Rate limiting | Redis (producción) / fallback local |
| Testing | pytest + pytest-asyncio + pytest-cov |

### Frontend Stack

| Componente | Versión/Detalle |
|------------|-----------------|
| React | 19.x |
| Vite | 6.x |
| React Router | v6 |
| Axios | HTTP client |
| ESLint | Linting |
| Vitest | Testing |

### Database

| Métrica | Valor |
|---------|-------|
| Total tablas | 59 |
| Tablas con empresa_id | 37+ |
| Tablas con RLS | ~20 (empresas, sedes, equipos, mantenimientos, solicitudes_correctivas, reportes_publicados, facturas, ot_repuestos, ot_incidencias, auditoria_eventos, auditoria_pro_eventos, seguridad_eventos, tecnicos, equipo_hoja_vida, evidencias, formatos_mantenimiento, hist_mantenimiento, historial_mantenimiento, bitacoras_dinamicas, bitacoras_respuestas, plantillas_reporte) |
| Tablas sin RLS | ~37 (repuestos, existencias_repuestos, movimientos_repuestos, solicitudes_repuestos, categorias_repuestos, bodegas, proveedores_repuestos, repuesto_proveedor, repuestos_compatibilidad, unidades_medida, notificaciones, configuracion_sistema, configuracion_saas, categorias, refresh_tokens, password_history, password_reset_tokens, login_intentos, logs_sistema, smtp_logs, automatizaciones, scheduler_reglas, devops_eventos, monitor_estado, etc.) |

### Routers Backend (45)

auditoria, auditoria_pro, auth, automatizacion, backups_inteligentes, bitacoras_dinamicas, bi_ejecutivo, categorias, cliente, configuracion, configuracion_saas, coordinador, cronograma, dashboard_tecnico, devops_saas, empresas, equipos, equipo_hoja_vida, evidencias, exportaciones, facturacion, formatos_dinamicos, formatos_mantenimiento, hoja_vida, logs_inteligentes, mantenimientos, monitor_vps, multiempresa, multiempresa_enterprise, notificaciones, password_recovery, permisos, plantillas_reporte, public_config, recovery_restore, reportes, reportes_publicados, repuestos, scheduler_inteligente, sedes, seguridad, smtp_inteligente, solicitudes_correctivas, tecnicos, usuarios

---

## 6. Arquitectura General del Sistema

**Calificación: 8/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| ARCH-001 | LOW | Separación clara backend/frontend. Backend con routers, models, schemas, services. | Estructura del proyecto |
| ARCH-002 | LOW | Arquitectura por dominios: inventario, activos, mantenimiento, OT, reportes, configuración. | 39 archivos de modelos, 45 routers |
| ARCH-003 | MEDIUM | Router `coordinador.py` es monolítico (múltiples dominios en un archivo). | `backend/app/routers/coordinador.py` |
| ARCH-004 | INFORMATIONAL | Router `multiempresa.py` y `multiempresa_enterprise.py` parecen tener superposición. | Ambos archivos existen |
| ARCH-005 | LOW | Servicios centralizados: `password_policy.py`, `coordinador_empresas.py`. | `backend/app/services/` |
| ARCH-006 | INFORMATIONAL | Sin dependencias circulares detectadas. | Análisis de imports |

### Recomendaciones

1. Dividir `coordinador.py` por dominio
2. Consolidar `multiempresa.py` y `multiempresa_enterprise.py`
3. Mantener la separación por dominios actual

---

## 7. Multiempresa / RLS

**Calificación: 2/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| RLS-001 | CRITICAL | RLS implementado solo para ~20 tablas. 37+ tablas operativas sin RLS. | `g37c5e080001_rls_multi_tenant.py` |
| RLS-002 | CRITICAL | Tablas de repuestos (10 tablas nuevas) sin RLS: `repuestos`, `categorias_repuestos`, `bodegas`, `existencias_repuestos`, `movimientos_repuestos`, `solicitudes_repuestos`, `proveedores_repuestos`, `repuesto_proveedor`, `repuestos_compatibilidad`, `unidades_medida`. | `r01a1b2c30001_repuestos_consumibles_modulo_completo.py` — sin políticas RLS |
| RLS-003 | CRITICAL | Tablas de notificaciones, configuración, categorías, logs sin RLS. | Modelos `notificacion.py`, `configuracion.py`, `categoria.py`, `log_sistema.py` |
| RLS-004 | CRITICAL | Tablas de autenticación (refresh_tokens, password_history, login_intentos) sin RLS — un atacante podría ver tokens de otros tenants. | Modelos `refresh_token.py`, `password_history.py`, `login_attempt.py` |
| RLS-005 | HIGH | Tabla `usuarios` tiene `empresa_id` pero no tiene RLS explícito (política en `empresas` protege la tabla padre). | `g37c5e080001_rls_multi_tenant.py` — `usuarios` no está en DIRECTAS ni INDIRECTAS |
| RLS-006 | HIGH | Tabla `roles_permisos` y `permisos_sistema` sin RLS — permisos globales accesibles por todos los tenants. | Modelos `permiso.py` — sin política RLS |
| RLS-007 | MEDIUM | Tablas `automatizaciones`, `scheduler_reglas_mantenimiento` sin RLS. | Modelos `automatizacion.py`, `scheduler_inteligente.py` |
| RLS-008 | MEDIUM | `plantillas_reporte` tiene RLS con lectura global (`empresa_id IS NULL OR empresa_id = TENANT`). Correcto para plantillas compartidas. | `g37c5e080001_rls_multi_tenant.py` línea 64 |

### Matriz de Tablas y Controles Multiempresa

| Tabla | empresa_id | FK | Índice | RLS | FORCE | Política |
|-------|:----------:|:--:|:------:|:---:|:-----:|----------|
| empresas | ✅ | — | ✅ | ✅ | ✅ | id = tenant |
| sedes | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id = tenant |
| equipos | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id = tenant |
| mantenimientos | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id = tenant |
| solicitudes_correctivas | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id = tenant |
| reportes_publicados | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id = tenant |
| facturas | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id = tenant |
| ot_repuestos | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id = tenant |
| ot_incidencias | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id = tenant |
| auditoria_eventos | ✅ | — | ✅ | ✅ | ✅ | empresa_id = tenant |
| auditoria_pro_eventos | ✅ | — | ✅ | ✅ | ✅ | empresa_id = tenant |
| seguridad_eventos | ✅ | — | ✅ | ✅ | ✅ | empresa_id = tenant |
| tecnicos | ✅ | ✅ | ✅ | ✅ | ✅ | EXISTS (usuarios.empresa_id) |
| equipo_hoja_vida | ✅ | ✅ | ✅ | ✅ | ✅ | EXISTS (equipos.empresa_id) |
| evidencias | ✅ | ✅ | ✅ | ✅ | ✅ | EXISTS (mantenimientos.empresa_id) |
| formatos_mantenimiento | ✅ | ✅ | ✅ | ✅ | ✅ | EXISTS (mantenimientos.empresa_id) |
| hist_mantenimiento | ✅ | ✅ | ✅ | ✅ | ✅ | EXISTS (mantenimientos.empresa_id) |
| historial_mantenimiento | ✅ | ✅ | ✅ | ✅ | ✅ | EXISTS (mantenimientos.empresa_id) |
| bitacoras_dinamicas | ✅ | ✅ | ✅ | ✅ | ✅ | EXISTS (mantenimientos.empresa_id) |
| bitacoras_respuestas | ✅ | ✅ | ✅ | ✅ | ✅ | EXISTS (bitacoras → mantenimientos) |
| plantillas_reporte | ✅ | ✅ | ✅ | ✅ | ✅ | empresa_id IS NULL OR = tenant |
| **repuestos** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **categorias_repuestos** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **bodegas** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **existencias_repuestos** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **movimientos_repuestos** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **solicitudes_repuestos** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **proveedores_repuestos** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **repuesto_proveedor** | — | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **repuestos_compatibilidad** | — | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **unidades_medida** | — | — | — | ❌ | ❌ | **SIN RLS (global)** |
| **notificaciones** | ✅ | ✅ | — | ❌ | ❌ | **SIN RLS** |
| **configuracion_sistema** | — | — | — | ❌ | ❌ | **SIN RLS (global)** |
| **configuracion_saas** | — | — | — | ❌ | ❌ | **SIN RLS (global)** |
| **categorias** | ✅ | ✅ | — | ❌ | ❌ | **SIN RLS** |
| **refresh_tokens** | — | ✅ | — | ❌ | ❌ | **SIN RLS** |
| **password_history** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS** |
| **password_reset_tokens** | — | ✅ | — | ❌ | ❌ | **SIN RLS** |
| **login_intentos** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **usuarios** | ✅ | ✅ | ✅ | ❌ | ❌ | **SIN RLS directo** |
| **roles_permisos** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **permisos_sistema** | — | — | — | ❌ | ❌ | **SIN RLS (global)** |
| **roles_sistema** | — | — | — | ❌ | ❌ | **SIN RLS (global)** |
| **automatizaciones** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **scheduler_reglas** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **logs_sistema** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **smtp_logs** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **devops_eventos** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **monitor_estado** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **backup_historial** | — | — | — | ❌ | ❌ | **SIN RLS** |
| **formatos_campos** | — | ✅ | — | ❌ | ❌ | **SIN RLS** |
| **tipos_formatos** | — | — | — | ❌ | ❌ | **SIN RLS (global)** |
| **usuario_empresas** | — | ✅ | — | ❌ | ❌ | **SIN RLS** |

### Escenarios de Aislamiento No Protegidos

| Escenario | Estado | Riesgo |
|-----------|--------|--------|
| Empresa A no puede ver mantenimientos de Empresa B | ✅ Protegido (RLS) | — |
| Empresa A puede ver repuestos de Empresa B | ❌ **NO PROTEGIDO** | Fuga de datos de inventario |
| Empresa A puede ver existencias de Empresa B | ❌ **NO PROTEGIDO** | Fuga de stock |
| Empresa A puede ver movimientos de Empresa B | ❌ **NO PROTEGIDO** | Trazabilidad comprometida |
| Empresa A puede ver usuarios de Empresa B | ❌ **NO PROTEGIDO** | Enumeración de usuarios |
| Empresa A puede ver refresh tokens de Empresa B | ❌ **NO PROTEGIDO** | Robo de sesiones |
| Empresa A puede ver configuración de Empresa B | ❌ **NO PROTEGIDO** | Exposición de configuración |

### Recomendaciones

1. **CRÍTICO**: Crear migración RLS para todas las tablas tenant-scoped restantes
2. **CRÍTICO**: Proteger tablas de autenticación (refresh_tokens, password_history, login_intentos)
3. **CRÍTICO**: Proteger tabla `usuarios` con RLS directo
4. **ALTO**: Decidir si tablas globales (configuracion_sistema, roles_sistema, permisos_sistema) deben ser legibles por todos o solo por admin

---

## 8. Autenticación y Autorización

**Calificación: 8/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| AUTHZ-001 | LOW | JWT con expiración configurable. Access token 30 min, refresh 7 días. | `.env.example` |
| AUTHZ-002 | LOW | Cookies HttpOnly, Secure (configurable), SameSite=lax. | `.env.example` |
| AUTHZ-003 | LOW | ProtectedRoute con guard de autorización. | `frontend/src/components/ProtectedRoute.jsx` |
| AUTHZ-004 | LOW | RoleRoute para guardas por rol. | `frontend/src/components/RoleRoute.jsx` |
| AUTHZ-005 | MEDIUM | Matriz de permisos no completamente documentada. | No se encontró matriz formal |
| AUTHZ-006 | LOW | CORS configurado con orígenes permitidos. | `backend/app/main.py` |

---

## 9. Gestión de Sesiones

**Calificación: 9/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| SES-001 | LOW | Access token en memoria (no en storage). | `frontend/src/AuthContext.jsx` |
| SES-002 | LOW | Refresh token en cookie HttpOnly. | `backend/app/routers/auth.py` |
| SES-003 | LOW | Bootstrap por refresh cookie + /auth/me. | `frontend/src/App.jsx` |
| SES-004 | LOW | Revocación al cambiar contraseña. | `backend/app/routers/auth.py` |
| SES-005 | LOW | Un solo refresh activo por sesión (rotación). | `backend/app/routers/auth.py` |

---

## 10. Permisos y Roles

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| PERM-001 | LOW | Roles: SuperAdministrador, Administrador, Coordinador, Técnico, Consulta, Empresa. | `backend/app/models/usuario.py` |
| PERM-002 | MEDIUM | Matriz de permisos no formalizada. No se encontró tabla de permisos por módulo/acción. | Búsqueda de archivos |
| PERM-003 | MEDIUM | `roles_permisos` y `usuarios_permisos` existen pero no se verificaron políticas RLS. | `l62a0d530001_privilegios_app_allowlist.py` |
| PERM-004 | LOW | Coordinador puede cambiar de empresa activa con cabecera `X-Empresa-Activa`. | `backend/app/routers/coordinador.py` |

### Matriz de Permisos Estimada

| Módulo/acción | ADMIN | COORDINADOR | TÉCNICO | EMPRESA |
|---------------|:-----:|:-----------:|:-------:|:-------:|
| Inventario (CRUD) | ✅ | ✅ | ❌ | ❌ |
| Activos (CRUD) | ✅ | ✅ | ❌ | ❌ |
| Mantenimientos (crear) | ✅ | ✅ | ❌ | ❌ |
| Mantenimientos (asignar) | ✅ | ✅ | ❌ | ❌ |
| OT (ejecutar) | ✅ | ❌ | ✅ | ❌ |
| Repuestos (CRUD) | ✅ | ✅ | ❌ | ❌ |
| Repuestos (consumir) | ✅ | ❌ | ✅ | ❌ |
| Reportes (ver) | ✅ | ✅ | ✅ | ✅ |
| Configuración | ✅ | ❌ | ❌ | ❌ |
| Usuarios | ✅ | ❌ | ❌ | ❌ |
| Auditoría | ✅ | ❌ | ❌ | ❌ |
| Backups | ✅ | ❌ | ❌ | ❌ |

---

## 11. Módulo de Mantenimientos

**Calificación: 8/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| MTTO-001 | LOW | Wizard de creación en 3 pasos con conflictos, sugerencias, borrador. | `frontend/src/pages/admin/MaintenanceWizard.jsx` |
| MTTO-002 | LOW | Soft-delete implementado (campo `activo`). | `backend/app/models/mantenimiento.py` |
| MTTO-003 | LOW | Detección de conflictos de fechas/técnico. | `backend/app/routers/mantenimientos.py` |
| MTTO-004 | LOW | Recurrencia (6 frecuencias). | `backend/app/routers/mantenimientos.py` |
| MTTO-005 | LOW | Paginación server-side. | `backend/app/routers/mantenimientos.py` |
| MTTO-006 | LOW | Integración OT-repuestos para consumir repuestos desde mantenimiento. | `commit a4383fa` |
| MTTO-007 | LOW | Aislamiento multi-tenant verificado. | `backend/app/routers/mantenimientos.py` |

---

## 12. Órdenes de Trabajo

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| OT-001 | LOW | Ciclo PROGRAMADO → ASIGNADO → EN_PROCESO → PAUSADO → FINALIZADO. | `backend/app/models/mantenimiento.py` |
| OT-002 | LOW | Repuestos e incidencias asociados a OT. | `backend/app/models/ot_repuesto.py`, `ot_incidencia.py` |
| OT-003 | MEDIUM | Sin verificación de inmutabilidad después del cierre. | Análisis de código |
| OT-004 | MEDIUM | Sin verificación de doble finalización. | Análisis de código |

---

## 13. Repuestos

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| REP-001 | LOW | Catálogo completo: código, nombre, tipo, categoría, marca, referencia, costos, stock min/max. | `backend/app/models/repuestos.py` |
| REP-002 | LOW | CheckConstraints: `existencia_fisica >= 0`, `cantidad_reservada >= 0`. | `backend/app/models/repuestos.py` línea 152-153 |
| REP-003 | LOW | UniqueConstraints: empresa+codigo, empresa+nombre, repuesto+bodega+lote+serial. | `backend/app/models/repuestos.py` |
| REP-004 | LOW | Movimientos inmutables con `idempotency_key`. | `backend/app/models/repuestos.py` línea 195 |
| REP-005 | MEDIUM | Sin `SELECT FOR UPDATE` para prevenir condiciones de carrera en reservas. | Análisis de código |
| REP-006 | MEDIUM | Sin verificación de `cantidad_reservada <= existencia_fisica` a nivel de BD (solo CheckConstraint de >= 0). | `backend/app/models/repuestos.py` |
| REP-007 | LOW | Workflow de solicitudes: SOLICITADO → APROBADO → RESERVADO → ENTREGADO → CONSUMIDO. | `backend/app/models/repuestos.py` línea 226-228 |
| REP-008 | LOW | 31 endpoints CRUD para repuestos. | `backend/app/routers/repuestos.py` |

### Escenario de Concurrency

```
Disponible: 5
Solicitud A: 4 (puede pasar si no hay lock)
Solicitud B: 3 (puede pasar si no hay lock)
Resultado: 2 solicitudes aprobadas para 5 disponibles → stock negativo
```

**Riesgo**: Sin `SELECT FOR UPDATE` o transacción serializable, dos solicitudes concurrentes pueden reservar más de lo disponible.

### Recomendaciones

1. Agregar `SELECT FOR UPDATE` en operaciones de reserva
2. Agregar CheckConstraint: `cantidad_reservada <= existencia_fisica`
3. Implementar transacciones serializables para movimientos de stock

---

## 14. Inventario General

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| INV-001 | LOW | Importación CSV/XLSX con validación de extensión, MIME, tamaño, UTF-8. | `backend/app/routers/exportaciones.py` |
| INV-002 | LOW | Exportación Excel con filtros por tenant. | `backend/app/routers/coordinador.py` |
| INV-003 | MEDIUM | Sin protección contra CSV injection en importaciones. | Análisis de código |
| INV-004 | LOW | Paginación server-side para listados. | `backend/app/routers/equipos.py` |

---

## 15. Archivos y Evidencia

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| FILE-001 | LOW | Validación MIME real en importaciones. | `backend/app/routers/exportaciones.py` |
| FILE-002 | LOW | Límites de tamaño configurables (`MAX_UPLOAD_SIZE_MB`). | `.env.example` |
| FILE-003 | MEDIUM | Sin antivirus o cuarentena para archivos subidos. | Análisis de código |
| FILE-004 | MEDIUM | Sin verificación de path traversal en uploads. | Análisis de código |
| FILE-005 | LOW | Evidencias asociadas a mantenimientos con RLS. | `backend/app/models/evidencia.py` |

---

## 16. Base de Datos y Migraciones

**Calificación: 6/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| DB-001 | LOW | Cadena Alembic lineal: 18 migraciones, una sola cabeza. | `alembic versions` |
| DB-002 | LOW | Todas las migraciones tienen `upgrade()` y `downgrade()`. | 18 archivos de migración |
| DB-003 | MEDIUM | Migración `l62a0d530001` tiene `downgrade()` vacío (pass). | `l62a0d530001_privilegios_app_allowlist.py` línea 111-112 |
| DB-004 | MEDIUM | Base de datos local en revisión `i59e7a2a0001`, código requiere `l62a0d530001`. | Auditoría v1.0.14 |
| DB-005 | LOW | Allowlist de tablas para `sga_app` verificada por test. | `l62a0d530001_privilegios_app_allowlist.py` |
| DB-006 | LOW | Índices tenant y operativos en migración `k61f9c420001`. | `k61f9c420001_indices_tenant_operativos.py` |
| DB-007 | MEDIUM | Sin test de downgrade en CI. | Sin pipeline CI |
| DB-008 | LOW | Uso de Numeric(14,4) para costos monetarios. Correcto. | `backend/app/models/repuestos.py` |

### Migraciones (18)

| # | Revisión | Descripción |
|---|----------|-------------|
| 1 | f284acc97939 | Initial clean final |
| 2 | f26b4d970001 | Plantillas reporte |
| 3 | g37c5e080001 | **RLS multi-tenant** |
| 4 | h48d6f190001 | RLS auditoría global |
| 5 | i59e7a2a0001 | Tablas sistema operativo |
| 6 | j60f8b310001 | Coordinador multiempresa |
| 7 | k61f9c420001 | Índices tenant operativos |
| 8 | l62a0d530001 | Privilegios app allowlist |
| 9 | a71c9e420001 | Solicitudes correctivas |
| 10 | b82d0f530001 | Reportes publicados |
| 11 | c93e1a640001 | Catálogo categorías canónico |
| 12 | d04f2b750001 | Facturación |
| 13 | e15a3c860001 | Repuestos incidencias OT |
| 14 | m63b1e640001 | Equipos fase 7 |
| 15 | n74c2f750001 | Mantenimientos fase 8 |
| 16 | o85d3e860001 | Password history policy |
| 17 | p91e4f720001 | Add activo mantenimientos |
| 18 | r01a1b2c30001 | **Repuestos consumibles módulo completo** |

---

## 17. Transacciones

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| TX-001 | MEDIUM | Crear mantenimiento y asignar técnico no es atómico en todas las implementaciones. | Análisis de código |
| TX-002 | MEDIUM | Consumo de repuestos puede tener condiciones de carrera (sin SELECT FOR UPDATE). | Análisis de código |
| TX-003 | LOW | Uso de `try/except` con rollback en operaciones críticas. | `backend/app/routers/repuestos.py` |
| TX-004 | LOW | `idempotency_key` en movimientos para prevenir duplicados. | `backend/app/models/repuestos.py` |

---

## 18. Frontend y Seguridad

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| FE-001 | LOW | Access token en memoria, no en storage. | `frontend/src/AuthContext.jsx` |
| FE-002 | LOW | localStorage/SESSIONStorage limpio de tokens. | `frontend/src/AuthContext.jsx` |
| FE-003 | LOW | Guardas por rol (`RoleRoute`). | `frontend/src/components/RoleRoute.jsx` |
| FE-004 | LOW | Toast global no bloqueante (sin `alert()`). | `frontend/src/App.jsx` |
| FE-005 | LOW | Lazy loading por módulo. | `frontend/src/App.jsx` |
| FE-006 | MEDIUM | Uso de `alert()`, `confirm()` en algunos componentes legacy. | Búsqueda de archivos |
| FE-007 | LOW | Build de producción verificado. | Auditoría v1.0.14 |
| FE-008 | LOW | ESLint sin errores. | Auditoría v1.0.14 |
| FE-009 | INFORMATIONAL | Sin tests E2E (Playwright/Cypress). | Sin configuración |
| FE-010 | LOW | UTF-8 verificación en build. | `backend/scripts/` |
| FE-011 | MEDIUM | Sin Content Security Policy (CSP) configurado en frontend. | Análisis de config |
| FE-012 | LOW | ~89 componentes/páginas. | Conteo de archivos |

---

## 19. Branding y UI

**Calificación: 3/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| BR-001 | LOW | 62+ referencias a "SGA", "SGA SaaS", "SGAHolding", "sgaholding.online". | Búsqueda grep |
| BR-002 | LOW | `package-lock.json` contiene `"name": "SGA_SaaS"`. | `package-lock.json` línea 2 |
| BR-003 | LOW | Documentos de usuario referencian `sgaholding.online`. | `docs/MANUAL_USUARIO.md` |
| BR-004 | LOW | Docker configs referencian `/opt/sga_saas`. | `docs/DESPLIEGUE_PRODUCCION.md` |
| BR-005 | LOW | Imágenes Docker: `vanstralhen/sga-backend`, `vanstralhen/sga-frontend`. | `docs/REGISTRO_CAMBIOS_V1.0.6.md` |
| BR-006 | LOW | Variable `sga-admin-sidebar-collapsed` en localStorage. | `docs/REGISTRO_CAMBIOS_V1.0.6.md` |
| BR-007 | LOW | Credenciales: `sga_app`, `sga_backup`. | `.env`, migraciones |

### Ubicaciones de Referencias SGA

| Categoría | Archivos | Acción |
|-----------|----------|--------|
| Documentación | `docs/MANUAL_USUARIO.md`, `docs/DESPLIEGUE_PRODUCCION.md`, `docs/INSTRUCCIONES_IMPORTACION_*.md` | Renombrar |
| Configuración | `.env` (usuarios DB), `docker-compose*.yml` | Renombrar usuarios DB |
| Código | `package-lock.json`, `docs/REGISTRO_CAMBIOS_*.md` | Actualizar |
| Imágenes Docker | Referencias en docs | Renombrar imágenes |
| Migraciones | Nombres de roles `sga_app`, `sga_backup` | Renombrar en nueva migración |

---

## 20. Configuración General

**Calificación: 6/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| CFG-001 | LOW | `.env.example` completo con todas las variables. | `.env.example` (83 líneas) |
| CFG-002 | LOW | Configuración por variables de entorno. | `.env` |
| CFG-003 | MEDIUM | `configuracion_sistema` y `configuracion_saas` existen pero no se verificó uso completo. | Modelos existentes |
| CFG-004 | LOW | `FEATURE_RLS` y `FEATURE_AUDIT` como feature flags. | `.env` línea 31-32 |
| CFG-005 | LOW | `DEBUG=True` en `.env` de desarrollo. Correcto para dev. | `.env` línea 9 |

---

## 21. Backups

**Calificación: 4/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| BK-001 | HIGH | Sin backup automatizado. No hay cron job, ni script programado. | Sin archivos de configuración |
| BK-002 | MEDIUM | Backup manual hecho una vez: 229KB, SHA verificado. | `docs/AUDITORIA_INTEGRAL_SGA_SAAS_2026-08-18.md` |
| BK-003 | LOW | Cifrado AES-GCM implementado. Cabecera `SGABKP1`. | Código de backups |
| BK-004 | LOW | Retención S3 configurada. | `.env.example` |
| BK-005 | HIGH | Sin restore drill completo (backup no restaurado en base temporal). | Auditoría v1.0.14 |
| BK-006 | MEDIUM | Sin backup de uploads/archivos subidos. | Análisis de código |
| BK-007 | MEDIUM | Sin RPO/RTO definidos. | Sin documentación |

### Recomendaciones

1. **Inmediato**: Script de backup con `pg_dump` + cifrado + retención
2. **Inmediato**: Cron job diario en VPS
3. **Corto plazo**: Restore drill mensual automatizado
4. **Corto plazo**: Backup de uploads a S3

---

## 22. Infraestructura

**Calificación: 5/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| INF-001 | LOW | Backend ejecuta como usuario no root. | Docker Compose |
| INF-002 | LOW | Backend usa filesystem read-only, tmpfs, cap_drop ALL, no-new-privileges. | `docker-compose.prod.yml` |
| INF-003 | LOW | Frontend usa Nginx no-root en puerto 8080. | `docker-compose.prod.yml` |
| INF-004 | LOW | Caddy sin access log de queries sensibles. | `docker-compose.prod.yml` |
| INF-005 | LOW | Redis autenticado y aislado en red interna. | `docker-compose.prod.yml` |
| INF-006 | MEDIUM | Sin health checks configurados en Docker Compose. | `docker-compose.yml` |
| INF-007 | MEDIUM | Sin límites de CPU/memoria específicos por servicio. | `docker-compose.yml` |
| INF-008 | LOW | `redis` deshabilitado en desarrollo. | `.env` sin `REDIS_URL` |
| INF-009 | MEDIUM | Sin monitoreo de VPS configurado. | Análisis de config |
| INF-010 | LOW | Caddy como reverse proxy con HTTPS. | `docker-compose.prod.yml` |

---

## 23. Tests

**Calificación: 8/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| TEST-001 | LOW | 316 tests backend aprobados. | `pytest` output |
| TEST-002 | LOW | 44 tests frontend aprobados. | `vitest` output |
| TEST-003 | LOW | 31 tests de política de contraseñas. | `test_password_policy.py` |
| TEST-004 | LOW | Tests de schemas, rutas, fecha/hora, herencia, exportación. | Auditoría Portal Coordinador |
| TEST-005 | MEDIUM | Sin tests E2E (Playwright/Cypress). | Sin configuración |
| TEST-006 | MEDIUM | Sin tests de integración RLS (dos tenants reales). | Sin implementación |
| TEST-007 | MEDIUM | Sin tests de concurrencia para stock. | Sin implementación |
| TEST-008 | LOW | Build de producción verificado. | Auditoría v1.0.14 |
| TEST-009 | LOW | ESLint sin errores. | Auditoría v1.0.14 |
| TEST-010 | LOW | pip-check sin dependencias rotas. | Auditoría v1.0.14 |

### Cobertura por Área

| Área | Tests | Estado |
|------|:-----:|--------|
| Password policy | 31 | ✅ |
| Schemas | ~50 | ✅ |
| Rutas/API | ~100 | ✅ |
| Auth | ~20 | ✅ |
| Mantenimiento | ~30 | ✅ |
| Inventario | ~25 | ✅ |
| Coordinador | ~40 | ✅ |
| Frontend (Vitest) | 44 | ✅ |
| E2E | 0 | ❌ |
| RLS | 0 | ❌ |
| Concurrencia | 0 | ❌ |

---

## 24. CI/CD

**Calificación: 1/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| CICD-001 | CRITICAL | Sin pipeline CI/CD configurado. No hay GitHub Actions. | Sin `.github/workflows/` |
| CICD-002 | MEDIUM | Sin Dependabot activo. | Sin `.github/dependabot.yml` |
| CICD-003 | MEDIUM | Sin automatización de tests en PRs. | Sin pipeline |
| CICD-004 | MEDIUM | Sin automatización de lint en PRs. | Sin pipeline |
| CICD-005 | MEDIUM | Sin automatización de build en PRs. | Sin pipeline |
| CICD-006 | LOW | `pip-audit` y `audit-ci` declarados pero sin pipeline. | `requirements.txt`, `package.json` |
| CICD-007 | MEDIUM | Sin secret scanning automatizado. | Sin pipeline |

### Recomendaciones

1. **Inmediato**: GitHub Actions mínimo: lint → test → build
2. **Corto plazo**: Dependabot activo
3. **Corto plazo**: Secret scanning en CI
4. **Mediano plazo**: Deploy automatizado a VPS

---

## 25. Rendimiento

**Calificación: 6/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| PERF-001 | MEDIUM | Sin paginación en algunos listados de catálogos. | Análisis de código |
| PERF-002 | LOW | Índices tenant y operativos en migración `k61f9c420001`. | `k61f9c420001_indices_tenant_operativos.py` |
| PERF-003 | MEDIUM | Sin caching de sesiones ni tokens. | Análisis de código |
| PERF-004 | LOW | Redis configurado para rate limiting en producción. | `docker-compose.prod.yml` |
| PERF-005 | MEDIUM | Sin métricas de rendimiento por endpoint. | Sin implementación |
| PERF-006 | LOW | Exportaciones paginadas. | `backend/app/routers/exportaciones.py` |

---

## 26. Observabilidad

**Calificación: 3/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| OBS-001 | MEDIUM | Sin Sentry o equivalente para tracking de errores. | Sin configuración |
| OBS-002 | MEDIUM | Sin métricas de sistema (Prometheus, etc.). | Sin configuración |
| OBS-003 | MEDIUM | Sin alertas configuradas. | Sin configuración |
| OBS-004 | LOW | Logs estructurados en backend. | `backend/app/routers/logs_inteligentes.py` |
| OBS-005 | LOW | Tablas de auditoría: `auditoria_eventos`, `auditoria_pro_eventos`, `seguridad_eventos`. | Modelos existentes |
| OBS-006 | LOW | Health check endpoint disponible. | `backend/app/main.py` |

---

## 27. Datos Maestros

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| DM-001 | LOW | Categorías canónicas en migración `c93e1a640001`. | Migración |
| DM-002 | LOW | Unidades de medida iniciales en migración `r01a1b2c30001`. | Migración |
| DM-003 | LOW | Empresas y sedes como datos maestros. | Modelos existentes |
| DM-004 | MEDIUM | Sin proceso reproducible de seed para nuevos tenants. | Sin script |

---

## 28. Cumplimiento Normativo

**Calificación: 3/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| COMP-001 | MEDIUM | Sin política de retención de datos. | Sin documentación |
| COMP-002 | MEDIUM | Sin GDPR/LGPD implementado. | Sin implementación |
| COMP-003 | MEDIUM | Sin auditoría de consentimiento. | Sin implementación |
| COMP-004 | LOW | Tabla de auditoría de eventos existe. | `backend/app/models/auditoria_evento.py` |
| COMP-005 | LOW | Logs de seguridad implementados. | `backend/app/models/security_event.py` |

---

## 29. Datos de Prueba

**Calificación: 6/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| TP-001 | LOW | Tests usan datos sintéticos/mock. | `backend/tests/` |
| TP-002 | MEDIUM | Sin script de seed para datos de prueba. | Sin archivo |
| TP-003 | LOW | Usuarios de prueba en tests. | `backend/tests/` |

---

## 30. Datos Maestros vs Producción

**Calificación: 5/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| DPP-001 | MEDIUM | Sin separación clara entre datos de prueba y producción. | Análisis |
| DPP-002 | MEDIUM | Credenciales de dev en `.env` podrían confundirse con producción. | `.env` |
| DPP-003 | LOW | `APP_ENV=development` en `.env` local. | `.env` línea 8 |

---

## 31. Gestión de Cambios

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| GC-001 | LOW | Git con ramas `product/vaner-asset`. | `git status` |
| GC-002 | LOW | Commits descriptivos con convención. | `git log` |
| GC-003 | LOW | Registros de cambios documentados. | `docs/REGISTRO_CAMBIOS_*.md` |
| GC-004 | MEDIUM | Sin changelog automatizado. | Sin configuración |
| GC-005 | LOW | Tags de versión recomendados. | `architecture/audit_actual.md` |

---

## 32. Documentación

**Calificación: 6/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| DOC-001 | LOW | README.md existe. | `README.md` |
| DOC-002 | LOW | Manual de usuario existe. | `docs/MANUAL_USUARIO.md` |
| DOC-003 | LOW | Arquitectura documentada. | `docs/ARQUITECTURA_GMAO_MULTI_TENANT.md` |
| DOC-004 | LOW | Guía de migración. | `docs/GUIA_MIGRACION_LOCAL_Y_VPS_V1.0.14.md` |
| DOC-005 | MEDIUM | Documentación referencian marca SGA. | Múltiples archivos |
| DOC-006 | MEDIUM | Sin documentación de API (OpenAPI/Swagger). | Sin archivo |
| DOC-007 | LOW | Estrategia de versiones documentada. | `docs/ESTRATEGIA_VERSIONES_CLIENTES.md` |

---

## 33. Roadmap y Deuda Técnica

**Calificación: 7/10**

### Deuda Técnica Identificada

| # | Componente | Tipo | Riesgo |
|---|------------|------|--------|
| DT1 | Hardcoding de configuración | Configuración | Dificultad para nuevos entornos |
| DT2 | Referencias SGA | Identificadores | Riesgo de exposición |
| DT3 | Sin tests E2E | Calidad | Regresiones no detectadas |
| DT4 | Migraciones sin downgrade completo | Versionado | Rollback imposible |
| DT5 | Docker sin healthchecks | Despliegue | Servicios no disponibles |
| DT6 | Sin CI/CD | Operaciones | Código sin validar |
| DT7 | Branding hardcodeado | Frontend | Multi-tenant limitado |
| DT8 | Sin backup automatizado | Operaciones | Pérdida de datos |
| DT9 | Docs desactualizados | Documentación | Onboarding difícil |
| DT10 | Sin monitoreo | Operaciones | Errores no detectados |

---

## 34. Equipo y Proceso

**Calificación: 7/10**

### Hallazgos

| ID | Severidad | Hallazgo | Evidencia |
|----|-----------|----------|-----------|
| TEAM-001 | LOW | Desarrollo con agente IA (opencode). | Evidencia del proyecto |
| TEAM-002 | LOW | Memoria persistente multi-IA. | `memory/` |
| TEAM-003 | LOW | Directivas operativas. | `directives/` |
| TEAM-004 | LOW | Scripts deterministas. | `execution/` |
| TEAM-005 | MEDIUM | Sin proceso formal de code review. | Sin configuración |

---

## 35. Inventario Técnico del Proyecto

### Backend

| Componente | Cantidad |
|------------|:--------:|
| Archivos Python (.py) | 273 |
| Modelos SQLAlchemy | 39 archivos |
| Routers FastAPI | 45 |
| Schemas Pydantic | ~20 archivos |
| Migraciones Alembic | 18 |
| Tests | 47 archivos (316 pruebas) |
| Servicios | ~5 archivos |

### Frontend

| Componente | Cantidad |
|------------|:--------:|
| Componentes/Páginas (.jsx) | 89 |
| Estilos (.css) | ~20 |
| Tests (Vitest) | 44 pruebas |

### Database

| Métrica | Valor |
|---------|-------|
| Total tablas | 59 |
| Tablas con empresa_id | 37+ |
| Tablas con RLS | ~20 |
| Tablas sin RLS | ~37 |
| Migraciones | 18 |
| Heads | 1 (r01a1b2c30001) |

### Infraestructura

| Componente | Estado |
|------------|--------|
| Docker Compose (dev) | ✅ |
| Docker Compose (prod) | ✅ |
| PostgreSQL | ✅ |
| Redis | ⚠️ Deshabilitado en dev |
| Caddy | ✅ |
| CI/CD | ❌ |
| Monitoring | ❌ |
| Backups auto | ❌ |

---

## 36. Plan de Acción 30-60-90 días

### Inmediato (0-30 días) — CRITICAL

| # | Acción | Hallazgo | Archivos probables | Duración | Criterio de cierre |
|---|--------|----------|-------------------|----------|-------------------|
| 1 | **Migración RLS completa** | RLS-002, RLS-003, RLS-004, RLS-005 | `alembic/versions/s01_rls_completo.py`, todos los modelos | 5 días | Todas las tablas tenant-scoped tienen RLS ENABLE + FORCE + POLICY |
| 2 | **Backup automatizado PostgreSQL** | BK-001, BK-005 | `scripts/backup.sh`, `cron`, `docker-compose.prod.yml` | 2 días | Cron diario ejecuta pg_dump + cifrado + retención; restore drill probado |
| 3 | **CI/CD pipeline mínimo** | CICD-001, CICD-003, CICD-004, CICD-005 | `.github/workflows/ci.yml` | 2 días | Lint + test + build se ejecutan en cada PR |
| 4 | **Limpiar .env.docker** | SEC-001, SEC-004 | `.env`, `.env.prod`, Docker secrets | 1 día | Secrets únicos generados; no reutilizar SECRET_KEY = REDIS_PASSWORD |
| 5 | **Branding completo** | BR-001, BR-002, BR-003, BR-004, BR-005 | Todos los archivos con referencias SGA | 3 días | 0 referencias a SGA en código fuente |

### Corto plazo (30-60 días) — HIGH

| # | Acción | Hallazgo | Archivos probables | Duración | Criterio de cierre |
|---|--------|----------|-------------------|----------|-------------------|
| 1 | **Migración productiva PostgreSQL** | DB-004 | `docker-compose.prod.yml`, scripts | 3 días | PostgreSQL 17 en VPS con roles separados |
| 2 | **Instalar y configurar Redis** | INF-008 | `docker-compose.prod.yml`, `.env.prod` | 1 día | Redis autenticado operativo para rate limiting |
| 3 | **Migración de usuarios** | BR-007 | Script de migración | 2 días | Usuarios con hashes Argon2id en producción |
| 4 | **Auditoría completa de permisos** | PERM-002, PERM-003 | Matriz formal de permisos | 3 días | Matriz documentada y verificada contra código |
| 5 | **Completar módulo usuarios** | PERM-002 | `usuarios.py`, frontend | 5 días | Tabla de usuarios con paginación y filtros |

### Mediano plazo (60-90 días) — MEDIUM

| # | Acción | Hallazgo | Archivos probables | Duración | Criterio de cierre |
|---|--------|----------|-------------------|----------|-------------------|
| 1 | **Monitoreo: Sentry o similar** | OBS-001 | `sentry_config`, `docker-compose.prod.yml` | 2 días | Errores capturados y notificados |
| 2 | **Métricas de sistema** | OBS-002, PERF-005 | Prometheus + Grafana | 3 días | Métricas por endpoint, tenant, HTTP code |
| 3 | **Documentación de API** | DOC-006 | OpenAPI/Swagger habilitado | 1 día | Docs de API accesibles |
| 4 | **Tests de integración E2E** | TEST-005, TEST-006 | Playwright config | 5 días | Login, CRUD, RLS verificados E2E |
| 5 | **Análisis de rendimiento** | PERF-001, PERF-003 | Benchmark scripts | 3 días | Consultas N+1 identificadas y optimizadas |

---

## 37. Decisión de Despliegue

### **NO APTO PARA PRODUCCIÓN en estado actual.**

**Motivos:**

1. **Multi-tenancy no protegido**: 37+ tablas sin RLS. Un atacante con acceso SQL puede ver datos de cualquier empresa. Esto es una brecha de seguridad crítica que impide cualquier despliegue multi-tenant.

2. **Sin backups automatizados**: No hay forma de recuperar datos ante un fallo de disco, error humano o ataque ransomware. El único backup exists es un dump manual de 229KB.

3. **Sin pipeline CI/CD**: No se ejecutan tests automáticamente. Cualquier cambio puede introducez regresiones sin detectar.

4. **Sin observabilidad en producción**: No hay Sentry, métricas ni alertas. Los errores en producción serían invisibles.

5. **62 referencias a marca antigua**: Exposición del cliente anterior (SGAHolding), riesgo contractual y reputacional.

6. **Secrets reutilizados**: `SECRET_KEY` = `REDIS_PASSWORD`. Compromiso de seguridad si uno se expone.

7. **Base de datos desactualizada**: El código requiere migración `l62a0d530001` pero la DB está en `i59e7a2a0001`.

### Condiciones para Aprobar

- [ ] Completar migración RLS para todos los modelos tenant-scoped
- [ ] Configurar backups automáticos con retención y restore drill probado
- [ ] CI/CD pipeline con lint, test, build en cada PR
- [ ] Branding completo: 0 referencias SGA en código fuente
- [ ] Producción PostgreSQL con autenticación segura y roles separados
- [ ] Redis configurado y operativo para rate limiting
- [ ] Migración de usuarios de dev → producción con hashes Argon2id
- [ ] Monitoreo de errores configurado (Sentry o similar)
- [ ] Base de datos en revisión `l62a0d530001` (aplicar migraciones pendientes)
- [ ] SECRET_KEY y CONFIG_ENCRYPTION_KEY únicos y rotados

### Riesgo Residual

Si se cumplen todas las condiciones, el riesgo residual sería **bajo-medio**. Se requieren además:
- Pentest dinámico
- Prueba de carga y concurrencia
- Revisión de firewall y DNS en VPS
- E2E visual completo por rol

---

## 38. Limitaciones de la Auditoría

1. No se ejecutó `alembic upgrade head` sobre PostgreSQL real (la DB local está desactualizada).
2. No se realizaron pruebas de penetración dinámicas.
3. No se verificó el estado real del VPS de producción.
4. No se probaron escenarios de concurrencia reales.
5. No se verificó la restauración completa de backups en base temporal.
6. No se inspeccionaron los contenedores Docker en ejecución.
7. No se verificaron los logs de producción.
8. Los agentes de auditoría originales (secrets, RLS, auth, DB, tests, architecture) no estaban disponibles en logs; la auditoría se basa en inspección directa del código fuente y documentos existentes.

---

*Informe generado el 27 de agosto de 2026*
*Auditor: opencode*
*Versión del código: `a4383fa` (branch `product/vaner-asset`)*
*Total hallazgos: 130+*
*Calificación global: 4.3/10 — CRÍTICO — No apto para producción*
