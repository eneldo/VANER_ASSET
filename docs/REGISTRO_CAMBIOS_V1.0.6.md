# Registro de cambios SGA SaaS v1.0.6

Fecha de liberacion: 12 de agosto de 2026

Zona horaria: America/Bogota

Estado: desplegado y confirmado como funcional por el usuario

## Identificacion de la version

- Version: `v1.0.6`
- Commit: `a9fa15668f66badbc12d97ce0e139828cf255820`
- Commit corto: `a9fa156`
- Mensaje: `feat(frontend): unificar menu lateral colapsable`
- Rama publicada: `main`
- Imagen de produccion: `vanstralhen/sga-frontend:a9fa15668f66badbc12d97ce0e139828cf255820`
- Dominio: `https://sgaholding.online`
- Directorio del VPS: `/opt/sga_saas`

## Objetivo funcional

Unificar el comportamiento del menu lateral administrativo para que Empresas, Sedes, Categorias y Tecnicos tengan el mismo boton hamburguesa y la misma respuesta de distribucion de espacio que el Dashboard General.

Al contraer el menu en escritorio, la barra lateral cambia de 270 px a 78 px y el contenido utiliza inmediatamente el espacio liberado hacia la izquierda. En moviles se conserva el comportamiento de apertura como panel superpuesto.

## Cambios implementados

- El control hamburguesa se centralizo en el componente compartido `Sidebar`.
- El estado contraido se conserva en `localStorage` con la clave `sga-admin-sidebar-collapsed`.
- Los iconos permanecen visibles al contraer el menu y las etiquetas siguen disponibles mediante titulos de ayuda.
- Dashboard y Auditoria usan el `AdminLayout` compartido.
- Automatizacion y SMTP Inteligente quedaron integrados dentro del mismo layout.
- Reportes PRO conserva su barra superior y menu especializados.
- Empresas y Sedes dejaron de usar un contenedor centrado con ancho maximo.
- Categorias y Tecnicos dejaron de usar un contenedor centrado con ancho maximo.
- El contenido de esos cuatro modulos ahora se expande hacia la izquierda al contraer el menu, igual que el Dashboard General.

## Archivos incluidos en el commit

- `frontend/src/components/Sidebar.jsx`
- `frontend/src/pages/DashboardAdmin.jsx`
- `frontend/src/pages/admin/AdminLayout.jsx`
- `frontend/src/pages/admin/AdminLayout.test.jsx`
- `frontend/src/pages/admin/AuditoriaPage.jsx`
- `frontend/src/pages/admin/AutomatizacionPage.jsx`
- `frontend/src/pages/admin/SMTPInteligentePage.jsx`
- `frontend/src/styles/admin.css`
- `frontend/src/styles/categorias-tecnicos-saas-pro.css`
- `frontend/src/styles/empresas-sedes-saas-pro.css`
- `frontend/src/styles/sidebar.css`

Resumen Git: 11 archivos, 306 inserciones y 50 eliminaciones.

## Validaciones previas

- `npm test`: 5 archivos de pruebas y 17 pruebas aprobadas.
- `npm run lint`: aprobado.
- `npm run build`: aprobado.
- Backend local: respuesta HTTP 200.
- Frontend local: respuesta HTTP 200.
- Auditoria de 26 rutas administrativas activas: 25 usan el `AdminLayout` compartido y Reportes usa su propio boton hamburguesa especializado.
- La prueba nueva valida Empresas, Categorias y Tecnicos, ademas de la contraccion y persistencia del estado.

## Publicacion y despliegue

La rama `main` y la etiqueta `v1.0.6` fueron publicadas en GitHub. La imagen inmutable del frontend se descargo en el VPS y se recreo exclusivamente el servicio `frontend` con `--no-deps`.

Resultados observados en produccion:

- Imagen anterior: `b2e72048630c4decf80d026c2dd3ae496d40efc2`.
- Respaldo del entorno: `/opt/sga_saas/.env.pre-v1.0.6-20260812_164521`.
- Contenedor: `sga_frontend`.
- Estado final: `running`.
- Salud final: `healthy`.
- La comprobacion HTTPS de `https://sgaholding.online/` fue satisfactoria.
- El usuario confirmo que la funcionalidad quedo operativa.

## Alcance controlado

El despliegue uso `docker compose up -d --no-deps --force-recreate frontend`. Por ello solo se reemplazo el contenedor del frontend. No se desplegaron ni se reiniciaron deliberadamente el backend, PostgreSQL, Caddy, migraciones o los demas servicios.

Los cambios locales ajenos a esta version permanecieron fuera del commit:

- `backend/app/routers/usuarios.py`
- `output/`
- `tmp/`

## Reversion operativa

En caso de necesitar volver a la version anterior, restaurar el valor de `IMAGE_TAG` a `b2e72048630c4decf80d026c2dd3ae496d40efc2` o recuperar el respaldo `.env.pre-v1.0.6-20260812_164521`. Luego descargar y recrear unicamente el frontend:

```bash
cd /opt/sga_saas
docker compose --env-file .env -f docker-compose.prod.yml pull frontend
docker compose --env-file .env -f docker-compose.prod.yml \\
  up -d --no-deps --force-recreate --wait --wait-timeout 120 frontend
```

## Revision funcional recomendada

Realizar una recarga completa del navegador y verificar el boton hamburguesa, la persistencia de su estado y la expansion horizontal del contenido en Dashboard General, Empresas, Sedes, Categorias, Tecnicos, Usuarios y Configuracion del sistema.
