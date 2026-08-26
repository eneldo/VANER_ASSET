# PROMPT MAESTRO — POLÍTICA SEGURA DE CONTRASEÑAS PARA VANER ASSET

Actúa como arquitecto de software y especialista en ciberseguridad, con experiencia en FastAPI, PostgreSQL, React/Vite, JWT, sistemas multiempresa y estándares OWASP y NIST.

Tu tarea es analizar e implementar una política profesional de contraseñas en VANER Asset, una plataforma multiempresa para la gestión de inventarios, activos, mantenimiento, órdenes de trabajo, repuestos, técnicos y trazabilidad.

## 1. Instrucciones iniciales

Antes de modificar el código:

1. Analiza completamente la estructura del proyecto.
2. Localiza:

   * Modelos de usuarios.
   * Esquemas Pydantic.
   * Endpoints de autenticación.
   * Servicio de contraseñas.
   * Creación de usuarios.
   * Recuperación y cambio de contraseña.
   * Script de creación del administrador inicial.
   * Componentes React relacionados con contraseñas.
   * Migraciones Alembic.
   * Pruebas existentes.
3. Identifica las librerías actuales de hash, autenticación y validación.
4. Conserva la arquitectura y convenciones existentes.
5. No elimines funcionalidades que ya estén operativas.
6. No inventes rutas, tablas ni nombres de archivos sin revisar primero el proyecto.
7. Realiza cambios mínimos, seguros y compatibles.
8. Antes de editar, presenta un resumen de los archivos que serán modificados.

## 2. Política de longitud

Implementa estas reglas:

* Contraseña mínima de 15 caracteres para cuentas sin MFA.
* Contraseña mínima de 12 caracteres cuando la cuenta tenga MFA habilitado.
* Longitud máxima admitida de 128 caracteres.
* Permitir:

  * Mayúsculas.
  * Minúsculas.
  * Números.
  * Caracteres especiales.
  * Espacios.
  * Caracteres Unicode válidos.
* No recortar la contraseña automáticamente.
* No modificar mayúsculas, minúsculas ni espacios introducidos por el usuario.
* No imponer obligatoriamente la combinación de mayúsculas, números y símbolos.
* Permitir frases de contraseña largas y fáciles de recordar.

Ejemplo válido:

`Inventarios seguros Casanare 2026`

## 3. Contraseñas prohibidas

Rechaza:

* Contraseñas comunes o conocidas.
* Contraseñas comprometidas.
* Secuencias predecibles.
* Contraseñas predeterminadas.
* Contraseñas relacionadas con VANER Asset.
* Contraseñas que contengan el nombre, apellido, usuario o correo del propietario.
* Contraseñas que contengan el nombre, NIT, dominio o identificador de la empresa.
* Contraseñas que coincidan con las últimas cinco contraseñas utilizadas.

La comparación debe ser insensible a mayúsculas y minúsculas cuando se busquen datos personales dentro de la contraseña.

Incluye inicialmente una lista local de términos prohibidos:

* `password`
* `contraseña`
* `admin`
* `administrador`
* `admin123`
* `123456`
* `12345678`
* `qwerty`
* `vaner`
* `vanerasset`
* `vaner asset`
* `inventario`
* `mantenimiento`
* `empresa123`

Diseña la validación para que posteriormente pueda integrarse con un servicio de detección de contraseñas comprometidas, sin enviar la contraseña completa a servicios externos.

## 4. Historial de contraseñas

Implementa un historial seguro que permita:

* Conservar los hashes de las últimas cinco contraseñas.
* Impedir su reutilización.
* Registrar:

  * Identificador del usuario.
  * Identificador de empresa o tenant.
  * Hash de la contraseña anterior.
  * Fecha del cambio.
  * Motivo del cambio.
* Nunca almacenar la contraseña en texto plano.
* Aplicar aislamiento multiempresa.
* Crear la migración Alembic correspondiente.
* Añadir índices y restricciones necesarias.

## 5. Almacenamiento seguro

Utiliza Argon2id como algoritmo recomendado para contraseñas nuevas.

Requisitos:

* Salt único y aleatorio.
* Parámetros configurables mediante variables de entorno.
* Comparación segura.
* No registrar contraseñas en logs.
* No devolver hashes mediante la API.
* No incluir hashes en esquemas Pydantic de respuesta.
* Migrar progresivamente hashes antiguos cuando el usuario inicie sesión correctamente.
* Si el proyecto ya utiliza bcrypt, conservar compatibilidad durante la transición.
* No aplicar una migración irreversible que impida el acceso a usuarios existentes.

## 6. Contraseñas temporales

Cuando un administrador cree o restablezca una cuenta:

* Generar una contraseña temporal criptográficamente segura.
* No utilizar contraseñas fijas.
* Marcar la cuenta con `debe_cambiar_password`.
* Establecer vencimiento máximo de 24 horas.
* Obligar a cambiarla durante el primer acceso.
* Impedir el acceso a los módulos hasta completar el cambio.
* Invalidar la contraseña temporal después de utilizarla.
* No enviar contraseñas permanentes por correo electrónico.

## 7. Cambio de contraseña

Para cambiar la contraseña desde una sesión autenticada:

* Solicitar la contraseña actual.
* Verificarla en el backend.
* Validar la nueva contraseña con la política completa.
* Solicitar confirmación de la nueva contraseña.
* Impedir que sea igual a la contraseña actual.
* Consultar el historial de las últimas cinco.
* Actualizar el hash mediante una transacción.
* Registrar el hash anterior en el historial.
* Actualizar la fecha del último cambio.
* Revocar todas las sesiones y refresh tokens anteriores.
* Permitir opcionalmente conservar únicamente la sesión desde la que se realizó el cambio.
* Generar un evento de auditoría.
* Notificar al usuario que su contraseña fue modificada.

## 8. Recuperación de contraseña

El proceso debe:

* Mostrar siempre este mensaje:

  `Si la cuenta está registrada, recibirás instrucciones para recuperar el acceso.`

* No revelar si un usuario o correo existe.

* Crear un token aleatorio, seguro y de un solo uso.

* Guardar únicamente el hash del token.

* Establecer una vigencia de 15 minutos.

* Invalidarlo después del primer uso.

* Invalidar tokens anteriores cuando se solicite uno nuevo.

* Aplicar limitación de solicitudes por usuario e IP.

* No iniciar sesión automáticamente después del cambio.

* Revocar todas las sesiones activas.

* Registrar el evento en la auditoría.

* Enviar una notificación de seguridad.

## 9. Validación centralizada

Crea un servicio centralizado y reutilizable para la política de contraseñas.

Debe poder utilizarse desde:

* Creación de usuarios.
* Creación del administrador inicial.
* Cambio de contraseña.
* Primer acceso.
* Recuperación de contraseña.
* Restablecimiento realizado por un administrador.
* Importación de usuarios.
* API administrativa.

No dupliques las reglas en diferentes endpoints.

La validación debe devolver códigos internos estructurados, por ejemplo:

* `PASSWORD_TOO_SHORT`
* `PASSWORD_TOO_LONG`
* `PASSWORD_COMMON`
* `PASSWORD_COMPROMISED`
* `PASSWORD_CONTAINS_USERNAME`
* `PASSWORD_CONTAINS_EMAIL`
* `PASSWORD_CONTAINS_TENANT_DATA`
* `PASSWORD_RECENTLY_USED`
* `PASSWORD_SAME_AS_CURRENT`

El frontend debe transformar esos códigos en mensajes claros en español.

## 10. Experiencia de usuario

En los formularios React:

* Incorporar botones para mostrar y ocultar contraseña.
* Mostrar los requisitos antes de guardar.
* Añadir un indicador de seguridad accesible.
* Actualizar cada regla en tiempo real.
* No mostrar la contraseña en consola.
* No guardar contraseñas en `localStorage` ni `sessionStorage`.
* Desactivar temporalmente el botón durante la solicitud.
* Evitar envíos duplicados.
* Permitir pegar contraseñas.
* Permitir el uso de gestores de contraseñas.
* Utilizar correctamente `autocomplete`:

  * `current-password`
  * `new-password`
* Mantener accesibilidad mediante etiquetas, mensajes ARIA y navegación por teclado.

Mensajes sugeridos:

* `La contraseña debe tener al menos 15 caracteres.`
* `Puedes utilizar una frase larga con espacios.`
* `Esta contraseña es demasiado común o fácil de adivinar.`
* `La contraseña contiene información relacionada con tu cuenta.`
* `Esta contraseña fue utilizada recientemente.`
* `Las contraseñas no coinciden.`
* `La contraseña fue actualizada correctamente.`

No revelar públicamente todos los criterios internos utilizados para detectar una contraseña prohibida.

## 11. Administración multiempresa

Permite que el superadministrador configure por empresa:

* Longitud mínima.
* Longitud máxima.
* Cantidad de contraseñas recordadas.
* Duración de contraseñas temporales.
* MFA obligatorio por rol.
* Número de intentos antes de aplicar demoras.
* Bloqueo temporal.
* Duración del bloqueo.

Las políticas de una empresa nunca deben afectar a otra.

Define una política global segura que se aplique cuando una empresa no tenga configuración propia. Una empresa podrá endurecer la política global, pero no reducirla por debajo del mínimo de seguridad establecido por VANER Asset.

## 12. Auditoría

Registrar los siguientes eventos:

* `PASSWORD_CHANGE_OK`
* `PASSWORD_CHANGE_FAILED`
* `PASSWORD_RESET_REQUESTED`
* `PASSWORD_RESET_COMPLETED`
* `PASSWORD_TEMPORARY_CREATED`
* `PASSWORD_TEMPORARY_EXPIRED`
* `PASSWORD_POLICY_REJECTED`
* `PASSWORD_HASH_UPGRADED`
* `SESSIONS_REVOKED`

Cada registro debe contener, cuando corresponda:

* Usuario.
* Empresa.
* Fecha y hora UTC.
* Dirección IP.
* Agente del navegador.
* Tipo de evento.
* Resultado.
* Motivo general.
* Identificador de correlación.

Nunca registrar:

* Contraseña.
* Contraseña temporal.
* Hash de contraseña.
* Token de recuperación.
* Hash del token.
* Datos sensibles innecesarios.

## 13. Variables de entorno

Si son necesarias, documenta variables como:

```env
PASSWORD_MIN_LENGTH=15
PASSWORD_MIN_LENGTH_WITH_MFA=12
PASSWORD_MAX_LENGTH=128
PASSWORD_HISTORY_COUNT=5
TEMP_PASSWORD_EXPIRATION_HOURS=24
PASSWORD_RESET_EXPIRATION_MINUTES=15
ARGON2_TIME_COST=3
ARGON2_MEMORY_COST=65536
ARGON2_PARALLELISM=4
```

No incluyas secretos reales en `.env.example`.

## 14. Pruebas obligatorias

Crea pruebas unitarias y de integración para comprobar:

1. Contraseña demasiado corta.
2. Contraseña superior al máximo.
3. Frase de contraseña válida.
4. Contraseña común.
5. Contraseña relacionada con VANER Asset.
6. Contraseña que contiene el usuario.
7. Contraseña que contiene el correo.
8. Contraseña relacionada con la empresa.
9. Reutilización de contraseña.
10. Contraseña temporal vencida.
11. Cambio exitoso.
12. Revocación de sesiones.
13. Recuperación con token válido.
14. Recuperación con token vencido.
15. Reutilización del token.
16. Aislamiento entre empresas.
17. Compatibilidad con hashes bcrypt existentes.
18. Migración automática a Argon2id.
19. Ausencia de contraseñas y hashes en logs.
20. Mensajes de error seguros.

## 15. Criterios de aceptación

La implementación estará completa solamente cuando:

* Todas las rutas que establecen contraseñas utilicen el servicio centralizado.
* No existan contraseñas ni hashes expuestos.
* Argon2id funcione correctamente.
* Los hashes bcrypt anteriores sigan siendo válidos.
* El historial impida reutilizar las últimas cinco contraseñas.
* Las contraseñas temporales venzan.
* Los tokens de recuperación sean de un solo uso.
* Las sesiones se revoquen después del cambio.
* La política respete el aislamiento multiempresa.
* El frontend muestre correctamente los requisitos.
* Las migraciones se ejecuten sin errores.
* Las pruebas nuevas y existentes sean satisfactorias.
* La documentación quede actualizada.

## 16. Entrega esperada

Al finalizar, entrega:

1. Diagnóstico del estado anterior.
2. Archivos creados.
3. Archivos modificados.
4. Migraciones generadas.
5. Explicación de las decisiones técnicas.
6. Variables de entorno añadidas.
7. Comandos exactos para ejecutar las migraciones.
8. Comandos exactos para ejecutar las pruebas.
9. Resultados obtenidos.
10. Riesgos o pendientes.
11. Lista de verificación manual.
12. Instrucciones para revertir de manera segura.

No afirmes que algo funciona sin ejecutar las pruebas correspondientes. No realices cambios destructivos en la base de datos. No elimines cambios existentes que no estén relacionados con esta tarea.
