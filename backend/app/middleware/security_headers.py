# =========================================================
# FASE 31.3 - HEADERS DE SEGURIDAD PRO
# Archivo: backend/app/middleware/security_headers.py
# Compatible con Swagger UI + React + API SaaS
# =========================================================

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        response = await call_next(request)

        # =====================================================
        # HEADERS BÁSICOS DE SEGURIDAD
        # =====================================================

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        response.headers["X-XSS-Protection"] = "1; mode=block"

        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # =====================================================
        # CSP COMPATIBLE CON:
        # - Swagger UI FastAPI
        # - ReDoc
        # - React/Vite
        # - Axios
        # - jsdelivr CDN
        # - Swagger assets
        # =====================================================

        if settings.APP_ENV.lower() == "production":
            csp = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
        else:
            csp = """
            default-src 'self';

            script-src
                'self'
                'unsafe-inline'
                'unsafe-eval'
                https://cdn.jsdelivr.net
                https://unpkg.com;

            style-src
                'self'
                'unsafe-inline'
                https://cdn.jsdelivr.net
                https://fonts.googleapis.com
                https://unpkg.com;

            img-src
                'self'
                data:
                blob:
                https:;

            font-src
                'self'
                data:
                https:
                https://fonts.gstatic.com;

            connect-src
                'self';

            worker-src
                'self'
                blob:;

            frame-src
                'self';

            frame-ancestors
                'self';

            base-uri
                'self';

            form-action
                'self';
            """

        response.headers["Content-Security-Policy"] = " ".join(csp.split())

        # =====================================================
        # HSTS SOLO EN HTTPS
        # =====================================================

        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response
