# Contexto del Proyecto — VANER ASSET

## Auditoría base

- **Fecha:** 2026-08-25.
- **Rama analizada:** `product/vaner-asset`.
- **Commit base:** `61ab76a` (`feat(product): iniciar VANER ASSET`).
- **Origen inmediato:** entrega congelada de SGAHolding `v1.0.14`, commit `d9b5891`.
- **Alcance:** código, configuración, infraestructura, documentación, activos, pruebas, reportes, datos iniciales y rastros de branding del cliente anterior.
- **Restricción aplicada:** no se modificó funcionalidad; esta auditoría solo actualiza memoria y documentación del agente.

## Objetivo

VANER ASSET es la línea de producto SaaS multi-tenant de VANER SOFTWARE para inventarios, activos, hojas de vida, mantenimiento, órdenes de trabajo, repuestos, técnicos, reportes, analítica y administración.

La intención declarada es mantener una sola base de código y representar cada cliente como tenant, con aislamiento mediante `empresa_id`, controles de autorización y PostgreSQL RLS. Las diferencias de marca, dominio, módulos, documentos e integraciones deben resolverse por configuración, no mediante copias del código.

## Estado actual

La transición de SGAHolding a VANER ASSET es **parcial**:

- La identidad principal ya aparece como `VANER SOFTWARE` / `VANER ASSET` en README, título HTML, manifiesto PWA, componentes principales, Docker, Caddy y módulos centrales `backend/app/product.py` y `frontend/src/config/product.js`.
- Persisten referencias visibles y técnicas a `SGA`, `SGA SaaS`, `SGAHolding`, el dominio anterior y una vertical hospitalaria concreta.
- El commit de transición modificó 53 archivos, pero el repositorio heredado contiene cientos de archivos y quedaron numerosos valores fuera de esa primera pasada.
- Existen mecanismos parciales de personalización, pero no una resolución completa de configuración por tenant antes del login ni una única fuente de verdad de branding.

## Fase 3 — separación CORE y cliente

Implementada el 2026-08-25 para despliegues configurados por entorno:

- El CORE conserva `VANER SOFTWARE`, `VANER ASSET`, descripción, módulos y activos base.
- `APP_NAME`, `CLIENT_CODE`, `CLIENT_NAME` y `APP_DOMAIN` se leen desde `.env`.
- Backend valida la identidad de producción y deriva `FRONTEND_URL` y `BACKEND_CORS_ORIGINS` desde `APP_DOMAIN` cuando quedan vacíos.
- `GET /public/config` expone únicamente metadatos no sensibles.
- `GET /public/manifest.webmanifest` genera el manifest del despliegue.
- El frontend consulta `/api/public/config` antes del primer render; la imagen compilada no contiene el nombre del cliente.
- Login y sidebar muestran `CLIENT_NAME` con fallback a `VANER SOFTWARE`.
- Caddy usa `APP_DOMAIN`; `deploy.sh` mantiene `DOMAIN` solo como alias temporal.

Esta fase configura una identidad por despliegue. La resolución de marcas distintas por `Host` dentro de una sola instancia multi-tenant continúa pendiente.

## Arquitectura

### Frontend

- React 19, Vite 8 y React Router.
- PWA con `manifest.webmanifest`, Service Worker, Cache Storage, IndexedDB y sincronización offline.
- Axios y `fetch` consumen normalmente `VITE_API_URL`, con `/api` como valor recomendado de mismo origen.
- Portales por rol: `ADMIN`, `COORDINADOR`, `EMPRESA` y `TECNICO`.
- La ruta y nomenclatura histórica `/cliente` continúa para el portal de empresa/director.
- La identidad visible se obtiene principalmente de `frontend/src/config/product.js`, pero el HTML, el manifiesto, algunos loaders, documentos y estilos mantienen valores independientes.

### Backend

- FastAPI, Pydantic 2, SQLAlchemy 2 síncrono y Alembic.
- Routers modulares para autenticación, empresas, sedes, categorías, equipos, hojas de vida, mantenimientos, evidencias, técnicos, usuarios, reportes, plantillas, facturación, auditoría, backups, recuperación, SMTP, automatización, scheduler, BI y portales por rol.
- Configuración de proceso mediante `backend/app/config.py` y variables de entorno.
- Scheduler interno para mantenimiento, backups, monitorización, SMTP, WhatsApp y limpieza.
- Almacenamiento local privado para evidencias y reportes; logos corporativos expuestos en `/uploads/logos`.
- Soporte opcional para backups remotos S3/R2.

### Base de datos

- PostgreSQL 16.
- Modelos multi-tenant con `empresa_id` en entidades operativas.
- RLS habilitado por migraciones para aislamiento adicional.
- Separación de credenciales para migración, aplicación y backup.
- Redis se utiliza para rate limiting distribuido y operación auxiliar.
- Las migraciones conservan nombres históricos de tablas y roles para compatibilidad.

### Infraestructura

- `docker-compose.yml` para build local y `docker-compose.prod.yml` para imágenes publicadas.
- Servicios: PostgreSQL, Redis, migración Alembic, backend y frontend.
- Caddy publica frontend, `/api/*` y health checks por un dominio configurado con `DOMAIN`.
- Contenedores actuales: `vaner_asset_postgres`, `vaner_asset_redis`, `vaner_asset_backend`, `vaner_asset_frontend` y `vaner_asset_caddy`.
- Red interna actual: `vaner_asset_internal`; red externa compartida: `caddy_net`.
- Directorio de despliegue por defecto: `/opt/vaner_asset`.

## Módulos funcionales existentes

- Dashboard administrativo, ejecutivo, coordinador y técnico.
- Empresas, sedes, categorías e inventario de equipos.
- Hoja de vida técnica y documental.
- Mantenimiento preventivo/correctivo y ejecución de OT.
- Evidencias antes/durante/después/soporte.
- Repuestos e incidencias de OT.
- Técnicos, usuarios, permisos y roles.
- Solicitudes correctivas del cliente.
- Reportes, reportes publicados y plantillas por empresa.
- Facturación, auditoría, seguridad, notificaciones y recuperación de contraseña.
- Backups, restore, monitor VPS, logs, DevOps, SMTP, automatización y scheduler.
- Operación offline para el portal técnico.

## Identidad actual de producto

La identidad deseada está definida de forma duplicada en:

- `backend/app/product.py`.
- `frontend/src/config/product.js`.
- `config/vaner_asset/product.json`.
- `frontend/index.html`.
- `frontend/public/manifest.webmanifest`.
- `.env.example`, Docker Compose, Caddy y scripts de despliegue.

Valores actuales:

- Empresa: `VANER SOFTWARE`.
- Producto: `VANER ASSET`.
- Descripción: `Plataforma para la gestión de inventarios, activos y mantenimiento.`
- Monograma: `VA`.
- Logo nuevo: `frontend/public/vaner-asset-logo.svg`.

El logo nuevo utiliza principalmente `#0f172a`, `#153e75`, `#0f766e`, `#f3ff63`, `#34d399` y blanco.

## Hallazgos específicos del cliente anterior

### 1. Nombre de empresa y producto anterior

Persisten referencias a `SGAHolding`, `SGA Holding SAS`, `SGA SaaS`, `SGA SaaS PRO`, prefijos técnicos `sga_` y clases CSS `sga-*`.

Las referencias se distribuyen entre backend, frontend, SQL, pruebas, documentación y artefactos generados. Muchas apariciones en comentarios o clases CSS no son visibles, pero confirman que la implementación sigue estructuralmente derivada del producto anterior.

### 2. Logos, favicon y activos

- `frontend/public/logo.png` contiene el logo completo de **SGA HOLDING SAS**. El Service Worker todavía lo incluye en `APP_SHELL`, por lo que sigue siendo distribuido y precacheado.
- `frontend/public/vaner-asset-logo.svg` contiene el monograma correcto de VANER ASSET y ya se usa en login y manifiesto.
- `frontend/public/favicon.svg` no corresponde a VANER ASSET; es un recurso violeta genérico/heredado distinto del logo nuevo.
- `frontend/src/components/AppLoader.jsx` muestra `SGA` y el texto `Cargando SGA` durante la carga.
- `frontend/src/pages/admin/EquiposPage.jsx` usa `SGA` como fallback cuando una empresa no tiene logo.
- `frontend/src/pages/tecnico/FormatoPrint.jsx` imprime `SGA` en el encabezado documental.

### 3. Colores y tema

Hay tres grupos de colores sin una jerarquía única:

- Logo VANER: azul marino, teal, lima y verde.
- Configuración global SaaS: primario `#2563eb`, secundario `#0f172a`, acento `#22c55e`.
- Plantillas de reporte: primario por defecto `#1E3A8A`.

El frontend contiene cientos de colores hexadecimales y gradientes codificados directamente en CSS/JSX. Los campos de color se pueden editar, pero no se aplican globalmente mediante variables CSS. La paleta azul/cian dominante parece heredada de SGA y no existe una prueba de que todos los módulos sigan el sistema visual de VANER.

### 4. Dominios, URLs, correos y CORS

Valores heredados encontrados:

- Dominio de producción anterior: `https://sgaholding.online`.
- Correo de prueba anterior: `tecnico.prueba@sgaholding.co`.
- Placeholders visibles: `admin@sga.com` y `correo@sga.com`.
- Placeholder nuevo pero aún codificado: `admin@vanerasset.com`; no está ligado a `DOMAIN` ni a una configuración de soporte.

Estado actual:

- `.env.example` usa `asset.example.com`, `FRONTEND_URL=https://asset.example.com` y `BACKEND_CORS_ORIGINS=https://asset.example.com`.
- Caddy usa `DOMAIN` y no fija el dominio en el proxy.
- En producción, el backend exige HTTPS, cookies seguras y CORS explícito; rechaza `*`.
- Documentación y pruebas todavía usan el dominio de SGAHolding y pueden inducir despliegues incorrectos.
- La URL de recuperación se construye con `FRONTEND_URL`, pero actualmente no resuelve dominio por tenant.

### 5. Base de datos y roles heredados

La configuración de ejemplo conserva:

- Base: `sga_db`.
- Propietario/migraciones: `sga_owner`.
- Aplicación: `sga_app`.
- Backups: `sga_backup`.
- Documentación histórica menciona también `sga_jobs` y `sga_restore_verify`.

Los URLs se configuran por entorno, pero los roles `sga_app` y `sga_backup` están codificados en scripts SQL, inicialización Docker, migraciones, pruebas y validaciones de seguridad. `backend/app/config.py` exige específicamente que `BACKUP_DATABASE_URL` use `sga_backup`.

Estos nombres no son branding visible, pero sí acoplamiento técnico heredado. No deben reemplazarse con una búsqueda global: están ligados a permisos, RLS, migraciones y compatibilidad operativa.

### 6. Usuarios iniciales

- No hay un usuario, contraseña o empresa inicial fija en código de producción.
- `backend/scripts/create_initial_admin.py` crea el primer administrador con nombre, username y correo recibidos por argumentos, y contraseña interactiva.
- Existe un endpoint bootstrap oculto protegido por `BOOTSTRAP_ADMIN_TOKEN`; debe permanecer deshabilitado salvo alta controlada.
- Correos de SGAHolding aparecen únicamente en pruebas y placeholders.

### 7. Rutas y nomenclatura de roles

- El backend conserva `/cliente` y el frontend `/cliente/*` para el portal del tenant.
- `CLIENTE` se admite como alias histórico de `EMPRESA`; el rol nuevo recomendado es `EMPRESA`.
- Persisten etiquetas como `PRO`, `SaaS PRO`, `Enterprise` y nombres de archivos/fases. No identifican directamente al cliente, pero mezclan producto, versión y capacidad funcional.
- Las rutas API no deben variar por cliente; cualquier cambio debe mantener alias o migración compatible.

### 8. Reportes, documentos y nombres de archivo

Valores visibles heredados:

- Hoja Excel: `Reporte SGA`.
- Exportación de inventario: `inventario_equipos_sga_<fecha>.xlsx`.
- Auditoría: `auditoria_sga_pro.csv`.
- Backups: `sga_backup_<fecha>.sql`, `sga_backup_<fecha>.zip`, `postgres_sga_<fecha>.sql`, fallback `backup_sga.zip`.
- Extensión de backup cifrado: `.sgaenc`.
- Firma de formato cifrado: `SGABKP1`.
- Formatos de mantenimiento: códigos `SGA - MAN -019`, `SGA - MAN -CCTV`, `SGA - MAN -REF`, `SGA - MAN -BOM`, `SGA - MAN -ELEC`, `SGA - MAN -LENF`, `SGA - MAN -ASC` y `SGA - MAN -IND`.
- Versión documental fija `00` y fecha de emisión fija `23/01/24`.
- Hoja de vida titulada `HOJA DE VIDA EQUIPO HOSPITALARIO`.

Capacidad ya existente:

- `plantillas_reporte` permite configuración global o por `empresa_id` de título, color primario, pie de página, logo, evidencias, firmas y costos.
- Los reportes publicados pueden usar el logo de la empresa.
- Esta capacidad no cubre todos los documentos HTML/impresos ni los nombres de archivo heredados.

`SGABKP1` debe tratarse como identificador de formato/versionado y mantenerse para poder restaurar backups existentes; no es una opción de branding por cliente.

### 9. Vertical hospitalaria heredada

Se encontraron datos y lógica que parecen provenir de la operación anterior, no de un núcleo genérico de gestión de activos:

- Placeholder visible `Ej: ESE Salud Yopal` en empresas.
- Fixtures `ESE SALUD YOPAL`, `ESE Salud Yopal`, `Hospital Central` y `Hospital Central de Yopal`.
- Textos `Equipos biomédicos`, `Tecnología clínica`, `Clasificación biomédica` y clases de riesgo I/IIA/IIB/III.
- Campos de registro sanitario, calibración y clasificación biomédica en hoja de vida.
- Plantilla y selector de `LLAMADO_ENFERMERIA` con términos `ENFERMERIA`, `PULSADOR` y `TIMBRE HOSPITALARIO`.
- Título fijo de hoja de vida de equipo hospitalario.

Parte de estos campos puede ser una capacidad válida del producto, pero debe convertirse en un **módulo vertical opcional** o en esquemas/plantillas configurables. No debería presentarse a todos los clientes de VANER ASSET por defecto.

### 10. Categorías y formatos predefinidos

La migración `c93e1a640001` impone cuatro categorías canónicas globales:

- Equipos Industriales.
- Aires Acondicionados.
- Cámaras de Seguridad.
- Sistemas de Protección Contra Incendios.

El frontend y el backend seleccionan formatos mediante reglas y palabras clave fijas para ascensores, plantas eléctricas, redes contra incendio, CCTV, refrigeración, bombas, tableros, llamado de enfermería e industrial general.

Esto es una decisión de catálogo del cliente/vertical y no una configuración multi-tenant real. Los tenants no pueden definir libremente su taxonomía si los códigos canónicos y selectores permanecen rígidos.

### 11. Docker y despliegue

Los nombres SGA de contenedores y red ya fueron cambiados a VANER ASSET. Sin embargo:

- `container_name` está fijado, por lo que dos clientes no pueden desplegar el mismo Compose en un mismo host sin colisión.
- `vaner_asset_caddy`, `/opt/vaner_asset`, `vaner_asset_internal` y el prefijo S3 por defecto son globales de producto, no de tenant/despliegue.
- `caddy_net` es una red externa compartida.
- Las imágenes por defecto usan el namespace `vanstralhen/vaner-asset-*`; las variables permiten sobrescribirlo, pero el valor sigue asociado al publicador actual.
- Los volúmenes reciben scope del proyecto Compose, pero los `container_name` fijos anulan parte de la flexibilidad multi-despliegue.

Para instalaciones separadas por cliente se requiere un identificador de despliegue estable y único, aunque la aplicación siga siendo multi-tenant.

### 12. Documentación y artefactos históricos

- Quince documentos conservan referencias a SGA/SGAHolding.
- `docs/MANUAL_USUARIO.md` y `docs/DESPLIEGUE_PRODUCCION.md` describen todavía `sgaholding.online` y rutas de `/opt/sga_saas`.
- `output/pdf/` contiene manuales y reportes con nombres SGA.
- `output/templates/Plantilla_Inventario_SGA_Corregida.xlsx` conserva el nombre anterior.
- Los artefactos históricos deben archivarse y etiquetarse como legado, no mezclarse con documentación operativa vigente de VANER ASSET.
- README declara un bundle legado en `backups/VANER_SOFTWARE/legacy/SGA_HOLDING/v1.0.14/`, pero esa ruta no existe en el workspace actual y `backups/` no contiene archivos rastreados por Git. Sí existen la etiqueta `v1.0.14` y la rama remota de soporte.

## Configuración existente reutilizable

### Configuración global de plataforma

`configuracion_saas` permite nombre de plataforma, logo, colores, SMTP, backups, políticas de evidencias, mantenimiento y notificaciones.

Limitación: es una sola fila global `id=1`, no una configuración por tenant.

### Configuración de empresa

`empresas` permite nombre, NIT, teléfono, dirección, correo, estado y `logo_url`.

Limitaciones:

- El logo de empresa se ingresa como URL manual; no existe un flujo de carga equivalente al logo global.
- No hay colores, dominio, favicon, contactos de soporte, textos, locale, zona horaria ni feature flags por empresa.

### Plantillas de reporte

`plantillas_reporte` ya soporta scope global o por empresa y constituye la mejor base existente para documentos white-label.

### Metadatos JSON de clientes

`config/vaner_asset/clients/*.example.json` define id, nombre, slug, estado y módulos habilitados, pero actualmente **ningún código de ejecución consume estos archivos**. Son documentación, no configuración efectiva.

## Propuesta: qué convertir en configuración por cliente

### A. Identidad y branding del tenant

- `display_name`, `legal_name`, `slug` e identificador estable.
- Logo principal, logo horizontal, logo para documentos, favicon e iconos PWA.
- Colores primario, secundario, acento, fondos, texto y estados.
- Tipografía opcional y variables CSS derivadas.
- Nombre corto/monograma.
- Texto de login, subtítulo, pie de página y copyright.
- Correos, teléfonos, URL y textos de soporte.
- Dominio o dominios autorizados por tenant.

### B. Configuración funcional

- Módulos habilitados y permisos de navegación.
- Terminología: cliente/empresa/director/coordinador, activo/equipo, OT/solicitud.
- Categorías y taxonomías propias.
- Formatos de mantenimiento y reglas de selección.
- Campos de hoja de vida por vertical.
- Estados, criticidades, tipos de mantenimiento y evidencias requeridas.
- Módulos verticales: biomédico, hospitalario, industrial, CCTV, HVAC, incendios, ascensores, etc.

### C. Documentos y reportes

- Códigos documentales, versión, fecha de emisión y responsables.
- Títulos de hoja de vida e informes.
- Plantillas por tipo de equipo/OT.
- Logo, colores, pie, encabezado y datos legales.
- Convenciones de nombres de archivos exportados.
- Locale, zona horaria, moneda y formatos de fecha/número.

### D. Comunicación e integraciones

- `from_name`, `from_email`, reply-to y plantillas de correo.
- SMTP por tenant o política explícita de SMTP compartido.
- WhatsApp y otros canales por tenant.
- URLs de callback/webhook.
- Destinatarios de copia y reglas de notificación.

### E. Configuración de despliegue por instalación

Debe permanecer fuera de la base y fuera de Git:

- `DOMAIN`, `FRONTEND_URL`, `BACKEND_CORS_ORIGINS`.
- `COMPOSE_PROJECT_NAME` o `DEPLOYMENT_ID`.
- Nombres/prefijos de contenedores, redes y volúmenes cuando sea necesario.
- URLs y nombres de base de datos.
- Usuarios PostgreSQL y secretos.
- Redis, cookies y secretos JWT/cifrado.
- Rutas de uploads/backups/exports.
- Bucket y prefijo S3.
- Imágenes, registro y tag inmutable.

### F. Compatibilidad técnica que no debe ser branding por cliente

- Nombres de tablas y revisiones Alembic.
- Rutas API públicas.
- Identificador de formato cifrado `SGABKP1` mientras existan backups compatibles.
- Alias de rol/ruta necesarios para compatibilidad.

Estos elementos deben versionarse o migrarse de forma explícita, no personalizarse por tenant.

## Diseño recomendado de configuración

1. Mantener una identidad de producto por defecto en una única fuente versionada.
2. Crear configuración pública de branding por tenant, resuelta por `Host`, slug o contexto autenticado.
3. Exponer un endpoint público mínimo de branding para que login, favicon y PWA se configuren antes de autenticar.
4. Aplicar colores mediante variables CSS (`--brand-primary`, `--brand-secondary`, etc.) antes del primer render.
5. Separar `platform_settings` de `tenant_settings`; la fila global actual no debe representar a todos los clientes.
6. Convertir los JSON de `config/vaner_asset/clients/` en entrada real de un comando determinista de provisioning, sin secretos.
7. Validar feature flags tanto en frontend como en backend; ocultar un menú no equivale a deshabilitar un módulo.
8. Migrar documentos fijos a plantillas versionadas por cliente/vertical.
9. Mantener un mapa explícito de compatibilidad para nombres `sga_*` que no puedan cambiarse inmediatamente.

## Seguridad

Fortalezas observadas:

- JWT con refresh tokens y cookies configurables.
- CORS estricto en producción.
- Roles de base separados y RLS.
- Rate limiting con Redis.
- Validaciones de secretos y HTTPS en producción.
- Evidencias privadas con autorización y URLs firmadas.
- Cifrado de secretos de configuración y backups.
- Bootstrap inicial controlado y creación interactiva de administrador.

Riesgos vinculados a la migración de cliente:

- Una configuración global compartida puede filtrar branding o integraciones entre tenants.
- Dominios/documentación obsoletos pueden provocar despliegues o pruebas contra el cliente anterior.
- Backups y archivos con nombres SGA pueden confundirse en operación y soporte.
- Los JSON de cliente no contienen secretos, pero tampoco son aplicados por el sistema.

## Prioridad recomendada

1. Eliminar branding visible de SGA en runtime sin romper compatibilidad.
2. Crear una única fuente de identidad y branding público.
3. Separar configuración global de configuración por tenant.
4. Parametrizar documentos, códigos, categorías y vertical hospitalaria.
5. Hacer multi-instancia el Compose mediante `COMPOSE_PROJECT_NAME`/`DEPLOYMENT_ID`.
6. Actualizar documentación, pruebas y artefactos operativos.
7. Planificar la migración controlada de nombres técnicos `sga_*` solo si aporta valor operativo.

## Riesgos conocidos

Consultar `memory/known_issues.md` para el registro priorizado y acciones de mitigación.
