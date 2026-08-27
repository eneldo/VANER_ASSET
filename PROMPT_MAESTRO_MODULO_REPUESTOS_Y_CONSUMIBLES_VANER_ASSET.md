# PROMPT MAESTRO — MÓDULO DE REPUESTOS Y CONSUMIBLES DE VANER ASSET

Actúa como arquitecto de software senior, especialista en sistemas GMAO/CMMS, gestión de inventarios, PostgreSQL, FastAPI, SQLAlchemy, Alembic, React, seguridad multiempresa y UX/UI profesional.

Debes auditar, diseñar e implementar un módulo independiente llamado:

# REPUESTOS Y CONSUMIBLES

para el proyecto **VANER ASSET**.

VANER ASSET es una plataforma SaaS multiempresa para administrar:

* Inventarios.
* Activos y equipos.
* Planificación de mantenimientos.
* Órdenes de trabajo.
* Técnicos.
* Repuestos y consumibles.
* Evidencias.
* Hojas de vida.
* Cronogramas.
* Costos.
* Reportes.
* Auditoría y trazabilidad.

El nuevo módulo debe controlar el ciclo completo de los repuestos: catálogo, existencias, entradas, reservas, entregas, consumos, devoluciones, ajustes, transferencias, costos y trazabilidad por orden de mantenimiento.

---

# 1. REGLA DE AUTORIZACIÓN

Antes de modificar archivos:

1. Lee completamente el proyecto.
2. Realiza una auditoría del estado actual.
3. Identifica archivos, modelos, tablas y funcionalidades relacionadas.
4. Entrega un diagnóstico y un plan por fases.
5. Indica las migraciones necesarias.
6. Espera autorización expresa antes de implementar.

No modifiques, elimines, renombres ni ejecutes migraciones sin autorización.

Después de recibir autorización, implementa por fases y verifica cada fase antes de continuar.

---

# 2. ESTADO ACTUAL CONOCIDO

Actualmente la ruta:

```text
/admin/repuestos
```

abre el mismo componente de Mantenimientos:

```text
MantenimientosPage
```

También existen varias estructuras relacionadas con repuestos:

```text
mantenimientos.repuestos
ot_repuestos
formatos_mantenimiento.repuestos_utilizados
formatos_dinamicos.repuestos_utilizados
```

El técnico puede registrar:

* Descripción.
* Referencia.
* Cantidad.
* Unidad.
* Costo unitario.

Sin embargo, esto funciona principalmente como registro textual dentro de una orden.

Actualmente se debe comprobar si faltan:

* Catálogo central.
* Existencias.
* Bodegas.
* Movimientos.
* Reservas.
* Entregas.
* Devoluciones.
* Stock mínimo.
* Proveedores.
* Relación con productos.
* Descuento automático del inventario.
* Trazabilidad completa.

No asumas que esta descripción está totalmente actualizada. Confirma todo directamente en el código y la base de datos.

---

# 3. AUDITORÍA INICIAL OBLIGATORIA

Busca globalmente:

```text
repuesto
repuestos
consumible
ot_repuestos
repuestos_utilizados
costo_repuestos
stock
existencia
movimiento_inventario
almacen
bodega
producto
material
```

Revisa especialmente:

```text
frontend/src/App.jsx
frontend/src/components/Sidebar.jsx
frontend/src/pages/admin/
frontend/src/pages/tecnico/
frontend/src/pages/ModalEjecucionTecnica.jsx
frontend/src/api/

backend/app/models/ot_repuesto.py
backend/app/models/mantenimiento.py
backend/app/models/formato_mantenimiento.py
backend/app/models/formato_dinamico.py
backend/app/routers/dashboard_tecnico.py
backend/app/routers/mantenimientos.py
backend/app/routers/reportes.py
backend/app/routers/reportes_publicados.py
backend/app/schemas/
backend/app/services/
backend/app/alembic/
backend/tests/

database/
docs/ARQUITECTURA_GMAO_MULTI_TENANT.md
```

Determina:

1. Cuál es la fuente actual de información de repuestos.
2. Qué campos están duplicados.
3. Qué pantallas escriben datos.
4. Qué informes leen esos datos.
5. Si existen productos, inventarios o movimientos reutilizables.
6. Cómo funciona el aislamiento por empresa.
7. Qué permisos existen por rol.
8. Qué migraciones ya fueron aplicadas.
9. Si existen datos que deban migrarse.
10. Qué riesgos de pérdida o inconsistencia existen.

---

# 4. OBJETIVO DEL MÓDULO

El módulo debe responder:

> ¿Qué repuestos posee cada empresa, dónde están almacenados, cuántos están disponibles, cuáles están reservados, en qué órdenes se utilizaron, quién autorizó el movimiento y cuánto costaron?

Debe administrar:

* Catálogo de repuestos y consumibles.
* Bodegas y ubicaciones.
* Existencias por empresa, sede y bodega.
* Movimientos.
* Reservas.
* Solicitudes.
* Entregas.
* Consumos.
* Devoluciones.
* Transferencias.
* Ajustes.
* Alertas.
* Costos.
* Proveedores.
* Compatibilidad con activos.
* Reportes y trazabilidad.

---

# 5. SEPARACIÓN FUNCIONAL

Mantén claramente separados:

## Inventario de activos

Elementos que la empresa controla individualmente:

* Equipos.
* Máquinas.
* Herramientas.
* Computadores.
* Dispositivos.
* Activos con hoja de vida.

## Repuestos y consumibles

Elementos almacenables que se utilizan, reemplazan o consumen:

* Rodamientos.
* Correas.
* Filtros.
* Fusibles.
* Tornillos.
* Lubricantes.
* Baterías.
* Cables.
* Sensores.
* Sellos.
* Kits.
* Materiales de limpieza.
* Consumibles técnicos.

Un repuesto puede manejar existencias sin convertirse en un activo individual.

---

# 6. NOMBRE Y NAVEGACIÓN

Nombre visible:

```text
Repuestos y consumibles
```

Ruta administrativa:

```text
/admin/repuestos
```

La ruta debe cargar una página propia. No debe reutilizar `MantenimientosPage`.

Agregar accesos según rol:

* Administrador: gestión completa.
* Coordinador: operación en empresas autorizadas.
* Técnico: solicitud, consulta y registro de consumo autorizado.
* Cliente: consulta limitada si está habilitada.
* Almacén o bodeguero: preparar, entregar, recibir y ajustar existencias, si el modelo de roles lo permite.

No inventes un rol nuevo sin revisar el sistema de permisos. Si se requiere, documenta la propuesta antes de implementarla.

---

# 7. PANTALLA PRINCIPAL

Crear un dashboard propio con indicadores:

* Total de referencias activas.
* Unidades disponibles.
* Repuestos con stock bajo.
* Repuestos agotados.
* Valor total del inventario.
* Reservas pendientes.
* Solicitudes pendientes.
* Entregas del periodo.
* Consumo mensual.
* Órdenes detenidas por falta de repuesto.

Incluir pestañas:

1. Catálogo.
2. Existencias.
3. Movimientos.
4. Solicitudes y reservas.
5. Entregas y devoluciones.
6. Stock bajo.
7. Compatibilidad.
8. Reportes.

Debe incluir:

* Búsqueda.
* Filtros.
* Ordenamiento.
* Paginación desde backend.
* Exportación autorizada.
* Diseño responsive.
* Estados vacíos.
* Skeletons.
* Mensajes claros.

---

# 8. CATÁLOGO DE REPUESTOS

Cada repuesto debe permitir registrar:

* ID UUID.
* Empresa o tenant.
* Código interno.
* Código de barras o QR.
* Nombre.
* Descripción.
* Tipo: repuesto o consumible.
* Categoría.
* Referencia.
* Marca.
* Fabricante.
* Unidad de medida.
* Precio promedio.
* Último costo.
* Stock mínimo.
* Stock máximo.
* Punto de reposición.
* Tiempo estimado de reposición.
* Fotografía opcional.
* Ficha técnica opcional.
* Estado activo/inactivo.
* Manejo por lote: Sí/No.
* Manejo por serial: Sí/No.
* Control de vencimiento: Sí/No.
* Observaciones.
* Fecha de creación.
* Fecha de actualización.
* Usuario creador.

Reglas:

1. El código debe ser único dentro de la empresa.
2. No eliminar físicamente repuestos que tengan movimientos.
3. Permitir desactivarlos.
4. No permitir cantidades negativas.
5. Validar unidades de medida.
6. Evitar duplicados por código, nombre, marca y referencia.
7. Mantener aislamiento multiempresa.

---

# 9. BODEGAS Y UBICACIONES

Permitir administrar:

* Empresa.
* Sede.
* Bodega.
* Zona.
* Estantería.
* Nivel.
* Posición.
* Responsable.
* Estado activo.

Un repuesto puede tener existencias en varias bodegas.

La existencia debe diferenciar:

```text
existencia_fisica
cantidad_reservada
cantidad_disponible
```

Aplicar:

```text
cantidad_disponible = existencia_fisica - cantidad_reservada
```

No almacenar valores derivados innecesariamente si pueden calcularse de manera segura.

---

# 10. MOVIMIENTOS

Implementar movimientos inmutables:

* Entrada por compra.
* Entrada inicial.
* Salida por orden de trabajo.
* Reserva.
* Liberación de reserva.
* Entrega a técnico.
* Consumo.
* Devolución.
* Transferencia.
* Ajuste positivo.
* Ajuste negativo.
* Baja por daño.
* Baja por vencimiento.

Cada movimiento debe guardar:

* Empresa.
* Repuesto.
* Bodega origen.
* Bodega destino.
* Tipo de movimiento.
* Cantidad.
* Unidad.
* Costo unitario.
* Costo total.
* Existencia anterior.
* Existencia posterior.
* Orden relacionada.
* Documento o comprobante.
* Motivo.
* Usuario responsable.
* Fecha y hora.
* Idempotency key o mecanismo equivalente.
* Información de auditoría.

Los movimientos confirmados no deben editarse. Las correcciones deben hacerse mediante contramovimientos.

---

# 11. INTEGRACIÓN CON ÓRDENES DE TRABAJO

La orden debe permitir:

1. Solicitar un repuesto.
2. Seleccionarlo desde el catálogo.
3. Indicar cantidad requerida.
4. Consultar disponibilidad.
5. Reservar existencias.
6. Autorizar entrega.
7. Entregar al técnico.
8. Registrar cantidad utilizada.
9. Devolver cantidad no utilizada.
10. Generar salida definitiva.
11. Calcular costo real.
12. Registrar faltantes.

Estados sugeridos de la solicitud:

```text
SOLICITADO
APROBADO
RESERVADO
ENTREGADO
CONSUMIDO
DEVUELTO_PARCIAL
DEVUELTO
RECHAZADO
CANCELADO
```

Adapta estos estados a la arquitectura existente.

No descontar definitivamente stock solo por agregar una línea visual a la orden.

El descuento debe producirse en el momento de negocio definido y documentado:

* Al entregar.
* Al consumir.
* O mediante entrega y posterior ajuste por devolución.

Selecciona la política más segura para VANER ASSET y explícalo antes de implementarla.

---

# 12. FLUJO RECOMENDADO

```text
Técnico solicita repuesto
→ Coordinador o almacén revisa
→ Sistema verifica disponibilidad
→ Se aprueba
→ Se reserva
→ Almacén entrega
→ Técnico registra cantidad utilizada
→ Devuelve sobrantes
→ Sistema confirma consumo
→ Actualiza existencias
→ Calcula costo de la orden
→ Registra trazabilidad
→ Actualiza reportes y hoja de vida
```

Si no existe disponibilidad:

```text
Solicitud pendiente
→ Alerta de stock
→ Necesidad de compra
→ Orden identificada como pendiente de repuesto
```

---

# 13. CONSOLIDACIÓN DE DATOS

Revisa estas posibles fuentes:

```text
mantenimientos.repuestos
ot_repuestos
formatos_mantenimiento.repuestos_utilizados
formatos_dinamicos.repuestos_utilizados
```

Define una fuente oficial.

Recomendación:

* Catálogo: tabla de repuestos.
* Existencias: tabla de existencias por bodega.
* Movimientos: libro mayor de inventario.
* Consumo por OT: tabla relacional de repuestos utilizados.
* Formatos e informes: vistas de lectura de esas tablas.

No mantengas múltiples copias independientes.

Si hay datos históricos:

1. Crear migración segura.
2. Respaldar antes de migrar.
3. Conservar descripciones históricas.
4. Relacionar registros con el catálogo cuando sea posible.
5. Marcar como “repuesto histórico no catalogado” cuando no pueda relacionarse.
6. No perder cantidades, referencias, costos ni orden relacionada.
7. Entregar conteos antes y después.
8. No borrar columnas antiguas en la primera migración.
9. Aplicar una transición compatible.
10. Retirar campos obsoletos solamente en una fase posterior autorizada.

---

# 14. MODELO DE DATOS PROPUESTO

Evalúa y adapta estas entidades:

```text
repuestos
categorias_repuestos
unidades_medida
bodegas
ubicaciones_bodega
existencias_repuestos
movimientos_repuestos
solicitudes_repuestos
solicitudes_repuestos_detalle
ot_repuestos
proveedores_repuestos
repuestos_compatibilidad
lotes_repuestos
seriales_repuestos
```

No crees todas las tablas si el proyecto ya tiene entidades equivalentes.

Relaciones principales:

```text
Empresa → Bodegas
Empresa → Repuestos
Bodega → Existencias
Repuesto → Existencias
Repuesto → Movimientos
Orden de trabajo → Solicitudes
Orden de trabajo → Consumos
Repuesto → Equipos compatibles
```

Todas las tablas operativas deben incluir `empresa_id` cuando sea necesario para RLS y aislamiento del tenant.

---

# 15. COMPATIBILIDAD CON EQUIPOS

Permitir relacionar repuestos con:

* Categoría de equipo.
* Marca.
* Modelo.
* Equipo específico.
* Fabricante.
* Referencia técnica.

Mostrar:

* Repuestos compatibles.
* Repuestos recomendados.
* Historial de repuestos usados.
* Última fecha de sustitución.
* Frecuencia de cambio.
* Costo acumulado por equipo.

La compatibilidad debe servir como ayuda, pero no reemplazar validaciones técnicas.

---

# 16. COSTOS

Calcular:

```text
costo_linea = cantidad_consumida × costo_unitario
```

El costo total de repuestos de la orden debe calcularse automáticamente desde consumos confirmados.

No permitir que el usuario escriba manualmente un costo total incompatible.

Definir una estrategia de valoración:

* Promedio ponderado.
* FIFO.
* Último costo.

Recomienda la apropiada para VANER ASSET y documenta la decisión.

Todos los cálculos monetarios deben usar `Decimal` o `Numeric`, nunca `float`.

---

# 17. PROVEEDORES Y COMPRAS

En la primera versión se puede registrar:

* Proveedor habitual.
* Código del proveedor.
* Precio reciente.
* Tiempo de entrega.
* Contacto.
* Fecha de última compra.

Si no existe un módulo de compras, no construyas un ERP completo.

Permite generar una necesidad de compra desde:

* Stock bajo.
* Repuesto agotado.
* Solicitud sin disponibilidad.
* Punto de reposición alcanzado.

Deja preparada la integración futura con Compras.

---

# 18. ALERTAS

Generar alertas por:

* Stock mínimo alcanzado.
* Repuesto agotado.
* Repuesto próximo a vencer.
* Lote vencido.
* Solicitud pendiente.
* Reserva no entregada.
* Orden detenida.
* Diferencia de inventario.
* Repuesto de alta rotación.
* Material sin movimiento.

Las alertas deben respetar:

* Empresa.
* Sede.
* Rol.
* Preferencias de notificación.
* Prevención de duplicados.

---

# 19. SEGURIDAD Y MULTIEMPRESA

Aplicar:

* Autenticación.
* Autorización por rol.
* Filtrado por tenant.
* RLS si está habilitado.
* Protección contra IDOR.
* Validación en backend.
* Auditoría.
* Operaciones transaccionales.
* Bloqueo de concurrencia.
* Idempotencia.
* Sanitización.
* Paginación.
* Límites de carga.

Comprobar que un usuario no pueda:

* Ver repuestos de otra empresa.
* Mover existencias ajenas.
* Consumir stock de otra sede sin autorización.
* Relacionar órdenes y repuestos de tenants diferentes.
* Alterar cantidades desde un payload manual.
* Generar movimientos duplicados.
* Modificar movimientos confirmados.

---

# 20. CONCURRENCIA Y TRANSACCIONES

Evitar sobreconsumo cuando dos usuarios soliciten el mismo repuesto.

Usar mecanismos apropiados:

* Transacciones.
* Bloqueo de filas.
* Versionado optimista.
* Restricciones.
* Validaciones dentro de la transacción.
* Idempotencia.

Ejemplo:

```text
Existencia disponible: 5
Usuario A solicita 4
Usuario B solicita 3
```

El sistema no debe aprobar un total de 7.

Toda operación debe ser atómica:

```text
crear movimiento
→ actualizar existencia
→ registrar auditoría
→ relacionar con la orden
→ confirmar
```

Si falla un paso crítico, hacer rollback.

---

# 21. API

Diseña endpoints REST coherentes con el proyecto para:

* Catálogo.
* Bodegas.
* Existencias.
* Movimientos.
* Solicitudes.
* Reservas.
* Entregas.
* Consumos.
* Devoluciones.
* Transferencias.
* Alertas.
* Compatibilidad.
* Reportes.

Ejemplos orientativos:

```text
GET    /repuestos
POST   /repuestos
GET    /repuestos/{id}
PUT    /repuestos/{id}
PATCH  /repuestos/{id}/estado

GET    /repuestos/existencias
GET    /repuestos/{id}/existencias
GET    /repuestos/{id}/movimientos

POST   /repuestos/movimientos/entrada
POST   /repuestos/movimientos/ajuste
POST   /repuestos/movimientos/transferencia

POST   /ordenes/{id}/repuestos/solicitar
POST   /ordenes/{id}/repuestos/reservar
POST   /ordenes/{id}/repuestos/entregar
POST   /ordenes/{id}/repuestos/consumir
POST   /ordenes/{id}/repuestos/devolver
```

No copies estos endpoints automáticamente. Adáptalos a las convenciones existentes y evita rutas duplicadas.

Usa:

* Schemas Pydantic estrictos.
* Enums.
* UUID.
* Decimal.
* Respuestas paginadas.
* Errores claros.
* OpenAPI correctamente documentado.

---

# 22. FRONTEND

Construye una interfaz profesional y separada.

Componentes sugeridos:

```text
RepuestosPage
RepuestoForm
RepuestoDetail
ExistenciasTable
MovimientosTable
SolicitudRepuestoModal
ReservaRepuestoModal
EntregaRepuestoModal
DevolucionRepuestoModal
TransferenciaModal
StockAlertPanel
RepuestoCompatibility
RepuestoHistory
```

Reutiliza componentes existentes cuando sea apropiado.

No construyas un archivo monolítico.

Usa:

* Formularios con validación.
* Errores en línea.
* Toasts.
* Modales accesibles.
* Indicadores de carga.
* Confirmaciones.
* Tablas responsive.
* Filtros.
* Paginación.
* Búsqueda con debounce.
* Estados vacíos.
* Diseño coherente con VANER ASSET.

Evita `alert()`, `prompt()` y `confirm()` nativos.

---

# 23. REPORTES E INDICADORES

Crear reportes por:

* Empresa.
* Sede.
* Bodega.
* Repuesto.
* Categoría.
* Orden.
* Equipo.
* Técnico.
* Periodo.
* Tipo de movimiento.
* Proveedor.

Indicadores:

* Valor del inventario.
* Consumo mensual.
* Costo por activo.
* Costo por orden.
* Repuestos más utilizados.
* Repuestos agotados.
* Stock bajo.
* Rotación.
* Días de inventario.
* Material sin movimiento.
* Diferencias de inventario.
* Órdenes pendientes por material.

Las exportaciones deben respetar filtros, permisos y tenant.

---

# 24. AUDITORÍA

Registrar:

* Creación y edición de catálogo.
* Activación y desactivación.
* Entradas.
* Salidas.
* Reservas.
* Liberaciones.
* Entregas.
* Consumos.
* Devoluciones.
* Ajustes.
* Transferencias.
* Cambios de costo.
* Cambios de stock mínimo.
* Usuario.
* Fecha.
* IP, cuando la arquitectura lo contemple.
* Valores anteriores y nuevos.

Los movimientos confirmados deben ser inmutables.

---

# 25. MIGRACIONES

Si se necesitan cambios:

1. Crear migraciones Alembic nuevas y reversibles.
2. No modificar migraciones aplicadas.
3. No borrar datos históricos.
4. No eliminar columnas existentes inmediatamente.
5. Crear índices y restricciones.
6. Preparar migración de datos.
7. Validar conteos.
8. Probar `upgrade()`.
9. Probar `downgrade()` cuando sea seguro.
10. Documentar comandos.
11. No ejecutar en producción sin autorización.

Incluir plan de respaldo y reversión.

---

# 26. PRUEBAS OBLIGATORIAS

## Backend

Probar:

1. Crear repuesto.
2. Evitar códigos duplicados por empresa.
3. Permitir mismo código en tenants diferentes si la regla lo admite.
4. Crear entrada.
5. Crear reserva.
6. Liberar reserva.
7. Entregar material.
8. Confirmar consumo.
9. Procesar devolución.
10. Procesar transferencia.
11. Procesar ajuste.
12. Rechazar cantidad negativa.
13. Rechazar stock insuficiente.
14. Evitar sobreconsumo concurrente.
15. Evitar movimiento duplicado.
16. Calcular costos con Decimal.
17. Relacionar consumo con orden.
18. Actualizar costo de la orden.
19. Respetar tenant.
20. Respetar roles.
21. Proteger movimientos inmutables.
22. Ejecutar rollback ante fallos.

## Frontend

Probar:

1. Abrir módulo propio.
2. Crear repuesto.
3. Buscar y filtrar.
4. Consultar existencias.
5. Registrar entrada.
6. Solicitar desde una orden.
7. Mostrar stock disponible.
8. Reservar.
9. Entregar.
10. Consumir.
11. Devolver.
12. Mostrar errores.
13. Impedir doble envío.
14. Navegar mediante teclado.
15. Funcionar en móvil.

## Flujo end-to-end

```text
Administrador crea repuesto
→ registra entrada en bodega
→ técnico solicita desde una orden
→ coordinador aprueba
→ sistema reserva
→ almacén entrega
→ técnico utiliza una parte
→ devuelve el sobrante
→ sistema actualiza existencias
→ calcula el costo
→ actualiza la orden
→ aparece en hoja de vida
→ aparece en reportes
```

---

# 27. CRITERIOS DE ACEPTACIÓN

El módulo estará terminado solamente si:

* `/admin/repuestos` abre una pantalla propia.
* Existe catálogo central.
* Se controlan existencias por bodega.
* Se registran movimientos inmutables.
* Se permiten reservas.
* Se impide stock negativo.
* La integración con órdenes es transaccional.
* Los consumos calculan costos.
* Se actualizan informes y hoja de vida.
* Se conserva la información histórica.
* No existen copias contradictorias.
* Se respeta el aislamiento multiempresa.
* Se evitan movimientos duplicados.
* Se controla la concurrencia.
* Las pruebas pasan.
* El frontend compila.
* El backend inicia.
* No existen errores en consola.
* La documentación queda actualizada.

---

# 28. IMPLEMENTACIÓN POR FASES

## Fase 1 — Auditoría y diseño

* Inventario de código existente.
* Modelo de datos.
* Fuente oficial.
* Plan de migración.
* Matriz de permisos.
* Política de valoración.
* Política de descuento.

## Fase 2 — Catálogo y existencias

* Catálogo.
* Bodegas.
* Ubicaciones.
* Existencias.
* Entradas.
* Ajustes.
* Pantalla propia.

## Fase 3 — Integración con órdenes

* Solicitudes.
* Reservas.
* Entregas.
* Consumos.
* Devoluciones.
* Costos.
* Trazabilidad.

## Fase 4 — Automatización

* Stock mínimo.
* Alertas.
* Compatibilidad.
* Sugerencias.
* Necesidades de compra.
* Reportes.

## Fase 5 — Consolidación

* Migración de datos históricos.
* Eliminación controlada de duplicidad.
* Actualización de informes.
* Actualización de formatos.
* Documentación.

## Fase 6 — Verificación

* Pruebas.
* Compilación.
* Migraciones.
* Seguridad.
* Rendimiento.
* Flujo end-to-end.

No avances si la fase anterior presenta errores.

---

# 29. ENTREGA FINAL

Entrega:

1. Diagnóstico inicial.
2. Arquitectura implementada.
3. Modelo de datos.
4. Fuente oficial de repuestos.
5. Lista de archivos modificados.
6. Migraciones creadas.
7. Endpoints.
8. Componentes frontend.
9. Matriz de permisos.
10. Reglas de negocio.
11. Política de valoración.
12. Política de existencias.
13. Estrategia de concurrencia.
14. Datos históricos migrados.
15. Conteos antes y después.
16. Pruebas ejecutadas.
17. Resultados.
18. Instrucciones manuales.
19. Comandos de migración.
20. Plan de respaldo y reversión.
21. Riesgos pendientes.
22. Confirmación de que no se perdieron datos.

---

# 30. RESTRICCIONES FINALES

* No conviertas repuestos en activos.
* No dupliques el módulo de inventario.
* No reutilices `MantenimientosPage`.
* No registres movimientos solamente en el frontend.
* No permitas stock negativo.
* No uses `float` para dinero.
* No confíes en cantidades enviadas por el cliente.
* No permitas acceso cruzado entre empresas.
* No borres datos históricos.
* No modifiques migraciones aplicadas.
* No expongas secretos.
* No ejecutes migraciones productivas automáticamente.
* No agregues dependencias innecesarias.
* No marques pruebas como exitosas sin ejecutarlas.
* No ocultes errores.
* No implementes antes de recibir autorización.

Comienza entregando únicamente:

```text
1. Auditoría del estado actual.
2. Duplicidades encontradas.
3. Modelo de datos propuesto.
4. Flujo operativo recomendado.
5. Matriz de permisos.
6. Migraciones necesarias.
7. Plan de implementación por fases.
8. Riesgos y compatibilidad.
```

Espera autorización antes de modificar el proyecto.
