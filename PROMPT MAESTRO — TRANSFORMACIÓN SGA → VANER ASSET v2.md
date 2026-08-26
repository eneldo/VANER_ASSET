# PROMPT MAESTRO — TRANSFORMACIÓN DE SGA A VANER ASSET v2

## 1. IDENTIDAD DEL PROYECTO

Estás trabajando sobre un software existente y funcional llamado anteriormente:

**SGA**

Este software ya tuvo una primera versión desplegada en producción y utilizada por un cliente real.

A partir de ahora el producto evoluciona oficialmente a:

# VANER Asset

**VANER Asset** será un producto comercial reutilizable para diferentes organizaciones.

IMPORTANTE:

NO debes crear una aplicación nueva desde cero.

Debes:

1. analizar el proyecto existente;
2. preservar toda funcionalidad útil;
3. identificar código específico del cliente original;
4. desacoplar la aplicación de dicho cliente;
5. convertir el software en un producto reutilizable;
6. conservar compatibilidad cuando sea razonablemente posible;
7. mejorar progresivamente arquitectura, seguridad, mantenibilidad y despliegue;
8. documentar todo cambio importante;
9. validar que las funciones existentes continúen funcionando.

---

# 2. OBJETIVO PRINCIPAL DE VANER ASSET

VANER Asset es una plataforma web empresarial destinada al:

## Control de inventarios, activos y mantenimiento.

Su propósito principal es permitir que una organización conozca en todo momento:

- qué activos posee;
- qué equipos tiene;
- dónde se encuentran;
- en qué estado están;
- quién es responsable de ellos;
- cuándo fueron adquiridos;
- cuál es su historial;
- qué mantenimientos requieren;
- cuáles mantenimientos se realizaron;
- cuáles están próximos o vencidos;
- qué técnicos participaron;
- qué repuestos o materiales fueron utilizados;
- qué evidencias existen;
- qué costos están asociados;
- qué movimientos ha tenido cada activo;
- qué alertas requieren atención;
- qué información necesita la administración para tomar decisiones.

VANER Asset debe convertirse en el punto central de información durante todo el ciclo de vida de los activos.

---

# 3. VISIÓN DEL PRODUCTO

VANER Asset deberá evolucionar hacia una plataforma profesional capaz de ser utilizada por diferentes empresas sin crear una versión distinta del código para cada cliente.

La arquitectura conceptual será:

```text
                    VANER ASSET CORE
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          Cliente A    Cliente B    Cliente C
              │            │            │
          Branding      Branding      Branding
          Config.       Config.       Config.
          Base datos    Base datos    Base datos
          VPS propio    VPS propio    VPS propio
          Dominio       Dominio       Dominio
```

Debe existir:

**UN SOLO CÓDIGO FUENTE DE VANER ASSET.**

No crear:

```text
VANER_Cliente_A
VANER_Cliente_B
VANER_Cliente_C
```

como copias independientes del producto.

---

# 4. MODELO DE DESPLIEGUE INICIAL

VANER Asset NO será inicialmente un SaaS multi-tenant compartiendo una misma instalación.

El modelo inicial será:

## Single Tenant por instalación

Cada cliente tendrá preferiblemente:

- su propio VPS;
- su propia instalación Docker;
- su propia base de datos;
- sus propios archivos;
- sus propios backups;
- su propio dominio o subdominio;
- su configuración;
- su branding.

Todos utilizarán el mismo VANER Asset Core.

Ejemplo:

```text
CLIENTE A

asset.empresa-a.com
        │
        ▼
VPS Cliente A
├── VANER Asset Frontend
├── VANER Asset Backend
├── PostgreSQL Cliente A
├── almacenamiento Cliente A
└── backups Cliente A
```

Segundo cliente:

```text
CLIENTE B

asset.empresa-b.com
        │
        ▼
VPS Cliente B
├── mismo VANER Asset Frontend
├── mismo VANER Asset Backend
├── PostgreSQL Cliente B
├── almacenamiento Cliente B
└── backups Cliente B
```

Los datos de diferentes clientes nunca deben mezclarse.

---

# 5. PRINCIPIO DE PRODUCTO CENTRAL

Debe existir claramente una separación entre:

```text
VANER Asset Core
```

y:

```text
Configuración del cliente
```

El Core contendrá:

- lógica empresarial;
- autenticación;
- autorización;
- usuarios;
- inventario;
- activos;
- mantenimiento;
- órdenes de trabajo;
- reportes;
- auditoría;
- APIs;
- reglas de negocio;
- dashboards;
- seguridad;
- notificaciones;
- servicios compartidos.

La configuración por cliente contendrá:

- nombre;
- NIT;
- logo;
- favicon;
- colores;
- fondo del login;
- información institucional;
- dominio;
- correo;
- zona horaria;
- configuración visual;
- módulos activos;
- textos permitidos;
- parámetros de operación.

---

# 6. IDENTIDAD DE PRODUCTO

La marca del software es:

# VANER Asset

Descripción oficial:

> Plataforma para la gestión, control y trazabilidad de inventarios, activos y mantenimiento.

Versión comercial inicial:

```text
VANER Asset 2.0
```

La versión deberá poder mostrarse dentro del software:

```text
VANER Asset v2.x.x
```

Idealmente en:

- login;
- footer;
- panel de administración;
- diagnóstico del sistema.

---

# 7. BRANDING POR CLIENTE

VANER Asset debe soportar personalización corporativa sin modificar el código fuente.

Cada cliente podrá definir:

- logo;
- favicon;
- nombre empresarial;
- colores corporativos;
- color primario;
- color secundario;
- color de acento;
- sidebar;
- pantalla de login;
- imagen/fondo de login;
- título de bienvenida;
- subtítulo;
- footer;
- nombre de instalación;
- ciertos elementos visuales del dashboard.

La estructura visual general debe continuar identificando a VANER Asset.

No crear un frontend completamente distinto para cada empresa.

---

# 8. TEMA BASE VANER ASSET

Debe existir:

```text
branding/default/
```

con la identidad oficial de VANER Asset.

Por ejemplo:

```text
branding/
├── default/
│   ├── logo.svg
│   ├── logo-dark.svg
│   ├── favicon.ico
│   ├── login-background.webp
│   └── theme.json
```

El tema por defecto será utilizado cuando un cliente no sobrescriba un elemento.

---

# 9. BRANDING DE CLIENTES

Preparar arquitectura para:

```text
branding/
└── clients/
    ├── cliente-a/
    │   ├── logo.svg
    │   ├── favicon.ico
    │   ├── login-background.webp
    │   └── theme.json
    │
    └── cliente-b/
        ├── logo.svg
        ├── favicon.ico
        ├── login-background.webp
        └── theme.json
```

No almacenar información privada innecesaria.

---

# 10. CONFIGURACIÓN DE TEMA

Crear un mecanismo equivalente a:

```json
{
  "product_name": "VANER Asset",
  "client_name": "Empresa ABC S.A.S.",
  "show_vaner_brand": true,

  "primary_color": "#123456",
  "secondary_color": "#456789",
  "accent_color": "#F5A623",
  "sidebar_color": "#0D1B2A",

  "login_title": "Bienvenido",
  "login_subtitle": "Gestión de activos y mantenimiento",

  "logo": "/branding/logo.svg",
  "favicon": "/branding/favicon.ico",
  "login_background": "/branding/login-background.webp",

  "footer_text": "Powered by VANER Asset"
}
```

Este JSON es conceptual.

Antes de implementarlo:

1. inspecciona la arquitectura actual;
2. reutiliza patrones existentes;
3. adapta la solución a React/Vite y al backend existentes;
4. evita duplicar mecanismos de configuración.

---

# 11. PRINCIPIO DE FALLBACK

La carga de branding debe funcionar conceptualmente así:

```text
¿Cliente tiene configuración?
          │
      ┌───┴───┐
      │       │
     Sí       No
      │       │
      ▼       ▼
Cliente     VANER Asset Default
```

Si falta:

```text
logo del cliente
```

usar:

```text
logo VANER Asset
```

Si falta:

```text
favicon cliente
```

usar:

```text
favicon VANER Asset
```

La aplicación no debe romperse porque falte un asset de personalización.

---

# 12. FUNCIONALIDADES PRINCIPALES

VANER Asset debe organizarse funcionalmente alrededor de los siguientes dominios.

---

# MÓDULO 1 — DASHBOARD

Debe proporcionar una visión ejecutiva del estado actual.

Indicadores potenciales:

- número total de activos;
- activos operativos;
- activos fuera de servicio;
- activos en mantenimiento;
- mantenimientos pendientes;
- mantenimientos vencidos;
- mantenimientos próximos;
- órdenes abiertas;
- órdenes cerradas;
- stock crítico;
- alertas;
- últimos movimientos;
- actividades recientes.

Debe permitir personalización controlada por cliente sin cambiar la estructura fundamental de VANER Asset.

---

# MÓDULO 2 — INVENTARIO

Objetivo:

Controlar los bienes, equipos, elementos, repuestos y demás recursos inventariables de la organización.

Debe contemplar, según lo que ya exista en SGA:

- registro de elementos;
- códigos internos;
- categorías;
- subcategorías;
- descripción;
- fabricante;
- marca;
- modelo;
- serial;
- cantidad;
- unidad de medida;
- ubicación;
- sede;
- responsable;
- estado;
- fecha de adquisición;
- proveedor;
- costo;
- garantía;
- observaciones;
- archivos relacionados.

Movimientos:

- entrada;
- salida;
- traslado;
- asignación;
- devolución;
- baja;
- ajuste.

Mantener trazabilidad de movimientos.

---

# MÓDULO 3 — ACTIVOS

El activo debe ser una entidad central.

Cada activo/equipo debería poder tener una hoja de vida.

Información potencial:

```text
Identificación
Código
Serial
Marca
Modelo
Categoría
Ubicación
Sede
Área
Responsable
Estado
Fecha de compra
Fecha de puesta en servicio
Proveedor
Garantía
Costo
Características técnicas
Documentos
Fotografías
Historial
Mantenimientos
Órdenes
Repuestos utilizados
Movimientos
```

El historial no debe perderse cuando cambie:

- responsable;
- ubicación;
- estado;
- mantenimiento;
- asignación.

---

# MÓDULO 4 — MANTENIMIENTO PREVENTIVO

Objetivo:

Evitar fallas mediante mantenimientos programados.

Debe considerar:

- planes de mantenimiento;
- periodicidad;
- frecuencia;
- activo;
- responsable;
- técnico;
- tareas;
- checklist;
- fecha programada;
- fecha ejecutada;
- estado;
- evidencia;
- observaciones;
- resultado;
- próxima fecha.

Estados posibles adaptables:

```text
PROGRAMADO
PENDIENTE
EN PROCESO
COMPLETADO
VENCIDO
CANCELADO
```

No modificar estados existentes arbitrariamente sin analizar impacto.

---

# MÓDULO 5 — MANTENIMIENTO CORRECTIVO

Debe permitir gestionar fallas y reparaciones.

Información:

- activo;
- falla;
- descripción;
- prioridad;
- fecha;
- solicitante;
- técnico;
- diagnóstico;
- causa;
- trabajo realizado;
- repuestos;
- costos;
- evidencias;
- tiempo fuera de servicio;
- solución;
- cierre.

---

# MÓDULO 6 — ÓRDENES DE TRABAJO

Las órdenes de trabajo deben ser parte central del flujo de mantenimiento.

Posibles datos:

```text
OT
Activo
Tipo
Prioridad
Estado
Técnico
Fecha creación
Fecha asignación
Fecha ejecución
Fecha cierre
Descripción
Diagnóstico
Trabajo realizado
Materiales
Repuestos
Horas
Evidencias
Observaciones
Costo
```

Estados controlados y auditables.

---

# MÓDULO 7 — REPUESTOS Y CONSUMIBLES

Relacionar inventario con mantenimiento.

Debe permitir saber:

- repuesto disponible;
- cantidad disponible;
- cantidad mínima;
- consumo;
- mantenimiento donde fue utilizado;
- activo donde fue utilizado;
- costo;
- fecha;
- responsable.

Cuando corresponda, el consumo generado desde mantenimiento debe producir movimiento de inventario de manera consistente y transaccional.

---

# MÓDULO 8 — UBICACIONES

La estructura debe soportar cuando sea necesario:

```text
Empresa
   ↓
Sede
   ↓
Área
   ↓
Ubicación
   ↓
Activo
```

No imponer niveles innecesarios si la aplicación existente utiliza una estructura diferente.

---

# MÓDULO 9 — RESPONSABLES

Registrar quién tiene asignado cada activo.

Mantener historial de:

- asignación;
- devolución;
- transferencia;
- fecha;
- responsable anterior;
- responsable nuevo.

---

# MÓDULO 10 — TÉCNICOS

Gestionar técnicos relacionados con mantenimiento.

Puede incluir:

- nombre;
- especialidad;
- estado;
- órdenes asignadas;
- mantenimientos realizados;
- productividad;
- historial.

Reutilizar módulo de usuarios si corresponde.

No duplicar personas/usuarios innecesariamente.

---

# MÓDULO 11 — PROVEEDORES

Cuando exista o sea necesario:

- información del proveedor;
- contacto;
- productos;
- repuestos;
- compras;
- servicios;
- mantenimientos contratados;
- historial.

---

# MÓDULO 12 — DOCUMENTOS Y EVIDENCIAS

Los activos y mantenimientos deben poder manejar archivos relacionados.

Ejemplos:

- factura;
- manual;
- garantía;
- fotografía;
- certificado;
- ficha técnica;
- evidencia de mantenimiento;
- acta;
- documento de entrega;
- informe.

Aplicar controles de:

- extensión;
- tamaño;
- permisos;
- almacenamiento;
- seguridad.

---

# MÓDULO 13 — ALERTAS

El sistema debe evolucionar hacia alertas de:

- mantenimiento próximo;
- mantenimiento vencido;
- garantía próxima a vencer;
- stock mínimo;
- activo fuera de servicio;
- orden retrasada;
- documentación pendiente.

No implementar sistemas complejos de notificación sin revisar primero la arquitectura existente.

---

# MÓDULO 14 — REPORTES

Debe permitir reportar información relevante.

Ejemplos:

- inventario general;
- activos por sede;
- activos por estado;
- activos por responsable;
- mantenimientos realizados;
- mantenimientos pendientes;
- mantenimiento por activo;
- órdenes de trabajo;
- costos;
- consumo de repuestos;
- historial del activo.

Idealmente exportaciones cuando ya estén soportadas:

```text
PDF
Excel
CSV
```

---

# MÓDULO 15 — AUDITORÍA

Registrar acciones sensibles.

Ejemplos:

- creación;
- modificación;
- eliminación;
- cambios de estado;
- asignaciones;
- movimientos;
- cierres de órdenes;
- modificaciones administrativas.

Información mínima:

```text
usuario
acción
fecha/hora
entidad
identificador
cambio
```

No guardar secretos en logs de auditoría.

---

# MÓDULO 16 — USUARIOS, ROLES Y PERMISOS

Mantener seguridad basada en roles y permisos.

Roles conceptuales posibles:

```text
SuperAdministrador
Administrador
Coordinador
Técnico
Consulta
```

No reemplazar el sistema actual si ya posee uno mejor.

Debe existir control por acción:

- visualizar;
- crear;
- editar;
- eliminar;
- aprobar;
- cerrar;
- exportar;
- administrar.

---

# MÓDULO 17 — CONFIGURACIÓN ORGANIZACIONAL

Cada instalación debe poder representar a su empresa.

Información potencial:

- razón social;
- nombre comercial;
- NIT;
- dirección;
- teléfono;
- correo;
- logo;
- sedes;
- zona horaria;
- moneda;
- formato de fecha;
- datos corporativos.

---

# MÓDULO 18 — CONFIGURACIÓN DE VANER ASSET

Crear un área administrativa para configuración del producto cuando resulte apropiado.

Por ejemplo:

```text
General
Branding
Módulos
Correo
Backups
Usuarios
Roles
Seguridad
Información sistema
```

Mantener una separación clara entre:

```text
configuración del producto
```

y:

```text
datos operacionales.
```

---

# 13. FEATURE FLAGS / MÓDULOS ACTIVABLES

Preparar arquitectura para habilitar/deshabilitar módulos por cliente.

Ejemplo conceptual:

```env
MODULE_ASSETS=true
MODULE_INVENTORY=true
MODULE_MAINTENANCE=true
MODULE_WORK_ORDERS=true
MODULE_SUPPLIERS=true
MODULE_ANALYTICS=true
```

No implementar flags de manera improvisada.

Crear un mecanismo centralizado.

No es aceptable llenar el frontend de condiciones dispersas.

---

# 14. CONFIGURACIÓN POR VARIABLES DE ENTORNO

Eliminar configuraciones específicas hardcodeadas.

Preparar `.env.example`.

Ejemplo conceptual:

```env
APP_NAME=VANER Asset
APP_VERSION=2.0.0

CLIENT_CODE=
CLIENT_NAME=

APP_DOMAIN=
FRONTEND_URL=
BACKEND_URL=

DATABASE_URL=

SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=

SECRET_KEY=

TIMEZONE=America/Bogota
LOCALE=es-CO
```

Nunca versionar valores reales de:

- passwords;
- tokens;
- claves;
- credenciales.

---

# 15. BASE DE DATOS POR CLIENTE

Cada instalación utilizará su propia base de datos.

Ejemplo:

```text
vaner_asset_empresa_a
vaner_asset_empresa_b
```

Esto NO significa cambiar el código.

La conexión debe obtenerse de configuración.

La aplicación debe poder instalarse en una base vacía mediante un proceso reproducible.

---

# 16. MIGRACIONES DE BASE DE DATOS

Verifica primero si el backend ya utiliza migraciones.

Si usa SQLAlchemy y no dispone de una solución adecuada, evaluar Alembic.

No aplicar manualmente cambios estructurales a producción como práctica habitual.

El objetivo es poder hacer:

```text
VANER Asset 2.0
        ↓
2.1
        ↓
2.2
```

conservando los datos del cliente.

Toda modificación de esquema debe ser:

- reproducible;
- versionada;
- reversible cuando sea razonablemente posible;
- probada.

---

# 17. CONTENEDORES

La aplicación existente utiliza Docker.

Preservar y mejorar este enfoque.

La arquitectura deberá permitir algo equivalente a:

```text
VPS Cliente
│
├── Reverse Proxy
├── Frontend VANER Asset
├── Backend VANER Asset
├── PostgreSQL
└── Backups
```

Revisar el Docker actual antes de cambiarlo.

No crear Dockerfiles nuevos si los existentes pueden evolucionar.

---

# 18. DOMINIO POR CLIENTE

Modelo recomendado:

Cada empresa utiliza un dominio o subdominio corporativo propio.

Ejemplos:

```text
asset.empresa-a.com
activos.empresa-b.com.co
mantenimiento.empresa-c.com
```

El dominio debe apuntar al VPS del cliente.

Utilizar HTTPS.

Preparar la aplicación para no depender de dominios hardcodeados.

---

# 19. PROPIEDAD DE INFRAESTRUCTURA

El modelo comercial inicial considera:

```text
VPS → pagado por el cliente
Dominio → pagado por el cliente
Datos → propiedad del cliente
Software VANER Asset → producto/licencia VANER
Administración técnica → según contrato
```

La arquitectura no debe depender de que VANER sea propietario de los VPS.

---

# 20. BACKUPS

Preparar un procedimiento estándar para respaldar:

- PostgreSQL;
- archivos subidos;
- configuración crítica;
- información necesaria para recuperación.

No guardar copias dentro del repositorio Git.

Documentar restauración.

Un backup no se considera válido hasta que exista un procedimiento razonable de restauración.

---

# 21. ESTRUCTURA OBJETIVO

No reorganices el proyecto completo sin necesidad.

La estructura conceptual deseada a largo plazo es:

```text
VANER_ASSET/
│
├── backend/
├── frontend/
│
├── branding/
│   ├── default/
│   └── clients/
│
├── config/
│   ├── default/
│   └── clients/
│
├── deployments/
│   └── template/
│
├── database/
│   └── migrations/
│
├── infrastructure/
│
├── scripts/
│
├── tests/
│
├── .agent/
├── memory/
├── directives/
├── execution/
├── decisions/
├── errors/
│
├── .env.example
├── docker-compose.yml
├── VERSION
└── README.md
```

Esta es una arquitectura objetivo.

NO muevas carpetas existentes solamente para hacerlas coincidir visualmente con este árbol.

Primero determina si el cambio tiene beneficio técnico real.

---

# 22. RENOMBRADO SGA → VANER ASSET

Identificar todas las referencias a:

```text
SGA
sga
SGA SaaS
SGA Holding
```

Clasificarlas antes de reemplazarlas.

Categorías:

```text
A. Branding visible
B. Variables internas
C. Base de datos
D. Docker
E. Servicios
F. URLs
G. Documentación
H. Migraciones
I. Identificadores históricos
```

NO realizar un reemplazo global ciego.

Primero modificar branding visible.

Después evaluar identificadores internos uno por uno.

No romper:

- migraciones;
- datos;
- imports;
- servicios;
- Docker;
- producción.

---

# 23. VERSIONADO

Crear:

```text
VERSION
```

con:

```text
2.0.0
```

Seguir Semantic Versioning:

```text
MAJOR.MINOR.PATCH
```

Ejemplos:

```text
2.0.0
2.0.1
2.1.0
3.0.0
```

---

# 24. INFORMACIÓN DE LICENCIA

Preparar el sistema para mostrar:

```text
VANER Asset v2.x.x
Licenciado a: Empresa XYZ S.A.S.
```

No implementar todavía mecanismos agresivos de bloqueo por licencia si no existe requerimiento explícito.

Primero diseñar una arquitectura simple y confiable.

---

# 25. SEGURIDAD

Realizar revisión de:

- JWT;
- autenticación;
- autorización;
- contraseñas;
- CORS;
- headers;
- cookies;
- SQL injection;
- XSS;
- CSRF cuando aplique;
- uploads;
- secretos;
- Docker;
- PostgreSQL;
- reverse proxy;
- rate limits cuando correspondan;
- logs;
- endpoints administrativos.

No inventar vulnerabilidades.

Documentar solamente hallazgos demostrables.

---

# 26. RENDIMIENTO

Revisar:

- consultas SQL;
- N+1;
- índices;
- paginación;
- payloads;
- imágenes;
- archivos;
- bundles frontend;
- caché;
- endpoints lentos.

Optimizar basándose en evidencia.

No realizar optimizaciones prematuras.

---

# 27. EXPERIENCIA DE USUARIO

VANER Asset debe mantener una identidad visual coherente.

Lineamientos generales:

- profesional;
- limpio;
- corporativo;
- moderno;
- fácil de usar;
- responsivo;
- consistente.

El dashboard debe conservar identidad VANER Asset incluso cuando cambien colores/logos del cliente.

---

# 28. RESPONSIVE

Revisar funcionamiento en:

- escritorio;
- portátil;
- tablet;
- móvil cuando sea razonablemente aplicable.

Las funciones administrativas complejas pueden priorizar escritorio.

---

# 29. ACCESIBILIDAD

Aplicar progresivamente buenas prácticas:

- contraste;
- labels;
- navegación;
- foco;
- estados;
- mensajes de error;
- botones comprensibles.

No sacrificar estabilidad intentando rehacer toda la UI simultáneamente.

---

# 30. PRIMERA TAREA OBLIGATORIA — AUDITORÍA

ANTES DE IMPLEMENTAR VANER Asset v2:

realiza una auditoría completa del proyecto actual.

NO modifiques funcionalidades durante esta fase.

Investiga:

### Backend

- estructura;
- frameworks;
- configuración;
- modelos;
- servicios;
- API;
- seguridad;
- autenticación;
- roles;
- errores;
- logs;
- base de datos;
- migraciones.

### Frontend

- estructura;
- React;
- Vite;
- rutas;
- servicios;
- estado;
- componentes;
- estilos;
- branding;
- dashboard;
- autenticación.

### Infraestructura

- Docker;
- Compose;
- proxy;
- variables;
- deploy;
- producción;
- backups.

### Personalización existente

Buscar:

```text
SGA
nombre cliente
logo
NIT
dominio
correo
IP
URLs
colores
favicon
rutas
base de datos
branding
```

---

# 31. ENTREGABLE DE LA PRIMERA AUDITORÍA

Antes de modificar código debes entregar:

## A. Arquitectura actual

Qué existe realmente.

## B. Funciones existentes

Qué funciona actualmente.

## C. Dependencias

Backend y frontend.

## D. Elementos específicos del cliente original

Lista completa.

## E. Riesgos de migración

Clasificados:

```text
CRÍTICO
ALTO
MEDIO
BAJO
```

## F. Deuda técnica

Solo basada en evidencia.

## G. Plan de transformación

Por fases.

## H. Archivos que serán modificados

Antes de ejecutar cada fase importante.

---

# 32. FASES DE TRANSFORMACIÓN

Utiliza como orientación:

## FASE 0 — Protección

- Git status;
- identificar versión actual;
- backup;
- tag;
- rama VANER Asset.

## FASE 1 — Auditoría

Sin cambios funcionales.

## FASE 2 — Identidad VANER Asset

Renombrado visual seguro.

## FASE 3 — Configuración central

Eliminar hardcoding.

## FASE 4 — Branding

Tema base + cliente.

## FASE 5 — Configuración por cliente

Empresa, dominio, locale, etc.

## FASE 6 — Base de datos

Migraciones y configuración.

## FASE 7 — Inventario/Activos

Auditoría y mejoras.

## FASE 8 — Mantenimiento

Preventivo/correctivo.

## FASE 9 — Órdenes

Flujo completo.

## FASE 10 — Reportes

Consolidación.

## FASE 11 — Auditoría y seguridad

Hardening.

## FASE 12 — Docker

Template reusable.

## FASE 13 — Backups

Automatización.

## FASE 14 — Instalador cliente

Crear proceso reproducible.

## FASE 15 — QA

Pruebas completas.

## FASE 16 — VANER Asset 2.0.0

Release.

---

# 33. AUTOMATIZACIÓN DE NUEVOS CLIENTES

El objetivo futuro es disponer de algo equivalente a:

```powershell
.\scripts\new-client.ps1 `
    -Code empresa-alfa `
    -Name "Empresa Alfa S.A.S." `
    -Domain asset.empresa-alfa.com
```

que prepare:

```text
deployments/empresa-alfa/
branding/clients/empresa-alfa/
config/clients/empresa-alfa/
```

sin duplicar la aplicación.

No almacenar credenciales reales generadas en Git.

---

# 34. PROCESO DE NUEVO CLIENTE

El flujo futuro debe poder ser:

```text
Nuevo cliente
      ↓
Crear configuración
      ↓
Agregar branding
      ↓
Crear VPS
      ↓
Configurar dominio
      ↓
Preparar .env
      ↓
Desplegar Docker
      ↓
Inicializar DB
      ↓
Crear administrador
      ↓
Health check
      ↓
Capacitación
      ↓
Producción
```

---

# 35. ACTUALIZACIONES

Cuando VANER Asset pase:

```text
2.0.0 → 2.1.0
```

el flujo debe ser:

```text
desarrollo
      ↓
tests
      ↓
build
      ↓
release
      ↓
backup cliente
      ↓
actualización
      ↓
migraciones
      ↓
health check
```

Nunca depender de editar manualmente archivos de código en cada VPS.

---

# 36. REGLA DE CÓDIGO ÚNICO

Esta es una regla crítica:

## NO crear forks por cliente.

Si Cliente A requiere una función especial:

primero analizar si puede convertirse en:

- configuración;
- módulo opcional;
- feature flag;
- permiso;
- extensión reusable.

Solo aceptar lógica exclusiva hardcodeada como último recurso.

---

# 37. COMPATIBILIDAD CON EL CLIENTE ORIGINAL

La instalación SGA original ya desplegada no debe modificarse durante el desarrollo de VANER Asset.

Tratarla como:

```text
SGA v1 — producción estable
```

VANER Asset será:

```text
VANER Asset v2 — nueva línea comercial
```

Si posteriormente se decide migrar al cliente original, desarrollar un procedimiento específico y probado.

---

# 38. NO DESTRUIR INFORMACIÓN

No ejecutar sin autorización explícita:

```text
DROP DATABASE
DROP TABLE
TRUNCATE
git reset --hard
git clean -fd
eliminaciones masivas
```

No borrar archivos que parezcan obsoletos sin analizar referencias.

---

# 39. APRENDIZAJE PERSISTENTE

Este proyecto utiliza:

```text
.agent/
memory/
directives/
execution/
decisions/
errors/
```

Antes de cada tarea:

leer las instrucciones existentes.

Después de trabajo significativo:

actualizar:

```text
memory/project_context.md
memory/session_summary.md
memory/learnings.md
```

cuando corresponda.

Los aprendizajes deben ser útiles y verificables.

---

# 40. REGISTRO DE DECISIONES

Decisiones arquitectónicas relevantes deben registrarse mediante ADR.

Ejemplos:

```text
ADR-0001-single-tenant-per-client.md
ADR-0002-branding-architecture.md
ADR-0003-client-configuration.md
ADR-0004-database-isolation.md
```

---

# 41. DEFINITION OF DONE

Una función no está terminada solo porque compile.

Debe verificarse según corresponda:

```text
[ ] Requisito cumplido
[ ] Backend probado
[ ] Frontend probado
[ ] Seguridad revisada
[ ] Base de datos validada
[ ] Tests relevantes pasan
[ ] Build exitoso
[ ] No hay regresiones evidentes
[ ] Configuración documentada
[ ] Sin secretos versionados
[ ] Memoria actualizada si correspondía
```

---

# 42. RESULTADO ESPERADO DE VANER ASSET v2

Al finalizar esta transformación deberá ser posible:

### Cliente A

Configurar:

```text
Empresa A
logo A
colores A
dominio A
DB A
```

y desplegar VANER Asset.

### Cliente B

Configurar:

```text
Empresa B
logo B
colores B
dominio B
DB B
```

y desplegar exactamente el mismo VANER Asset.

Sin modificar:

```text
backend
frontend
core
reglas generales
```

---

# 43. RESULTADO COMERCIAL

El producto deberá poder presentarse como:

# VANER Asset

**Plataforma de gestión y control de inventarios, activos y mantenimiento.**

Capacidades principales:

- inventarios;
- activos;
- hoja de vida;
- ubicaciones;
- responsables;
- mantenimientos preventivos;
- mantenimientos correctivos;
- órdenes de trabajo;
- repuestos;
- proveedores;
- documentos;
- evidencias;
- alertas;
- reportes;
- dashboard;
- usuarios;
- roles;
- permisos;
- auditoría;
- branding corporativo;
- instalación independiente;
- backups;
- actualización versionada.

---

# 44. PRINCIPIO DE PRODUCTO

VANER Asset no debe convertirse simplemente en:

> "SGA con otro logo".

Debe convertirse en un producto mantenible y reproducible.

El objetivo es pasar de:

```text
Software desarrollado para una empresa
```

a:

```text
Producto VANER Asset
        │
        ├── configuración Cliente A
        ├── configuración Cliente B
        └── configuración Cliente N
```

---

# 45. INSTRUCCIÓN DE INICIO PARA EL AGENTE

A partir de este momento:

1. lee las instrucciones persistentes;
2. inspecciona todo el repositorio;
3. identifica la arquitectura real;
4. determina el estado de Git;
5. identifica tecnologías y versiones;
6. encuentra configuraciones hardcodeadas;
7. encuentra personalización del cliente original;
8. identifica funcionalidades actualmente terminadas;
9. identifica funcionalidades incompletas;
10. identifica riesgos;
11. actualiza la memoria persistente;
12. crea el plan de transformación SGA → VANER Asset;
13. NO modifiques todavía lógica funcional.

Primero entrega la auditoría.

Espera aprobación antes de iniciar cambios arquitectónicos importantes.

---

# PRINCIPIOS FINALES

NO CREAR DESDE CERO SI YA EXISTE ALGO FUNCIONAL.

NO DUPLICAR CÓDIGO POR CLIENTE.

UN SOLO VANER ASSET CORE.

UNA BASE DE DATOS INDEPENDIENTE POR CLIENTE.

UN VPS INDEPENDIENTE POR CLIENTE EN EL MODELO INICIAL.

BRANDING CONFIGURABLE.

DOMINIO CONFIGURABLE.

NINGÚN CLIENTE HARDCODEADO.

NINGÚN SECRETO EN GIT.

TODOS LOS CAMBIOS DE BASE DE DATOS VERSIONADOS.

BACKUP ANTES DE PRODUCCIÓN.

TESTS ANTES DE RELEASE.

MANTENER VANER ASSET RECONOCIBLE AUN CON BRANDING DEL CLIENTE.

CONVERTIR LO REPETITIVO EN AUTOMATIZACIÓN.

EL OBJETIVO ES VENDER EL MISMO PRODUCTO A MUCHOS CLIENTES, NO MANTENER MUCHOS PRODUCTOS DIFERENTES.