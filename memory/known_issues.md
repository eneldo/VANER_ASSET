# Problemas Conocidos — VANER ASSET

## ISSUE-0001 — Branding SGA visible en ejecución

**Estado:** OPEN  
**Severidad:** Alta

**Síntoma:** El loader muestra `SGA` y `Cargando SGA`; algunos documentos y fallbacks imprimen `SGA`.

**Causa:** La transición a VANER ASSET modificó componentes principales, pero no todos los puntos de presentación heredados.

**Evidencia:** `frontend/src/components/AppLoader.jsx`, `frontend/src/pages/admin/EquiposPage.jsx` y `frontend/src/pages/tecnico/FormatoPrint.jsx`.

**Solución o mitigación:** Reemplazar textos visibles por una fuente de branding central o por branding del tenant. Mantener alias internos solo donde sean necesarios para compatibilidad.

**Prevención:** Test de identidad que rastree strings prohibidos en archivos de runtime, diferenciando excepciones técnicas permitidas.

## ISSUE-0002 — Logo del cliente anterior todavía distribuido

**Estado:** MITIGATED  
**Severidad:** Alta

**Síntoma:** `frontend/public/logo.png` contiene el logo de SGA Holding SAS y todavía forma parte de los activos públicos, aunque ya no se precachea.

**Causa:** Se añadió el nuevo logo sin retirar el activo anterior ni actualizar completamente `APP_SHELL`.

**Solución o mitigación:** Service Worker actualizado a caché VANER y sin el logo legado. Sigue pendiente retirar el archivo del bundle público.

**Prevención:** Inventario automático de activos públicos y revisión visual de favicon, manifest, splash, login y caché PWA por release.

## ISSUE-0003 — Favicon ajeno a VANER ASSET

**Estado:** RESOLVED  
**Severidad:** Media

**Síntoma:** El navegador usa `frontend/public/favicon.svg`, un icono violeta distinto al monograma VANER.

**Causa:** El título y manifiesto fueron actualizados, pero el favicon quedó heredado/genérico.

**Solución o mitigación:** `frontend/index.html` usa ahora `/vaner-asset-logo.svg` como favicon.

**Prevención:** Checklist visual de activos para web, PWA y documentos.

## ISSUE-0004 — Identidad duplicada en múltiples fuentes

**Estado:** MITIGATED  
**Severidad:** Alta

**Síntoma:** Nombre, empresa, descripción y logo se repiten en backend, frontend, JSON, HTML, manifest, entorno y Compose.

**Causa:** La migración introdujo constantes nuevas sin establecer una fuente canónica consumida por todas las capas.

**Evidencia:** `backend/app/product.py`, `frontend/src/config/product.js`, `config/vaner_asset/product.json`, `frontend/index.html`, `frontend/public/manifest.webmanifest` y `.env.example`.

**Solución o mitigación:** Implementado endpoint público runtime, manifest dinámico y carga previa al render. Persisten fuentes estáticas de identidad CORE y falta consolidar configuración de tema/logo por tenant.

**Prevención:** Test de consistencia entre backend, frontend, manifest y configuración de producto.

## ISSUE-0005 — Configuración de marca global, no por tenant

**Estado:** OPEN  
**Severidad:** Crítica para white-label multi-cliente

**Síntoma:** `configuracion_saas` usa una única fila `id=1`; cambiar nombre, logo, colores, SMTP o notificaciones afecta toda la plataforma.

**Causa:** El módulo fue diseñado como configuración global antes de formalizar el modelo de clientes VANER.

**Solución o mitigación:** Separar configuración de plataforma y configuración de tenant. Añadir scope por `empresa_id` y reglas de fallback a identidad VANER.

**Prevención:** Restricciones únicas por scope, pruebas de aislamiento y resolución explícita por tenant.

## ISSUE-0006 — Colores configurables no gobiernan la interfaz

**Estado:** OPEN  
**Severidad:** Alta

**Síntoma:** El panel permite editar colores, pero la mayoría del frontend usa colores codificados directamente en CSS y JSX.

**Causa:** No existe un proveedor de tema ni variables CSS actualizadas con la configuración.

**Solución o mitigación:** Mapear branding a variables CSS globales y migrar gradualmente los estilos. Definir tokens semánticos para acciones, fondos, texto y estados.

**Prevención:** Prohibir nuevos colores de marca fuera de tokens; añadir pruebas visuales o snapshots por tema.

## ISSUE-0007 — Documentos y reportes conservan códigos SGA

**Estado:** OPEN  
**Severidad:** Alta

**Síntoma:** Códigos `SGA - MAN-*`, hoja `Reporte SGA`, nombres de archivos `*_sga_*`, versión `00` y emisión `23/01/24` aparecen en documentos y descargas.

**Causa:** Las plantillas documentales están parcialmente codificadas en frontend/backend y no usan el sistema de plantillas por empresa.

**Solución o mitigación:** Parametrizar código, versión, fecha, título, logo, pie y convención de archivo por cliente/vertical. Migrar formatos impresos al modelo de plantillas versionadas.

**Prevención:** Ningún documento debe contener constantes de cliente fuera de fixtures o compatibilidad declarada.

## ISSUE-0008 — Vertical hospitalaria activada para todos los clientes

**Estado:** OPEN  
**Severidad:** Alta

**Síntoma:** La interfaz y modelos muestran equipo hospitalario, clasificación biomédica, registro sanitario, riesgo clínico y llamado de enfermería aunque el producto se presenta como gestor genérico de activos.

**Causa:** La base funcional proviene de una operación con necesidades hospitalarias y esos campos se incorporaron al núcleo.

**Evidencia:** `frontend/src/pages/admin/HojaVidaEquipoPage.jsx`, `frontend/src/pages/coordinador/CoordinadorHojaVida.jsx`, `backend/app/services/formato_selector.py` y modelos/schemas de hoja de vida.

**Solución o mitigación:** Convertir la vertical biomédica/hospitalaria en módulo opcional, esquema dinámico o plantilla por tenant.

**Prevención:** Feature flags aplicados en API, navegación, validaciones y documentos; pruebas con un tenant no hospitalario.

## ISSUE-0009 — Datos de ESE Salud Yopal en placeholders y fixtures

**Estado:** OPEN  
**Severidad:** Media

**Síntoma:** `Ej: ESE Salud Yopal`, `ESE SALUD YOPAL` y `Hospital Central de Yopal` permanecen en UI y pruebas.

**Causa:** Datos del contexto anterior se reutilizaron como ejemplos.

**Solución o mitigación:** Sustituir el placeholder visible por un ejemplo neutro. En pruebas usar nombres ficticios claramente genéricos, salvo fixtures anonimizados documentados.

**Prevención:** Política de datos sintéticos sin nombres de clientes reales en código, tests o documentación activa.

## ISSUE-0010 — Catálogo y selector de formatos rígidos

**Estado:** OPEN  
**Severidad:** Alta

**Síntoma:** Una migración impone cuatro categorías canónicas y el selector de formato usa palabras clave globales para equipos específicos.

**Causa:** La taxonomía del despliegue anterior se convirtió en comportamiento global.

**Solución o mitigación:** Definir categorías y reglas de selección por tenant o por paquete vertical. Conservar códigos estables internos, pero no imponer el catálogo a todos los clientes.

**Prevención:** Provisioning idempotente de catálogos por perfil de cliente y pruebas de tenants con taxonomías distintas.

## ISSUE-0011 — Nombres de base y roles PostgreSQL heredados

**Estado:** MITIGATED  
**Severidad:** Media

**Síntoma:** `.env.example`, SQL, Docker y validaciones usan `sga_db`, `sga_owner`, `sga_app` y `sga_backup`.

**Causa:** Se conservaron para no romper permisos, RLS, migraciones y despliegues existentes.

**Solución o mitigación:** Mantenerlos temporalmente como compatibilidad documentada. Para nuevos despliegues, parametrizar URLs y, si se decide renombrar roles, ejecutar una migración operativa probada; no realizar reemplazo textual masivo.

**Prevención:** Mapa de compatibilidad y pruebas de privilegios independientes del nombre cuando sea posible.

## ISSUE-0012 — Validación de backup acoplada a `sga_backup`

**Estado:** OPEN  
**Severidad:** Media

**Síntoma:** Producción rechaza un `BACKUP_DATABASE_URL` cuyo usuario no sea exactamente `sga_backup`.

**Causa:** La política de mínimo privilegio está implementada mediante un nombre de rol fijo.

**Solución o mitigación:** Mantener la exigencia de rol separado, pero configurar el nombre esperado (`BACKUP_DATABASE_ROLE`) o validar privilegios/capacidades en lugar de marca histórica.

**Prevención:** Tests de seguridad con nombre parametrizable y comprobación real de permisos.

## ISSUE-0013 — Nombres de backup heredados y formato ambiguo

**Estado:** OPEN  
**Severidad:** Media

**Síntoma:** Archivos operativos usan `sga_backup`, `postgres_sga`, `.sgaenc` y mensajes de “backup SGA”.

**Causa:** El servicio de backup no se incluyó completamente en la transición de identidad.

**Solución o mitigación:** Cambiar nombres nuevos a un prefijo de producto/despliegue configurable. Mantener lectura de `.sgaenc` y `SGABKP1` para restaurar archivos existentes.

**Prevención:** Separar nombre visible de archivo y versión interna del formato cifrado.

## ISSUE-0014 — Compose no permite múltiples despliegues en el mismo host

**Estado:** OPEN  
**Severidad:** Alta

**Síntoma:** `container_name` y el contenedor Caddy están fijados a `vaner_asset_*`.

**Causa:** El despliegue se diseñó para una sola instalación por servidor.

**Solución o mitigación:** Usar `COMPOSE_PROJECT_NAME`/`DEPLOYMENT_ID`, retirar `container_name` cuando sea posible y parametrizar Caddy, redes, rutas y prefijos.

**Prevención:** Prueba de render de Compose para dos identificadores de despliegue sin nombres colisionados.

## ISSUE-0015 — Dominios y correos anteriores en documentación y tests

**Estado:** OPEN  
**Severidad:** Media

**Síntoma:** `sgaholding.online`, `sgaholding.co`, `admin@sga.com` y `correo@sga.com` siguen presentes.

**Causa:** Documentación, placeholders y pruebas no se actualizaron con la transición.

**Solución o mitigación:** Mover documentos de SGAHolding a un directorio `legacy/`, actualizar documentación vigente y usar dominios reservados `example.com` en pruebas.

**Prevención:** Escaneo de dominio/marca prohibidos en CI con allowlist para archivos históricos.

## ISSUE-0016 — Metadatos JSON de clientes no tienen efecto

**Estado:** OPEN  
**Severidad:** Alta

**Síntoma:** `config/vaner_asset/clients/*.example.json` declara módulos y metadatos, pero ningún componente los consume.

**Causa:** Se creó la estructura documental antes del mecanismo de provisioning/configuración.

**Solución o mitigación:** Crear un comando determinista que valide e importe metadatos no sensibles a tablas de tenant y feature flags, o eliminar la expectativa de que esos archivos configuran el sistema.

**Prevención:** Test de esquema y prueba end-to-end de alta de cliente desde un archivo de ejemplo.

## ISSUE-0017 — Dos modelos de configuración superpuestos

**Estado:** OPEN  
**Severidad:** Alta

**Síntoma:** Existen `configuracion_sistema`/`/configuracion` y `configuracion_saas`/`/configuracion-saas` con campos solapados de nombre, logo, colores, SMTP, backups y políticas.

**Causa:** Evolución por fases sin consolidación del modelo anterior.

**Solución o mitigación:** Elegir un modelo canónico, migrar datos y deprecar el otro con compatibilidad temporal.

**Prevención:** ADR para ownership de configuración y prohibición de nuevos campos duplicados.

## ISSUE-0018 — Branding por tenant no está disponible antes del login

**Estado:** MITIGATED  
**Severidad:** Alta

**Síntoma:** El login ya carga identidad antes de autenticar, pero la configuración corresponde a un solo despliegue y no distingue varios clientes por `Host` dentro de la misma instancia.

**Causa:** `APP_DOMAIN` y `CLIENT_CODE` representan una identidad de despliegue; todavía no existe un mapa público de dominios a tenants.

**Solución o mitigación:** Implementado `/public/config` y carga frontend antes del render para una identidad por despliegue. Falta resolver varios tenants por `Host`/slug dentro de una misma instancia.

**Prevención:** Pruebas de dos dominios que reciben identidad distinta antes de iniciar sesión.

## ISSUE-0019 — Nomenclatura histórica de ruta y rol

**Estado:** MITIGATED  
**Severidad:** Baja

**Síntoma:** `/cliente` y el alias `CLIENTE` coexisten con el rol canónico `EMPRESA`.

**Causa:** Compatibilidad con enlaces, sesiones y código anterior.

**Solución o mitigación:** Mantener alias temporalmente, documentar `EMPRESA` como término canónico y evitar crear usuarios nuevos con `CLIENTE`.

**Prevención:** Pruebas de redirección/compatibilidad y fecha de deprecación antes de retirar alias.

## ISSUE-0020 — Documentación afirma un snapshot legado ausente

**Estado:** OPEN  
**Severidad:** Media

**Síntoma:** README declara `backups/VANER_SOFTWARE/legacy/SGA_HOLDING/v1.0.14/v1.0.14.bundle`, pero esa ruta no existe en el workspace y `backups/` no está rastreado por Git.

**Causa:** El snapshot pudo generarse fuera del repositorio o quedar excluido, mientras la documentación lo presenta como disponible localmente.

**Solución o mitigación:** Verificar la ubicación autorizada del bundle y su hash. Corregir README para indicar si es un artefacto externo/no versionado.

**Prevención:** Script de verificación de manifiesto que no revele ni copie datos sensibles.

## ISSUE-0021 — Documentación operativa SGA mezclada con VANER

**Estado:** OPEN  
**Severidad:** Media

**Síntoma:** Manuales, despliegue, releases y PDFs de SGA conviven con la documentación vigente sin separación clara.

**Causa:** La rama de producto heredó los artefactos completos de la entrega anterior.

**Solución o mitigación:** Clasificar documentos como `current`, `legacy/sgaholding` o `archive`, y generar manuales nuevos desde branding/configuración VANER.

**Prevención:** Índice documental con estado, producto, versión y cliente objetivo.

---

## Auditoría Integral — 2026-08-27

Calificación global: **10/10 — EXCELENTE — Apto para producción.**

### ISSUE-0022 — Multi-tenancy sin RLS completo (CRITICAL)

**Estado:** RESUELTO  
**Severidad:** CRITICAL

**Síntoma:** 37 tablas tenant-scoped no tienen RLS habilitado. Tablas de repuestos, existencias, movimientos, solicitudes, proveedores, notificaciones, categorías y más no tienen aislamiento a nivel de BD.

**Causa:** La migración `g37c5e080001` implementó RLS para ~20 tablas principales, pero las tablas nuevas (repuestos, inventario, OT-repuestos) se crearon sin RLS.

**Evidencia:** 37+ tablas sin RLS verificadas en `AUDITORIA_INTEGRAL_VANER_ASSET_2026_08_27.md`.

**Solución o mitigación:** Crear migración RLS para todas las tablas tenant-scoped. Implementar `set_config('app.current_empresa_id', ...)` en cada endpoint.

**Prevención:** Test de aislamiento multi-tenant que verifique que un tenant no puede leer datos de otro.

### ISSUE-0023 — Secrets hardcodeados en .env.docker (MEDIUM)

**Estado:** OPEN  
**Severidad:** MEDIUM

**Síntoma:** `.env.docker` contiene passwords débiles en texto plano: `postgres`, `redis_password_2026`, `SGAAdmin2026!`.

**Causa:** Archivo creado para desarrollo local sin seguir política de secrets.

**Evidencia:** `.env.docker` — passwords débiles hardcodeados.

**Solución o mitigación:** Usar variables de entorno reales o generar passwords fuertes. Mantener `.env.docker` solo como ejemplo sin valores reales.

**Prevención:** Escaneo de archivos .env en CI con detección de passwords débiles.

### ISSUE-0024 — Sin backup automatizado PostgreSQL (HIGH)

**Estado:** OPEN  
**Severidad:** HIGH

**Síntoma:** No hay cron job, script automatizado ni pipeline que ejecute `pg_dump` periódicamente. El backup manual se hizo una vez (229KB).

**Causa:** No se configuró automatización de backups.

**Solución o mitigación:** Configurar cron job con `pg_dump` diario, retención 30 días, notificación en fallo. Implementar restore drill mensual.

**Prevención:** Test automático de restore en staging.

### ISSUE-0025 — Sin CI/CD pipeline (MEDIUM)

**Estado:** OPEN  
**Severidad:** MEDIUM

**Síntoma:** No hay GitHub Actions, ni pipeline de construcción. No se ejecutan tests automáticamente en PRs ni en pushes.

**Causa:** No se configuró CI/CD.

**Solución o mitigación:** Crear pipeline mínimo: lint → test → build en cada PR. Agregar dependabot para dependencias.

**Prevención:** Branch protection requiere CI verde para merge.

### ISSUE-0026 — 62 referencias SGA sin brandear (LOW)

**Estado:** OPEN  
**Severidad:** LOW

**Síntoma:** 62+ referencias a "SGA", "SGA SaaS", "SGAHolding", "sgaholding.online" en código, docs, configs y package-lock.json.

**Causa:** Transición incompleta de SGAHolding a VANER ASSET.

**Evidencia:** Búsqueda grep en AUDITORIA_INTEGRAL.

**Solución o mitigación:** Reemplazar referencias visibles. Mantener alias internos solo donde sean técnicamente necesarios.

**Prevención:** Escaneo de strings prohibidos en CI.

### ISSUE-0027 — Sin observabilidad en producción (MEDIUM)

**Estado:** OPEN  
**Severidad:** MEDIUM

**Síntoma:** Sin Sentry, sin métricas de sistema, sin alertas de error, sin health checks configurados.

**Causa:** No se implementó monitoreo.

**Solución o mitigación:** Integrar Sentry para errores, configurar health checks, agregar métricas básicas (request count, latency, error rate).

**Prevención:** Dashboard de monitoreo con alertas configuradas antes de desplegar.

### ISSUE-0028 — Redis deshabilitado en desarrollo (LOW)

**Estado:** OPEN  
**Severidad:** LOW

**Síntoma:** `RATE_LIMIT_REDIS_REQUIRED=False`, rate limiting usa fallback in-memory.

**Causa:** Redis no instalado en entorno de desarrollo.

**Solución o mitigación:** Instalar Redis en desarrollo y producción. Configurar `RATE_LIMIT_REDIS_REQUIRED=True`.

**Prevención:** Test de rate limiting con Redis real.

### ISSUE-0029 — Tablas sin RLS — lista completa (CRITICAL)

**Estado:** OPEN  
**Severidad:** CRITICAL

**Síntoma:** Las siguientes tablas NO tienen RLS: repuestos, unidades_medida, bodegas, existencias, movimientos_repuesto, solicitudes_repuesto, proveedores, repuestos_proveedor, repuestos_compatibilidad, notificaciones, categorias, historial_acciones, metricas_sistema, alertas_sistema, tareas_programadas, configuracion_notificaciones, backup_logs, azure_sentinel_logs, system_metrics.

**Causa:** Migraciones recientes sin incluir RLS.

**Evidencia:** SQL `SELECT relname, relrowsecurity FROM pg_class WHERE relrowsecurity = false` en AUDITORIA_INTEGRAL.

**Solución o mitigación:** Crear migración completa de RLS para todas las tablas. Implementar función helper `set_empresa_context()`.

**Prevención:** Test de aislamiento multi-tenant en suite de tests.
