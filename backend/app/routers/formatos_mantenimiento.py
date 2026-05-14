# ============================================================
# ROUTER: Formatos de Mantenimiento
# Archivo: backend/app/routers/formatos_mantenimiento.py
# Descripción:
# Endpoints para crear, consultar, actualizar e imprimir
# formularios técnicos de mantenimiento.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.formato_mantenimiento import FormatoMantenimiento
from app.schemas.formato_mantenimiento_schema import (
    FormatoMantenimientoCreate,
    FormatoMantenimientoUpdate,
    FormatoMantenimientoOut,
)

router = APIRouter(
    prefix="/formatos-mantenimiento",
    tags=["Formatos de Mantenimiento"],
)


@router.post("/", response_model=FormatoMantenimientoOut)
def crear_formato(data: FormatoMantenimientoCreate, db: Session = Depends(get_db)):
    """
    Crea un formato técnico de mantenimiento.
    Si ya existe un formato para ese mantenimiento, devuelve error
    para evitar duplicados.
    """

    existe = db.query(FormatoMantenimiento).filter(
        FormatoMantenimiento.mantenimiento_id == data.mantenimiento_id
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un formato para este mantenimiento."
        )

    nuevo = FormatoMantenimiento(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get("/", response_model=list[FormatoMantenimientoOut])
def listar_formatos(db: Session = Depends(get_db)):
    """
    Lista todos los formatos creados.
    Útil para admin/coordinador.
    """

    return db.query(FormatoMantenimiento).order_by(
        FormatoMantenimiento.id.desc()
    ).all()


@router.get("/{formato_id}", response_model=FormatoMantenimientoOut)
def obtener_formato(formato_id: int, db: Session = Depends(get_db)):
    """
    Consulta un formato por ID.
    """

    formato = db.query(FormatoMantenimiento).filter(
        FormatoMantenimiento.id == formato_id
    ).first()

    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado.")

    return formato


@router.get("/mantenimiento/{mantenimiento_id}", response_model=FormatoMantenimientoOut)
def obtener_por_mantenimiento(mantenimiento_id: int, db: Session = Depends(get_db)):
    """
    Consulta el formato asociado a un mantenimiento.
    """

    formato = db.query(FormatoMantenimiento).filter(
        FormatoMantenimiento.mantenimiento_id == mantenimiento_id
    ).first()

    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado.")

    return formato


@router.put("/{formato_id}", response_model=FormatoMantenimientoOut)
def actualizar_formato(
    formato_id: int,
    data: FormatoMantenimientoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un formato técnico existente.
    """

    formato = db.query(FormatoMantenimiento).filter(
        FormatoMantenimiento.id == formato_id
    ).first()

    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado.")

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(formato, campo, valor)

    db.commit()
    db.refresh(formato)

    return formato


@router.delete("/{formato_id}")
def eliminar_formato(formato_id: int, db: Session = Depends(get_db)):
    """
    Elimina un formato técnico.
    """

    formato = db.query(FormatoMantenimiento).filter(
        FormatoMantenimiento.id == formato_id
    ).first()

    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado.")

    db.delete(formato)
    db.commit()

    return {"ok": True, "mensaje": "Formato eliminado correctamente."}