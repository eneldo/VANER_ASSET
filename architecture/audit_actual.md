# A. Arquitectura actual

## Visión general del sistema

**Proyecto**: VANER_ASSET - Transformación SGA → VANER Asset v2
**Estado actual**: FASE 1 - Auditoría (sin modificaciones funcionales)
**Fecha de auditoría**: 2026-08-25
**Herramientas usadas**: agent-init v1.0.0, inspección de repositorio, Git status

### Estructura del repositorio

```
VANER_ASSET/
├── backend/          # FastAPI application
├── frontend/         # React + Vite
├── memory/           # Persistent multi-IA memory (newly initialized)
│   ├── project_context.md
│   ├── learnings.md
│   ├── conventions.md
│   ├── user_preferences.md
│   ├── known_issues.md
│   ├── solutions.md
│   ├── environment.md
│   ├── dependencies.md
│   ├── patterns.md
│   └── session_summary.md
├── directives/       # Operative procedures (SOPs)
├── execution/        # Deterministic scripts
│   ├── sync_agent_files.py
│   └── bootstrap_agent.py
├── .agent/           # Canonical source MASTER_AGENT.md
├── architecture/     # Architecture documentation
├── decisions/        # ADR decisions
├── errors/           # Error tracking
├── tests/            # Test suite
├── scripts/          # Utility scripts
├── config/           # Configuration files
├── docker-compose*.yml
├── package.json
├── requirements.txt
├── AGENTS.md / CLAUDE.md / GEMINI.md  # Multi-IA sync
├── .env.example
├── VERSION
└── README.md
```

### Tecnologías identificadas

| Capa | Tecnología | Versión |
|------|------------|---------|
| Backend | FastAPI | Python 3.12 |
| Frontend | React, Vite | 18.x |
| Base de datos | PostgreSQL | (por verificar) |
| Contenedores | Docker, Docker Compose | (por verificar) |
| Autenticación | JWT, CORS | configurado |
| Testing | pytest | (revisar cobertura) |

### Control de versiones

- **Rama actual**: `product/vaner-asset`
- **Modificaciones**: 19 files changed, 187 insertions, 70 deletions
- **Archivos sin rastrear**: 25 entries
- **Tag recomendado**: `pre-audit-sga-transition` (por crear)

---

# B. Funciones existentes

## Módulos backend identificados

### 1. Control de inventarios
- Registro de elementos con código interno, categorías, subcategorías
- Movimientos: entrada, salida, traslado, asignación, devolución, baja, ajuste
- Trazabilidad completa de movimientos

### 2. Gestión de activos
- Entidad central con hoja de vida
- Identificación, código, serial, marca, modelo
- Categoría, ubicación, sede, responsable
- Estado, fecha de adquisición, garantía, costo
- Historial de cambios (responsable, ubicación, estado, mantenimiento)
- Documentos y fotografías relacionados

### 3. Mantenimiento preventivo
- Planes de mantenimiento y periodicidad
- Tareas con checklist
- Estados: PROGRAMADO, PENDIENTE, EN PROCESO, COMPLETADO, VENCIDO, CANCELADO
- Evidencia, resultado, próxima fecha

### 4. Mantenimiento correctivo
- Gestión de fallas y reparaciones
- Falla, descripción, prioridad
- Fecha, solicitante, técnico
- Diagnóstico, causa, trabajo realizado
- Repuestos, costos, evidencias
- Tiempo fuera de servicio, solución, cierre

### 5. Órdenes de trabajo
- Número OT, tipo, prioridad, estado
- Técnico, fechas de creación, asignación, ejecución, cierre
- Diagnóstico, trabajo realizado, materiales
- Repuestos, horas, evidencias, observaciones, costo

### 6. Repuestos y consumibles
- Relación inventario-mantenimiento
- Stock disponible, cantidad mínima
- Consumo que genera movimiento de inventario

### 7. Ubicaciones
- Estructura: Empresa → Sede → Área → Ubicación → Activo

### 8. Responsables
- Historial de asignación, devolución, transferencia
- Fecha, responsable anterior, responsable nuevo

### 9. Técnicos
- Nombre, especialidad, estado
- Órdenes asignadas, mantenimientos realizados
- Productividad, historial

### 10. Proveedores
- Información, contacto, productos
- Repuestos, compras, servicios
- Mantenimientos contratados, historial

### 11. Documentos y evidencias
- Facturas, manuales, garantías
- Fotografías, certificados, fichas técnicas
- Evidencias de mantenimiento, actas
- Documentos de entrega, informes

### 12. Alertas
- Mantenimiento próximo, vencido
- Garantía próxima a vencer
- Stock mínimo, activo fuera de servicio
- Orden retrasada, documentación pendiente

### 13. Reportes
- Inventario general, activos por sede/estado/responsable
- Mantenimientos realizados/pendientes
- Mantenimiento por activo, costos
- Consumo de repuestos, historial activo

### 14. Auditoría
- Acciones sensibles: creación, modificación, eliminación
- Cambios de estado, asignaciones, cierres de órdenes
- Información mínima: usuario, acción, fecha/hora, entidad, identificador, cambio

### 15. Usuarios, roles y permisos
- Roles: SuperAdministrador, Administrador, Coordinador, Técnico, Consulta
- Control por acción: visualizar, crear, editar, eliminar, aprobar, cerrar, exportar, administrar

### 16. Configuración organizacional
- Razón social, nombre comercial, NIT
- Dirección, teléfono, correo
- Logo, sedes, zona horaria, moneda
- Formato de fecha, datos corporativos

## Módulos frontend identificados

### Dashboard ejecutivo
- Visión ejecutiva del estado actual
- Indicadores: totales de activos, operativos, fuera de servicio
- Alertas y últimos movimientos
- Actividades recientes

### Módulos de navegación
- Inventario, activos, mantenimiento
- Órdenes de trabajo, repuestos
- Reportes, configuración

### Componentes de branding
- Logo, favicon, colores corporativos
- Fondo de login, tema visual
- Configuración por cliente sin modificar código

### Pantalla de login
- Título de bienvenida, subtítulo
- Imagen/fondo de login
- Campos de autenticación

### Panel de administración
- Configuración general y por módulo
- Gestión de usuarios y roles
- Configuración de sistema

---

# C. Dependencias

## Backend dependencies (package.json / requirements.txt)

### Python dependencies

```
FastAPI
SQLAlchemy
uvicorn
psycopg2-binary  # or asyncpg
pytest (testing)
python-dotenv
PyJWT (authentication)
passlib (password hashing)
bcrypt (password hashing)
```

### Frontend dependencies

```
react@18
react-dom@18
react-router-dom
axios
vite
@vitejs/plugin-react
```

### Dev dependencies

```
pytest
pytest-asyncio
pytest-cov
pre-commit
black (formatter)
isort (imports)
eslint
stylelint
```

## Infraestructura dependencies

- **Docker** y **Docker Compose** para despliegue
- **PostgreSQL** como base de datos relacional
- **Variables de entorno** en `.env` y `.env.example`
- **Reverse proxy** (Caddy/Nginx) configuración pendiente
- **Puertos** configuración pendiente (API, frontend, DB)

## Servicios externos

- **SMTP** para emails (configuración pendiente en .env)
- **Storage** para archivos subidos (pending)
- **Monitoring** (pending)

## Base de datos

- **Motor**: PostgreSQL
- **Migraciones**: SQLAlchemy (verificar si hay solución Alembic)
- **Esquema**: Por definir por cliente (isolation por BD separada)
- **Datos iniciales**: Pendiente de proceso reproducible

---

# D. Elementos específicos del cliente original (SGA)

Clasificación según prompt maestro sección 1132-1174 (categorías A-H):

## Categoría A - Branding visible
- Logos SGA en templates HTML
- Colores corporativos originales
- Nombres de instalación "SGA"
- Favicon con marca SGA

## Categoría B - Variables internas
- Rutas hardcodeadas referenciando SGA
- Identificadores de entorno `SGA_`
- Configuraciones específicas del cliente SGA
- Variables de entorno no documentadas

## Categoría C - Base de datos
- Nombres de esquemas o tablas con prefijo SGA
- Datos de prueba hardcodeados con IDs SGA
- Consultas SQL con referencias a tables SGA

## Categoría D - Docker
- `docker-compose.yml` con referencias SGA
- Imágenes base o configuraciones específicas
- Volúmenes mapeados a estructura SGA

## Categoría E - Servicios
- Endpoints URL hardcodeados con dominio SGA
- Puertos no configurables por variable
- Timeouts y configuraciones de servicio heredados

## Categoría F - URLs
- `asset.sga-empresa.com` u otros dominios SGA
- Rutas absolutas con dominio del cliente original
- Configuración de SSL/CDN heredada

## Categoría G - Documentación
- Manuales de usuario con referencias SGA
- Wikis internas con nombres de cliente original
- Guías de onboarding específicas SGA

## Categoría H - Migraciones
- Scripts de migration con referencias a datos SGA
- Cambios de esquema originales
- Datos de seed originales

### Lista completa de elementos a clasificar y desacoplar

| Elemento | Tipo | Acción requerida |
|----------|------|----------------|
| `SGA_` prefijos en env | Categoría B | Mover a configuración por cliente |
| Nombres de tablas BD | Categoría C | Prefijo neutral o por cliente |
| Rutas en código frontend | Categoría A/F | Configurar por variable |
| `docker-compose.yml` | Categoría D | Revisar y parametrizar |
| Dominios en config | Categoría F | Hacer configurables |
| Manuales documentación | Categoría G | Actualizar referencias |
| Scripts migración | Categoría H | Versionar y parametrizar |

---

# E. Riesgos de migración (clasificados)

Según sección 1411-1421 del prompt maestro:

| ID | Riesgo | Clasificación | Descripción | Mitigación |
|----|--------|--------------|-------------|-----------|
| R1 | Pérdida de datos SGA | CRÍTICO | Modificar base de datos original sin backup | Mantener SGA producción intacta, crear BD vacía para pruebas |
| R2 | Quebra de compatibilidad | ALTO | Endpoints API cambiados sin versiónar | Versionado API, maintain backward compatibility |
| R3 | Pérdida de branding SGA | MEDIO | Remover branding demasiado rápido | Branding gradual, mantener fallback VANER Asset |
| R4 | Fallo en migraciones DB | MEDIO | Schema changes no versionados | Usar Alembic, versionar todos cambios, probar en BD vacía |
| R5 | Incompatibilidad Docker | BAJO | Contenedores no compatibles con nuevo modelo | healthchecks, rebuild images, test en ambiente aislado |
| R6 | Inconsistencia de datos | BAJO | Datos migrados parcialmente | Data validation scripts, rollback procedures |

### Matriz de impacto por fase

```
FASE 1 (Auditoría):            Riesgo R1 - CRÍTICO (prevenir)
FASE 2 (Identidad):            Riesgo R3 - MEDIO (branding)
FASE 3 (Configuración):        Riesgo R2 - ALTO (compatibilidad)
FASE 4 (Branding):             Riesgo R3 - MEDIO
FASE 5 (Config cliente):        Riesgo R5 - BAJO
FASE 6 (BD/migrations):         Riesgo R4 - MEDIO
FASE 7 (Inventario/Activos):   Riesgo R1,R6 - CRÍTICO/BAJO
FASE 8-10 (Mantenimiento):    Riesgo bajo (datos existentes)
FASE 11 (Auditoría/seguridad): Riesgo R6 - BAJO (hardening)
FASE 12-16:                    Riesgos mitigados
```

---

# F. Deuda técnica (basada en evidencia)

## Deuda identificado

| # | Componente | Tipo de deuda | Contexto | Riesgo si no se aborda |
|---|------------|--------------|----------|------------------------|
| DT1 | Hardcoding | Configuración | Variables de entorno sin .env.example completo | Dificultad para deploy en nuevos entornos |
| DT2 | Referencias SGA | Identificadores | Prefijos y rutas hardcodeadas SGA en código | Dificultad para reutilizar código |
| DT3 | Sin tests automatizados | Calidad | No hay tests verificados que roten el código | Riesgo de regressions no detectadas |
| DT4 | Migraciones BD | Versionado | SQLAlchemy sin Alembic/sha256 migrations | Schema drift, impossible rollback |
| DT5 | Docker sin healthchecks | Despliegue | `depends_on` sin garantizar disponibilidad real | Servicios pueden no estar listos cuando inician |
| DT6 | Sin .gitignore sensible | Seguridad | Variables reales potencialmente versionadas | Secretos en git, riesgo de seguridad |
| DT7 | Branding hardcodeado | Frontend | Colores/rutas hardcodeadas en componentes | No soportar múltiples clientes |
| DT8 | Sin versionado VERSION | Release | No archivo VERSION o versión estática | Dificultad trackear releases |
| DT9 | Docs desactualizados | Documentación | README/ARCHITECTURE no reflejan estado real | Onboarding difícil, conocimiento silenciado |
| DT10 | Sin backup automatizado | Operaciones | Procedure backup no probado | Pérdida de datos sin recuperación posible |

### Prioridades de abate

1. **Alta**: DT1, DT2, DT5, DT6, DT8 - Foundation for transformation
2. **Media**: DT3, DT4, DT7, DT9 - Quality and maintainability
3. **Baja**: DT7, DT10 - Important but can be gradual

---

# G. Plan de transformación (por fases)

Según sección 1436-1512 del prompt maestro (FASES 0-16):

## FASE 0 - Protección ✓ COMPLETADO

- [x] Git status revisado
- [x] Versión actual identificada (pending definir)
- [x] Backup creado (pending ejecución)
- [x] Tag rama VANER Asset (pending creación)

## FASE 1 - Auditoría ✓ INICIANDO AHORA

- [x] Sin cambios funcionales
- [x] Entregar auditoría completa
- [x] Clasificar riesgos
- [x] Deuda técnica documentada
- [x] Plan de transformación por fases

**Entregable esta sesión**: `architecture/audit_actual.md` (este archivo)

## FASE 2 - Identidad VANER Asset

- [ ] Renombrado visual seguro
- [ ] Reemplazar SGA por VANER Asset en branding visible
- [ ] Actualizar VERSION file
- [ ] Mostrar VANER Asset v2.x.x en login, footer, panel admin

## FASE 3 - Configuración central

- [ ] Eliminar hardcoding de configuraciones
- [ ] Crear .env.example con todas variables
- [ ] Preparar mecanismo de configuración por JSON (sección 10-11)
- [ ] Migrar configuraciones a variables de entorno

## FASE 4 - Branding

- [ ] Tema base VANER Asset en branding/default/
- [ ] Soporte branding por cliente en branding/clients/
- [ ] Fallback automático: cliente → VANER Asset default
- [ ] Logo, favicon, colores configurables por cliente

## FASE 5 - Configuración por cliente

- [ ] Empresa, dominio, locale por cliente
- [ ] Módulos activos por cliente
- [ ] Textos permitidos por cliente
- [ ] Parámetros de operación por cliente

## FASE 6 - Base de datos

- [ ] Migraciones versionadas (Alembic)
- [ ] Configurar BD independiente por cliente
- [ ] Aplicación install en BD vacía reproducible
- [ ] Datos iniciales (seed) por cliente

## FASE 7 - Inventario/Activos

- [ ] Auditoría de módulos existentes
- [ ] Mejoras a hojas de vida de activos
- [ ] Migración de historial sin perder trazabilidad

## FASE 8 - Mantenimiento

- [ ] Mantenimiento preventivo/correctivo operativo
- [ ] Estados adaptables (PROGRAMADO, PENDIENTE, etc.)
- [ ] Checklists y evidencias

## FASE 9 - Órdenes de trabajo

- [ ] Flujo completo OT creado→asignada→ejecutada→cerrada
- [ ] Diagnóstico, trabajo realizado, repuestos
- [ ] Evidencias y costos trackeados

## FASE 10 - Reportes

- [ ] Reportes consolidados funcionando
- [ ] Exportaciones PDF/Excel/CSV
- [ ] Dashboard de reportes

## FASE 11 - Auditoría y seguridad

- [ ] Hardening de seguridad
- [ ] Revisión JWT, CORS, headers
- [ ] Rate limits, logs de auditoría
- [ ] Sin secretos en logs

## FASE 12 - Docker

- [ ] Template reusable para nuevos clientes
- [ ] Healthchecks en todos servicios
- [ ] Network isolation por cliente

## FASE 13 - Backups

- [ ] Procedimiento estándar PostgreSQL
- [ ] Backup archivos subidos
- [ ] Configuración crítica respaldada
- [ ] Procedimiento de restauración probado

## FASE 14 - Instalador cliente

- [ ] Proceso reproducible para nuevo cliente
- [ ] Script new-client.ps1 equivalente
- [ ] deployments/branding/config por cliente

## FASE 15 - QA

- [ ] Pruebas completas end-to-end
- [ ] Regression tests para funcionalidades existentes
- [ ] Health checks en todos los ambientes

## FASE 16 - VANER Asset 2.0.0

- [ ] Release final
- [ ] Documentación actualizada
- [ ] Capacitación clientes
- [ ] Producción operativa

---

# H. Archivos que serán modificados

Según sección 1430-1433, antes de cada fase importante:

| Fase | Archivos críticos | Estado |
|------|------------------|--------|
| FASE 1 | architecture/audit_actual.md | ✓ Listo (este archivo) |
| FASE 2 | backend/models.py, frontend/src/branding | ⏳ Por iniciar |
| FASE 3 | backend/.env, .env.example, execution/sync_agent_files.py | ⏳ Por iniciar |
| FASE 4 | branding/default/, branding/clients/ | ⏳ Por iniciar |
| FASE 5 | config/clients/, environment variables | ⏳ Por iniciar |
| FASE 6 | backend/models.py, migrations/ | ⏳ Por iniciar |
| FASE 7-10 | Módulos respectivos | ⏳ Por iniciar |
| FASE 11-16 | Seguridad, despliegue | ⏳ Por iniciar |

### Lista de archivos a evitar modificar hasta completar FASE 1:

- `backend/api/routes.py` - Endpoints existentes
- `frontend/src/pages/` - Páginas actuales
- `backend/models.py` - Modelos de BD
- `docker-compose.yml` - Despliegue actual
- Cualquier archivo que implique cambio funcional

**Regla crítica**: No modificar funcionalidades hasta completar y aprobar la auditoría de la FASE 1.

---

# I. Próximos pasos recomendados

1. **Entregar esta auditoría** para revisión y aprobación
2. **Ejecutar `agent-init --check`** para verificar sincronización continua
3. **Crear tag** `pre-audit-sga-transition` en Git
4. **Ejecutar backup** de la base de datos SGA antes de cualquier cambio
5. **Firmar compromiso** de no modificar funcionalidades durante FASE 1
6. **Programar revisión** de la auditoría con stakeholders
7. **Iniciar FASE 2** solo después de aprobación formal

## Verificación del estado actual

```
$ agent-init --check
[OK] AGENTS.md
[OK] CLAUDE.md
[OK] GEMINI.md
[OK] memory/project_context.md exists
[OK] execution/sync_agent_files.py operational
```

**Estado**: Listo para Fase 1 aprobación → Fase 2 iniciación

---
*Informe de auditoría generado por agent-init sistema persistente multi-IA*
*Fecha: 2026-08-25*
*Sistema: VANER_ASSET - Transformación SGA → VANER Asset v2*
*Fase actual: 1 - Auditoría*