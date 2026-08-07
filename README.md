# SGAHolding — Plataforma GMAO Multi-Tenant

Sistema SaaS de Gestión de Mantenimiento Asistido por Computadora (GMAO/CMMS) para administrar empresas, activos, órdenes de trabajo y evidencias técnicas.

**Dominio:** `sgaholding.online`
**Stack:** React 19 + FastAPI + PostgreSQL 16 + Docker

## Requisitos del VPS

- Ubuntu 24.04 LTS
- 2 vCPU, 8 GB RAM y 100 GB NVMe como base recomendada
- Docker Engine + Docker Compose
- Puertos 80 y 443 públicos; PostgreSQL únicamente en la red interna

## Despliegue

### 1. Configurar DNS

Crear registros `A` hacia la IP pública del VPS:

- `sgaholding.online`
- `www.sgaholding.online`

### 2. Preparar el proyecto

```bash
sudo mkdir -p /opt/sga_saas
cd /opt/sga_saas
cp .env.example .env
openssl rand -hex 32
```

Reemplazar en `.env` todos los valores `CAMBIAR_*` y usar claves distintas para PostgreSQL, el rol de aplicación y JWT.

Generar también una clave Fernet para `CONFIG_ENCRYPTION_KEY`:

`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

El workflow `Release immutable images` publica backend y frontend usando el SHA completo del commit. Configurar ese SHA en `IMAGE_TAG`; producción no utiliza la etiqueta mutable `latest`.

### 3. Desplegar

```bash
chmod +x deploy.sh
./deploy.sh
```

El script crea la red externa `caddy_net`, inicia Caddy, descarga las imágenes publicadas y levanta PostgreSQL, backend y frontend.

### 4. Crear el primer administrador

Después del primer despliegue, ejecutar el bootstrap local dentro del contenedor. La contraseña se solicita de forma interactiva y no queda en el historial del shell:

`docker compose --env-file .env -f docker-compose.prod.yml exec backend python scripts/create_initial_admin.py --name "Administrador" --username admin --email admin@dominio.com`

El comando se niega a crear otro usuario cuando ya existe un ADMIN. El endpoint HTTP de bootstrap permanece deshabilitado mientras `BOOTSTRAP_ADMIN_TOKEN` esté vacío.

### 5. Verificar

```bash
curl -f https://sgaholding.online/health/ready
curl -f https://sgaholding.online/api/health/ready
```

Verificar además que cada backup muestre una clave remota en S3/R2 y ejecutar una restauración de prueba en una base temporal antes de abrir el servicio a usuarios.

## Estructura

```text
SGA_SaaS/
├── backend/          # FastAPI + SQLAlchemy + Alembic
├── frontend/         # React 19 + Vite
├── docs/             # Arquitectura y operación
├── Caddyfile
├── deploy.sh
├── docker-compose.yml
└── .env.example
```
