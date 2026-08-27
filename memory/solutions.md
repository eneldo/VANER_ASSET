# Soluciones Verificadas

Soluciones técnicas reutilizables comprobadas.

## 1. RLS para tablas tenant-scoped (2026-08-27)

**Problema:** Tablas sin RLS permiten acceso cruzado entre tenants.

**Solución:**
```sql
ALTER TABLE tabla ENABLE ROW LEVEL SECURITY;
CREATE POLICY tabla_empresa_policy ON tabla
    USING (empresa_id::text = current_setting('app.current_empresa_id'));
```

**Aplicación:** 34 tablas protegidas con RLS.

## 2. Backup automatizado con pg_dump (2026-08-27)

**Problema:** Sin backups automatizados de PostgreSQL.

**Solución:**
```bash
pg_dump --format=custom --compress=9 --file=backup.sql.gz
```

**Verificación:** Script `restore_drill.py` crea BD temporal, restaura y verifica integridad.

## 3. Pentest con Bandit y pip-audit (2026-08-27)

**Problema:** Sin escaneos de seguridad automatizados.

**Solución:**
```bash
bandit -r app/ -f json -o bandit_report.json
pip-audit -r requirements.txt
```

**Nota:** Bandit genera falsos positivos con f-strings en SQL parametrizado.

## 4. E2E tests con Playwright (2026-08-27)

**Problema:** Sin tests de extremo a extremo.

**Solución:**
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
```

**Recomendación:** Usar requests para API, Playwright para UI.

## 5. GDPR/LGPD endpoints (2026-08-27)

**Problema:** Sin cumplimiento de derechos ARCO.

**Solución:**
- `/auth/mis-datos`: Derecho de acceso
- `/auth/rectificar-datos`: Derecho de rectificación
- `/auth/solicitar-supresion`: Derecho de supresión (anonimización)
- `/auth/exportar-datos`: Derecho a portabilidad

## 6. Security headers (2026-08-27)

**Problema:** Headers de seguridad incompletos.

**Solución:**
```python
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "SAMEORIGIN"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
response.headers["Content-Security-Policy"] = "..."
```

## 7. MFA con TOTP (2026-08-27)

**Problema:** Sin autenticación de dos factores.

**Solución:**
```python
# Generar secreto
secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)
uri = totp.provisioning_uri(name=email, issuer_name="VANER ASSET")

# Verificar código
totp.verify(code)
```

## 8. Rate limiting con fallback (2026-08-27)

**Problema:** Rate limiting requiere Redis que puede no estar disponible.

**Solución:**
```python
if settings.REDIS_URL:
    # Usar Redis
else:
    # Fallback in-memory
```
