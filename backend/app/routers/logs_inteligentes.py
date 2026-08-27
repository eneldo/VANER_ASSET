# ============================================================
# ROUTER: Logs Inteligentes SaaS PRO
# Archivo: backend/app/routers/logs_inteligentes.py
# FASE 34.2.5
# ============================================================

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.log_sistema import LogSistema
from app.schemas.log_sistema import LogSistemaCreate, LogSistemaOut, LogSistemaResumen
from app.services.logs_inteligentes_service import (
    crear_log,
    listar_logs,
    resumen_logs,
    limpiar_logs_antiguos,
    crear_logs_demo,
)

router = APIRouter(prefix="/logs-inteligentes", tags=["Logs Inteligentes SaaS PRO"])


@router.get("/resumen", response_model=LogSistemaResumen)
def resumen(db: Session = Depends(get_db)):
    return resumen_logs(db)


@router.get("/", response_model=list[LogSistemaOut])
def listar(
    modulo: str | None = Query(default=None),
    nivel: str | None = Query(default=None),
    texto: str | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return listar_logs(db, modulo=modulo, nivel=nivel, texto=texto, limite=limite)


@router.post("/", response_model=LogSistemaOut)
def crear(payload: LogSistemaCreate, db: Session = Depends(get_db)):
    return crear_log(db, **payload.model_dump())


@router.post("/demo")
def demo(db: Session = Depends(get_db)):
    return crear_logs_demo(db)


@router.delete("/limpiar")
def limpiar(dias: int = Query(default=30, ge=1, le=3650), db: Session = Depends(get_db)):
    return limpiar_logs_antiguos(db, dias=dias)


@router.get("/exportar.csv")
def exportar_csv(
    modulo: str | None = Query(default=None),
    nivel: str | None = Query(default=None),
    texto: str | None = Query(default=None),
    limite: int = Query(default=500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    logs = listar_logs(db, modulo=modulo, nivel=nivel, texto=texto, limite=limite)
    rows = ["fecha,modulo,nivel,evento,mensaje,ruta,usuario"]
    for log in logs:
        def clean(v):
            return str(v or "").replace('"', '""').replace("\n", " ")
        rows.append(
            f'"{clean(log.creado_en)}","{clean(log.modulo)}","{clean(log.nivel)}","{clean(log.evento)}","{clean(log.mensaje)}","{clean(log.ruta)}","{clean(log.usuario)}"'
        )
    return Response("\n".join(rows), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=logs_vaner_asset.csv"})
