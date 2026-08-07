# Despliegue de producción

## Dominio

La aplicación se publica en `sgaholding.online` y consume el backend por la ruta del mismo origen `/api`. `www.sgaholding.online` redirige al dominio raíz.

## Infraestructura inicial

- VPS con Ubuntu 24.04 LTS, al menos 2 vCPU, 8 GB de RAM y 100 GB NVMe.
- Docker Compose y Caddy como proxy inverso con HTTPS automático.
- PostgreSQL accesible únicamente desde la red interna de Docker.
- Firewall con solamente SSH controlado, HTTP y HTTPS habilitados.
- Almacenamiento S3/R2 externo para una segunda copia de los backups.

## Variables

1. Copiar `.env.example` a `/opt/sga_saas/.env`.
2. Reemplazar todas las claves `CAMBIAR_*` por valores diferentes y aleatorios.
3. Mantener `DATABASE_URL` con el rol restringido `sga_app`.
4. Mantener `MIGRATION_DATABASE_URL` con el rol propietario usado únicamente por Alembic.
5. Configurar `BACKEND_CORS_ORIGINS=https://sgaholding.online`.
6. Mantener `VITE_API_URL=/api` y `REFRESH_COOKIE_SECURE=true`.
7. Generar `CONFIG_ENCRYPTION_KEY` con Fernet y guardarla fuera del repositorio.
8. Definir `IMAGE_TAG` con el SHA exacto publicado por CI.
9. Configurar S3/R2 y mantener `S3_BACKUP_ENABLED=true`.

## Primera instalación

El script `backend/docker/init-app-role.sh` crea el rol restringido `sga_app` solamente cuando PostgreSQL inicializa un volumen nuevo. El servicio one-shot `migrate` ejecuta `alembic upgrade head` antes de iniciar el backend. El proceso web no recibe la URL de migración ni la contraseña propietaria.

Si la base ya existe, se debe provisionar o actualizar manualmente `sga_app`, ejecutar `backend/sql/provision_app_role.sql` con el propietario y verificar RLS mediante `backend/scripts/verify_postgres_rls.py`.

Crear el primer administrador con `docker compose --env-file .env -f docker-compose.prod.yml exec backend python scripts/create_initial_admin.py --name "Administrador" --username admin --email admin@dominio.com`. La contraseña se solicita de forma interactiva y el comando se niega a crear un segundo ADMIN.

## DNS y acceso

- Crear registros `A` para `sgaholding.online` y `www.sgaholding.online` hacia la IP pública del VPS.
- Publicar solamente los puertos 80 y 443.
- Restringir SSH por IP o VPN y deshabilitar autenticación por contraseña.
- No publicar el puerto 5432 de PostgreSQL.

## Backups

- `postgres_data`, `uploads_data` y `backups_data` son volúmenes nombrados.
- Ejecutar un backup diario y copiarlo después a almacenamiento externo cifrado.
- Mantener al menos 7 copias diarias, 4 semanales y 6 mensuales.
- Probar la restauración en una base temporal antes de usarla sobre producción.
- `ALLOW_DATABASE_RESTORE` permanece en `false` salvo durante una ventana controlada.

## Escalamiento

La primera instalación debe usar una sola réplica del backend porque APScheduler se ejecuta dentro del proceso web. Antes de agregar réplicas o varios workers, se debe desplegar el scheduler como un servicio separado con `RUN_SCHEDULER=false` en los procesos web.

## Verificación

1. Confirmar que `/health/live` y `/health/ready` responden `200`.
2. Confirmar que `/api/health/live` y `/api/health/ready` responden `200`.
3. Crear dos tenants de prueba y ejecutar la verificación RLS.
4. Probar login, refresh automático, logout y revocación de cookie.
5. Configurar y probar el SMTP corporativo desde el panel administrativo.
6. Subir y descargar una evidencia privada.
7. Generar un backup y verificar que existe fuera del contenedor.
