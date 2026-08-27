# Convenciones del Proyecto

Registrar convenciones estables.

## Commits

```
tipo(alcance): descripción

Tipos:
- feat: nueva funcionalidad
- fix: corrección de bug
- docs: documentación
- test: tests
- chore: mantenimiento
- security: seguridad
- refactor: refactoring
- perf: performance
```

## Archivos

- Backend: `app/routers/`, `app/models/`, `app/services/`
- Frontend: `src/pages/`, `src/components/`
- Tests: `tests/`
- Scripts: `scripts/`
- Docs: raíz del proyecto

## Naming

- Python: snake_case
- React: PascalCase para componentes
- CSS: kebab-case
- SQL: snake_case

## Seguridad

- Nunca guardar secretos en código
- Usar .env para configuración
- .env.example sin valores sensibles
- RLS obligatorio para tablas tenant-scoped

## Testing

- pytest para backend
- Vitest para frontend
- Playwright para E2E
- Siempre ejecutar antes de declarar terminada una tarea
