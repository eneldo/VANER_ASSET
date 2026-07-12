# =========================================================
# MIDDLEWARE AUDITORÍA AUTOMÁTICA PRO
# Archivo: backend/app/middleware/audit_middleware.py
# =========================================================
# Registra automáticamente eventos HTTP relevantes:
# - operaciones POST/PUT/PATCH/DELETE,
# - errores 4xx/5xx,
# - accesos a módulos críticos.
# =========================================================

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.database import SessionLocal, establecer_contexto_sistema
from app.models.auditoria_pro import AuditoriaProEvento
from app.services.audit_service import get_client_ip, get_request_id


class AuditMiddleware(BaseHTTPMiddleware):
    """Auditoría HTTP liviana y segura."""

    EXCLUDED_PREFIXES = (
        "/docs",
        "/redoc",
        "/openapi.json",
        "/uploads",
        "/favicon.ico",
    )

    def _should_skip(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.EXCLUDED_PREFIXES)

    def _modulo_from_path(self, path: str) -> str:
        parts = [p for p in path.split("/") if p]
        if not parts:
            return "SISTEMA"
        return parts[0].upper()

    def _accion_from_method(self, method: str, status_code: int) -> str:
        if status_code in (401, 403):
            return "ACCESS_DENIED"
        if status_code >= 500:
            return "ERROR_SERVER"
        return {
            "POST": "CREATE_OR_ACTION",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
            "GET": "READ",
        }.get(method.upper(), "REQUEST")

    def _severidad(self, method: str, status_code: int) -> str:
        if status_code >= 500:
            return "CRITICA"
        if status_code in (401, 403):
            return "ALTA"
        if method.upper() in ("DELETE",):
            return "ALTA"
        if method.upper() in ("POST", "PUT", "PATCH"):
            return "MEDIA"
        return "INFO"

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if self._should_skip(path):
            return await call_next(request)

        response = await call_next(request)

        # Evita guardar todos los GET exitosos para no llenar la BD.
        should_log = (
            request.method.upper() in ("POST", "PUT", "PATCH", "DELETE")
            or response.status_code >= 400
            or path.startswith("/auth")
        )

        if should_log:
            db = SessionLocal()
            try:
                establecer_contexto_sistema(db)
                evento = AuditoriaProEvento(
                    modulo=self._modulo_from_path(path),
                    accion=self._accion_from_method(request.method, response.status_code),
                    metodo=request.method,
                    ruta=path,
                    status_code=response.status_code,
                    ip_origen=get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    request_id=get_request_id(request),
                    permitido=response.status_code < 400,
                    severidad=self._severidad(request.method, response.status_code),
                    detalle=f"{request.method} {path} -> {response.status_code}",
                    metadata={"query": str(request.url.query or "")},
                )
                db.add(evento)
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()

        return response
