# ============================================================
# BI EJECUTIVO ROUTER
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.services.bi_service import BIService

router = APIRouter(
    prefix="/bi-ejecutivo",
    tags=["BI Ejecutivo"]
)


# ============================================================
# KPI GLOBALES
# ============================================================

@router.get("/kpis")
def obtener_kpis(db: Session = Depends(get_db)):

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