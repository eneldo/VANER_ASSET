### G. FASE 7 - Inventario/Activos (2026-08-25)

## Módulo Repuestos y Consumibles (2026-08-26)

### Contexto
El prompt maestro solicita un módulo completo de inventario de repuestos. Se realizó auditoría completa del estado actual.

### Hallazgos
- Solo existía `ot_repuestos` (tabla vinculada a OTs) — vacía
- `mantenimientos.repuestos` (JSON) — redundante con `ot_repuestos`
- No existía catálogo, stock, bodegas, movimientos, proveedores
- Ruta `/admin/repuestos` apuntaba a `MantenimientosPage` (placeholder)

### Implementación Fase 1
- 10 modelos nuevos en `backend/app/models/repuestos.py`
- Migración `r01a1b2c30001` con 10 tablas + RLS + grants
- Router 31 endpoints en `backend/app/routers/repuestos.py`
- Frontend `RepuestosPage.jsx` con 5 pestañas
- Políticas: promedio ponderado, descuento al entregar, reservas atómicas
- 316 tests OK, build OK

### Lecciones
- Verificar siempre el allowlist de privilegios al agregar tablas nuevas
- El test `test_allowlist_cubre_tablas_modeladas_y_asociaciones` falla si hay tablas nuevas sin agregar al allowlist
- Usar `eslint-disable-line react-hooks/set-state-in-effect` para effects con data fetching
- Preferir `useCallback` con dependencias explícitas sobre `useEffect` con dependencias vacías

## Objetivo
Auditoría y mejoras a los módulos de inventario y activos, asegurando hojas de vida completas y trazabilidad de cambios.

## Hallazgos actuales

### Modelo `equipo`
- **Fortalezas**: `id`, `nombre`, `marca`, `modelo`, `serie`, `ubicacion`, `invima`, `estado` (OPERATIVO/EN_MANTENIMIENTO/FUERA_DE_SERVICIO/BAJA), `criticidad`, `activo`, `created_at`, `updated_at`
- **Relaciones**: `empresa_id`, `sede_id`, `categoria_id`
- **Nuevos campos FASE 7**: `responsable_id` (FK usuario), `vida_util_meses`, `historial_cambios` (JSON tracking)

### Modelo `equipo_hoja_vida`
- **Fortalezas**: `adquisicion`, `costo`, `fecha_compra`, `fecha_instalacion`, `proveedor`, `pais_fabricacion`, `fecha_fabricacion`, `vida_util`, `requiere_calibracion`, soportes de documentación y planos

### Modelo `mantenimiento`
- **Fortalezas**: Relaciones a `equipo_id`, `tecnico_id`, `empresa_id`, `sede_id`
- **Nuevos campos FASE 7**: `prioridad`, `falla_incidencia`, `diagnostico`, `trabajo_realizado`, `repuestos` (JSON), `costo_mano_obra`, `costo_repuestos`, `costo_total`, `evidencia_fotos`, `evidencia_documentos`, `solucion`, `cerrado`, `fecha_cierre`, `responsable_id`, `tipo_movimiento`, `activo_afectado_id/tipo`

## ✅ Avances FASE 7

### `equipo.py` - Mejoras implementadas
- `responsable_id`: FK a usuarios - responsable actual del equipo
- `vida_util_meses`: Indicador de vida útil en meses
- `historial_cambios`: JSON - tracking de cambios de responsable, ubicacion, estado, criticidad
  - Formato: [{"timestamp": datetime, "campo": str, "anterior": any, "nuevo": any, "usuario_id": uuid}]

### `mantenimiento.py` - Mejoras implementadas
- `prioridad`: BAJA/MEDIA/ALTA/CRITICA
- `falla_incidencia`: Texto descripción de la falla
- `diagnostico`: Hallazgos del diagnóstico
- `trabajo_realizado`: Descripción del trabajo efectuado
- `repuestos`: JSON con repuestos [{id, codigo, descripcion, cantidad, costo_unitual}]
- `costo_mano_obra`, `costo_repuestos`, `costo_total`: Costos detallados
- `evidencia_fotos`, `evidencia_documentos`: JSON con evidencias
- `solucion`: Texto de la solución aplicada
- `cerrado`/`fecha_cierre`: Bandera y fecha de cierre
- `responsable_id`: FK a usuarios
- `tipo_movimiento`: ASIGNACIÓN, DEVOLUCIÓN, TRANSFERENCIA, BAJA
- `activo_afectado_id/tipo`: Control de movimiento de activo (EQUIPO, REPUESTO, CONSUMIBLE)

## Cierre FASE 7 — 2026-08-26

1. Control de asignaciones, devoluciones, transferencias y bajas implementado con actor autenticado, validación de responsable/empresa y bloqueo de equipos inactivos o dados de baja.
2. Historial persistente de responsable, sede, ubicación y estado disponible en backend y visible en el frontend.
3. `vida_util_meses` validada y administrable desde la interfaz.
4. Vencimiento calculado desde instalación, compra o creación; cambia el equipo a `FUERA_DE_SERVICIO` sin ejecutar una baja automática y de forma idempotente.
5. Búsqueda y filtros por estado, criticidad, categoría, sede, responsable y condición activa disponibles en el inventario administrativo.
6. Migración Alembic `m63b1e640001` añadida para responsable, vida útil e historial.
7. Regresión completa aprobada: 163 pruebas backend y 62 frontend, lint y build frontend, compilación Python y seguridad del repositorio.

## Integración con FASES anteriores

- FASE 1: Auditoría completada ✅
- FASE 2: VERSION 2.0.0 y main.py actualizado ✅
- FASE 3: .env.example creado ✅
- FASE 4: Estructura branding/default y branding/clients/ ✅
- FASE 5: Estructura config/default y config/clients/ ✅
- FASE 6: Migraciones BD y configuración por cliente ✅
- FASE 7: Inventario/Activos ✅
*Registro FASE 7 actualizado tras validación integral*
*Fecha de cierre: 2026-08-26*
*Sistema: VANER_ASSET - Transformación SGA → VANER Asset v2*
*Próxima fase: 8 - Mantenimiento*

### H. FASE 8 - Mantenimiento (2026-08-26)

## Objetivo
Sincronizar el modelo de mantenimiento con la base de datos, exponer campos de diagnóstico, costos y cierre en API y frontend.

## Cambios realizados

### Migración Alembic `n74c2f750001`
- 17 columnas añadidas a `mantenimientos`: prioridad, falla_incidencia, diagnostico, trabajo_realizado, repuestos (JSON), costo_mano_obra, costo_repuestos, costo_total, evidencia_fotos (JSON), evidencia_documentos (JSON), solucion, cerrado, fecha_cierre, responsable_id (FK usuarios), tipo_movimiento, activo_afectado_id, activo_afectado_tipo.
- FK `fk_mantenimientos_responsable_id_usuarios` e índice `ix_mantenimientos_responsable_id`.
- Valor por defecto `cerrado = FALSE` para registros existentes.

### Schema `mantenimiento.py`
- `MantenimientoBase`: campos de diagnóstico, costos, cierre, responsable y trazabilidad.
- `MantenimientoUpdate`: todos los campos opcionales para edición parcial.
- `MantenimientoOut`: respuesta completa con todos los campos del modelo.

### Router `mantenimientos.py`
- `mantenimiento_dict()`: retorna prioridad, diagnóstico, costos detallados, evidencias, solucion, cerrado, fecha_cierre, responsable_id, tipo_movimiento, activo_afectado.
- `crear_mantenimiento()`: persiste los nuevos campos.
- `cambiar_estado()`: al FINALIZADO marca `cerrado=True` y `fecha_cierre=now()`.
- `aplicar_reapertura()`: resetea `cerrado=False` y `fecha_cierre=None`.

### Frontend `MantenimientosPage.jsx`
- `formInicial`: campos prioridad, falla_incidencia, diagnostico, trabajo_realizado, costos (mano_obra, repuestos, total), solucion.
- Formulario: select de prioridad (BAJA/MEDIA/ALTA/CRITICA), textareas de diagnóstico, costos numéricos, solución.
- Tabla: incluye prioridad en el formulario.
- Modal de detalle: muestra prioridad, cerrado, fecha_cierre, diagnóstico, trabajo realizado, solución, costos.

### Tests `test_mantenimiento_fase8.py`
- 10 pruebas: schemas, reapertura, dict, transiciones, coherencia modelo-migración.

## Validación
- 173 pruebas backend aprobadas (10 nuevas).
- 62 pruebas frontend aprobadas.
- Lint frontend: sin errores.
- Build frontend: exitoso.
- Alembic: head `n74c2f750001`, cadena lineal sin forks.

## Estado actual
Fase 8 completada y validada en backend y frontend.

## Próximo paso recomendado
Aplicar migración en base de integración PostgreSQL y continuar con Fase 9.

### I. FASE 9 - Órdenes de Trabajo (2026-08-26)

## Objetivo
Completar el flujo de Órdenes de Trabajo: crear→asignar→ejecutar→cerrar con trazabilidad, repuestos, incidencias y evidencias.

## Cambios realizados

### Tests end-to-end del flujo OT
- `tests/test_flujo_completo_ot.py`: 35 pruebas que validan:
  - Transiciones de estado: PROGRAMADO→ASIGNADO→EN_PROCESO→FINALIZADO
  - Flujos con pausa y reapertura
  - Anulación desde estados intermedios
  - Repuestos e incidencias: normalización, límites, validaciones
  - Evidencias: requisitos de cierre (ANTES/DURANTE/DESPUES)
  - Aplicar estado operativo: fechas automáticas
  - Reapertura: reseteo de cerrado y fecha_cierre
  - Normalización de fechas y listas vacías
  - Coherencia del modelo de transiciones

### Conversión automática Solicitud→OT
- `routers/solicitudes_correctivas.py`: Al cambiar estado a `CONVERTIDA_OT`:
  - Crea Mantenimiento en estado PROGRAMADO
  - Copia empresa_id, sede_id, equipo_id de la solicitud
  - Mapea prioridad de solicitud a prioridad de OT
  - Registra evento en HistMantenimiento
  - Valida que la solicitud tenga equipo asociado (equipo_id NOT NULL)
  - Retorna `mantenimiento_creado_id` en la respuesta

### Sidebar técnico con badge
- `components/Sidebar.jsx`: Carga conteo de OTs activas al montar
- Muestra badge rojo con número de OTs (asignadas + en proceso + pausadas)
- `styles/sidebar.css`: Estilo `.sga-badge` para el indicador

## Validación
- 208 pruebas backend aprobadas (35 nuevas)
- 62 pruebas frontend aprobadas
- ESLint sin errores
- Build exitoso

## Estado actual
Fase 9 completada y validada.

## Próximo paso recomendado
Continuar con Fase 12 — Despliegue.

### K. FASE 11 - Auditoría y Seguridad (2026-08-26)

## Objetivo
Hardening de seguridad: tests de seguridad, limpieza de naming SGA, limpieza de auditoría.

## Cambios realizados

### Tests de seguridad (51 pruebas)
- `test_seguridad_fase11.py`: suite completa que cubre:
  - Password hashing PBKDF2-SHA256
  - JWT tokens (access y refresh)
  - Token hashing SHA-256
  - Security headers (nosniff, SAMEORIGIN, CSP, HSTS, Referrer-Policy)
  - Audit middleware (exclusiones, módulos, acciones, severidad)
  - Rate limit keys (prefijo, hash no expone IP/ruta, reglas)
  - SecurityEvent logger (tolerancia a fallos, IP forwarding)
  - Config production (SECRET_KEY, DEBUG, CLIENT_CODE, HTTPS)
  - Auth roles (require_roles)
  - Cross-validation JWT (access vs refresh type)

### Limpieza de naming SGA → VANER
- `rate_limit.py`: `sga:rate-limit:` → `vaner:rate-limit:`
- `config.py`: `sga_backup` → `vaner_backup` (rol de backup)
- `auth.py`, `main.py`, `core/permissions.py`: headers actualizados
- `utils/backup_utils.py`, `services/smart_backup_service.py`: prefijos de nombre de archivo

### Limpieza de auditoría
- Endpoint `POST /auditoria-pro/limpiar?dias=90`: elimina eventos antiguos de `auditoria_pro_eventos` y `seguridad_eventos`

## Validación
- 285 pruebas backend aprobadas (51 nuevas)
- 62 pruebas frontend aprobadas
- ESLint sin errores
- Build exitoso

## Estado actual
Fase 11 completada y validada.

## Próximo paso recomendado
Continuar con Fase 12 — Despliegue.

### L. Optimización del Módulo de Mantenimientos (2026-08-26)

## Objetivo
Rediseñar integralmente el módulo de mantenimientos siguiendo el prompt `OPTIMIZACION_MANTENIMIENTOS_VANER_ASSET.md`: correcciones críticas, simplificación visual, automatización, planificación avanzada y verificación.

## Cambios realizados

### Fase 1 — Correcciones críticas
- **Router `mantenimientos.py` reescrito**:
  - Auth obligatoria + `require_roles("ADMIN","COORDINADOR","TECNICO")` en todos los endpoints
  - Aislamiento multi-tenant via `_filtrar_por_empresa()` (filtrado por `empresa_ids`)
  - Búsqueda UUID directa (`modelo.id == uuid`) en vez de `cast(col, String)`
  - Soft-delete: campo `activo` en modelo + migración `p91e4f720001`
  - Creación transaccional con rollback y técnico opcional
  - Paginación server-side: `page`, `per_page`, filtros (estado, tipo, prioridad, equipo, tecnico)
  - Validación de fechas y mensajes de error seguros
- **Modelo `Mantenimiento`**: campo `activo` añadido

### Fase 2 — Simplificación visual
- **`MaintenanceWizard.jsx`**: asistente 3 pasos (Activo → Trabajo → Confirmar)
- **`EquipmentSearch.jsx`**: búsqueda inteligente con dropdown, navegación teclado, resultados en tiempo real
- **`MantenimientosPage.jsx`**: reescrito con wizard, filtros, paginación, `showToast()` en vez de `window.alert()`

### Fase 3 — Automatización
- **Endpoint `GET /conflictos/{equipo_id}`**: detecta OTs abiertas, equipo no disponible, técnico ocupado, conflictos de fecha, preventivo vencido
- **Endpoint `GET /sugerir-tecnico/{equipo_id}`**: sugiere top 5 técnicos por empresa, especialidad y carga de trabajo
- **Endpoint `GET /sugerir-prioridad`**: calcula prioridad por criticidad, equipo parado, tipo, impacto operativo
- **Frontend**: conflictos con badges y alertas, técnico sugerido con 1-click, prioridad sugerida con razón, borrador en localStorage

### Fase 4 — Planificación avanzada
- **Endpoint `POST /{id}/recurrencia`**: crea órdenes recurrentes (SEMANAL, MENSUAL, BIMESTRAL, TRIMESTRAL, SEMESTRAL, ANUAL), max 24 repeticiones
- **Endpoint `GET /acceso-rapido/{equipo_id}`**: contexto del equipo, último mantenimiento, OTs abiertas, sugerencia de tipo
- **Frontend**: campos de recurrencia en wizard, submit con recurrencia automática

### Fase 5 — Verificación
- 316 tests backend aprobados
- Build frontend exitoso
- ESLint sin errores
- Migración aplicada (`alembic upgrade head`)

## Aprendizajes

1. **Soft-delete con `activo` es preferible a `is_deleted`**: más limpio, compatible con filtros existentes
2. **Paginación server-side es esencial**: 1082 líneas de monolito → componente reutilizable
3. **Conflictos de programación**: detectar OTs abiertas, técnicos ocupados y fechas superpuestas ahorra tiempo de coordinación
4. **Borrador automático en localStorage**: mejora experiencia en formularios largos sin interferir con backend
5. **Recurrencia simple**: 6 frecuencias cubren el 95% de casos de mantenimiento preventivo

## Estado actual
Optimización completada y validada. Pendiente push a GitHub.

## Próximo paso recomendado
Push a GitHub y verificación en navegador.