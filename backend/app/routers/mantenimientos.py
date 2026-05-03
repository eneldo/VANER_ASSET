# =========================================================
# ROUTER MANTENIMIENTOS
# Gestión completa de mantenimientos y cambios de estado
# =========================================================

from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.mantenimiento import Mantenimiento
from app.models.historial_mantenimiento import HistorialMantenimiento
from app.models.equipo import Equipo
from app.models.tecnico import Tecnico
from app.schemas.mantenimiento import (
    MantenimientoCreate,
    MantenimientoUpdate,
    CambioEstadoMantenimiento,
    MantenimientoOut
)


router = APIRouter(prefix="/mantenimientos", tags=["Mantenimientos"])


TIPOS_MANTENIMIENTO = [
    "PREVENTIVO",
    "CORRECTIVO",
    "CALIBRACION",
    "INSPECCION"
]

ESTADOS_MANTENIMIENTO = [
    "PROGRAMADO",
    "ASIGNADO",
    "EN_PROCESO",
    "PAUSADO",
    "FINALIZADO",
    "ANULADO"
]


def validar_tipo_estado(tipo: str | None = None, estado: str | None = None):
    """
    Valida tipo y estado permitidos del mantenimiento.
    """

    if tipo and tipo not in TIPOS_MANTENIMIENTO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo no permitido. Use uno de: {TIPOS_MANTENIMIENTO}"
        )

    if estado and estado not in ESTADOS_MANTENIMIENTO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado no permitido. Use uno de: {ESTADOS_MANTENIMIENTO}"
        )


def validar_equipo_tecnico(equipo_id: UUID | None, tecnico_id: UUID | None, db: Session):
    """
    Valida que el equipo y el técnico existan cuando se envían.
    """

    if equipo_id:
        equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()

        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo no encontrado"
            )

    if tecnico_id:
        tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

        if not tecnico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Técnico no encontrado"
            )


def registrar_historial(
    mantenimiento_id: UUID,
    estado_anterior: str | None,
    estado_nuevo: str | None,
    usuario_id: UUID | None,
    comentario: str | None,
    db: Session
):
    """
    Registra historial de cambio de estado del mantenimiento.
    """

    historial = HistorialMantenimiento(
        mantenimiento_id=mantenimiento_id,
        usuario_id=usuario_id,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        comentario=comentario
    )

    db.add(historial)


@router.post("/", response_model=MantenimientoOut)
def crear_mantenimiento(data: MantenimientoCreate, db: Session = Depends(get_db)):
    """
    Crea un mantenimiento para un equipo.
    Si tiene técnico asignado, puede iniciar como ASIGNADO.
    """

    validar_tipo_estado(data.tipo, data.estado)
    validar_equipo_tecnico(data.equipo_id, data.tecnico_id, db)

    nuevo = Mantenimiento(**data.model_dump())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    # Registrar estado inicial en historial
    registrar_historial(
        mantenimiento_id=nuevo.id,
        estado_anterior=None,
        estado_nuevo=nuevo.estado,
        usuario_id=None,
        comentario="Mantenimiento creado",
        db=db
    )

    db.commit()

    return nuevo


@router.get("/", response_model=list[MantenimientoOut])
def listar_mantenimientos(db: Session = Depends(get_db)):
    """
    Lista todos los mantenimientos.
    """

    return db.query(Mantenimiento).order_by(
        Mantenimiento.fecha_programada.desc()
    ).all()


@router.get("/{mantenimiento_id}", response_model=MantenimientoOut)
def obtener_mantenimiento(mantenimiento_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene un mantenimiento por ID.
    """

    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()

    if not mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantenimiento no encontrado"
        )

    return mantenimiento


@router.get("/equipo/{equipo_id}", response_model=list[MantenimientoOut])
def listar_por_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """
    Lista mantenimientos de un equipo.
    """

    return db.query(Mantenimiento).filter(
        Mantenimiento.equipo_id == equipo_id
    ).order_by(Mantenimiento.fecha_programada.desc()).all()


@router.get("/tecnico/{tecnico_id}", response_model=list[MantenimientoOut])
def listar_por_tecnico(tecnico_id: UUID, db: Session = Depends(get_db)):
    """
    Lista mantenimientos asignados a un técnico.
    Esta ruta alimenta el dashboard del técnico.
    """

    return db.query(Mantenimiento).filter(
        Mantenimiento.tecnico_id == tecnico_id
    ).order_by(Mantenimiento.fecha_programada.desc()).all()


@router.get("/equipo/{equipo_id}/ultimo")
def ultimo_mantenimiento_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """
    Retorna el último mantenimiento finalizado o registrado del equipo.
    """

    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.equipo_id == equipo_id
    ).order_by(Mantenimiento.fecha_programada.desc()).first()

    if not mantenimiento:
        return {"message": "Este equipo aún no tiene mantenimientos registrados"}

    return mantenimiento


@router.put("/{mantenimiento_id}", response_model=MantenimientoOut)
def actualizar_mantenimiento(
    mantenimiento_id: UUID,
    data: MantenimientoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente un mantenimiento.
    """

    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()

    if not mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantenimiento no encontrado"
        )

    datos = data.model_dump(exclude_unset=True)

    if "tipo" in datos:
        validar_tipo_estado(tipo=datos["tipo"])

    if "estado" in datos:
        validar_tipo_estado(estado=datos["estado"])

    equipo_id_final = datos.get("equipo_id", mantenimiento.equipo_id)
    tecnico_id_final = datos.get("tecnico_id", mantenimiento.tecnico_id)

    validar_equipo_tecnico(equipo_id_final, tecnico_id_final, db)

    estado_anterior = mantenimiento.estado

    for campo, valor in datos.items():
        setattr(mantenimiento, campo, valor)

    # Si cambió el estado, registrar historial
    if "estado" in datos and datos["estado"] != estado_anterior:
        registrar_historial(
            mantenimiento_id=mantenimiento.id,
            estado_anterior=estado_anterior,
            estado_nuevo=datos["estado"],
            usuario_id=None,
            comentario="Estado actualizado desde edición de mantenimiento",
            db=db
        )

    db.commit()
    db.refresh(mantenimiento)

    return mantenimiento


@router.patch("/{mantenimiento_id}/estado", response_model=MantenimientoOut)
def cambiar_estado_mantenimiento(
    mantenimiento_id: UUID,
    data: CambioEstadoMantenimiento,
    db: Session = Depends(get_db)
):
    """
    Cambia el estado del mantenimiento y registra historial.
    También actualiza fechas de inicio/fin automáticamente.
    """

    validar_tipo_estado(estado=data.estado_nuevo)

    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()

    if not mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantenimiento no encontrado"
        )

    estado_anterior = mantenimiento.estado
    mantenimiento.estado = data.estado_nuevo

    # Fechas automáticas según estado
    if data.estado_nuevo == "EN_PROCESO" and not mantenimiento.fecha_inicio:
        mantenimiento.fecha_inicio = datetime.now()

    if data.estado_nuevo == "FINALIZADO" and not mantenimiento.fecha_fin:
        mantenimiento.fecha_fin = datetime.now()

    registrar_historial(
        mantenimiento_id=mantenimiento.id,
        estado_anterior=estado_anterior,
        estado_nuevo=data.estado_nuevo,
        usuario_id=data.usuario_id,
        comentario=data.comentario,
        db=db
    )

    db.commit()
    db.refresh(mantenimiento)

    return mantenimiento


@router.delete("/{mantenimiento_id}")
def eliminar_mantenimiento(mantenimiento_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina un mantenimiento.
    Más adelante podemos cambiar esto a estado ANULADO.
    """

    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()

    if not mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantenimiento no encontrado"
        )

    db.delete(mantenimiento)
    db.commit()

    return {"message": "Mantenimiento eliminado correctamente"}