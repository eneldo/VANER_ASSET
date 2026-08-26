from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.equipo import Equipo
from app.models.sede import Sede
from app.models.mantenimiento import Mantenimiento
from app.models.hist_mantenimiento import HistMantenimiento
from app.models.solicitud_correctiva import SolicitudCorrectiva
from app.models.usuario import Usuario
from app.routers.auth import obtener_usuario_actual


router = APIRouter(prefix="/solicitudes-correctivas", tags=["Solicitudes correctivas"])

ESTADOS = {"NUEVA", "EN_REVISION", "APROBADA", "CONVERTIDA_OT", "RECHAZADA", "CERRADA"}
PRIORIDADES = {"ALTA", "CRITICA", "EMERGENCIA"}


class SolicitudCreate(BaseModel):
    sede_id: UUID
    equipo_id: UUID | None = None
    titulo: str = Field(min_length=5, max_length=160)
    descripcion: str = Field(min_length=15, max_length=4000)
    prioridad: str = "EMERGENCIA"
    contacto_nombre: str | None = Field(default=None, max_length=150)
    contacto_telefono: str | None = Field(default=None, max_length=50)


class SolicitudEstado(BaseModel):
    estado: str
    respuesta_coordinador: str | None = Field(default=None, max_length=4000)


def _rol(usuario):
    return str(getattr(usuario, "rol", "") or "").upper()


def _tenant_usuario(usuario: Usuario):
    if not usuario.empresa_id:
        raise HTTPException(status_code=403, detail="El usuario no tiene empresa asociada")
    return usuario.empresa_id


def _serializar(item, db):
    sede = db.query(Sede).filter(Sede.id == item.sede_id).first()
    equipo = db.query(Equipo).filter(Equipo.id == item.equipo_id).first() if item.equipo_id else None
    return {
        "id": str(item.id),
        "empresa_id": str(item.empresa_id),
        "sede_id": str(item.sede_id),
        "sede_nombre": sede.nombre if sede else None,
        "equipo_id": str(item.equipo_id) if item.equipo_id else None,
        "equipo_nombre": equipo.nombre if equipo else None,
        "mantenimiento_id": str(item.mantenimiento_id) if item.mantenimiento_id else None,
        "titulo": item.titulo,
        "descripcion": item.descripcion,
        "prioridad": item.prioridad,
        "estado": item.estado,
        "contacto_nombre": item.contacto_nombre,
        "contacto_telefono": item.contacto_telefono,
        "respuesta_coordinador": item.respuesta_coordinador,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


@router.post("/", status_code=201)
def crear_solicitud(
    data: SolicitudCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
    idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
):
    if _rol(usuario) not in {"EMPRESA", "CLIENTE"}:
        raise HTTPException(status_code=403, detail="Solo el director cliente puede radicar solicitudes")
    empresa_id = _tenant_usuario(usuario)

    if idempotency_key:
        existente = db.query(SolicitudCorrectiva).filter(
            SolicitudCorrectiva.client_request_id == idempotency_key
        ).first()
        if existente:
            if str(existente.empresa_id) != str(empresa_id):
                raise HTTPException(status_code=409, detail="Clave idempotente en conflicto")
            return _serializar(existente, db)

    sede = db.query(Sede).filter(Sede.id == data.sede_id, Sede.empresa_id == empresa_id).first()
    if not sede:
        raise HTTPException(status_code=422, detail="La sede no pertenece a tu empresa")

    if data.equipo_id:
        equipo = db.query(Equipo).filter(
            Equipo.id == data.equipo_id,
            Equipo.empresa_id == empresa_id,
            Equipo.sede_id == data.sede_id,
        ).first()
        if not equipo:
            raise HTTPException(status_code=422, detail="El equipo no pertenece a la sede seleccionada")

    prioridad = data.prioridad.strip().upper()
    if prioridad not in PRIORIDADES:
        raise HTTPException(status_code=422, detail="Prioridad no permitida")

    item = SolicitudCorrectiva(
        empresa_id=empresa_id,
        sede_id=data.sede_id,
        equipo_id=data.equipo_id,
        solicitante_id=usuario.id,
        client_request_id=idempotency_key,
        titulo=data.titulo.strip(),
        descripcion=data.descripcion.strip(),
        prioridad=prioridad,
        contacto_nombre=(data.contacto_nombre or "").strip() or None,
        contacto_telefono=(data.contacto_telefono or "").strip() or None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serializar(item, db)


@router.get("/")
def listar_solicitudes(
    estado: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    rol = _rol(usuario)
    query = db.query(SolicitudCorrectiva)
    if rol == "ADMIN":
        pass
    elif rol in {"EMPRESA", "CLIENTE", "COORDINADOR"}:
        query = query.filter(SolicitudCorrectiva.empresa_id == _tenant_usuario(usuario))
    else:
        raise HTTPException(status_code=403, detail="Sin acceso a solicitudes correctivas")
    if estado:
        query = query.filter(SolicitudCorrectiva.estado == estado.upper())
    items = query.order_by(SolicitudCorrectiva.created_at.desc()).all()
    return [_serializar(item, db) for item in items]


@router.patch("/{solicitud_id}/estado")
def actualizar_estado(
    solicitud_id: UUID,
    data: SolicitudEstado,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    if _rol(usuario) not in {"ADMIN", "COORDINADOR"}:
        raise HTTPException(status_code=403, detail="Solo coordinación puede gestionar la solicitud")
    item = db.query(SolicitudCorrectiva).filter(SolicitudCorrectiva.id == solicitud_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if _rol(usuario) == "COORDINADOR" and str(item.empresa_id) != str(_tenant_usuario(usuario)):
        raise HTTPException(status_code=403, detail="Solicitud fuera de tu empresa")
    estado = data.estado.strip().upper()
    if estado not in ESTADOS:
        raise HTTPException(status_code=422, detail="Estado no permitido")

    es_conversion = estado == "CONVERTIDA_OT" and item.estado != "CONVERTIDA_OT"

    item.estado = estado
    item.respuesta_coordinador = data.respuesta_coordinador
    if estado in {"RECHAZADA", "CERRADA", "CONVERTIDA_OT"}:
        item.atendida_at = datetime.utcnow()

    mantenimiento_creado = None

    if es_conversion:
        if not item.equipo_id:
            raise HTTPException(
                status_code=422,
                detail="La solicitud debe tener un equipo asociado para convertir a OT.",
            )

        mantenimiento = Mantenimiento(
            equipo_id=item.equipo_id,
            tipo="CORRECTIVO",
            descripcion=f"Solicitud correctiva: {item.titulo}\n\n{item.descripcion}",
            prioridad=item.prioridad if item.prioridad in {"BAJA", "MEDIA", "ALTA", "CRITICA"} else "ALTA",
            estado="PROGRAMADO",
            empresa_id=item.empresa_id,
            sede_id=item.sede_id,
            observaciones=data.respuesta_coordinador or "",
        )
        db.add(mantenimiento)
        db.flush()

        item.mantenimiento_id = mantenimiento.id

        evento = HistMantenimiento(
            mantenimiento_id=mantenimiento.id,
            estado_anterior=None,
            estado_nuevo="PROGRAMADO",
            observacion=f"OT creada desde solicitud correctiva #{str(item.id)[:8]}",
            creado_por=usuario.username or str(usuario.id),
        )
        db.add(evento)
        mantenimiento_creado = str(mantenimiento.id)

    db.commit()
    db.refresh(item)

    resultado = _serializar(item, db)
    if mantenimiento_creado:
        resultado["mantenimiento_creado_id"] = mantenimiento_creado
    return resultado
