# =========================================================
# FASE 31.3 - MIDDLEWARE REQUEST ID
# Archivo: backend/app/middleware/request_id.py
# Objetivo:
#   Generar un identificador único por petición para trazabilidad.
#   Este ID ayuda a cruzar errores del frontend, logs backend y auditoría.
# =========================================================

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Agrega X-Request-ID a cada request/response.
    Si el cliente ya envía uno, se conserva; si no, se genera.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
