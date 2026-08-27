# =========================================================
# MONITORING — Sentry + Health Checks
# Archivo: app/monitoring.py
#
# Inicializa Sentry si SENTRY_DSN está configurado.
# Expone health checks para Docker/k8s.
# =========================================================

import logging
from typing import Dict, Any

from fastapi import APIRouter, Response
from sqlalchemy import text

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Monitoring"])


def init_sentry() -> None:
    """Inicializa Sentry si DSN está configurado."""
    if not settings.SENTRY_DSN:
        logger.info("Sentry no configurado (SENTRY_DSN vacío)")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT or settings.APP_ENV,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            send_default_pii=False,
            attach_stacktrace=True,
        )
        logger.info(f"Sentry inicializado (env: {settings.SENTRY_ENVIRONMENT or settings.APP_ENV})")
    except ImportError:
        logger.warning("sentry-sdk no instalado. Instalar con: pip install sentry-sdk[fastapi]")
    except Exception as e:
        logger.error(f"Error inicializando Sentry: {e}")


@router.get("/health/ready")
async def health_ready(response: Response) -> Dict[str, Any]:
    """Health check para Docker/k8s — verifica DB y servicios."""
    from app.database import SessionLocal

    checks = {"status": "ok", "checks": {}}

    # Verificar DB
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["checks"]["database"] = "ok"
    except Exception as e:
        checks["checks"]["database"] = f"error: {str(e)}"
        checks["status"] = "degraded"
        response.status_code = 503

    # Verificar Sentry
    if settings.SENTRY_DSN:
        checks["checks"]["sentry"] = "configured"
    else:
        checks["checks"]["sentry"] = "not_configured"

    return checks


@router.get("/health/live")
async def health_live() -> Dict[str, str]:
    """Liveness check — el proceso está vivo."""
    return {"status": "ok"}


@router.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """Métricas básicas del sistema."""
    import psutil
    import os

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory": {
            "total_mb": round(psutil.virtual_memory().total / 1024 / 1024),
            "used_mb": round(psutil.virtual_memory().used / 1024 / 1024),
            "percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "total_gb": round(psutil.disk_usage("/").total / 1024 / 1024 / 1024, 1),
            "used_gb": round(psutil.disk_usage("/").used / 1024 / 1024 / 1024, 1),
            "percent": psutil.disk_usage("/").percent,
        },
        "pid": os.getpid(),
    }
