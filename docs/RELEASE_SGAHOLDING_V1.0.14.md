# Entrega congelada SGAHolding v1.0.14

**Fecha de congelacion:** 25 de agosto de 2026

**Cliente:** SGAHolding

**Etiqueta:** `v1.0.14`

**Rama de soporte:** `support/sgaholding-v1`

**Rama de nueva implementacion:** `client/nuevo-cliente-v2`

## Alcance preservado

- Backend FastAPI, modelos, routers, servicios, migraciones Alembic y pruebas.
- Frontend React/Vite, estilos, pruebas y build reproducible.
- Docker Compose de desarrollo y produccion, Caddy y despliegue.
- Plantillas, manuales y documentacion operativa entregable.
- Esquema de configuracion mediante `.env.example`, sin secretos reales.

## Datos que permanecen fuera de Git

- `.env` y credenciales de produccion;
- base de datos PostgreSQL;
- archivos subidos y evidencias;
- backups de aplicacion y almacenamiento S3/R2;
- volumenes Docker y certificados privados.

Estos elementos se respaldan en el VPS con `scripts/backup_production_release.sh` y deben copiarse cifrados a almacenamiento externo.

## Validaciones de congelacion

- Backend: 148 pruebas aprobadas.
- Frontend: 58 pruebas aprobadas.
- Frontend: lint, build, UTF-8 y control sin RSC aprobados.
- Python: `compileall` y `pip check` aprobados.
- Repositorio: control de `.env`, secretos y autenticacion heredada aprobado.
- Docker Compose: configuraciones de desarrollo y produccion validas.
- Alembic: unico head `l62a0d530001`.

Las auditorias online `pip-audit` y `audit-ci` deben confirmarse en GitHub Actions, porque la red administrada local no permitio consultar los registros de paquetes durante la congelacion.

## Reconstruccion

Para recuperar el codigo completo se puede clonar el repositorio y hacer checkout de `v1.0.14`, o restaurar el archivo `.bundle` generado por `scripts/create_release_snapshot.ps1`.

La congelacion y publicacion completa se automatiza con `scripts/finalize_release_git.ps1`. El script rechaza referencias existentes y no utiliza operaciones destructivas ni publicaciones forzadas.

La identidad exacta del release se obtiene con:

```bash
git rev-list -n 1 v1.0.14
```

Produccion debe usar ese SHA completo como `IMAGE_TAG`; no se debe usar `latest`.
