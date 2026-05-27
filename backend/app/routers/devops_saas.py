# ============================================================
# ROUTER: DevOps SaaS PRO
# Archivo: backend/app/routers/devops_saas.py
# FASE 34.2.6
# ============================================================

from fastapi import APIRouter, Query

from app.schemas.devops_saas import DevOpsAccionRequest
from app.services.devops_service import (
    ejecutar_accion_servicio,
    obtener_estado_devops,
    obtener_logs_servicio,
)

router = APIRouter(
    prefix="/devops",
    tags=["DevOps SaaS PRO"],
)


@router.get("/estado")
def estado_devops():
    """Estado general DevOps: VPS, Docker y servicios clave."""
    return obtener_estado_devops()


@router.get("/logs/{servicio}")
def logs_servicio(servicio: str, lineas: int = Query(default=80, ge=10, le=300)):
    """Logs rápidos de un contenedor/servicio."""
    return obtener_logs_servicio(servicio=servicio, lineas=lineas)


@router.post("/accion")
def accion_servicio(payload: DevOpsAccionRequest):
    """Acciones controladas sobre servicios. Deshabilitadas por defecto."""
    return ejecutar_accion_servicio(servicio=payload.servicio, accion=payload.accion)
