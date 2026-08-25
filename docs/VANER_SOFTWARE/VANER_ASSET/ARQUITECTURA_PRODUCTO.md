# Arquitectura de VANER ASSET

## Identidad

- Empresa: VANER SOFTWARE
- Producto: VANER ASSET
- Descripción: Plataforma para la gestión de inventarios, activos y mantenimiento.

## Modulos funcionales

1. Dashboard
2. Inventarios
3. Activos y hojas de vida
4. Mantenimiento
5. Ordenes de trabajo
6. Repuestos utilizados en ordenes
7. Tecnicos
8. Reportes
9. Administracion

## Modelo de clientes

Cada cliente corresponde a una empresa o tenant. El identificador `empresa_id` y las politicas RLS existentes mantienen la separacion operativa.

No se deben crear ramas, carpetas de codigo o tablas duplicadas por cliente. Las diferencias de marca, dominio, modulos e integraciones deben resolverse mediante configuracion.

## Cliente VANER

Cliente VANER es el tenant interno de VANER SOFTWARE. Debe utilizar credenciales, archivos y datos independientes de los clientes comerciales.

## Compatibilidad heredada

Los nombres tecnicos `sga_app`, `sga_backup` y varias tablas historicas se conservan temporalmente para mantener la cadena de migraciones. No representan la identidad visible del producto.
