# Auditoría Integral y Profunda — SGA SaaS

**Fecha de cierre técnico:** 18 de agosto de 2026

**Versión de trabajo:** v1.0.14

**Alcance:** backend, frontend, autenticación, autorización, Portal Coordinador, multiempresa, inventario, hoja de vida, mantenimiento, archivos, backups, PostgreSQL, Docker, Caddy, CI/CD y operación VPS.

## 1. Resumen ejecutivo

La auditoría encontró brechas críticas en recuperación de contraseña, persistencia de tokens, autenticación duplicada, rate limiting local, importación de inventario, backups, paginación, privilegios PostgreSQL, hardening de contenedores y experiencia del Portal Coordinador.

La remediación de código quedó aplicada y validada. El riesgo técnico del repositorio baja de **alto** a **medio controlado**. No quedan hallazgos críticos abiertos en el código revisado.

Existe un bloqueo operativo antes de considerar el entorno local completamente alineado: la base de datos está en la revisión **i59e7a2a0001** y el código exige **l62a0d530001**. La aplicación usa correctamente el rol sin DDL **sga_app**, pero no está configurada la variable **MIGRATION_DATABASE_URL** con el propietario de la base. La migración no debe ejecutarse con sga_app.

## 2. Estado por área

| Área | Estado final | Riesgo residual |
|---|---|---:|
| Login ADMIN y COORDINADOR | Validado contra PostgreSQL local | Bajo |
| Recuperación de contraseña | Remediado y probado | Bajo |
| Sesiones y refresh tokens | Remediado y probado | Bajo |
| Portal Coordinador | Funciones heredadas, paginadas y probadas | Bajo/Medio |
| Inventario y exportación | Remediado y probado | Bajo |
| Hoja de vida | Navegación y sesión corregidas | Bajo |
| Mantenimiento Coordinador | Alineado con alcance multiempresa | Bajo/Medio |
| Importación de archivos | Endurecida | Bajo |
| Backups | Cifrados y con retención remota | Medio |
| RLS y privilegios DB | Allowlist implementada; migración pendiente | Medio/Alto operativo |
| Frontend, UX y UTF-8 | Remediado, lint y build correctos | Bajo/Medio |
| Docker, Caddy y CI | Endurecido y validado estáticamente | Bajo/Medio |
| Dependencias | Gates CI configurados; auditoría online local bloqueada | Medio |

## 3. Remediaciones ejecutadas

### 3.1 Autenticación y recuperación

- El token de recuperación dejó de viajar en query string.
- La validación usa POST y body.
- El enlace de correo usa fragmento del navegador y el frontend lo elimina después de leerlo.
- La auditoría registra nombres de parámetros, no sus valores sensibles.
- El cambio de contraseña revoca todos los refresh tokens activos.
- También invalida los demás tokens de recuperación pendientes.
- Se registra el evento PASSWORD_RESET_COMPLETADO.
- La longitud mínima de contraseña quedó alineada en 12 caracteres.
- Se eliminó el router huérfano cliente_seguro.py.
- Se eliminó la dependencia HTTP duplicada de app/security.py.
- Se agregó una prueba anti-regresión para impedir reintroducir autenticación heredada.

### 3.2 Sesión frontend

- El access token vive únicamente en memoria.
- Se eliminaron access_token, token y refresh_token de localStorage y sessionStorage.
- El bootstrap usa refresh cookie HttpOnly y luego consulta /auth/me.
- Se migraron módulos de evidencias, categorías, equipos, técnicos, hoja de vida e indicadores.
- ProtectedRoute quedó con un único guard de autorización.

### 3.3 Portal Coordinador

- El Coordinador puede operar sobre empresas autorizadas y escoger la empresa activa.
- La empresa principal sigue funcionando en bases con el esquema anterior.
- Inventario usa lista paginada desde servidor.
- Se mantienen acciones para editar y abrir hoja de vida.
- Se habilita exportación de inventario autenticada.
- Equipos, mantenimientos, cronograma, evidencias e informes exponen paginación compatible.
- Las respuestas incluyen X-Total-Count, X-Limit y X-Offset.
- CORS expone los encabezados de paginación.
- Botones operativos incluyen tipo explícito y etiquetas accesibles.

### 3.4 Archivos e inventario

- La importación acepta únicamente CSV y XLSX.
- Se validan extensión, MIME, tamaño, UTF-8, estructura ZIP/XLSX y traversal.
- Se limitan filas, columnas y expansión del archivo.
- CSV se procesa por bloques para controlar memoria.
- Se agregaron pruebas de archivos inválidos y límites.

### 3.5 Rate limiting

- Redis es el backend distribuido en producción.
- Desarrollo conserva fallback local.
- Producción puede operar fail-closed cuando Redis es obligatorio.
- Login, refresh, recuperación y reset tienen límites independientes.
- Las claves se almacenan con SHA-256 sin exponer IP ni ruta.
- Redis exige contraseña en ambos Compose.

### 3.6 Backups

- Los backups se cifran por bloques con AES-GCM antes de persistir o subir.
- El formato cifrado usa cabecera SGABKP1.
- Las descargas se descifran en temporal y eliminan el archivo temporal al finalizar.
- La retención elimina también el objeto remoto S3.
- Si falla la limpieza remota, el registro conserva metadata del error para reintento.
- Se protegen las rutas para impedir salir de BACKUP_DIR.

### 3.7 PostgreSQL y rendimiento

- Se añadió la migración k61f9c420001 con índices tenant y operativos.
- Se añadió la migración l62a0d530001 para privilegios explícitos de sga_app.
- Se eliminaron privilegios DML automáticos para futuras tablas de public.
- La allowlist cubre tablas modeladas y asociaciones usuario_empresas y roles_permisos.
- alembic_version queda fuera del rol web.
- La prueba compara la allowlist con los modelos para detectar omisiones futuras.

### 3.8 Frontend y UX

- Se corrigió mojibake del Dashboard Admin.
- Se añadió un verificador UTF-8 al build y CI.
- Se implementó un viewport global de toast.
- Los alert del navegador se transforman en notificaciones no bloqueantes.
- El build genera chunks por módulo y conserva carga diferida.

### 3.9 Despliegue y suministro

- Backend ejecuta como usuario no root.
- Backend usa filesystem de solo lectura, tmpfs, cap_drop ALL, no-new-privileges y límite PID.
- Frontend usa Nginx no-root en puerto 8080.
- Caddy apunta al puerto 8080 y no registra access logs con queries sensibles.
- Redis está autenticado y aislado en red interna.
- Se eliminó backend/.env del repositorio.
- Se agregó Dependabot, EditorConfig, pip-audit, audit-ci y escaneo local de secretos.
- El escaneo incluye archivos versionados y archivos nuevos no ignorados.

## 4. Validación realizada

| Control | Resultado |
|---|---|
| Backend unittest | 143 de 143 aprobadas |
| Frontend Vitest | 44 de 44 aprobadas |
| Compilación Python | Correcta |
| Alembic heads | l62a0d530001, una sola cabeza |
| ESLint | Correcto |
| Vite production build | Correcto |
| Verificación UTF-8 | Correcta |
| Verificación React Router RSC | Correcta |
| pip check | Sin dependencias rotas |
| docker-compose.yml config | Válido |
| docker-compose.prod.yml config | Válido |
| git diff --check | Correcto |
| Escaneo local de .env y secretos | Correcto |
| Login real ADMIN | HTTP 200 y /auth/me HTTP 200 |
| Login real COORDINADOR | HTTP 200 y /auth/me HTTP 200 |
| Limpieza de usuarios smoke | Correcta |

## 5. Backup local previo

Se generó y verificó un backup custom de PostgreSQL antes de migrar:

- Archivo: backend/backups/pre_migracion_20260817_204943.dump
- Tamaño: 229822 bytes
- Entradas de catálogo: 379
- SHA-256: 2f79cd5faebd27fa567d9df8a685ad8e1911e122396bacb13cfc6aa9ed0f1cd2

La verificación confirma que el archivo es legible por pg_restore. Aún falta una restauración completa en una base temporal, porque el rol local sga_app no puede crear bases ni esquemas.

## 6. Bloqueos y riesgos residuales

### 6.1 Base local desactualizada — prioridad alta operativa

- Revisión actual: i59e7a2a0001.
- Revisión requerida: l62a0d530001.
- MIGRATION_DATABASE_URL no está configurada.
- BACKUP_DATABASE_URL no está configurada en local.
- sga_app no tiene CREATE en base ni esquema y no es propietario de tablas.

**Decisión correcta:** no elevar sga_app y no ejecutar Alembic con ese rol. Se requiere la URL del propietario local para aplicar las migraciones.

### 6.2 Modelo de confianza RLS

Las políticas RLS usan contexto de transacción establecido por la aplicación. Este control protege contra errores de filtrado y cruces accidentales entre tenants, pero no debe considerarse una frontera única contra una inyección SQL capaz de ejecutar sentencias arbitrarias con el rol web. La prevención de SQLi, el uso exclusivo de parámetros y el RBAC de aplicación siguen siendo obligatorios.

Optimización recomendada para una etapa enterprise: firmar el contexto tenant o separar credenciales/roles de operaciones privilegiadas, junto con pruebas de penetración específicas de RLS.

### 6.3 Auditoría de dependencias online

- pip-audit está declarado y se ejecuta en CI, pero no está instalado en la venv local.
- npm audit local fue bloqueado por el entorno externo de credenciales/red.
- CI ejecuta pip-audit y audit-ci en cada push o pull request.

No se debe omitir el resultado de CI antes del despliegue VPS.

### 6.4 Validaciones externas pendientes

- Pentest dinámico.
- Prueba de carga y concurrencia.
- Restauración completa en base temporal.
- Revisión real de firewall, DNS, IAM/S3 y rotación de secretos del VPS.
- E2E visual completo por rol en navegador.

## 7. Recomendaciones de optimización PRO

1. Ejecutar importaciones, exportaciones, reportes, correo y backups mediante cola de trabajos con progreso.
2. Extender paginación server-side a todos los listados administrativos grandes.
3. Dividir coordinador.py y las páginas React de más de 800 líneas por dominio y hooks.
4. Añadir Playwright para login, cambio de empresa, inventario, hoja de vida y mantenimiento.
5. Implementar métricas por endpoint, tenant, código HTTP y tiempo de consulta.
6. Añadir request ID extremo a extremo en Caddy, backend y frontend.
7. Ejecutar restauración automática mensual en entorno aislado y comparar conteos/checksums.
8. Definir SLO para login, consulta de inventario, generación de reportes y disponibilidad.
9. Añadir límites de CPU y memoria específicos por servicio en producción.
10. Mantener un release gate que exija CI verde, backup verificado, migración aplicada y smoke tests por rol.

## 8. Criterio de salida a VPS

No desplegar todavía hasta completar estos puntos:

- Configurar MIGRATION_DATABASE_URL local con el propietario.
- Restaurar el backup en una base temporal o realizar un restore drill equivalente.
- Ejecutar alembic upgrade head.
- Confirmar alembic current igual a l62a0d530001.
- Repetir login ADMIN y COORDINADOR.
- Validar inventario, editar, hoja de vida, exportar y mantenimiento.
- Confirmar CI completo en verde.

Después de esos controles, el mismo procedimiento se puede ejecutar en VPS con backup previo, ventana controlada y rollback preparado.

## 9. Conclusión

La plataforma quedó sustancialmente más segura, escalable y profesional. Los problemas originales de sesión, Portal Coordinador, inventario, hoja de vida y mantenimiento fueron corregidos a nivel de código y cubiertos por pruebas. El único bloqueo principal para cerrar local es operativo: aplicar las cuatro migraciones pendientes usando el propietario de PostgreSQL, nunca el rol web.
