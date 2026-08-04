# Despliegue de producción

## Dominio recomendado

La marca propuesta es `vanergmao.com`. La aplicación se publica en
`app.vanergmao.com` y consume el backend por la ruta del mismo origen `/api`.
La disponibilidad del dominio debe confirmarse antes de comprarlo.

## Infraestructura inicial

- Un VPS con Ubuntu 24.04 LTS, 6 vCPU, 12 GB de RAM y al menos 100 GB NVMe.
- Dokploy como plataforma de despliegue.
- PostgreSQL accesible únicamente desde la red interna de Docker.
- Cloudflare para DNS y protección del dominio.
- Almacenamiento S3/R2 externo para una segunda copia de los backups.

## Variables

1. Copiar `.env.example` a un archivo local ignorado o al gestor de secretos de Dokploy.
2. Reemplazar todas las claves `CAMBIAR_*` por valores diferentes y aleatorios.
3. Mantener `DATABASE_URL` con el rol restringido `sga_app`.
4. Mantener `MIGRATION_DATABASE_URL` con el rol propietario usado únicamente por Alembic.
5. Configurar `BACKEND_CORS_ORIGINS=https://app.vanergmao.com`.
6. Mantener `VITE_API_URL=/api` y `REFRESH_COOKIE_SECURE=true`.

## Primera instalación

El script `backend/docker/init-app-role.sh` crea el rol restringido `sga_app`
solamente cuando PostgreSQL inicializa un volumen nuevo. El backend ejecuta
`alembic upgrade head` antes de iniciar Uvicorn.

Si la base ya existe, se debe provisionar o actualizar manualmente `sga_app`,
ejecutar `backend/sql/provision_app_role.sql` con el propietario y verificar RLS
mediante `backend/scripts/verify_postgres_rls.py`.

## DNS y acceso

- Crear un registro `A` para `app.vanergmao.com` hacia la IP pública del VPS.
- Publicar solamente los puertos 80 y 443.
- Restringir SSH por IP o VPN y deshabilitar autenticación por contraseña.
- Restringir el panel de Dokploy mediante IP, VPN o una capa de acceso adicional.
- No publicar el puerto 5432 de PostgreSQL.

## Backups

- `postgres_data`, `uploads_data` y `backups_data` son volúmenes nombrados.
- Ejecutar un backup diario y copiarlo después a almacenamiento externo cifrado.
- Mantener al menos 7 copias diarias, 4 semanales y 6 mensuales.
- Probar la restauración en una base temporal antes de usarla sobre producción.
- `ALLOW_DATABASE_RESTORE` permanece en `false` salvo durante una ventana controlada.

## Escalamiento

La primera instalación debe usar una sola réplica del backend porque APScheduler
se ejecuta dentro del proceso web. Antes de agregar réplicas o varios workers,
se debe desplegar el scheduler como un servicio separado con `RUN_SCHEDULER=false`
en los procesos web.

## Verificación

1. Confirmar que `/api/health/live` responde `200`.
2. Confirmar que `/api/health/ready` responde `200` y valida PostgreSQL.
3. Crear dos tenants de prueba y ejecutar la verificación RLS.
4. Probar login, refresh automático, logout y revocación de cookie.
5. Subir y descargar una evidencia privada.
6. Generar un backup y verificar que existe fuera del contenedor.
