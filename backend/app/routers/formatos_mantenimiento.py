# ============================================================
# ROUTER: Formatos de Mantenimiento
# Archivo: backend/app/routers/formatos_mantenimiento.py
# Función:
# - Crear, consultar, actualizar y eliminar bitácoras técnicas.
# - Soporta mantenimiento_id tipo UUID/string.
# - Corrige error 422 cuando el mantenimiento_id no es entero.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, String

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
    Crea una bitácora técnica.
    Evita duplicados por mantenimiento_id.
    """

    mantenimiento_id_str = str(data.mantenimiento_id)

    existe = (
        db.query(FormatoMantenimiento)
        .filter(cast(FormatoMantenimiento.mantenimiento_id, String) == mantenimiento_id_str)
        .first()
    )

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un formato para este mantenimiento.",
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
    """

    return (
        db.query(FormatoMantenimiento)
        .order_by(FormatoMantenimiento.id.desc())
        .all()
    )


@router.get("/mantenimiento/{mantenimiento_id}", response_model=FormatoMantenimientoOut)
def obtener_por_mantenimiento(mantenimiento_id: str, db: Session = Depends(get_db)):
    """
    Consulta la bitácora asociada a un mantenimiento.
    Acepta mantenimiento_id UUID/string.
    """

    formato = (
        db.query(FormatoMantenimiento)
        .filter(cast(FormatoMantenimiento.mantenimiento_id, String) == str(mantenimiento_id))
        .first()
    )

    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado.")

    return formato


@router.get("/{formato_id}", response_model=FormatoMantenimientoOut)
def obtener_formato(formato_id: int, db: Session = Depends(get_db)):
    """
    Consulta una bitácora por ID interno.
    """

    formato = (
        db.query(FormatoMantenimiento)
        .filter(FormatoMantenimiento.id == formato_id)
        .first()
    )

    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado.")

    return formato


@router.put("/{formato_id}", response_model=FormatoMantenimientoOut)
def actualizar_formato(
    formato_id: int,
    data: FormatoMantenimientoUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza una bitácora existente.
    """

    formato = (
        db.query(FormatoMantenimiento)
        .filter(FormatoMantenimiento.id == formato_id)
        .first()
    )

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
    Elimina una bitácora técnica.
    """

    formato = (
        db.query(FormatoMantenimiento)
        .filter(FormatoMantenimiento.id == formato_id)
        .first()
    )

    if not formato:
        raise HTTPException(status_code=404, detail="Formato no encontrado.")

    db.delete(formato)
    db.commit()

    return {"ok": True, "mensaje": "Formato eliminado correctamente."}