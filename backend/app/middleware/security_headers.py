# =========================================================
# FASE 31.3 - HEADERS DE SEGURIDAD PRO
# Archivo: backend/app/middleware/security_headers.py
# =========================================================

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        response = await call_next(request)

        # ==========================================
        # HEADERS BÁSICOS
        # ==========================================

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # ==========================================
        # CSP COMPATIBLE CON:
        # - React/Vite
        # - Swagger
        # - Axios
        # - jsdelivr
        # ==========================================

        csp = """
            default-src 'self';
            script-src 'self' 'unsafe-inline' 'unsafe-eval'
                https://cdn.jsdelivr.net;
            style-src 'self' 'unsafe-inline'
                https://cdn.jsdelivr.net;
            img-src 'self' data: https:;
            font-src 'self' data: https:;
            connect-src 'self'
                https://api.sga.vaner.cloud
                https://sga.vaner.cloud;
            frame-ancestors 'self';
            base-uri 'self';
        """

        response.headers["Content-Security-Policy"] = " ".join(csp.split())

        # ==========================================
        # HSTS
        # ==========================================

        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response