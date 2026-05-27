# ============================================================
# BI EJECUTIVO ROUTER
# Archivo: backend/app/routers/bi_ejecutivo.py
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.services.bi_service import BIService

router = APIRouter(
    prefix="/bi-ejecutivo",
    tags=["BI Ejecutivo PRO"]
)


# ============================================================
# KPI GLOBALES
# ============================================================

@router.get("/kpis")
def obtener_kpis(
    db: Session = Depends(get_db)
):

    return BIService.obtener_kpis_generales(db)


# ============================================================
# MANTENIMIENTOS POR ESTADO
# ============================================================

@router.get("/mantenimientos-estados")
def mantenimientos_estados(
    db: Session = Depends(get_db)
):

    return BIService.mantenimientos_por_estado(db)


# ============================================================
# EQUIPOS POR EMPRESA
# ============================================================

@router.get("/equipos-empresa")
def equipos_empresa(
    db: Session = Depends(get_db)
):

    return BIService.equipos_por_empresa(db)


# ============================================================
# COSTOS POR EMPRESA
# ============================================================

@router.get("/costos-empresa")
def costos_empresa(
    db: Session = Depends(get_db)
):

    return BIService.costos_por_empresa(db)


# ============================================================
# TÉCNICOS PRODUCTIVOS
# ============================================================

@router.get("/tecnicos-productivos")
def tecnicos_productivos(
    db: Session = Depends(get_db)
):

    return BIService.tecnicos_productivos(db)


# ============================================================
# EQUIPOS CRÍTICOS
# ============================================================

@router.get("/equipos-criticos")
def equipos_criticos(
    db: Session = Depends(get_db)
):

    return BIService.equipos_criticos(db)