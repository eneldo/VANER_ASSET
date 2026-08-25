# Registro de cambios SGA SaaS v1.0.8

Fecha: 13 de agosto de 2026

Estado: desplegado en produccion; validacion tecnica completada

## Version desplegada

- Tag: `v1.0.8`
- Commit: `81ef7133d20d855859ca5e577aa35c54549df2a9`
- Backend: `vanstralhen/sga-backend:81ef7133d20d855859ca5e577aa35c54549df2a9`
- Frontend: `vanstralhen/sga-frontend:81ef7133d20d855859ca5e577aa35c54549df2a9`
- Dominio: `https://sgaholding.online`

## Cambios

- Exportacion corregida para usar inventario real antes de `SIN-INVENTARIO-`.
- Busqueda y filtro de equipos por sede, incluido el selector de cabecera `SEDE`.
- Importaciones consecutivas con duplicados omitidos sin cancelar filas nuevas.
- Normalizacion de codigos numericos de Excel y reporte de creados, omitidos y errores.

## Validaciones

- Backend: 91 pruebas aprobadas.
- Frontend: 25 pruebas aprobadas.
- ESLint, build y `git diff --check`: aprobados.
- Backend, frontend y PostgreSQL: `running` y `healthy`.
- Sitio publico: HTTP `200`; API: `{"status":"ready"}`.
- No se ejecuto `deploy.sh` ni `migrate`; PostgreSQL y Caddy no se reiniciaron.

## Respaldo y retorno

- Base: `/opt/sga_saas/predeploy-backups/sga_pre_v1.0.8_20260813_005515.dump`
- SHA-256: `948eb245049aa1ce35a373a9addf55fa5c0bfa4b3e7a28186538e5b9e80949b2`
- Copia de entorno: `/opt/sga_saas/predeploy-backups/env_pre_v1.0.8_20260813_010144`
- Copia Compose: `/opt/sga_saas/predeploy-backups/docker-compose.prod_pre_v1.0.8_20260813_010144.yml`
- Version de retorno: `4b65ce3f039a09fcc622ab7a30e110cd326a7476`.

## Integridad de datos

| Entidad | Antes | Despues |
| --- | ---: | ---: |
| Equipos | 85 | 85 |
| Hojas de vida | 47 | 47 |
| Empresas | 1 | 1 |

## Pendiente al continuar

1. Recargar la plataforma con `Ctrl + F5`.
2. Verificar exportacion sin falsos `SIN-INVENTARIO-`.
3. Probar busqueda, filtro y cabecera `SEDE`.
4. Realizar dos importaciones consecutivas.
5. Confirmar que duplicados se omiten y filas nuevas se crean.
6. Conservar respaldos e imagenes anteriores hasta completar estas pruebas.

## Cambios locales excluidos

No forman parte de `v1.0.8`: `backend/app/routers/usuarios.py`, `docs/REGISTRO_CAMBIOS_V1.0.6.md`, `output/` y `tmp/`.
