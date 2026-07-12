# Rotación de secretos y saneamiento del historial

Este procedimiento debe ejecutarse antes de publicar o compartir el repositorio. La eliminación de un archivo del estado actual no invalida credenciales que hayan quedado en commits anteriores.

## Estado de ejecución — 12 de julio de 2026

- `backend/.env` fue eliminado de todos los commits locales mediante `git-filter-repo`.
- Se reintrodujo únicamente como plantilla sin credenciales operativas.
- Se creó una copia de recuperación local restringida antes de la reescritura; contiene el historial anterior y no debe compartirse.
- La revocación de la credencial en el proveedor sigue siendo obligatoria y debe registrarse cuando el entorno de staging/producción inyecte acceso administrativo.

## 1. Contención y rotación

1. Identificar las credenciales históricas sin copiarlas a tickets, chats ni registros.
2. Rotar primero la contraseña del propietario de PostgreSQL y después la del rol de aplicación `sga_app`.
3. Actualizar el gestor de secretos del entorno y reiniciar los servicios de forma coordinada.
4. Rotar `SECRET_KEY`; esto invalida deliberadamente los tokens JWT activos y obliga a iniciar sesión de nuevo.
5. Revocar cualquier otra clave que hubiese compartido el mismo archivo o canal.

## 2. Verificación operativa

Tras la rotación:

- ejecutar las migraciones con `MIGRATION_DATABASE_URL` usando el rol propietario;
- verificar que `sga_app` conserva `NOBYPASSRLS` y no es superusuario;
- ejecutar `backend/scripts/verify_postgres_rls.py`;
- ejecutar las pruebas del backend y el build/lint del frontend;
- comprobar autenticación, acceso por tenant, carga de evidencias y descarga privada de reportes.

## 3. Purga coordinada del historial Git

La reescritura del historial es disruptiva y requiere aprobación explícita, ventana de mantenimiento y coordinación con todas las personas que tengan clones o ramas abiertas. Una opción es `git filter-repo` para retirar `backend/.env` de todos los commits. Después se revisan los objetos resultantes y se hace un `push --force-with-lease` únicamente con autorización.

Todos los colaboradores deben descartar clones antiguos y volver a clonar. Los forks, artefactos de CI, cachés y copias de seguridad deben revisarse por separado: reescribir Git no revoca secretos ni elimina copias externas.

## 4. Prevención

- Mantener únicamente plantillas sin secretos (`.env.example` y `backend/.env`).
- Inyectar secretos reales desde el gestor del entorno o un archivo local ignorado.
- Activar escaneo de secretos en pre-commit y CI.
- Aplicar privilegio mínimo y rotación periódica a cuentas de base de datos y almacenamiento.
- Registrar responsable, fecha, alcance y evidencia de cada rotación sin registrar el valor secreto.
