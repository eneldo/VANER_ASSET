import hashlib
import logging
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover - protegido por requirements de producción
    Redis = None


logger = logging.getLogger(__name__)


class DistributedRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting por IP/ruta con Redis y fallback local controlado."""

    RULES = {
        "/auth/login": (8, 60),
        "/auth/refresh": (30, 60),
        "/auth/forgot-password": (5, 900),
        "/auth/reset-password/validate": (15, 300),
        "/auth/reset-password": (10, 300),
        "default": (300, 60),
    }

    EXCLUDED_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/uploads")

    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(deque)
        self.redis = None
        self.redis_unavailable_logged = False

        if settings.REDIS_URL and Redis is not None:
            self.redis = Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _rule_for_path(self, path: str) -> tuple[int, int]:
        for prefix, rule in self.RULES.items():
            if prefix != "default" and path.startswith(prefix):
                return rule
        return self.RULES["default"]

    def _key(self, ip: str, path: str, window: int, now: float) -> str:
        bucket = int(now // window)
        digest = hashlib.sha256(f"{ip}:{path}".encode("utf-8")).hexdigest()
        return f"vaner:rate-limit:{digest}:{bucket}"

    async def _redis_count(self, key: str, window: int) -> int | None:
        if self.redis is None:
            return None
        try:
            async with self.redis.pipeline(transaction=True) as pipeline:
                pipeline.incr(key)
                pipeline.expire(key, window + 1)
                result = await pipeline.execute()
            return int(result[0])
        except Exception as exc:
            if settings.RATE_LIMIT_REDIS_REQUIRED:
                logger.error("Redis de rate limiting no disponible: %s", type(exc).__name__)
                return -1
            if not self.redis_unavailable_logged:
                logger.warning(
                    "Redis de rate limiting no disponible; usando fallback local"
                )
                self.redis_unavailable_logged = True
            return None

    def _memory_count(self, key: str, window: int, now: float) -> int:
        bucket = self.requests[key]
        while bucket and bucket[0] <= now - window:
            bucket.popleft()
        bucket.append(now)
        return len(bucket)

    def _limited_response(self, window: int):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Demasiadas solicitudes. Intenta nuevamente más tarde.",
                "retry_after_seconds": window,
            },
            headers={"Retry-After": str(window)},
        )

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith(self.EXCLUDED_PREFIXES):
            return await call_next(request)

        limit, window = self._rule_for_path(path)
        now = time.time()
        key = self._key(self._client_ip(request), path, window, now)
        count = await self._redis_count(key, window)

        if count == -1:
            return JSONResponse(
                status_code=503,
                content={"detail": "Protección de acceso temporalmente no disponible."},
                headers={"Retry-After": "5"},
            )
        if count is None:
            count = self._memory_count(key, window, now)
        if count > limit:
            return self._limited_response(window)

        return await call_next(request)
