# ADR-0001 — Separación CORE y configuración de cliente en runtime

## Estado

Aceptada — 2026-08-25.

## Contexto

VANER ASSET debe reutilizar el mismo backend y la misma imagen frontend para distintos despliegues sin codificar nombres, dominios o datos de un cliente dentro del CORE.

Las variables de despliegue requeridas son:

- `APP_NAME`: nombre visible de la aplicación.
- `CLIENT_CODE`: identificador técnico estable del despliegue.
- `CLIENT_NAME`: nombre comercial del cliente.
- `APP_DOMAIN`: hostname público sin protocolo ni ruta.

## Decisión

1. El CORE conserva únicamente la identidad del producto y de VANER SOFTWARE.
2. El backend lee la identidad del cliente desde variables de entorno.
3. `FRONTEND_URL` y `BACKEND_CORS_ORIGINS` se derivan de `APP_DOMAIN` cuando no se proporcionan overrides.
4. El backend publica metadatos no sensibles en `/public/config` y un manifest en `/public/manifest.webmanifest`.
5. El frontend carga `/api/public/config` antes del primer render y actualiza título, organización visible y metadatos.
6. La imagen frontend no contiene variables de un cliente concreto y puede reutilizarse entre despliegues.
7. Caddy utiliza `APP_DOMAIN`; `DOMAIN` se admite solo como fallback temporal en `deploy.sh`.

## Consecuencias

- Un cambio de cliente no requiere editar backend o frontend.
- La configuración del cliente permanece fuera de Git.
- El endpoint público debe limitarse a datos no sensibles.
- La configuración actual representa un despliegue; resolver múltiples marcas por `Host` dentro de una sola instancia queda como evolución futura.

## Validación

- Pruebas backend para derivación, seguridad y endpoint público.
- Pruebas frontend para separación CORE/cliente y carga runtime.
- Validación de Compose, build, lint y regresión completa.
