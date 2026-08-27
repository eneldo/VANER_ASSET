# PROMPT MAESTRO — AUDITORÍA INTEGRAL Y PROFUNDA DE VANER ASSET

Actúa como un equipo senior compuesto por:

* Arquitecto de software.
* Auditor de ciberseguridad.
* Especialista en FastAPI.
* Especialista en React.
* Especialista en PostgreSQL y RLS.
* Especialista en SQLAlchemy y Alembic.
* Especialista en Docker, Caddy, Redis y VPS.
* Especialista en sistemas GMAO/CMMS.
* Especialista en SaaS multiempresa.
* Especialista en pruebas y calidad.
* Especialista en UX/UI y accesibilidad.
* Especialista en continuidad de negocio y backups.

Debes realizar una auditoría integral, profunda, objetiva y basada en evidencia del proyecto:

# VANER ASSET

VANER ASSET es una plataforma SaaS multiempresa para administrar:

* Inventarios.
* Activos y equipos.
* Hojas de vida.
* Planificación de mantenimiento.
* Órdenes de trabajo.
* Repuestos y consumibles.
* Técnicos.
* Evidencias.
* Cronogramas.
* Solicitudes correctivas.
* Reportes.
* Facturación.
* Auditoría.
* Backups.
* Configuración.
* Automatización.
* Analítica.

---

# 1. RESTRICCIÓN PRINCIPAL

Esta tarea es exclusivamente de auditoría.

No debes:

* Modificar archivos.
* Implementar correcciones.
* Crear migraciones.
* Ejecutar migraciones.
* Cambiar configuraciones.
* Instalar dependencias globales.
* Actualizar paquetes.
* Alterar la base de datos.
* Iniciar despliegues.
* Hacer commits.
* Hacer push.
* Eliminar archivos.
* Rotar credenciales.
* Reescribir historial Git.
* Ejecutar comandos destructivos.

Puedes ejecutar verificaciones de solo lectura, compilaciones y pruebas que no alteren información importante.

Si una prueba requiere modificar datos, usar exclusivamente:

* Base de pruebas.
* Contenedor temporal.
* Copia aislada.
* Datos sintéticos.

Antes de cualquier implementación posterior, debes esperar autorización expresa.

---

# 2. PRINCIPIOS DE LA AUDITORÍA

Aplica estas reglas:

1. No confíes únicamente en README, memoria, comentarios o informes anteriores.
2. Comprueba que lo documentado coincida con el código.
3. No declares “tests OK” sin ejecutarlos.
4. No declares “producción lista” sin verificar seguridad, migraciones, backups y despliegue.
5. No supongas que el frontend protege el backend.
6. No supongas que tener `empresa_id` garantiza aislamiento.
7. No supongas que una migración antigua protege tablas creadas después.
8. No inventes resultados.
9. Diferencia claramente:

   * Verificado.
   * Parcialmente verificado.
   * No verificado.
   * Bloqueado.
10. Toda conclusión debe tener evidencia.
11. Identifica causa raíz, no solamente síntomas.
12. Prioriza los riesgos que puedan causar:

* Pérdida de información.
* Fuga entre empresas.
* Alteración de inventario.
* Acceso no autorizado.
* Inconsistencia financiera.
* Interrupción del servicio.
* Imposibilidad de restaurar backups.

---

# 3. MANEJO SEGURO DE SECRETOS

Antes de comenzar, busca sin mostrar valores:

```text
.env
.env.*
backend/.env
contraseñas
tokens
API keys
SECRET_KEY
CONFIG_ENCRYPTION_KEY
DATABASE_URL
MIGRATION_DATABASE_URL
BACKUP_DATABASE_URL
AUDIT_DATABASE_URL
REDIS_URL
credenciales S3
cookies
llaves privadas
certificados
backups
```

Si encuentras secretos:

1. No imprimas el valor.
2. No lo copies al informe.
3. Indica únicamente:

   * Archivo.
   * Nombre de variable.
   * Si contiene un valor real o placeholder.
   * Nivel de riesgo.
4. Determina si el archivo está:

   * Rastreado por Git.
   * Ignorado.
   * Incluido en ZIP.
   * Incluido en Docker.
   * Incluido en backups.
5. Recomienda rotación cuando corresponda.
6. Revisa el artefacto final, no solamente `git ls-files`.

Detén cualquier comando que pueda mostrar secretos completos.

---

# 4. INICIO OBLIGATORIO

Antes de auditar:

1. Localiza y lee `AGENTS.md`.
2. Lee las instrucciones del proyecto.
3. Lee:

   * `memory/project_context.md`.
   * `memory/session_summary.md`.
   * `memory/learnings.md`.
   * `memory/known_issues.md`.
4. Revisa:

   * `directives/security.md`.
   * `directives/testing.md`.
   * `directives/deployment.md`.
5. Identifica:

   * Rama.
   * Commit.
   * Estado Git.
   * Archivos modificados.
   * Archivos no rastreados.
   * Etiquetas.
   * Versión.
6. Determina si la copia auditada es reproducible.
7. No modifiques la memoria ni la documentación durante esta auditoría.

---

# 5. INVENTARIO DEL PROYECTO

Entrega un inventario de:

* Stack.
* Versiones.
* Backend.
* Frontend.
* Base de datos.
* Redis.
* Docker.
* Caddy.
* CI/CD.
* Módulos.
* Routers.
* Modelos.
* Schemas.
* Migraciones.
* Servicios.
* Middlewares.
* Pruebas.
* Scripts.
* Documentación.
* Archivos generados.
* Dependencias.
* Volumen y cantidad de archivos.

Identifica archivos que no deberían estar en una entrega:

```text
.git
node_modules
dist
.env
*.db
logs
backups
uploads
__pycache__
.pytest_cache
.tmp
credenciales
artefactos antiguos
```

---

# 6. AUDITORÍA DE ARQUITECTURA

Evalúa:

* Separación de responsabilidades.
* Organización por dominios.
* Acoplamiento.
* Duplicidad.
* Archivos monolíticos.
* Servicios reutilizables.
* Dependencias circulares.
* Código muerto.
* Endpoints duplicados.
* Modelos duplicados.
* Configuraciones superpuestas.
* Fuente oficial de datos.
* Consistencia entre frontend y backend.
* Manejo de transacciones.
* Escalabilidad.
* Mantenibilidad.
* Observabilidad.
* Extensibilidad por tenant.

Revisa especialmente si existen implementaciones duplicadas para:

* Configuración.
* Historial de mantenimiento.
* Repuestos utilizados.
* Solicitudes de repuestos.
* Reportes.
* Formatos.
* Branding.
* Usuarios y empresas.
* Permisos.

---

# 7. AUDITORÍA MULTIEMPRESA

Para cada tabla operativa determina:

* Si tiene `empresa_id`.
* Si `empresa_id` es obligatorio.
* Si tiene índice.
* Si tiene FK.
* Si tiene RLS.
* Si usa `FORCE ROW LEVEL SECURITY`.
* Si el rol web tiene `BYPASSRLS`.
* Si las políticas filtran correctamente.
* Si los endpoints filtran también en aplicación.
* Si se valida la relación entre entidades.
* Si un UUID ajeno puede producir IDOR.

Prueba conceptualmente y, cuando sea posible, automáticamente:

```text
Empresa A no puede ver Empresa B
Empresa A no puede editar Empresa B
Empresa A no puede usar bodegas de Empresa B
Empresa A no puede asignar técnicos de Empresa B
Empresa A no puede consumir repuestos de Empresa B
Empresa A no puede acceder a evidencias de Empresa B
Empresa A no puede consultar reportes de Empresa B
```

Revisa administradores:

* Globales sin empresa.
* Administradores con empresa.
* Coordinadores con varias empresas.
* Empresa activa.
* Contexto del tenant.
* Resolución por dominio.
* Resolución antes del login.

Entrega una matriz de tablas y controles multiempresa.

---

# 8. AUTENTICACIÓN Y SESIONES

Audita:

* Login.
* Logout.
* Access token.
* Refresh token.
* Rotación.
* Revocación.
* Cookies.
* `HttpOnly`.
* `Secure`.
* `SameSite`.
* Path.
* Expiración.
* Hash de tokens.
* Protección contra replay.
* Cierre de todas las sesiones.
* Cambio obligatorio de contraseña.
* Contraseña temporal.
* Recuperación.
* Enumeración de usuarios.
* Bloqueo por intentos.
* Rate limiting.
* MFA si existe.
* Eventos de seguridad.
* Sesiones offline.
* Almacenamiento en frontend.
* Exposición en localStorage o IndexedDB.

Comprueba que access y refresh tokens no puedan intercambiarse.

---

# 9. POLÍTICA DE CONTRASEÑAS

Verifica:

* Longitud mínima y máxima.
* Argon2id.
* Compatibilidad con hashes antiguos.
* Migración automática de hash.
* Historial.
* Contraseñas comunes.
* Contraseñas relacionadas con usuario o empresa.
* Caducidad de temporales.
* Cambio administrativo.
* Recuperación.
* Mensajes seguros.
* Consistencia entre frontend y backend.
* Placeholders correctos.
* Configuración por entorno.
* Pruebas específicas.

No recomiendes cambios periódicos forzosos sin justificación.

---

# 10. AUTORIZACIÓN Y PERMISOS

Construye una matriz:

| Módulo/acción | ADMIN | COORDINADOR | TÉCNICO | EMPRESA |
| ------------- | ----: | ----------: | ------: | ------: |

Revisa individualmente:

* Lectura.
* Creación.
* Edición.
* Eliminación.
* Aprobación.
* Reapertura.
* Exportación.
* Descarga.
* Restore.
* Auditoría.
* Facturación.
* Ajustes de inventario.
* Entregas.
* Consumos.
* Configuración.

Comprueba que un permiso global aplicado a un router no conceda acceso excesivo a todos sus endpoints.

---

# 11. MÓDULO DE MANTENIMIENTOS

Audita:

* Asistente de creación.
* Búsqueda de equipo.
* Autocompletado.
* Técnico opcional.
* Estado automático.
* Fechas.
* Duración.
* Conflictos.
* Prioridad sugerida.
* Técnico sugerido.
* Borrador.
* Recurrencia.
* Soft delete.
* Paginación.
* Historial.
* Reapertura.
* Auditoría.
* Relación con cronograma.
* Relación con hoja de vida.
* Acceso rápido.
* Aislamiento multiempresa.
* Doble envío.
* Transacciones.
* Notificaciones.
* Roles.

Verifica que creación y asignación sean atómicas.

---

# 12. ÓRDENES DE TRABAJO

Audita el ciclo:

```text
PROGRAMADO
→ ASIGNADO
→ EN_PROCESO
→ PAUSADO
→ FINALIZADO
```

Y los flujos:

* Anulación.
* Reapertura.
* Reasignación.
* Evidencias.
* Firmas.
* Incidencias.
* Repuestos.
* Costos.
* Cierre.
* Informe.
* Hoja de vida.
* Auditoría.

Comprueba:

* Transiciones permitidas.
* Requisitos de finalización.
* Inmutabilidad después del cierre.
* Motivo de reapertura.
* Identidad del técnico.
* Acceso a órdenes ajenas.
* Fechas automáticas.
* Doble finalización.
* Condiciones de carrera.

---

# 13. REPUESTOS Y CONSUMIBLES

Realiza una auditoría especialmente profunda.

## Catálogo

Verifica:

* Código único por empresa.
* Tipo.
* Categoría.
* Unidad.
* Marca.
* Referencia.
* Costos.
* Stock mínimo y máximo.
* Lotes.
* Seriales.
* Vencimientos.
* Estado activo.
* Eliminación lógica.

## Bodegas

Verifica:

* Empresa.
* Sede.
* Responsable.
* Ubicación.
* Acceso por tenant.
* Transferencias.

## Existencias

Comprueba:

```text
disponible = existencia_fisica - cantidad_reservada
```

Nunca permitir:

```text
existencia_fisica < 0
cantidad_reservada < 0
cantidad_reservada > existencia_fisica
```

## Movimientos

Verifica:

* Entrada.
* Ajuste.
* Transferencia.
* Reserva.
* Liberación.
* Entrega.
* Consumo.
* Devolución.
* Baja.
* Inmutabilidad.
* Idempotencia.
* Auditoría.
* Existencia anterior y posterior.
* Costo histórico.

## Concurrencia

Busca:

* `SELECT FOR UPDATE`.
* Bloqueos.
* Versionado optimista.
* Actualizaciones atómicas.
* Restricciones.
* Prevención de doble reserva.
* Creación simultánea de existencias.

Prueba el escenario:

```text
Disponible: 5
Solicitud A: 4
Solicitud B: 3
```

## Solicitudes

Valida:

```text
cantidad_consumida + cantidad_devuelta <= cantidad_entregada
```

Busca riesgos de:

* Devolver más de lo entregado.
* Devolver dos veces.
* Consumir dos veces.
* Reservar dos veces.
* Cancelar sin liberar.
* Transferir stock reservado.
* Ajustar stock reservado.
* Acceder por UUID de otra empresa.

## Costos

Comprueba que la orden use el costo histórico del movimiento y no el precio actual del catálogo.

## Duplicidades

Compara:

```text
mantenimientos.repuestos
ot_repuestos
formatos_mantenimiento.repuestos_utilizados
formatos_dinamicos.repuestos_utilizados
solicitudes_repuestos
movimientos_repuestos
```

Determina la fuente oficial.

---

# 14. INVENTARIO Y ACTIVOS

Audita:

* Creación.
* Edición.
* Importación.
* Exportación.
* Códigos.
* Seriales.
* Estado.
* Criticidad.
* Empresa.
* Sede.
* Categoría.
* Ubicación.
* Movimientos.
* Préstamos.
* Traslados.
* Bajas.
* Documentación.
* Hoja de vida.
* Duplicados.
* Archivos.
* Aislamiento.
* Historial.
* Eliminación.

Valida importaciones contra:

* Fórmulas.
* CSV injection.
* Filas excesivas.
* Archivos maliciosos.
* Columnas inesperadas.
* Duplicados.
* Tenant incorrecto.

---

# 15. ARCHIVOS, EVIDENCIAS Y FIRMAS

Audita:

* MIME real.
* Extensión.
* Tamaño.
* Path traversal.
* Nombres.
* Acceso privado.
* URLs firmadas.
* Caducidad.
* Eliminación.
* Antivirus o cuarentena.
* Metadatos EXIF.
* Optimización.
* Archivos huérfanos.
* Firmas PNG.
* Límites base64.
* Exposición de uploads.
* Backups de archivos.
* Tenant.

Comprueba que solamente logos autorizados sean públicos.

---

# 16. BASE DE DATOS Y MIGRACIONES

Audita:

* Cadena Alembic.
* Heads.
* Forks.
* Revisiones duplicadas.
* Migraciones modificadas.
* `upgrade()`.
* `downgrade()`.
* Orden de creación.
* FKs.
* Índices.
* Unique constraints.
* Checks.
* Defaults.
* Tipos monetarios.
* UUID.
* Zona horaria.
* Borrados en cascada.
* Datos históricos.
* Migraciones de datos.
* Privilegios.
* RLS.
* Tablas creadas después de políticas globales.

Comprueba si migraciones antiguas fueron editadas para mencionar tablas futuras.

Si es posible, prueba en PostgreSQL temporal:

```text
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

No ejecutar downgrade sobre una base con datos reales.

---

# 17. TRANSACCIONES E INTEGRIDAD

Identifica operaciones que deben ser atómicas:

* Crear mantenimiento y asignar técnico.
* Finalizar OT.
* Consumir repuestos.
* Reservar existencias.
* Transferir.
* Ajustar.
* Crear historial.
* Registrar auditoría.
* Crear notificación.
* Publicar reporte.
* Restaurar backup.

Busca commits parciales y ausencia de rollback.

Revisa manejo de:

* `IntegrityError`.
* `OperationalError`.
* Deadlocks.
* Reintentos.
* Idempotencia.
* Excepciones después de modificar datos.

---

# 18. FRONTEND

Audita:

* Rutas.
* Guards.
* Roles.
* Lazy loading.
* Manejo de errores.
* Loading.
* Doble clic.
* Formularios.
* Validación.
* Toasts.
* Uso de `alert`, `prompt` y `confirm`.
* Accesibilidad.
* Teclado.
* Responsive.
* Móvil.
* Contraste.
* Estados vacíos.
* Paginación.
* Debounce.
* Cancelación de solicitudes.
* Componentes monolíticos.
* Duplicación.
* Manejo de tokens.
* XSS.
* URLs.
* PWA.
* Service Worker.
* Caché de información sensible.
* Modo offline.
* Sincronización.

Identifica pantallas que carguen catálogos completos sin paginación.

---

# 19. BRANDING Y WHITE-LABEL

Busca referencias visibles y técnicas a:

```text
SGA
SGAHolding
SGA SaaS
sgaholding.online
ESE Salud Yopal
Hospital Central
equipos biomédicos
códigos SGA-MAN
```

Clasifica:

* Visible y debe corregirse.
* Interno compatible y puede mantenerse.
* Histórico y debe archivarse.
* Fixture de pruebas.
* Riesgo de exposición del cliente anterior.

Audita:

* Logo.
* Favicon.
* Login.
* Loader.
* Sidebar.
* Colores.
* Reportes.
* Formatos.
* PDFs.
* Excel.
* Correos.
* Dominios.
* Códigos documentales.
* Plantillas.
* Tema por tenant.
* Branding antes del login.
* Resolución por dominio.

---

# 20. CONFIGURACIÓN

Compara:

```text
configuracion_sistema
configuracion_saas
config/vaner_asset
.env
product.py
product.js
/public/config
manifest
```

Determina:

* Fuente canónica.
* Campos duplicados.
* Configuración global.
* Configuración por tenant.
* Secretos cifrados.
* Configuración pública.
* Fallbacks.
* Datos sin uso.
* Feature flags.
* Módulos habilitados.
* Configuración antes del login.

---

# 21. BACKUPS Y RECUPERACIÓN

Audita:

* `pg_dump`.
* Compatibilidad de versión.
* Rol de backup.
* Cifrado.
* Clave.
* S3/R2.
* Retención.
* Integridad.
* Hash.
* Logs.
* Restore.
* Restricción de restore.
* Backup de uploads.
* Backup de configuración.
* RPO.
* RTO.
* Pruebas de restauración.
* Restauración en base temporal.
* Separación por tenant.
* Nombres heredados.
* Compatibilidad con backups antiguos.

Un backup no se considera válido hasta demostrar que puede restaurarse.

---

# 22. INFRAESTRUCTURA Y DESPLIEGUE

Audita:

* Dockerfiles.
* Imágenes.
* Usuarios no root.
* `read_only`.
* `cap_drop`.
* `no-new-privileges`.
* Health checks.
* Límites.
* Redes.
* Volúmenes.
* Secretos.
* Logs.
* Restart.
* Caddy.
* HTTPS.
* CORS.
* Headers.
* HSTS.
* CSP.
* Redis.
* PostgreSQL.
* Puertos.
* Exposición.
* Imágenes inmutables.
* Tags.
* Rollback.
* Deploy script.
* Múltiples clientes en un VPS.

Comprueba colisiones por:

```text
container_name
nombre de red
volúmenes
puertos
dominios
rutas
COMPOSE_PROJECT_NAME
DEPLOYMENT_ID
```

---

# 23. CI/CD Y DEPENDENCIAS

Audita:

* Workflow CI.
* Versiones de Python y Node.
* Instalación reproducible.
* Lockfiles.
* Dependencias fijadas.
* `pip-audit`.
* `npm audit`.
* Lint.
* Build.
* Tests.
* UTF-8.
* Secret scanning.
* Artefactos.
* Protección de ramas.
* Imágenes.
* Firma y SBOM.
* Actualizaciones automáticas.

No actualices dependencias durante la auditoría.

Reporta vulnerabilidades conocidas sin imprimir información sensible.

---

# 24. PRUEBAS

Clasifica las pruebas existentes:

* Unitarias.
* Integración.
* API.
* Seguridad.
* Multiempresa.
* Migraciones.
* Frontend.
* End-to-end.
* PostgreSQL.
* Concurrencia.
* Recuperación.
* Rendimiento.

Ejecuta únicamente comandos documentados.

Registra:

```text
Comando
Resultado
Aprobadas
Fallidas
Omitidas
Tiempo
Bloqueo
```

No confundas:

* Pruebas que existen.
* Pruebas que se ejecutaron.
* Pruebas que pasaron.
* Pruebas que no pudieron ejecutarse.

Busca módulos nuevos sin pruebas específicas.

---

# 25. RENDIMIENTO

Audita:

* Consultas N+1.
* Carga completa de catálogos.
* Paginación real.
* Índices.
* Filtros.
* Joins.
* Agregaciones.
* Exportaciones grandes.
* Subida de archivos.
* Compresión.
* Caching.
* Redis.
* Scheduler.
* Jobs duplicados.
* Varias instancias del backend.
* Bloqueos.
* Timeouts.
* Pool SQLAlchemy.
* Consultas por `cast(UUID, String)`.
* Serialización.
* Dashboard.

Identifica límites prácticos para:

* Empresas.
* Usuarios.
* Equipos.
* Mantenimientos.
* Evidencias.
* Repuestos.
* Movimientos.
* Reportes.

---

# 26. OBSERVABILIDAD

Audita:

* Logs estructurados.
* Request ID.
* Usuario.
* Tenant.
* Severidad.
* Eventos de seguridad.
* Métricas.
* Health checks.
* Readiness.
* Liveness.
* Alertas.
* Errores.
* Sentry u opción equivalente.
* Retención.
* Limpieza.
* Información sensible en logs.

No registrar:

* Contraseñas.
* Tokens.
* Cookies.
* URLs con credenciales.
* Claves.
* Contenido sensible innecesario.

---

# 27. FACTURACIÓN Y DATOS FINANCIEROS

Audita:

* Uso de `Decimal`/`Numeric`.
* Impuestos.
* Totales.
* Redondeo.
* Estados.
* Inmutabilidad.
* Notas crédito.
* Datos por tenant.
* Permisos.
* Exportación.
* Auditoría.
* Relación con costos de mantenimiento.
* Costo histórico de repuestos.

No aceptar cálculos financieros basados en `float`.

---

# 28. DOCUMENTACIÓN

Compara documentación y realidad:

* README.
* Manual.
* Arquitectura.
* Despliegue.
* Migraciones.
* Seguridad.
* Release.
* Versión.
* Módulos.
* Endpoints.
* Variables.
* Dominios.
* Comandos.
* Backups.
* Pruebas.

Señala afirmaciones no demostradas como:

```text
Producción lista
Tests OK
Migración aplicada
RLS completo
Módulo terminado
Backup verificado
```

---

# 29. ESCALA DE SEVERIDAD

Clasifica cada hallazgo:

## Crítica

Puede causar:

* Fuga entre tenants.
* Compromiso de credenciales.
* Pérdida de datos.
* Alteración de stock.
* Fraude.
* Acceso administrativo.
* Restore imposible.
* Despliegue inseguro.

## Alta

Puede causar:

* Inconsistencia importante.
* Autorización excesiva.
* Costos incorrectos.
* Registros parciales.
* Incumplimiento.
* Interrupción operativa.

## Media

Afecta:

* Rendimiento.
* Experiencia.
* Mantenibilidad.
* Escalabilidad.
* Documentación.

## Baja

Incluye:

* Limpieza.
* Naming.
* Comentarios.
* Mejoras menores.

Cada hallazgo debe incluir:

```text
ID
Severidad
Área
Evidencia
Riesgo
Causa raíz
Recomendación
Esfuerzo
Dependencias
Criterio de aceptación
```

---

# 30. CALIFICACIÓN

Califica de 0 a 10:

* Arquitectura.
* Backend.
* Frontend.
* Seguridad.
* Autenticación.
* Autorización.
* Multiempresa.
* Base de datos.
* Migraciones.
* Mantenimientos.
* Órdenes.
* Repuestos.
* Inventario.
* Evidencias.
* Reportes.
* Backups.
* Infraestructura.
* CI/CD.
* Pruebas.
* UX/UI.
* Branding.
* Documentación.
* Preparación para producción.

Justifica cada nota.

---

# 31. ACTUALIZACIONES RECOMENDADAS

Después de los hallazgos, propone mejoras divididas en:

## Antes de producción

Solamente bloqueantes y correcciones imprescindibles.

## Corto plazo

Estabilidad, seguridad, operación y experiencia.

## Mediano plazo

Automatización, analítica, escalabilidad y nuevos flujos.

## Largo plazo

Integraciones, IA, predicción, expansión comercial y verticales.

No propongas nuevas funciones si primero existen riesgos críticos sin corregir.

---

# 32. PLAN DE ACCIÓN

Entrega un plan por fases:

```text
Fase
Objetivo
Hallazgos incluidos
Archivos probables
Migraciones
Pruebas
Riesgos
Dependencias
Duración estimada
Criterio de cierre
```

Orden obligatorio:

1. Secretos.
2. Seguridad.
3. Tenant y RLS.
4. Integridad de datos.
5. Migraciones.
6. Transacciones.
7. Pruebas.
8. Rendimiento.
9. UX.
10. Branding.
11. Nuevas funcionalidades.
12. Piloto.
13. Producción.

---

# 33. DECISIÓN DE DESPLIEGUE

Finaliza con una conclusión inequívoca:

```text
NO DESPLEGAR
APTO SOLO PARA DESARROLLO
APTO PARA PRUEBAS INTERNAS
APTO PARA PILOTO CONTROLADO
APTO PARA PRODUCCIÓN CON CONDICIONES
APTO PARA PRODUCCIÓN
```

Indica:

* Razón.
* Bloqueantes.
* Condiciones.
* Evidencia faltante.
* Riesgo residual.

---

# 34. FORMATO DE ENTREGA

Entrega el informe con esta estructura:

```text
1. Resumen ejecutivo
2. Alcance
3. Metodología
4. Estado verificado
5. Inventario técnico
6. Fortalezas
7. Hallazgos críticos
8. Hallazgos altos
9. Hallazgos medios
10. Hallazgos bajos
11. Matriz multiempresa
12. Matriz de permisos
13. Auditoría por módulo
14. Seguridad
15. Base de datos y migraciones
16. Infraestructura
17. Pruebas
18. Rendimiento
19. Branding
20. Documentación
21. Calificaciones
22. Actualizaciones recomendadas
23. Plan por fases
24. Decisión de despliegue
25. Evidencias y comandos ejecutados
26. Limitaciones de la auditoría
```

---

# 35. ENTREGA INICIAL

Comienza mostrando únicamente:

```text
1. Proyecto y versión identificados.
2. Rama y commit.
3. Estado del repositorio.
4. Presencia de archivos sensibles sin revelar valores.
5. Stack detectado.
6. Comandos de validación que ejecutarás.
7. Alcance exacto.
```

Después realiza la auditoría completa.

No implementes ninguna corrección. Espera autorización expresa después de entregar el informe.
