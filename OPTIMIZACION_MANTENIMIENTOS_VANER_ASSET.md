# PROMPT MAESTRO — AUTOMATIZACIÓN Y OPTIMIZACIÓN DEL MÓDULO DE MANTENIMIENTOS DE VANER ASSET

Actúa como arquitecto de software senior, desarrollador full-stack, especialista en UX/UI, PostgreSQL, FastAPI, React y sistemas GMAO/CMMS multiempresa.

Debes analizar, rediseñar, automatizar, implementar y probar profesionalmente el módulo de creación y gestión de mantenimientos del proyecto:

**VANER ASSET**

VANER ASSET es una plataforma SaaS multiempresa para gestionar:

* Inventarios.
* Activos y equipos.
* Mantenimientos preventivos y correctivos.
* Órdenes de trabajo.
* Técnicos.
* Repuestos.
* Evidencias.
* Cronogramas.
* Hojas de vida.
* Reportes.
* Auditoría y trazabilidad.

El objetivo es transformar el formulario actual de creación de mantenimientos en un proceso más rápido, sencillo, dinámico, seguro y profesional.

---

# 1. REGLA PRINCIPAL DE TRABAJO

Antes de modificar archivos:

1. Lee completamente el proyecto.
2. Localiza y analiza:

   * Frontend del módulo de mantenimientos.
   * Backend FastAPI.
   * Schemas Pydantic.
   * Modelos SQLAlchemy.
   * Migraciones Alembic.
   * Tablas PostgreSQL relacionadas.
   * Pruebas existentes.
   * Permisos por rol.
   * Políticas multiempresa y RLS.
   * Historial y auditoría.
3. Identifica las dependencias con:

   * Equipos.
   * Empresas.
   * Sedes.
   * Técnicos.
   * Repuestos.
   * Evidencias.
   * Cronograma.
   * Hoja de vida.
   * Notificaciones.
4. No reemplaces tecnologías ni reestructures todo el proyecto sin necesidad.
5. Conserva la arquitectura, convenciones, estilos y componentes reutilizables existentes.
6. No rompas funcionalidades que ya estén operativas.
7. No elimines datos, tablas, migraciones ni archivos existentes.
8. No ejecutes comandos destructivos.
9. Antes de implementar, entrega un diagnóstico breve y un plan de cambios.
10. Implementa únicamente después de comprobar cómo funciona realmente el proyecto.

---

# 2. ARCHIVOS PRINCIPALES QUE DEBES REVISAR

Verifica especialmente, sin limitarte exclusivamente a ellos:

```text
frontend/src/pages/admin/MantenimientosPage.jsx
frontend/src/pages/admin/MantenimientosPage.css
frontend/src/pages/admin/mantenimientosEquipoUtils.js
frontend/src/pages/coordinador/
frontend/src/pages/tecnico/
frontend/src/api/

backend/app/routers/mantenimientos.py
backend/app/routers/coordinador.py
backend/app/routers/dashboard_tecnico.py
backend/app/schemas/mantenimiento.py
backend/app/models/mantenimiento.py
backend/app/models/hist_mantenimiento.py
backend/app/models/equipo.py
backend/app/models/tecnico.py
backend/app/services/
backend/app/alembic/
backend/tests/
```

Busca también cualquier referencia adicional mediante búsquedas globales por:

```text
Mantenimiento
mantenimiento_id
crear_mantenimiento
asignar_tecnico
fecha_programada
fecha_inicio_programada
fecha_fin_programada
HistMantenimiento
```

---

# 3. PROBLEMAS QUE SE DEBEN CORREGIR

El módulo actual presenta los siguientes problemas:

## 3.1 Formulario excesivamente largo

La creación mezcla:

* Programación.
* Ejecución técnica.
* Diagnóstico.
* Registro de trabajos.
* Costos.
* Solución.
* Resultado.
* Cierre.

Estos procesos deben separarse según el momento del ciclo de mantenimiento.

## 3.2 Creación y asignación no atómicas

Actualmente puede ocurrir:

1. Se crea el mantenimiento.
2. Se realiza una segunda petición para asignar al técnico.
3. La asignación falla.
4. El mantenimiento queda creado parcialmente.

La creación, asignación inicial, historial y notificación deben manejarse de forma transaccional.

## 3.3 Riesgo de duplicados

El formulario debe impedir dobles envíos causados por:

* Doble clic.
* Lentitud de red.
* Reintentos accidentales.
* Recarga del navegador.

## 3.4 Estado inicial inconsistente

El usuario puede ver o seleccionar un estado que no coincide con lo que finalmente guarda el backend.

El estado inicial debe establecerse automáticamente:

* Sin técnico: `PROGRAMADO`.
* Con técnico: `ASIGNADO`.

No permitir crear directamente en:

* `EN_PROCESO`.
* `PAUSADO`.
* `FINALIZADO`.
* `ANULADO`.

## 3.5 Técnicos sin filtrado suficiente

Mostrar solamente técnicos:

* Activos.
* Autorizados para la empresa del equipo.
* Preferiblemente compatibles con la especialidad requerida.
* Con información de disponibilidad y carga de trabajo.

## 3.6 Selección lenta del activo

Actualmente se exige navegar por:

1. Empresa.
2. Sede.
3. Ubicación.
4. Equipo.

Debe incorporarse un buscador inteligente que permita localizar el equipo por:

* Nombre.
* Código interno.
* Número de inventario.
* Número de serie.
* Marca.
* Modelo.
* Ubicación.
* Empresa.
* Sede.

---

# 4. NUEVO DISEÑO DEL FORMULARIO

Implementa un asistente de tres pasos.

## PASO 1 — SELECCIONAR ACTIVO

Crear un buscador principal con búsqueda dinámica y debounce.

Debe buscar por:

* Nombre del equipo.
* Código.
* Inventario.
* Serie.
* Marca.
* Modelo.
* Ubicación.

Cada resultado debe mostrar:

* Nombre.
* Código.
* Número de inventario.
* Serie.
* Empresa.
* Sede.
* Ubicación.
* Estado operativo.
* Criticidad.
* Último mantenimiento.
* Próximo mantenimiento.
* Existencia de órdenes abiertas.

Al seleccionar el activo:

* Completar automáticamente empresa.
* Completar automáticamente sede.
* Completar automáticamente ubicación.
* Guardar `equipo_id`.
* Mostrar una tarjeta de confirmación.
* Evitar que el usuario pueda enviar una combinación incoherente de empresa, sede y equipo.

Conservar los selectores tradicionales como filtros avanzados opcionales.

## PASO 2 — PROGRAMAR TRABAJO

Mostrar únicamente:

* Tipo de mantenimiento.
* Descripción o trabajo solicitado.
* Prioridad.
* Fecha y hora de inicio.
* Duración estimada.
* Fecha y hora final calculada.
* Técnico responsable opcional.
* Observaciones opcionales.

El campo principal de descripción debe ser obligatorio y tener un nombre claro:

* Para preventivo: `Trabajo preventivo solicitado`.
* Para correctivo: `Falla o incidencia reportada`.
* Para calibración: `Calibración requerida`.
* Para inspección: `Objetivo de la inspección`.

No utilizar automáticamente una descripción genérica salvo como último mecanismo de compatibilidad.

## PASO 3 — CONFIRMAR

Mostrar un resumen antes de guardar:

* Equipo.
* Código e inventario.
* Empresa.
* Sede.
* Ubicación.
* Tipo.
* Prioridad.
* Descripción.
* Fecha y horario.
* Duración.
* Técnico o “Pendiente por asignar”.
* Advertencias detectadas.

Botón final:

```text
Crear orden de mantenimiento
```

Después de crear correctamente, ofrecer:

* Ver orden.
* Ir al cronograma.
* Crear otra orden.
* Imprimir.
* Notificar al técnico, cuando corresponda.

---

# 5. COMPORTAMIENTO DINÁMICO POR TIPO

## 5.1 Mantenimiento preventivo

Mostrar:

* Plan o rutina preventiva.
* Checklist asociado.
* Frecuencia.
* Último mantenimiento.
* Próxima fecha recomendada.

Permitir crear una programación recurrente:

* Semanal.
* Mensual.
* Bimestral.
* Trimestral.
* Semestral.
* Anual.
* Personalizada.

## 5.2 Mantenimiento correctivo

Mostrar:

* Falla reportada.
* Síntomas.
* Equipo detenido: Sí/No.
* Afectación operativa.
* Nivel de urgencia.
* Persona que reportó.

Si el equipo está detenido o es crítico, sugerir prioridad `ALTA` o `CRITICA`, pero permitir que un usuario autorizado confirme o modifique la sugerencia.

## 5.3 Calibración

Mostrar:

* Tipo de calibración.
* Fecha de vencimiento actual.
* Proveedor o responsable.
* Certificado requerido.
* Periodicidad.

## 5.4 Inspección

Mostrar:

* Tipo de inspección.
* Lista de verificación.
* Normativa o criterio aplicable.
* Resultado esperado.

---

# 6. CAMPOS QUE NO DEBEN APARECER AL CREAR

Mover al proceso de ejecución técnica:

* Estado inicial del equipo.
* Diagnóstico técnico.
* Trabajo realizado.
* Acciones realizadas.
* Repuestos utilizados.
* Solución aplicada.
* Resultado final.
* Evidencias.
* Costo real de mano de obra.
* Costo real de repuestos.
* Costo total real.
* Firmas.
* Geolocalización real de ejecución.
* Fecha real de inicio.
* Fecha real de finalización.
* Cierre.

Estos campos deben diligenciarse cuando el técnico inicie o ejecute la orden.

---

# 7. AUTOMATIZACIONES REQUERIDAS

## 7.1 Estado automático

Aplicar:

```text
Sin técnico asignado → PROGRAMADO
Con técnico asignado → ASIGNADO
```

Los cambios posteriores deben respetar la máquina de estados existente.

## 7.2 Fecha final automática

El usuario debe seleccionar:

* Fecha y hora de inicio.
* Duración estimada.

Calcular automáticamente la fecha y hora final.

Permitir editar la fecha final solo mediante una opción avanzada.

## 7.3 Técnico sugerido

Sugerir técnicos considerando:

* Empresa.
* Estado activo.
* Especialidad.
* Sede.
* Disponibilidad.
* Cantidad de órdenes abiertas.
* Coincidencias de horario.

La sugerencia no debe asignar automáticamente sin confirmación del usuario.

## 7.4 Prioridad sugerida

Calcular una sugerencia basada en:

* Criticidad del equipo.
* Equipo detenido.
* Tipo de mantenimiento.
* Falla reportada.
* Afectación operativa.
* Tiempo desde el último mantenimiento.

Mostrar el motivo de la sugerencia.

## 7.5 Detección de conflictos

Antes de guardar, comprobar:

* Otra orden abierta para el mismo equipo.
* Mantenimiento duplicado en fecha cercana.
* Técnico ocupado.
* Cruce de horarios.
* Equipo dado de baja.
* Equipo inactivo.
* Equipo fuera de servicio.
* Mantenimiento preventivo vencido.
* Fechas incoherentes.

Las advertencias no siempre deben bloquear. Clasificarlas en:

* Informativa.
* Advertencia.
* Bloqueante.

## 7.6 Plantillas

Permitir plantillas por:

* Tipo de mantenimiento.
* Categoría del equipo.
* Marca o modelo.
* Empresa.
* Plan preventivo.

Una plantilla puede completar:

* Descripción.
* Duración estimada.
* Prioridad.
* Checklist.
* Especialidad técnica requerida.
* Repuestos previstos.

## 7.7 Borrador automático

Guardar temporalmente el formulario para evitar pérdida de información.

Eliminar el borrador después de crear correctamente la orden.

## 7.8 Notificación

Después de una creación exitosa:

* Notificar al técnico si fue asignado.
* Registrar la notificación.
* No enviar notificaciones si la transacción falla.
* Evitar notificaciones duplicadas.

---

# 8. REGLAS DE NEGOCIO

1. Todo mantenimiento debe pertenecer al mismo tenant del equipo.
2. La empresa y sede deben derivarse del equipo seleccionado.
3. No confiar en `empresa_id` o `sede_id` enviados manualmente por el cliente.
4. Un técnico debe estar activo.
5. El técnico debe estar autorizado para la empresa correspondiente.
6. Permitir mantenimiento sin técnico.
7. La descripción del trabajo debe ser obligatoria.
8. La fecha final debe ser posterior a la inicial.
9. Los costos no pueden ser negativos.
10. El costo total debe calcularse automáticamente cuando corresponda.
11. Un mantenimiento finalizado solamente puede modificarse mediante reapertura autorizada.
12. Una reapertura requiere motivo.
13. Los cambios de estado deben producir historial.
14. Las operaciones deben respetar los permisos por rol.
15. Los coordinadores solamente pueden trabajar con sus empresas autorizadas.
16. Los técnicos solamente pueden ejecutar órdenes asignadas.
17. Los clientes solamente pueden consultar información autorizada.
18. Las consultas deben respetar tenant, RLS y aislamiento multiempresa.
19. No confiar solamente en filtros del frontend.
20. Toda validación crítica debe repetirse en el backend.

---

# 9. TRANSACCIÓN DE CREACIÓN

Diseña un endpoint profesional que pueda recibir en una sola solicitud:

```json
{
  "equipo_id": "UUID",
  "tipo": "PREVENTIVO",
  "descripcion": "Realizar mantenimiento preventivo trimestral",
  "prioridad": "MEDIA",
  "fecha_inicio_programada": "ISO-8601",
  "fecha_fin_programada": "ISO-8601",
  "duracion_estimada_minutos": 120,
  "tecnico_id": "UUID opcional",
  "observaciones": "Texto opcional",
  "plantilla_id": "UUID opcional",
  "recurrencia": null
}
```

La operación debe:

1. Validar usuario y permisos.
2. Validar equipo.
3. Obtener tenant, empresa y sede desde el equipo.
4. Validar técnico si viene informado.
5. Validar fechas.
6. Detectar conflictos.
7. Crear mantenimiento.
8. Establecer estado.
9. Asignar técnico.
10. Crear historial inicial.
11. Crear recurrencia cuando corresponda.
12. Registrar auditoría.
13. Confirmar la transacción.
14. Generar notificación después de confirmar.
15. Retornar la orden completa.

Si cualquier operación crítica falla, debe hacerse rollback.

No debe quedar una orden parcialmente creada.

---

# 10. VALIDACIÓN DEL BACKEND

Utiliza validaciones estrictas con Pydantic:

* Enums para tipo.
* Enums para prioridad.
* Enums para estado.
* UUID para identificadores.
* Fechas con zona horaria definida.
* Duración mayor que cero.
* Longitudes mínimas y máximas.
* Números no negativos.
* Campos obligatorios según tipo de mantenimiento.

No aceptar silenciosamente valores desconocidos.

No convertir fechas inválidas en `None` sin informar el error.

Entregar mensajes claros, por ejemplo:

```text
La fecha de finalización debe ser posterior a la fecha de inicio.
```

```text
El técnico seleccionado no pertenece a la empresa del equipo.
```

```text
Este equipo ya tiene una orden abierta.
```

---

# 11. EXPERIENCIA DE USUARIO

Reemplazar `alert()`, `prompt()` y `confirm()` por componentes visuales consistentes:

* Toast de éxito.
* Toast de error.
* Modal de confirmación.
* Mensajes debajo de los campos.
* Resumen de errores.
* Indicadores de carga.
* Skeletons cuando sea necesario.

Durante el guardado:

* Desactivar el botón.
* Mostrar `Creando orden…`.
* Impedir doble envío.
* Conservar los datos si ocurre un error.
* Llevar el foco al primer campo inválido.

El formulario debe ser:

* Responsive.
* Accesible mediante teclado.
* Compatible con lectores de pantalla.
* Claro en escritorio, tableta y móvil.
* Consistente con la identidad visual de VANER ASSET.

---

# 12. ACCESOS RÁPIDOS

Permitir iniciar la creación desde:

* Módulo de mantenimientos.
* Dashboard.
* Cronograma.
* Hoja de vida del equipo.
* Inventario.
* Detalle del activo.
* Solicitud correctiva.

Cuando se accede desde un equipo, debe abrirse con:

* Equipo preseleccionado.
* Empresa preseleccionada.
* Sede preseleccionada.
* Ubicación preseleccionada.

Cuando se accede desde una solicitud correctiva, debe traer la falla reportada.

---

# 13. RENDIMIENTO

No cargar catálogos completos sin necesidad.

Implementar:

* Búsqueda remota paginada de equipos.
* Debounce.
* Paginación en backend.
* Filtros por tenant.
* Índices necesarios.
* Cancelación de búsquedas anteriores.
* Caché controlada de catálogos pequeños.
* Consultas sin problemas N+1.

Revisar índices para:

* `empresa_id`.
* `sede_id`.
* `equipo_id`.
* `tecnico_id`.
* `estado`.
* `fecha_programada`.
* `fecha_inicio_programada`.
* `fecha_fin_programada`.
* Combinaciones utilizadas para detectar conflictos.

No crear índices redundantes sin revisar los existentes.

---

# 14. SEGURIDAD Y MULTIEMPRESA

Mantener estrictamente:

* Autenticación.
* Autorización por rol.
* Aislamiento de tenant.
* RLS cuando esté habilitado.
* Auditoría.
* Validaciones en backend.
* Protección contra IDOR.
* Restricción por empresa.
* Sanitización de textos.
* Límites de tamaño.
* Registro de operaciones relevantes.

Prueba expresamente que un usuario de una empresa no pueda:

* Buscar equipos de otra empresa.
* Seleccionar técnicos de otra empresa.
* Crear mantenimientos para otra empresa.
* Consultar órdenes de otro tenant.
* Modificar órdenes ajenas.

---

# 15. COMPATIBILIDAD

La actualización debe conservar:

* Mantenimientos existentes.
* Historial existente.
* Cronograma.
* Portal administrador.
* Portal coordinador.
* Portal técnico.
* Portal cliente.
* Hojas de vida.
* Evidencias.
* Reportes.
* Exportaciones.
* Reapertura.
* Estados actuales.
* Relaciones con PostgreSQL.

Si se necesita una migración:

1. Crear migración Alembic reversible.
2. No editar migraciones históricas ya aplicadas.
3. Incluir `upgrade()` y `downgrade()`.
4. Añadir valores predeterminados seguros.
5. Probar con datos existentes.
6. Documentar el comando para ejecutarla.
7. No ejecutar migraciones en producción automáticamente.

---

# 16. PRUEBAS OBLIGATORIAS

## Backend

Crear pruebas para:

1. Crear mantenimiento sin técnico.
2. Crear mantenimiento con técnico.
3. Asignar estado automático correcto.
4. Rechazar técnico de otra empresa.
5. Rechazar equipo de otro tenant.
6. Rechazar fechas inválidas.
7. Rechazar duración negativa.
8. Detectar orden duplicada.
9. Detectar conflicto de técnico.
10. Crear historial inicial.
11. Ejecutar rollback ante error.
12. Evitar creación parcial.
13. Validar permisos por rol.
14. Crear mantenimiento recurrente.
15. Reabrir mantenimiento con motivo.
16. Rechazar reapertura sin motivo.

## Frontend

Crear pruebas para:

1. Buscar equipo.
2. Seleccionar equipo.
3. Autocompletar empresa, sede y ubicación.
4. Cambiar campos según tipo.
5. Permitir técnico opcional.
6. Calcular fecha final.
7. Mostrar conflictos.
8. Validar campos.
9. Impedir doble envío.
10. Conservar información si falla el servidor.
11. Limpiar borrador después del éxito.
12. Navegar mediante teclado.
13. Ver correctamente en móvil.

## Flujo end-to-end

Probar:

```text
Administrador selecciona equipo
→ programa mantenimiento
→ asigna técnico
→ se crea la orden
→ aparece en cronograma
→ técnico recibe la orden
→ técnico inicia ejecución
→ registra diagnóstico y trabajo
→ carga evidencias
→ finaliza
→ queda en hoja de vida
→ aparece en reportes
```

---

# 17. CRITERIOS DE ACEPTACIÓN

El trabajo solamente se considera terminado si:

* Crear una orden básica requiere como máximo tres pasos.
* Empresa, sede y ubicación se obtienen desde el equipo.
* El formulario inicial no muestra campos de ejecución.
* El técnico es opcional.
* El estado se determina automáticamente.
* La creación es transaccional.
* No se producen registros parciales.
* No se producen duplicados por doble clic.
* Las fechas se validan correctamente.
* Los técnicos se filtran por empresa.
* Los conflictos se muestran antes de confirmar.
* El módulo funciona para Administrador y Coordinador.
* Se conserva el aislamiento multiempresa.
* La orden aparece correctamente en cronograma y hoja de vida.
* Las pruebas pasan.
* El frontend compila sin errores.
* El backend inicia sin errores.
* No aparecen errores en consola.
* No se rompen funcionalidades existentes.

---

# 18. ORDEN DE IMPLEMENTACIÓN

Trabaja en este orden:

## Fase 1 — Correcciones críticas

* Transacción única de creación.
* Técnico opcional.
* Estado automático.
* Filtrado de técnicos.
* Validación de fechas.
* Prevención de doble envío.
* Validaciones backend.
* Historial y auditoría.

## Fase 2 — Simplificación visual

* Asistente de tres pasos.
* Buscador inteligente de equipos.
* Autocompletado.
* Campos dinámicos por tipo.
* Resumen antes de guardar.
* Toasts y errores en línea.

## Fase 3 — Automatización

* Técnico sugerido.
* Prioridad sugerida.
* Detección de conflictos.
* Plantillas.
* Duración automática.
* Borrador.
* Notificaciones.

## Fase 4 — Planificación avanzada

* Recurrencia.
* Integración con cronograma.
* Alertas.
* Accesos rápidos.
* Indicadores.
* Optimización de consultas.

## Fase 5 — Verificación

* Pruebas backend.
* Pruebas frontend.
* Pruebas end-to-end.
* Compilación.
* Documentación.
* Informe final.

No continúes a una fase si la anterior tiene errores.

---

# 19. ENTREGA FINAL OBLIGATORIA

Al terminar, entrega:

1. Resumen de la auditoría inicial.
2. Lista de archivos modificados.
3. Explicación de cada cambio.
4. Migraciones creadas.
5. Endpoints nuevos o modificados.
6. Reglas de negocio implementadas.
7. Pruebas agregadas.
8. Resultados de las pruebas.
9. Resultado de compilación frontend.
10. Resultado del inicio del backend.
11. Riesgos pendientes.
12. Instrucciones exactas para probar manualmente.
13. Instrucciones para aplicar migraciones.
14. Plan de reversión.
15. Confirmación de que no se eliminaron datos.

Si alguna prueba no puede ejecutarse, explica claramente:

* Qué prueba faltó.
* Por qué no se ejecutó.
* Qué riesgo deja.
* Cómo debe ejecutarse manualmente.

---

# 20. RESTRICCIONES FINALES

* No inventes endpoints sin revisar los existentes.
* No dupliques módulos por rol.
* Reutiliza el componente compartido cuando sea seguro.
* No confíes en validaciones únicamente del frontend.
* No elimines funcionalidades existentes.
* No cambies nombres de tablas sin justificación.
* No modifiques producción.
* No expongas secretos ni archivos `.env`.
* No incluyas contraseñas, tokens o credenciales en logs.
* No ignores errores para hacer que las pruebas aparenten pasar.
* No marques como terminado algo que no haya sido verificado.
* No agregues dependencias innecesarias.
* Conserva la marca y el diseño profesional de VANER ASSET.

Comienza leyendo el proyecto y entrega primero:

```text
1. Diagnóstico del módulo actual.
2. Archivos involucrados.
3. Riesgos encontrados.
4. Plan de implementación por fases.
5. Cambios que requieren migración.
```

Después procede con la implementación completa, verificando cada fase antes de avanzar.
