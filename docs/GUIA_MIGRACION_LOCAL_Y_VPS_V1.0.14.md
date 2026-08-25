# Guía Segura de Migración Local y VPS — v1.0.14

## 1. Requisitos

- URL de aplicación con usuario sga_app.
- URL de migración con el propietario de las tablas.
- URL de backup con usuario sga_backup en producción.
- Copia del archivo .env fuera de Git y con permisos restringidos.
- PostgreSQL 16 o cliente pg_dump compatible.

## 2. Verificación previa local

Desde backend:

    .venv\Scripts\python.exe -m alembic current
    .venv\Scripts\python.exe -m alembic heads

Resultado esperado antes de migrar en este equipo:

- current: i59e7a2a0001
- head: l62a0d530001

## 3. Configurar credenciales sin imprimir secretos

Definir temporalmente en la sesión PowerShell:

    $env:MIGRATION_DATABASE_URL = leer desde un gestor seguro
    $env:BACKUP_DATABASE_URL = leer desde un gestor seguro

No guardar estas URLs en archivos versionados, historial de comandos compartido, tickets o capturas.

## 4. Backup

Crear backup custom con sga_backup o con el propietario:

    pg_dump --format=custom --no-owner --no-acl --file pre_migracion.dump nombre_base

Validar catálogo:

    pg_restore --list pre_migracion.dump

Recomendado: restaurar en una base temporal y ejecutar conteos de usuarios, empresas, equipos, mantenimientos, evidencias y auditoría.

## 5. Migración local

    .venv\Scripts\python.exe -m alembic upgrade head
    .venv\Scripts\python.exe -m alembic current

El resultado obligatorio es l62a0d530001.

## 6. Validación local posterior

    .venv\Scripts\python.exe -m compileall -q app alembic tests
    .venv\Scripts\python.exe -m unittest discover -s tests -v
    .venv\Scripts\python.exe -m pip check

Desde frontend:

    npm run verify:utf8
    npm test
    npm run lint
    npm run build
    npm run verify:no-rsc

Pruebas manuales mínimas:

- Login ADMIN.
- Login COORDINADOR.
- Cambio de empresa autorizada.
- Listar inventario.
- Editar equipo.
- Abrir hoja de vida.
- Exportar inventario.
- Crear y editar mantenimiento.
- Cerrar sesión y renovar sesión.

## 7. Preparación VPS

1. Confirmar CI verde en el commit a desplegar.
2. Crear backup cifrado y verificar restauración.
3. Confirmar espacio libre y salud de PostgreSQL/Redis.
4. Actualizar imágenes con un IMAGE_TAG inmutable.
5. Ejecutar el servicio migrate con MIGRATION_DATABASE_URL.
6. Levantar backend y esperar healthcheck.
7. Levantar frontend y Caddy.
8. Ejecutar smoke tests por rol.

## 8. Validación VPS

    docker compose -f docker-compose.prod.yml config --quiet
    docker compose -f docker-compose.prod.yml run --rm migrate current
    docker compose -f docker-compose.prod.yml ps

Comprobar que la revisión sea l62a0d530001 y que backend, frontend, PostgreSQL y Redis estén saludables.

## 9. Rollback

No ejecutar downgrade automático sobre producción sin revisar pérdida de datos. Si falla el despliegue:

1. Detener tráfico nuevo.
2. Conservar logs y evidencia del error.
3. Restaurar el backup en una base limpia.
4. Volver al IMAGE_TAG anterior.
5. Ejecutar smoke tests antes de reabrir tráfico.

## 10. Regla de seguridad

Nunca otorgar CREATE, propietario o BYPASSRLS a sga_app para simplificar una migración. Migraciones, aplicación y backups deben usar credenciales separadas.
