# =========================================================
# FASE 31.3 - RATE LIMITING SIN DEPENDENCIAS EXTERNAS
# Archivo: backend/app/middleware/rate_limit.py
# Objetivo:
#   Proteger el backend contra abuso básico y fuerza bruta.
#   Implementación en memoria para desarrollo/VM pequeña.
#   En producción distribuida, reemplazar por Redis o Nginx rate limit.
# =========================================================

import time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limit por IP y ruta.

    Límites por defecto:
    - /auth/login: más estricto.
    - /auth/refresh: moderado.
    - resto de API: amplio para operación normal.
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(deque)

        # Configuración por ruta: path_prefix -> (cantidad, ventana_segundos)
        self.rules = {
            "/auth/login": (10, 60),       # 10 intentos por minuto por IP
            "/auth/refresh": (30, 60),    # 30 renovaciones por minuto por IP
            "default": (300, 60),         # 300 requests por minuto por IP/ruta
        }

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _rule_for_path(self, path: str):
        for prefix, rule in self.rules.items():
            if prefix != "default" and path.startswith(prefix):
                return rule
        return self.rules["default"]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Evita limitar documentación local y archivos estáticos.
        if path.startswith(("/docs", "/redoc", "/openapi.json", "/uploads")):
            return await call_next(request)

        ip = self._client_ip(request)
        limit, window = self._rule_for_path(path)
        key = f"{ip}:{path}"
        now = time.time()
        bucket = self.requests[key]

        # Limpieza de eventos antiguos fuera de ventana.
        while bucket and bucket[0] <= now - window:
            bucket.popleft()

        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas solicitudes. Intenta nuevamente en unos segundos.",
                    "retry_after_seconds": window,
                },
                headers={"Retry-After": str(window)},
            )

        bucket.append(now)
        return await call_next(request)
