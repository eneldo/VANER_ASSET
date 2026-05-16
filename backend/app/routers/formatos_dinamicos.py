# ============================================================
# ROUTER: FORMATOS DINÁMICOS PRO
# Archivo: backend/app/routers/formatos_dinamicos.py
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.database import get_db
from app.models.formato_dinamico import TipoFormato, CampoFormato
from app.schemas.formato_dinamico_schema import TipoFormatoCreate, TipoFormatoOut, CampoFormatoCreate, CampoFormatoOut

router = APIRouter(prefix="/formatos-dinamicos", tags=["Formatos Dinámicos PRO"])


@router.get("/", response_model=list[TipoFormatoOut])
def listar_formatos(db: Session = Depends(get_db)):
    """Lista todos los formatos activos con sus campos ordenados."""
    return (
        db.query(TipoFormato)
        .options(joinedload(TipoFormato.campos))
        .filter(TipoFormato.activo == True)
        .order_by(TipoFormato.nombre.asc())
        .all()
    )


@router.get("/{formato_id}", response_model=TipoFormatoOut)
def obtener_formato(formato_id: UUID, db: Session = Depends(get_db)):
    formato = (
        db.query(TipoFormato)
        .options(joinedload(TipoFormato.campos))
        .filter(TipoFormato.id == formato_id)
        .first()
    )
    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado")
    return formato


@router.get("/codigo/{codigo}", response_model=TipoFormatoOut)
def obtener_por_codigo(codigo: str, db: Session = Depends(get_db)):
    formato = (
        db.query(TipoFormato)
        .options(joinedload(TipoFormato.campos))
        .filter(TipoFormato.codigo == codigo.upper())
        .first()
    )
    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado")
    return formato


@router.post("/", response_model=TipoFormatoOut)
def crear_formato(data: TipoFormatoCreate, db: Session = Depends(get_db)):
    codigo = data.codigo.upper().strip()
    if db.query(TipoFormato).filter(TipoFormato.codigo == codigo).first():
        raise HTTPException(status_code=400, detail="Ya existe un formato con ese código")
    datos = data.model_dump()
    datos["codigo"] = codigo
    nuevo = TipoFormato(**datos)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.post("/campos", response_model=CampoFormatoOut)
def crear_campo(data: CampoFormatoCreate, db: Session = Depends(get_db)):
    if not db.query(TipoFormato).filter(TipoFormato.id == data.formato_id).first():
        raise HTTPException(status_code=404, detail="Formato no existe")
    campo = CampoFormato(**data.model_dump())
    db.add(campo)
    db.commit()
    db.refresh(campo)
    return campo


@router.delete("/campos/{campo_id}")
def eliminar_campo(campo_id: UUID, db: Session = Depends(get_db)):
    campo = db.query(CampoFormato).filter(CampoFormato.id == campo_id).first()
    if not campo:
        raise HTTPException(status_code=404, detail="Campo no encontrado")
    db.delete(campo)
    db.commit()
    return {"ok": True, "mensaje": "Campo eliminado correctamente"}
