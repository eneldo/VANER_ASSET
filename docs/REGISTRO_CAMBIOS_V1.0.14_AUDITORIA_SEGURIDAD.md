# Registro de Cambios — v1.0.14 Auditoría y Seguridad

**Fecha:** 18 de agosto de 2026

## Seguridad

- Recuperación de contraseña por POST y token en fragmento.
- Redacción de parámetros sensibles en auditoría.
- Revocación global de sesiones al cambiar contraseña.
- Refresh token únicamente en cookie HttpOnly.
- Access token únicamente en memoria.
- Rate limiting distribuido con Redis autenticado.
- Importación CSV/XLSX endurecida.
- Backups cifrados AES-GCM y retención S3 consistente.
- Eliminación de autenticación heredada y router huérfano.
- Escaneo de secretos, .env y autenticación legacy en CI.

## Portal Coordinador

- Selección de empresa autorizada.
- Compatibilidad con empresa principal en esquema anterior.
- Inventario en lista paginada.
- Acciones editar y ver hoja de vida.
- Exportación autenticada de inventario.
- Paginación de equipos, mantenimientos, cronograma, evidencias e informes.
- Mejoras de accesibilidad en acciones.

## Base de datos

- Nueva migración k61f9c420001 para índices operativos y tenant.
- Nueva migración l62a0d530001 para allowlist del rol sga_app.
- Eliminación de privilegios DML automáticos sobre tablas futuras.
- Pruebas de cobertura de tablas y asociaciones.

## Frontend

- Bootstrap de sesión mediante refresh cookie y /auth/me.
- Toast global no bloqueante.
- Normalización UTF-8 y control automático.
- Guard de rutas simplificado.
- Build de producción verificado.

## Infraestructura

- Redis en ambos Compose.
- Backend read-only, tmpfs, cap_drop, no-new-privileges y PID limit.
- Nginx no-root en puerto 8080.
- Caddy sin access log de queries sensibles.
- Dependabot, pip-audit y audit-ci en CI.
- backend/.env retirado del repositorio.

## Validación

- Backend: 143 pruebas aprobadas.
- Frontend: 44 pruebas aprobadas.
- Login local real: ADMIN y COORDINADOR aprobados.
- Compose desarrollo y producción válidos.
- Alembic head: l62a0d530001.

## Pendiente antes del VPS

- La base local permanece en i59e7a2a0001.
- Configurar MIGRATION_DATABASE_URL con el propietario.
- Ejecutar restore drill y migración local.
- Confirmar CI online de dependencias.
