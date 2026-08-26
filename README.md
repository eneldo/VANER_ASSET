# VANER ASSET

**VANER SOFTWARE**

**Descripción:** Plataforma para la gestión de inventarios, activos y mantenimiento.

VANER ASSET es una plataforma SaaS multi-tenant para administrar inventarios, activos, mantenimientos, ordenes de trabajo, repuestos, tecnicos, reportes y operacion administrativa.

## Estructura comercial

```text
VANER SOFTWARE
└── VANER ASSET
    ├── Cliente 1
    ├── Cliente 2
    ├── Cliente 3
    └── Cliente VANER
```

Los clientes son tenants de una sola base de codigo. Cada tenant conserva aislamiento de datos, usuarios, archivos, configuracion y auditoria mediante el modelo multiempresa existente.

## Modulos

- Inventarios
- Activos y hojas de vida
- Mantenimiento
- Ordenes de trabajo
- Repuestos asociados a ordenes
- Tecnicos
- Reportes
- Dashboard
- Administracion

## Version anterior preservada

La entrega SGAHolding permanece congelada en:

- etiqueta `v1.0.14`;
- rama `support/sgaholding-v1`;
- bundle `backups/VANER_SOFTWARE/legacy/SGA_HOLDING/v1.0.14/v1.0.14.bundle`;
- ZIP y manifiesto con hashes SHA-256 en el mismo directorio.

La nueva linea de producto se desarrolla fuera de la rama de soporte SGA.

## Desarrollo local

```bash
cp .env.example .env
docker compose --env-file .env up -d --build
```

No use valores `CAMBIAR_*` fuera de un entorno local aislado.

## Produccion

1. Configure `APP_NAME`, `CLIENT_CODE`, `CLIENT_NAME`, `APP_DOMAIN`, `PROJECT_DIR` y secretos en `.env`.
2. Publique imagenes inmutables usando el SHA completo del commit.
3. Configure `IMAGE_TAG` con ese SHA.
4. Ejecute `./deploy.sh` en el servidor autorizado.
5. Verifique `/health/ready` y `/api/health/ready`.

El CORE no contiene el nombre del cliente. Backend, frontend y Caddy reciben la identidad del despliegue desde `.env`; `FRONTEND_URL` y CORS se derivan de `APP_DOMAIN` si no se especifican.

## Clientes

Los metadatos de ejemplo estan en `config/vaner_asset/clients/`. Los archivos reales con secretos, integraciones o credenciales no deben entrar en Git.

## Stack

- React 19 + Vite
- FastAPI + SQLAlchemy + Alembic
- PostgreSQL 16 + Redis
- Docker Compose + Caddy
