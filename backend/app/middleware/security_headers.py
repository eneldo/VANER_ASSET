# =========================================================
# FASE 31.3 - HEADERS DE SEGURIDAD
# Archivo: backend/app/middleware/security_headers.py
# Objetivo:
#   Endurecer las respuestas HTTP con cabeceras de seguridad.
#   En producción, Nginx/Traefik también debe reforzar estas cabeceras.
# =========================================================

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Inserta cabeceras HTTP recomendadas para reducir riesgos comunes:
    - clickjacking
    - MIME sniffing
    - exposición de referrer
    - permisos del navegador innecesarios
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # CSP básica para API. El frontend React debe tener su propia CSP en producción.
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"

        # HSTS solo se debe activar cuando el backend esté detrás de HTTPS real.
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response
