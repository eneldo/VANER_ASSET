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
from app.models.mantenimiento import Mantenimiento
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.routers.auth import obtener_usuario_actual
from app.schemas.formato_mantenimiento_schema import (
    FormatoMantenimientoCreate,
    FormatoMantenimientoUpdate,
    FormatoMantenimientoOut,
)

router = APIRouter(
    prefix="/formatos-mantenimiento",
    tags=["Formatos de Mantenimiento"],
)


def _mantenimiento(db: Session, mantenimiento_id):
    mantenimiento = db.query(Mantenimiento).filter(
        cast(Mantenimiento.id, String) == str(mantenimiento_id)
    ).first()
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada.")
    return mantenimiento


def _autorizar_formato(usuario: Usuario, mantenimiento: Mantenimiento, db: Session, escritura=True):
    rol = str(usuario.rol or "").upper()
    if rol == "ADMIN":
        return
    if rol == "COORDINADOR" and str(usuario.empresa_id) == str(mantenimiento.empresa_id):
        return
    if rol in {"EMPRESA", "CLIENTE"}:
        if escritura or str(usuario.empresa_id) != str(mantenimiento.empresa_id):
            raise HTTPException(status_code=403, detail="Sin permiso para modificar este formato.")
        return
    if rol == "TECNICO":
        tecnico = db.query(Tecnico).filter(Tecnico.usuario_id == usuario.id).first()
        if tecnico and str(tecnico.id) == str(mantenimiento.tecnico_id):
            return
    raise HTTPException(status_code=403, detail="Sin acceso a esta orden de trabajo.")


@router.post("/", response_model=FormatoMantenimientoOut)
def crear_formato(
    data: FormatoMantenimientoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """
    Crea una bitácora técnica.
    Evita duplicados por mantenimiento_id.
    """

    mantenimiento_id_str = str(data.mantenimiento_id)
    mantenimiento = _mantenimiento(db, data.mantenimiento_id)
    _autorizar_formato(usuario, mantenimiento, db)

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
def listar_formatos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """
    Lista todos los formatos creados.
    """

    query = db.query(FormatoMantenimiento).join(
        Mantenimiento, FormatoMantenimiento.mantenimiento_id == Mantenimiento.id
    )
    rol = str(usuario.rol or "").upper()
    if rol in {"COORDINADOR", "EMPRESA", "CLIENTE"}:
        query = query.filter(Mantenimiento.empresa_id == usuario.empresa_id)
    elif rol == "TECNICO":
        tecnico = db.query(Tecnico).filter(Tecnico.usuario_id == usuario.id).first()
        if not tecnico:
            return []
        query = query.filter(Mantenimiento.tecnico_id == tecnico.id)
    elif rol != "ADMIN":
        raise HTTPException(status_code=403, detail="Sin acceso a formatos.")
    return query.order_by(FormatoMantenimiento.id.desc()).all()


@router.get("/mantenimiento/{mantenimiento_id}", response_model=FormatoMantenimientoOut)
def obtener_por_mantenimiento(
    mantenimiento_id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
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

    _autorizar_formato(usuario, _mantenimiento(db, formato.mantenimiento_id), db, escritura=False)

    return formato


@router.get("/{formato_id}", response_model=FormatoMantenimientoOut)
def obtener_formato(
    formato_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
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

    _autorizar_formato(usuario, _mantenimiento(db, formato.mantenimiento_id), db, escritura=False)

    return formato


@router.put("/{formato_id}", response_model=FormatoMantenimientoOut)
def actualizar_formato(
    formato_id: int,
    data: FormatoMantenimientoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
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

    _autorizar_formato(usuario, _mantenimiento(db, formato.mantenimiento_id), db)

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(formato, campo, valor)

    db.commit()
    db.refresh(formato)

    return formato


@router.delete("/{formato_id}")
def eliminar_formato(
    formato_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
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

    _autorizar_formato(usuario, _mantenimiento(db, formato.mantenimiento_id), db)

    db.delete(formato)
    db.commit()

    return {"ok": True, "mensaje": "Formato eliminado correctamente."}
