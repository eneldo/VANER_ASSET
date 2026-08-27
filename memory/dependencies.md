# Dependencias Importantes

Registrar dependencias críticas y compatibilidades.

## Backend (Python)

### Seguridad
- `passlib[argon2]`: Argon2id para contraseñas
- `python-jose[cryptography]`: JWT tokens
- `cryptography`: Cifrado AES-256
- `argon2-cffi`: Backend Argon2

### Web
- `fastapi`: Framework web
- `uvicorn`: Servidor ASGI
- `sqlalchemy`: ORM
- `alembic`: Migraciones
- `psycopg2-binary`: PostgreSQL driver

### Utilidades
- `pydantic`: Validación de datos
- `pydantic-settings`: Configuración
- `python-dotenv`: Variables de entorno
- `apscheduler`: Tareas programadas
- `psutil`: Métricas del sistema

### Testing
- `pytest`: Framework de tests
- `bandit`: SAST
- `pip-audit`: SCA

## Frontend (Node.js)

### Core
- `react`: UI library
- `react-router-dom`: Routing
- `axios`: HTTP client

### Build
- `vite`: Build tool
- `@vitejs/plugin-react`: React plugin

### UI
- `@fortawesome/react-fontawesome`: Icons
- `chart-react`: Charts

### Testing
- `vitest`: Unit tests
- `playwright`: E2E tests

## Dependencias con vulnerabilidades conocidas

| Paquete | Versión | Vulnerabilidad | Estado |
|---------|---------|----------------|--------|
| ecdsa | 0.19.2 | PYSEC-2026-1325 | Sin fix (dependencia transitiva) |

## Compatibilidades

- Python 3.12+ requerido
- Node.js 18+ requerido
- PostgreSQL 14+ recomendado
- Redis 7+ opcional (fallback in-memory)
