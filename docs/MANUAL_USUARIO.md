# Manual de Usuario — SGAHolding (SGA SaaS)

Sistema SaaS de Gestión de Mantenimiento Asistido por Computadora (GMAO/CMMS) para administrar empresas, sedes, activos, órdenes de trabajo y evidencias técnicas.

**Plataforma web:** `https://sgaholding.online`
**Versión de referencia:** v1.0.14

---

## Tabla de contenido

1. [Introducción](#1-introducción)
2. [Acceso al sistema](#2-acceso-al-sistema)
3. [Roles y perfiles](#3-roles-y-perfiles)
4. [Conceptos clave del GMAO](#4-conceptos-clave-del-gmao)
5. [Portal Administrador](#5-portal-administrador)
6. [Portal Coordinador](#6-portal-coordinador)
7. [Portal Técnico](#7-portal-técnico)
8. [Portal Cliente (Empresa)](#8-portal-cliente-empresa)
9. [Flujo de trabajo de un mantenimiento](#9-flujo-de-trabajo-de-un-mantenimiento)
10. [Seguridad y buenas prácticas](#10-seguridad-y-buenas-prácticas)
11. [Preguntas frecuentes](#11-preguntas-frecuentes)

---

## 1. Introducción

SGAHolding permite gestionar de forma centralizada el mantenimiento de equipos de múltiples empresas (multi-tenant). Cada usuario trabaja sobre los datos que le corresponden según su rol:

- **Administradores** configuran el sistema, las empresas clientes y supervisan la operación completa.
- **Coordinadores** administran inventario, hojas de vida, mantenimientos, evidencias y reportes de las empresas que tienen asignadas.
- **Técnicos** ejecutan los mantenimientos asignados y registran evidencias.
- **Clientes / Empresas** consultan el estado de sus equipos, mantienen su hoja de vida, reportan emergencias y descargan reportes aprobados.

---

## 2. Acceso al sistema

### 2.1 Ingreso

1. Abra el navegador y diríjase a `https://sgaholding.online`.
2. En la pantalla de **Inicio de sesión**, ingrese:
   - **Usuario o correo** (no distingue mayúsculas/minúsculas).
   - **Contraseña** (el campo permite mostrar/ocultar el texto con el ícono del ojo).
3. Pulse **Ingresar**.

El sistema lo redirigirá automáticamente a su portal según su rol:

| Rol       | Destino                     |
|-----------|-----------------------------|
| ADMIN     | `/admin/dashboard`          |
| COORDINADOR | `/coordinador/dashboard`   |
| TECNICO   | `/tecnico/dashboard`        |
| EMPRESA / CLIENTE | `/cliente/dashboard` |

### 2.2 Recuperar contraseña

1. En la pantalla de login pulse **¿Olvidó su contraseña?**.
2. Ingrese su correo electrónico registrado.
3. Recibirá un enlace en su correo para restablecer la contraseña.
4. La nueva contraseña debe tener **mínimo 12 caracteres** y debe confirmarla escribiéndola dos veces.

### 2.3 Cerrar sesión

Pulse **Cerrar sesión** en el menú lateral de su portal. Es recomendable cerrar sesión siempre que se abandone un equipo compartido.

---

## 3. Roles y perfiles

| Rol          | Descripción |
|--------------|-------------|
| **ADMIN**    | Acceso total. Administra empresas, sedes, categorías, técnicos, usuarios, equipos, mantenimientos, evidencias, reportes, facturación, plantillas PDF, auditoría y los módulos inteligentes del sistema. |
| **COORDINADOR** | Gestión operativa de inventario, hojas de vida, mantenimientos, evidencias, informes y reportes publicados. Puede atender una o varias empresas asignadas. |
| **TECNICO**  | Ejecuta los mantenimientos asignados en su bandeja, diligenciando el formato técnico y cargando evidencias (fotos/PDF). |
| **EMPRESA / CLIENTE** | Visualiza el estado de su empresa, sedes y equipos, consulta el cronograma, reporta emergencias y descarga reportes aprobados. |

---

## 4. Conceptos clave del GMAO

- **Empresa:** cliente o compañía registrada en la plataforma. Es el nivel más alto del modelo de datos.
- **Sede:** ubicación física o filial de una empresa (planta, bodega, oficina, sucursal, etc.).
- **Categoría:** clasificación de equipos por tipo, alcance y uso (ej. eléctrico, mecánico, HVAC).
- **Equipo / Activo:** máquina o elemento del inventario que requiere mantenimiento (bom: código, serie, marca, modelo, estado, criticidad).
- **Hoja de vida:** historial técnico del equipo (datos de adquisición, datos técnicos, mantenimientos realizados y documento de vida del activo).
- **Mantenimiento / Orden de trabajo:** intervención programada o correctiva sobre un equipo.
- **Evidencia:** registro fotográfico o PDF que soporta la ejecución del mantenimiento (etapas **ANTES**, **DURANTE** y **DESPUÉS**).
- **Cronograma:** agenda operativa con los mantenimientos organizados por fecha y estado.
- **Reporte:** informe de mantenimientos e indicadores que puede exportarse (Excel/PDF) y publicarse para el cliente.

---

## 5. Portal Administrador

Al ingresar como **ADMIN** verá el menú lateral con los siguientes módulos:

### 5.1 Dashboard general
Vista ejecutiva con KPIs (empresas, sedes, equipos, mantenimientos, técnicos activos), **salud operativa**, alertas (atrasados, próximos 7 días, equipos críticos, fuera de servicio), gráficas (mantenimientos por mes, equipos por estado, carga por técnico) y accesos rápidos.

- Botón **Actualizar** refresca los datos.
- Botón **Nuevo control** va directo a crear un mantenimiento.
- La **Vista rápida inteligente** permite buscar y navegar registros de empresas, sedes, equipos, mantenimientos, técnicos y alertas, con paginación y ajuste de filas por página.

### 5.2 Empresas
Alta, edición y baja de empresas clientes.

- **Crear empresa:** nombre, NIT, teléfono, correo, estado y datos de contacto.
- **Editar** o **desactivar** empresas desde el listado.
- Al crear la empresa se pueden asociar sedes, equipos y usuarios.

### 5.3 Sedes
Registra las ubicaciones de cada empresa (dirección, teléfono, empresa propietaria). El dashboard enlaza cada sede con su cantidad de equipos y mantenimientos.

### 5.4 Categorías
Clasifica los equipos por tipo y alcance. Cada categoría incluye nombre y descripción del tipo de equipos que agrupa.

### 5.5 Técnicos
Administra el catálogo de técnicos (especialidad, contacto, estado activo/inactivo). El dashboard muestra su carga de trabajo (mantenimientos asignados, activos y finalizados).

### 5.6 Usuarios
Crea y administra las cuentas de acceso del sistema.

- Asigne **rol** (ADMIN, COORDINADOR, TECNICO, EMPRESA, CLIENTE).
- Asocie el usuario a una **empresa** cuando corresponda.
- Active o desactive cuentas según necesidad.

### 5.7 Equipos (Inventario)
Registro y consulta del inventario de equipos por empresa y sede.

- **Crear equipo:** nombre, código/inventario, serie, marca, modelo, estado, criticidad y ubicación (empresa/sede).
- Busque y filtre por nombre, inventario, código, serie, marca o ubicación.
- Desde la **hoja de vida** accede al historial completo del activo.

### 5.8 Hoja de vida de equipo
Documento técnico del activo con:

- Datos generales y de adquisición (tipo, costo, vida útil estimada).
- Datos técnicos y de placa.
- Historial de mantenimientos y estado del equipo.
- Volver al listado de equipos desde el botón correspondiente.

### 5.9 Mantenimientos
Centro de control de órdenes de trabajo.

- **Crear mantenimiento** (preventivo, correctivo u otro tipo) seleccionando empresa, sede, equipo, técnico, tipo, fecha programada y estado inicial.
- **Estados:** Programado → Asignado → En proceso → Pausado → Finalizado / Anulado.
- Cambio de estado con observación (p. ej. pasar a **En proceso** con el motivo).
- Filtros por estado, tipo, fecha, empresa, sede y técnico.

### 5.10 Evidencias
Consultas de las evidencias cargadas por los técnicos.

- Filtros por tipo de evidencia (**ANTES**, **DURANTE**, **DESPUÉS**), equipo o mantenimiento.
- Vista previa y descarga de imágenes y PDFs.

### 5.11 Reportes PRO
Indicadores y exportación de mantenimientos.

- **Exportar** a **Excel** o **PDF** el listado general o un mantenimiento específico.
- Filtros por estados y fechas.

### 5.12 Facturación
Gestión de facturas de las empresas clientes (creación, edición y estado de cobros).

### 5.13 Plantillas PDF
Personaliza la apariencia de los reportes corporativos (colores, títulos, tipo AMBOS / OT / MENSUAL). Marque la plantilla como **ACTIVA** o **INACTIVA**.

### 5.14 Auditoría PRO
Consulta de la trazabilidad de eventos del sistema (quién, qué y cuándo). Herramienta de control y compliance.

### 5.15 Configuración del Sistema
Centro de configuración SaaS con acceso a los módulos inteligentes:

| Módulo | Descripción |
|--------|-------------|
| Centro Sistema / Configuración General | Parámetros globales, branding y configuración del sistema. |
| Recovery & Restore PRO | Backups PostgreSQL, restauración inteligente y recuperación. |
| Configuración Inteligente | Automatización SaaS y comportamiento inteligente. |
| Backups Inteligentes | Respaldos de base de datos, descarga y restauración segura. |
| SMTP Inteligente | Correos corporativos, plantillas y notificaciones. |
| Monitor VPS + PostgreSQL | Estado del servidor, Docker, CPU, RAM y PostgreSQL. |
| Logs Inteligentes | Eventos, errores, trazabilidad y monitoreo. |
| DevOps SaaS PRO | Contenedores, infraestructura y salud del sistema. |
| Seguridad PRO | Auditoría, permisos y hardening del sistema. |
| Scheduler Inteligente | Automatización avanzada de mantenimientos. |
| BI Ejecutivo | Business Intelligence, KPIs y análisis empresarial. |
| Multiempresa Enterprise | Gestión de múltiples empresas con accesos directos a sus datos. |

---

## 6. Portal Coordinador

Menú siempre visible con: **Dashboard, Mantenimientos, Cronograma, Inventario/Equipos, Hojas de vida, Evidencias, Reportes, Aprobar y publicar**.

- **Selector de empresa activa:** si el coordinador tiene varias empresas autorizadas, seleccione cuál está gestionando en la barra superior. Los datos mostrados se ajustan automáticamente.

### 6.1 Dashboard
Resumen operativo de mantenimientos, técnicos, estados e inventario de la empresa activa.

### 6.2 Mantenimientos
Consulta, filtrado y control de las órdenes de trabajo de la empresa activa.

### 6.3 Cronograma
Agenda operativa por fechas y estados, con filtros por empresa, sede, técnico y tipo de mantenimiento. Permite ver eventos agrupados por día.

### 6.4 Inventario / Equipos
Consulta del inventario de la empresa activa con búsqueda por nombre, inventario, código, serie, marca o ubicación.

### 6.5 Hojas de vida
Visualización y edición de la hoja de vida de los equipos:

- Datos de adquisición (compra, comodato, donación; costo; vida útil estimada).
- Datos técnicos del equipo.
- Acceso al historial de mantenimientos del activo.

### 6.6 Evidencias
Revisión de las evidencias cargadas por los técnicos en los mantenimientos de la empresa activa.

### 6.7 Reportes (Informes)
Genera y descarga informes operativos de mantenimientos e indicadores.

### 6.8 Aprobar y publicar
Revisa los reportes generados, los **aprueba** y los **publica** para que el cliente pueda consultarlos desde su portal.

---

## 7. Portal Técnico

### 7.1 Bandeja de mantenimientos
El técnico ve los mantenimientos asignados en su **Dashboard técnico**:

- Tabs por estado (activos, pendientes, finalizados, etc.).
- Búsqueda por equipo, empresa, sede, código, serie, tipo o estado.
- Acceso al **histórico** de mantenimientos finalizados.

### 7.2 Ejecución técnica
Al abrir un mantenimiento asignado, el técnico puede:

1. Registrar **diagnóstico inicial** (estado del equipo al llegar).
2. Documentar **actividades realizadas**.
3. Registrar **resultado final / recomendaciones**.
4. Agregar **repuestos** y **referencias** utilizados.
5. Registrar **incidencias** encontradas.
6. Cargar **evidencias** en las etapas **ANTES**, **DURANTE** y **DESPUÉS** (imágenes y PDF).
7. **Finalizar** el mantenimiento.

### 7.3 Formato de mantenimiento
Formato técnico estructurado (checklist) según el tipo de mantenimiento, con:

- Checklist de limpieza y control eléctrico.
- Pruebas de funcionamiento y lecturas (voltaje, presión, temperatura).
- Observaciones técnicas.
- Repuestos y cantidades.
- Impresión del formato para archivo físico (botón **Imprimir**).

### 7.4 Bitácora dinámica
Registro dinámico del estado operativo del equipo (operativo, fuera de servicio, intermitente), código, descripción, cantidad, serial y recomendaciones para el próximo mantenimiento.

---

## 8. Portal Cliente (Empresa)

Menú: **Dashboard, Sedes, Hoja de vida equipos, Mantenimientos, Cronograma, Emergencias, Reportes aprobados**.

### 8.1 Dashboard
Resumen del estado de la empresa: equipos, mantenimientos, indicadores y alertas de la compañía.

### 8.2 Sedes
Consulta las sedes de su empresa y su información de contacto.

### 8.3 Hoja de vida equipos
Consulta la hoja de vida de sus equipos (datos técnicos, adquisición e historial de mantenimientos).

### 8.4 Mantenimientos
Consulta el estado de las órdenes de trabajo de su empresa: programadas, en proceso, finalizadas y anuladas.

### 8.5 Cronograma
Calendario/agenda con los mantenimientos programados de su empresa. Búsqueda por equipo, tipo, estado, técnico o fecha.

### 8.6 Emergencias (Solicitudes correctivas)
Reporte de emergencias o fallas de equipos:

1. Seleccione la **sede** y luego el **equipo** afectado.
2. Describa el problema (**título** y **descripción**).
3. Indique **prioridad** (por defecto *EMERGENCIA*).
4. Deje un **contacto** (nombre y teléfono) de la persona que reporta.
5. Pulse **Enviar**.

La solicitud queda registrada y visible en el listado para su seguimiento. Si el dispositivo no tiene conexión, la solicitud se encola y se envía automáticamente al recuperar la conectividad.

### 8.7 Reportes aprobados
Consulta y descarga los reportes que el coordinador ha **aprobado y publicado** para su empresa.

---

## 9. Flujo de trabajo de un mantenimiento

```
1. ADMIN/COORDINADOR crea el mantenimiento (empresa, sede, equipo, tipo, fecha)
        │  Estado: PROGRAMADO
        ▼
2. Se asigna a un técnico          Estado: ASIGNADO
        │
        ▼
3. El técnico inicia la ejecución  Estado: EN_PROCESO
        │    - Diligencia formato técnico
        │    - Registra repuestos / incidencias
        │    - Carga evidencias (ANTES / DURANTE / DESPUÉS)
        ▼
4. Opcional: pausa                  Estado: PAUSADO
        │
        ▼
5. El técnico finaliza             Estado: FINALIZADO
        │    - Resultado y recomendaciones
        ▼
6. COORDINADOR revisa evidencias, genera informe
        ▼
7. COORDINADOR aprueba y publica el reporte
        ▼
8. El CLIENTE consulta el reporte aprobado en su portal
```

---

## 10. Seguridad y buenas prácticas

- **Contraseñas:** use contraseñas de al menos 12 caracteres. No las comparta ni las reutilice en otros sistemas.
- **Cuentas:** no comparta su usuario. Si abandona la compañía, notifique al administrador para desactivar la cuenta.
- **Cierre de sesión:** siempre cierre sesión en equipos compartidos o públicos.
- **Evidencias:** cargue solo archivos de soporte técnico válidos (imágenes o PDF). Verifique que las fotos sean legibles y relevantes.
- **Datos sensibles:** no registre información de tarjetas, contraseñas o datos personales en campos de observación o descripción.
- **Backups:** los respaldos del sistema son automáticos e inteligentes; ante cualquier duda contacte al administrador del sistema.

---

## 11. Preguntas frecuentes

**¿Olvidé mi contraseña?**
Pulse **¿Olvidó su contraseña?** en el login, ingrese su correo y siga el enlace que recibirá.

**¿Por qué veo una pantalla de "No autorizado"?**
Su usuario no tiene permiso para esa sección. Contacte al administrador para ajustar su rol o permisos.

**¿Cómo reporto un equipo dañado?**
En el Portal Cliente vaya a **Emergencias**, seleccione sede y equipo, describa el problema y envíe la solicitud.

**¿Qué evidencias debo cargar en un mantenimiento?**
Como mínimo una evidencia de cada etapa: **ANTES** (estado inicial), **DURANTE** (trabajo en ejecución) y **DESPUÉS** (resultado final).

**¿Cómo publico un reporte para el cliente?**
Desde el Portal Coordinador, en **Reportes** genere el informe y luego pase a **Aprobar y publicar** para habilitarlo al cliente.

**¿El sistema funciona sin conexión?**
Las solicitudes de emergencia del cliente se encolan localmente y se envían cuando se restablece la conexión. El resto de funciones requiere conexión a internet.