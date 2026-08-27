# Patrones Reutilizables

Registrar patrones técnicos verificados.

## 1. Patrón de migración RLS (2026-08-27)

```python
def upgrade() -> None:
    op.execute("ALTER TABLE tabla ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tabla_empresa_policy ON tabla
        USING (empresa_id::text = current_setting('app.current_empresa_id'))
    """)
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON tabla TO sga_app")
```

## 2. Patrón de health check (2026-08-27)

```python
@router.get("/health/ready")
async def health_ready(response: Response):
    checks = {"status": "ok", "checks": {}}
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["checks"]["database"] = "ok"
    except Exception as e:
        checks["checks"]["database"] = f"error: {str(e)}"
        checks["status"] = "degraded"
        response.status_code = 503
    return checks
```

## 3. Patrón de backup con retención (2026-08-27)

```python
def ejecutar_backup(db_config, backup_dir, retention_days):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"vaner_asset_{timestamp}.sql.gz"
    # pg_dump...
    limpiar_backups_antiguos(backup_dir, retention_days)

def limpiar_backups_antiguos(backup_dir, retention_days):
    cutoff = datetime.now() - timedelta(days=retention_days)
    for backup in backup_dir.glob("vaner_asset_*.sql.gz"):
        if file_date < cutoff:
            backup.unlink()
```

## 4. Patrón de GDPR endpoints (2026-08-27)

```python
@router.get("/mis-datos")
async def obtener_mis_datos(usuario = Depends(obtener_usuario_actual)):
    return {
        "id": str(usuario.id),
        "email": usuario.email,
        "nombre_completo": usuario.nombre_completo,
    }

@router.post("/solicitar-supresion")
async def solicitar_supresion(solicitud, usuario = Depends(obtener_usuario_actual)):
    # Anonimizar en lugar de eliminar
    usuario.email = f"deleted_{usuario.id}@deleted.com"
    usuario.nombre_completo = "Usuario Eliminado"
    usuario.is_active = False
```

## 5. Patrón de security headers (2026-08-27)

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
```

## 6. Patrón de MFA TOTP (2026-08-27)

```python
def generate_mfa_secret():
    return pyotp.random_base32()

def get_mfa_uri(secret, email):
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="VANER ASSET")

def verify_mfa_code(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
```

## 7. Patrón de E2E test (2026-08-27)

```python
def test_health_endpoints():
    import requests
    response = requests.get(f"{API_URL}/health/live", timeout=10)
    assert response.status_code == 200
```

## 8. Patrón de rate limiting con fallback (2026-08-27)

```python
class RateLimitMiddleware:
    def __init__(self, app):
        self.app = app
        self.redis = None
        self.memory_store = {}

    async def dispatch(self, request, call_next):
        if self.redis:
            # Usar Redis
        else:
            # Fallback in-memory
```
