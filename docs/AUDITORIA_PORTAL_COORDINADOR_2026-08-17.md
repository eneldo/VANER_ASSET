# Auditoria tecnica y funcional - Portal Coordinador

Fecha: 17 de agosto de 2026

## Alcance

- Navegacion y control de acceso del portal Coordinador.
- Hoja de vida de equipos.
- Modulo de mantenimientos comparado con Administrador.
- Listado y exportacion de inventario.
- Aislamiento multiempresa por `empresa_id`.
- Contratos frontend/backend, persistencia y trazabilidad.
- Pruebas de regresion, compilacion y lint.

## Resumen ejecutivo

La salida aparente de la plataforma al abrir Hoja de Vida era causada por dos rutas incompatibles y un fallback global que enviaba cualquier URL no reconocida al login. El modulo de mantenimientos del Coordinador era una implementacion duplicada y reducida, por lo que habia divergido del modulo profesional de Administrador. Ademas, varios campos visibles de la bitacora profesional no se enviaban o no se devolvian, y la fecha programada perdia la hora en el backend administrativo.

La correccion elimina la duplicacion del frontend de mantenimientos, agrega un adaptador por rol, incorpora seleccion segura entre empresas autorizadas, mantiene el filtrado RLS del tenant activo, agrega inventario profesional con exportacion filtrada y rediseña la Hoja de Vida como centro dinamico del ciclo de vida del activo.

## Hallazgos y estado

| ID | Severidad | Hallazgo | Estado |
| --- | --- | --- | --- |
| COORD-001 | Critica | El boton de equipo navegaba a `/coordinador/equipos/:id/hoja-vida`, pero la aplicacion declaraba `/coordinador/hoja-vida/:id`. | Corregido |
| COORD-002 | Critica | `CoordinadorHojaVida` esperaba `equipoId`, mientras la ruta usaba el parametro `id`. | Corregido |
| COORD-003 | Alta | El fallback global enviaba rutas invalidas a `/`, mostrando Login aunque la sesion siguiera activa. | Corregido con redireccion al dashboard del rol |
| COORD-004 | Alta | Coordinador mantenia una copia reducida del modulo de mantenimientos y no heredaba mejoras de Administrador. | Corregido; ambos usan el mismo componente profesional |
| COORD-005 | Alta | Coordinador no tenia exportacion de inventario. | Corregido con Excel filtrado por tenant |
| COORD-006 | Alta | Campos profesionales visibles no se persistian: fechas de inicio/fin programadas, estado inicial, acciones, resultado y coordenadas. | Corregido en frontend, schemas, alta, edicion y serializacion |
| COORD-007 | Alta | La normalizacion administrativa convertia `datetime` a `date` y eliminaba la hora. | Corregido |
| COORD-008 | Alta | Las rutas administrativas del frontend solo verificaban sesion, no rol. | Corregido con guardas `RoleRoute` |
| COORD-009 | Media | El layout Coordinador consultaba `/permisos/me`, endpoint registrado como ADMIN, generando un 403 innecesario. | Corregido; el rol base no hace esa llamada |
| COORD-010 | Media | El CRUD Coordinador no aplicaba todas las validaciones de estado, criticidad, inventario y codigo ya existentes en Admin. | Corregido |
| COORD-011 | Media | La creacion de mantenimiento del Coordinador no registraba evento inicial de historial. | Corregido |
| COORD-012 | Media | Un payload manual podia intentar enviar una sede distinta al equipo en mantenimiento. | Corregido; Coordinador hereda empresa y sede del equipo |
| COORD-013 | Critica | Un Coordinador con alcance sobre varias empresas no tenia un mecanismo seguro para cambiar de tenant. | Corregido con asignaciones `usuario_empresas`, cabecera validada y contexto RLS por solicitud |
| COORD-014 | Alta | El inventario se presentaba en tarjetas poco eficientes para operacion masiva. | Corregido con tabla, filtros, paginacion, detalle, edicion y acciones directas |
| COORD-015 | Alta | La Hoja de Vida no mostraba todos los campos existentes ni el historial del equipo. | Corregido con seis secciones, campos completos e historial de mantenimientos |
| COORD-016 | Media | El formulario de mantenimiento de Coordinador exponia datos propios de ejecucion tecnica. | Corregido; se ocultan coordenadas, estado inicial, acciones y resultado final |
| COORD-017 | Alta | El primer helper multiempresa se ubico bajo una carpeta que colisionaba con `app/security.py`. | Corregido al moverlo a `app/services/coordinador_empresas.py` y validado con import real de FastAPI |

## Cambios aplicados

- Rutas canonicas y compatibles para Hoja de Vida, con seleccion general o por equipo.
- Fallback autenticado y consciente del rol.
- Modulo unico de mantenimientos con modo `admin` o `coordinador`.
- Selector global de empresa para Coordinador, limitado a empresas asignadas por Administrador.
- Cabecera `X-Empresa-Activa` validada en backend antes de cambiar el contexto RLS.
- Empresa principal deterministica como seleccion predeterminada.
- Asignacion multiempresa desde el CRUD administrativo de usuarios.
- Adaptador de endpoints para cargar catalogos, crear, editar, asignar tecnico, reabrir y eliminar.
- Formulario de Coordinador simplificado: conserva planeacion y costo opcional, pero no solicita datos de ejecucion tecnica.
- Persistencia completa de la bitacora profesional.
- Exportacion Excel desde `/coordinador/equipos/exportar`.
- Exportacion limitada al tenant activo y compatible con filtros de busqueda, sede, categoria, estado y criticidad.
- Inventario en tabla profesional con detalle, edicion, Hoja de Vida y acceso a mantenimiento.
- Hoja de Vida con identificacion, adquisicion, ficha tecnica adaptativa, documentacion, mantenimientos, calibracion y riesgo.
- Autoguardado con debounce, guardado manual, indicador de estado y porcentaje de completitud.
- Historial del equipo cargado directamente desde mantenimientos y opcion de impresion/PDF del navegador.
- Validaciones equivalentes de inventario, codigo, estado y criticidad.
- Guardas de rol para Admin, Tecnico, Cliente y Coordinador.
- Pruebas nuevas de rutas, schemas, fecha/hora, herencia, exportacion, Hoja de Vida y autorizacion multiempresa.

## Evidencia de validacion

- Backend: 127 pruebas aprobadas.
- Frontend: 44 pruebas aprobadas.
- Frontend: build de produccion aprobado.
- Frontend: ESLint completo aprobado.
- Backend: compilacion de `app` y `tests` aprobada.
- Backend: import real de FastAPI aprobado con 229 rutas registradas.
- Alembic: `j60f8b310001` validada como unica cabeza de migracion.

## Riesgos residuales

- No se realizo prueba visual con datos reales porque los servicios locales `5173` y `8000` estaban detenidos.
- No se ejecuto una prueba integrada contra PostgreSQL con un tenant real; las pruebas cubren rutas, contratos y logica aislada.
- No se ejecuto `alembic upgrade head` sobre una base de datos desconocida para evitar modificar un entorno posiblemente productivo.
- El entorno local usa un rol de aplicacion sin permisos DDL y no tiene `MIGRATION_DATABASE_URL`; mientras se configura el rol propietario, el login mantiene compatibilidad con el esquema anterior usando la empresa principal del Coordinador.
- La variable externa `DEBUG=release` es invalida para Pydantic; las pruebas backend requirieron `DEBUG=false`. Debe corregirse en el entorno que la inyecta.
- Los permisos del Coordinador siguen siendo amplios en el frontend base. Si se requiere segregacion fina, debe definirse una matriz por accion y no solo por modulo.

## Optimizaciones recomendadas

### Prioridad 1

1. Agregar prueba E2E con usuarios sembrados ADMIN, COORDINADOR, TECNICO y EMPRESA.
2. Registrar auditoria de cada exportacion: usuario, empresa, fecha, filtros, cantidad y nombre del archivo.
3. Llevar filtros y paginacion de equipos/mantenimientos al backend para evitar cargar inventarios completos.
4. Corregir `DEBUG=release` en Docker, CI o variables del sistema.

### Prioridad 2

1. Centralizar politicas RBAC y tenant en dependencias reutilizables para reducir routers paralelos.
2. Extraer generacion de inventario Excel a un servicio de dominio en vez de importar utilidades entre routers.
3. Sustituir `alert`, `confirm` y `prompt` por modales y notificaciones consistentes.
4. Agregar repositorio documental para adjuntar archivos reales a manuales, planos y certificados de calibracion.

### Prioridad 3

1. Generar exportaciones grandes en segundo plano y entregar enlace temporal.
2. Agregar metricas de tiempos de respuesta y errores por modulo/rol.
3. Crear una pagina 404 interna con contexto, en vez de redireccion silenciosa.

## Despliegue requerido

Antes de publicar esta version se debe respaldar la base de datos y ejecutar, en el backend y con `DEBUG=false`:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

La migracion `j60f8b310001_coordinador_multiempresa.py` crea `usuario_empresas`, indexa `empresa_id` y migra automaticamente la empresa principal de los Coordinadores existentes como primera asignacion autorizada.
