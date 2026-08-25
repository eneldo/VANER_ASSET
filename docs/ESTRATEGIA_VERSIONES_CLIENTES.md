# Estrategia de versiones por cliente

## Objetivo

Conservar de forma inmutable la version entregada a SGAHolding y desarrollar nuevas implementaciones sin mezclar codigo, datos, secretos ni despliegues.

## Referencias Git

- `v1.0.14`: entrega congelada del producto para SGAHolding.
- `support/sgaholding-v1`: mantenimiento exclusivo de la version entregada.
- `client/nuevo-cliente-v2`: punto de partida de la siguiente implementacion.
- `main`: integracion estable del producto; no debe usarse como entorno de produccion mutable.

Las correcciones para SGAHolding se realizan en su rama de soporte. Una correccion reutilizable se incorpora a otras ramas mediante un commit revisado o `cherry-pick`; nunca se reemplaza una rama completa de cliente.

## Separacion obligatoria

Cada cliente debe tener recursos independientes:

- archivo `.env` fuera de Git;
- base de datos y usuarios PostgreSQL propios;
- volumen de archivos subidos;
- volumen y almacenamiento remoto de backups;
- Redis y credenciales propias;
- dominio, certificados, correo e integraciones;
- secretos JWT, cifrado, cookies y cuentas administrativas;
- proyecto Compose o VPS claramente identificado.

No se deben copiar datos personales, archivos, backups ni credenciales de SGAHolding hacia el nuevo cliente.

## Configuracion y personalizacion

Nombre comercial, logotipo, dominio, colores, textos, integraciones y funcionalidades deben parametrizarse. No se deben crear copias manuales de modulos completos cuando una configuracion por cliente resuelve la diferencia.

## Flujo de entrega

1. Validar pruebas, build, migraciones y Compose.
2. Crear commit de release y etiqueta anotada.
3. Crear snapshot con `scripts/create_release_snapshot.ps1`.
4. Ejecutar `scripts/backup_production_release.sh` en el VPS.
5. Copiar el respaldo cifrado fuera del VPS.
6. Publicar imagenes inmutables con el SHA del commit.
7. Desplegar con `IMAGE_TAG` exacto y registrar el resultado.
8. Ejecutar smoke tests y una restauracion de prueba.

## Regla de soporte

Las etiquetas no se mueven ni se reutilizan. Cada actualizacion de un cliente recibe una etiqueta nueva y un registro de cambios propio.
