# ============================================================
# ROUTER: BITÁCORAS DINÁMICAS PRO
# Archivo: backend/app/routers/bitacoras_dinamicas.py
# ============================================================
# Integra el portal técnico con formatos dinámicos según equipo.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.database import get_db
from app.models.mantenimiento import Mantenimiento
from app.models.equipo import Equipo
from app.models.categoria import Categoria
from app.models.tecnico import Tecnico
from app.models.formato_dinamico import TipoFormato, BitacoraDinamica, BitacoraRespuesta
from app.schemas.formato_dinamico_schema import BitacoraGuardarIn, BitacoraOut, BitacoraContextoOut
from app.services.formato_selector import seleccionar_codigo_formato

router = APIRouter(prefix="/bitacoras-dinamicas", tags=["Bitácoras Dinámicas PRO"])


def equipo_to_dict(equipo: Equipo, categoria_nombre: str | None = None):
    return {
        "id": str(equipo.id),
        "nombre": equipo.nombre,
        "marca": equipo.marca,
        "modelo": equipo.modelo,
        "serie": equipo.serie,
        "codigo_id": equipo.codigo_id,
        "inventario": equipo.inventario,
        "ubicacion": equipo.ubicacion,
        "estado": equipo.estado,
        "criticidad": equipo.criticidad,
        "categoria_id": str(equipo.categoria_id) if equipo.categoria_id else None,
        "categoria_nombre": categoria_nombre,
    }


def mantenimiento_to_dict(m: Mantenimiento):
    return {
        "id": str(m.id),
        "tipo": m.tipo,
        "estado": m.estado,
        "descripcion": m.descripcion,
        "observaciones": m.observaciones,
        "estado_inicial": m.estado_inicial or m.estado_inicial_equipo,
        "fecha_programada": m.fecha_programada.isoformat() if m.fecha_programada else None,
        "tecnico_id": str(m.tecnico_id) if m.tecnico_id else None,
        "empresa_id": str(m.empresa_id) if m.empresa_id else None,
        "sede_id": str(m.sede_id) if m.sede_id else None,
    }


@router.get("/mantenimiento/{mantenimiento_id}", response_model=BitacoraContextoOut)
def obtener_bitacora_por_mantenimiento(mantenimiento_id: UUID, db: Session = Depends(get_db)):
    """
    Devuelve el mantenimiento, equipo, formato correspondiente y bitácora previa si existe.
    Esta es la ruta que consume el portal técnico.
    """

    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    equipo = db.query(Equipo).filter(Equipo.id == mantenimiento.equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    categoria_nombre = None
    if equipo.categoria_id:
        categoria = db.query(Categoria).filter(Categoria.id == equipo.categoria_id).first()
        categoria_nombre = categoria.nombre if categoria else None

    codigo_formato = seleccionar_codigo_formato(equipo.nombre, categoria_nombre, equipo.marca, equipo.modelo)

    formato = (
        db.query(TipoFormato)
        .options(joinedload(TipoFormato.campos))
        .filter(TipoFormato.codigo == codigo_formato, TipoFormato.activo == True)
        .first()
    )

    if not formato:
        formato = (
            db.query(TipoFormato)
            .options(joinedload(TipoFormato.campos))
            .filter(TipoFormato.codigo == "INDUSTRIAL_GENERAL")
            .first()
        )

    if not formato:
        raise HTTPException(
            status_code=404,
            detail="No hay formato dinámico configurado. Ejecuta los SQL de la Fase 33.",
        )

    bitacora = (
        db.query(BitacoraDinamica)
        .options(joinedload(BitacoraDinamica.respuestas))
        .filter(BitacoraDinamica.mantenimiento_id == mantenimiento_id)
        .first()
    )

    return {
        "mantenimiento": mantenimiento_to_dict(mantenimiento),
        "equipo": equipo_to_dict(equipo, categoria_nombre),
        "formato": formato,
        "bitacora": bitacora,
    }


@router.post("/guardar", response_model=BitacoraOut)
def guardar_bitacora(data: BitacoraGuardarIn, db: Session = Depends(get_db)):
    """
    Crea o actualiza una bitácora dinámica y reemplaza sus respuestas.
    """

    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == data.mantenimiento_id).first()
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    bitacora = db.query(BitacoraDinamica).filter(BitacoraDinamica.mantenimiento_id == data.mantenimiento_id).first()

    if not bitacora:
        bitacora = BitacoraDinamica(mantenimiento_id=data.mantenimiento_id)
        db.add(bitacora)

    bitacora.tecnico_id = data.tecnico_id or mantenimiento.tecnico_id
    bitacora.formato_id = data.formato_id
    bitacora.estado_inicial = data.estado_inicial
    bitacora.estado_final = data.estado_final
    bitacora.observaciones = data.observaciones
    bitacora.recomendaciones = data.recomendaciones
    bitacora.repuestos_utilizados = data.repuestos_utilizados

    db.flush()

    db.query(BitacoraRespuesta).filter(BitacoraRespuesta.bitacora_id == bitacora.id).delete()

    for r in data.respuestas:
        db.add(BitacoraRespuesta(
            bitacora_id=bitacora.id,
            campo_id=r.campo_id,
            valor=r.valor,
            observacion=r.observacion,
        ))

    # Actualiza mantenimiento para conservar trazabilidad operacional.
    if data.estado_final:
        mantenimiento.resultado_final = data.estado_final
    if data.observaciones:
        mantenimiento.observaciones = data.observaciones

    db.commit()
    db.refresh(bitacora)
    return bitacora


@router.get("/historial/equipo/{equipo_id}", response_model=list[BitacoraOut])
def historial_por_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """Lista bitácoras dinámicas asociadas al historial de un equipo."""

    mantenimientos = db.query(Mantenimiento.id).filter(Mantenimiento.equipo_id == equipo_id).all()
    ids = [m.id for m in mantenimientos]

    if not ids:
        return []

    return (
        db.query(BitacoraDinamica)
        .options(joinedload(BitacoraDinamica.respuestas))
        .filter(BitacoraDinamica.mantenimiento_id.in_(ids))
        .order_by(BitacoraDinamica.created_at.desc())
        .all()
    )
