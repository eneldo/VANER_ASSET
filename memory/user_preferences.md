# Preferencias del Proyecto

Registrar preferencias técnicas y operativas estables.

## Flujo de trabajo
- Todos los cambios se commitean y pushean a GitHub después de cada fase
- Usar convenciones de commits: tipo(alcance): descripción
- No sobrescribir trabajo existente del usuario

## Código
- Python: seguir estilo existente, sin comentarios除非solicitados
- React: usar functional components, hooks, JSX
- SQL: usar queries parametrizados, nunca f-strings con input del usuario

## Seguridad
- Contraseñas: Argon2id con memory-hard
- JWT: access + refresh tokens, HttpOnly cookies
- RLS: obligatorio para tablas tenant-scoped
- Rate limiting: Redis en producción, in-memory en desarrollo

## Testing
- Backend: pytest con fixtures
- Frontend: Vitest
- E2E: Playwright
- Siempre ejecutar tests antes de declarar una tarea terminada

## Despliegue
- APP_ENV=production en producción
- Sentry para monitoreo de errores
- Backups automáticos diarios
- CI/CD con GitHub Actions
