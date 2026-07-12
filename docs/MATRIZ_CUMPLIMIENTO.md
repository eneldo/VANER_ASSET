# Matriz de cumplimiento funcional

| Requisito | Evidencia actual | Estado |
|---|---|---|
| Cuatro roles | Guards frontend, dependencias FastAPI y pruebas de scope | Implementado |
| Empresas y múltiples sedes | Modelos, CRUD ADMIN y portal tenant-scoped | Implementado |
| Cuatro categorías | Catálogo canónico y migración `c93e1a640001` | Implementado |
| Inventario global ADMIN | Panel y API ADMIN | Implementado |
| Personal y asignación | Usuarios, técnicos, coordinación y OTs | Implementado |
| Facturación | Facturas, cartera y migración `d04f2b750001` | Implementado |
| Plantillas PDF | Alcance global/tenant, estilo y secciones configurables | Implementado |
| Planificación coordinador | CRUD y cronograma tenant-scoped | Implementado |
| Monitoreo OTs | Dashboard coordinador con polling autenticado cada 15 s, estado de conexión y hora del último dato válido | Implementado (near real-time) |
| Reporte PDF por OT | PDF con ejecución, fotos, repuestos, incidencias y firma | Implementado |
| Consolidado mensual | Generación privada y aprobación | Implementado |
| Dashboard director | KPIs, dona, barras y actividad del día | Implementado |
| Descarga de aprobados | Listado y descarga JWT tenant-scoped | Implementado |
| Emergencias correctivas | Portal, API, estados e idempotencia | Implementado |
| Flujo técnico 3 fotos | Secuencia y finalización validadas en backend | Implementado |
| Firma digital | Canvas táctil y PNG validado | Implementado |
| Repuestos e incidencias | Tablas relacionales y formulario offline | Implementado |
| PWA offline | Manifest, SW, IndexedDB y sincronización | Implementado con límites documentados |
| Aislamiento aplicación | JWT, RBAC, tenant filters y pruebas | Implementado |
| RLS PostgreSQL | Políticas directas/indirectas, rol `sga_app` sin BYPASSRLS y prueba real con dos tenants | Implementado y verificado localmente |
| Migraciones aplicadas | 46 tablas auditadas y base local en `i59e7a2a0001 (head)`; sin DDL al arrancar | Implementado localmente |
| Calidad frontend | Build, code splitting, lint global limpio y 12 pruebas Vitest/Testing Library; entrada principal ~290 KB | Implementado |

La plataforma no debe declararse lista para producción mientras permanezcan pendientes las advertencias de hooks, la rotación/purga del secreto presente en el historial Git y los demás gates descritos en la arquitectura. La restauración del backup y la restricción CORS ya fueron verificadas.
