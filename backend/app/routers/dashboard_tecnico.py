# =========================================================
# ROUTER DASHBOARD TÉCNICO
# Vista especializada para técnicos:
# - mantenimientos asignados
# - datos básicos del equipo
# - hoja de vida técnica
# - último mantenimiento
# - evidencias
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.tecnico import Tecnico
from app.models.mantenimiento import Mantenimiento
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.categoria import Categoria

# =========================================================
# IMPORT CORREGIDO
# Usar SOLO el modelo nuevo equipo_hoja_vida.py
# No usar app.models.hoja_vida porque duplica la tabla
# =========================================================
from app.models.equipo_hoja_vida import EquipoHojaVida

from app.models.evidencia import Evidencia


router = APIRouter(
    prefix="/dashboard-tecnico",
    tags=["Dashboard Técnico"]
)


@router.get("/usuario/{usuario_id}")
def dashboard_por_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """
    Carga el dashboard del técnico usando el ID del usuario.

    Flujo:
    Usuario TECNICO -> Perfil técnico -> Mantenimientos asignados.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if usuario.rol != "TECNICO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene rol TECNICO"
        )

    tecnico = db.query(Tecnico).filter(
        Tecnico.usuario_id == usuario.id
    ).first()

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario técnico aún no tiene perfil técnico creado"
        )

    mantenimientos = db.query(Mantenimiento).filter(
        Mantenimiento.tecnico_id == tecnico.id
    ).order_by(Mantenimiento.fecha_programada.desc()).all()

    return {
        "usuario": {
            "id": str(usuario.id),
            "nombre_completo": usuario.nombre_completo,
            "username": usuario.username,
            "email": usuario.email,
            "rol": usuario.rol
        },
        "tecnico": {
            "id": str(tecnico.id),
            "documento": tecnico.documento,
            "telefono": tecnico.telefono,
            "especialidad": tecnico.especialidad,
            "cargo": tecnico.cargo
        },
        "resumen": {
            "total_asignados": len(mantenimientos),
            "programados": len([m for m in mantenimientos if m.estado == "PROGRAMADO"]),
            "asignados": len([m for m in mantenimientos if m.estado == "ASIGNADO"]),
            "en_proceso": len([m for m in mantenimientos if m.estado == "EN_PROCESO"]),
            "pausados": len([m for m in mantenimientos if m.estado == "PAUSADO"]),
            "finalizados": len([m for m in mantenimientos if m.estado == "FINALIZADO"])
        },
        "mantenimientos": [
            construir_card_mantenimiento(m, db) for m in mantenimientos
        ]
    }


@router.get("/tecnico/{tecnico_id}")
def dashboard_por_tecnico(tecnico_id: UUID, db: Session = Depends(get_db)):
    """
    Carga el dashboard usando directamente el ID del técnico.
    """

    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )

    mantenimientos = db.query(Mantenimiento).filter(
        Mantenimiento.tecnico_id == tecnico.id
    ).order_by(Mantenimiento.fecha_programada.desc()).all()

    return {
        "tecnico": {
            "id": str(tecnico.id),
            "usuario_id": str(tecnico.usuario_id),
            "documento": tecnico.documento,
            "telefono": tecnico.telefono,
            "especialidad": tecnico.especialidad,
            "cargo": tecnico.cargo
        },
        "resumen": {
            "total_asignados": len(mantenimientos),
            "programados": len([m for m in mantenimientos if m.estado == "PROGRAMADO"]),
            "asignados": len([m for m in mantenimientos if m.estado == "ASIGNADO"]),
            "en_proceso": len([m for m in mantenimientos if m.estado == "EN_PROCESO"]),
            "pausados": len([m for m in mantenimientos if m.estado == "PAUSADO"]),
            "finalizados": len([m for m in mantenimientos if m.estado == "FINALIZADO"])
        },
        "mantenimientos": [
            construir_card_mantenimiento(m, db) for m in mantenimientos
        ]
    }


@router.get("/mantenimiento/{mantenimiento_id}/detalle")
def detalle_mantenimiento_tecnico(
    mantenimiento_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Devuelve toda la información que necesita el técnico
    al abrir un mantenimiento específico.
    """

    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()

    if not mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantenimiento no encontrado"
        )

    equipo = db.query(Equipo).filter(
        Equipo.id == mantenimiento.equipo_id
    ).first()

    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo asociado no encontrado"
        )

    empresa = db.query(Empresa).filter(
        Empresa.id == equipo.empresa_id
    ).first()

    sede = db.query(Sede).filter(
        Sede.id == equipo.sede_id
    ).first()

    categoria = None
    if equipo.categoria_id:
        categoria = db.query(Categoria).filter(
            Categoria.id == equipo.categoria_id
        ).first()

    hoja_vida = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.equipo_id == equipo.id
    ).first()

    ultimo_mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.equipo_id == equipo.id,
        Mantenimiento.id != mantenimiento.id
    ).order_by(Mantenimiento.fecha_programada.desc()).first()

    evidencias = db.query(Evidencia).filter(
        Evidencia.mantenimiento_id == mantenimiento.id
    ).order_by(Evidencia.created_at.desc()).all()

    return {
        "encabezado": {
            "empresa_nombre": empresa.nombre if empresa else None,
            "empresa_logo_url": empresa.logo_url if empresa else None,
            "sede_nombre": sede.nombre if sede else None
        },
        "mantenimiento": {
            "id": str(mantenimiento.id),
            "tipo": mantenimiento.tipo,
            "estado": mantenimiento.estado,
            "fecha_programada": mantenimiento.fecha_programada,
            "fecha_inicio": mantenimiento.fecha_inicio,
            "fecha_fin": mantenimiento.fecha_fin,
            "estado_inicial": mantenimiento.estado_inicial,
            "acciones_realizadas": mantenimiento.acciones_realizadas,
            "resultado_final": mantenimiento.resultado_final,
            "observaciones": mantenimiento.observaciones
        },
        "equipo_basico": {
            "id": str(equipo.id),
            "nombre": equipo.nombre,
            "marca": equipo.marca,
            "modelo": equipo.modelo,
            "serie": equipo.serie,
            "ubicacion": equipo.ubicacion,
            "invima": equipo.invima,
            "codigo_id": equipo.codigo_id,
            "inventario": getattr(equipo, "inventario", None),
            "estado": equipo.estado,
            "criticidad": equipo.criticidad,
            "categoria": categoria.nombre if categoria else None
        },
        "hoja_vida_tecnica": hoja_vida,
        "ultimo_mantenimiento": construir_mantenimiento_simple(ultimo_mantenimiento),
        "evidencias": [
            {
                "id": str(e.id),
                "tipo": e.tipo,
                "archivo_url": e.archivo_url,
                "nombre_original": e.nombre_original,
                "descripcion": e.descripcion,
                "created_at": e.created_at
            }
            for e in evidencias
        ]
    }


def construir_card_mantenimiento(mantenimiento: Mantenimiento, db: Session):
    """
    Construye una tarjeta resumida de mantenimiento
    para mostrar en el dashboard del técnico.
    """

    equipo = db.query(Equipo).filter(
        Equipo.id == mantenimiento.equipo_id
    ).first()

    empresa = None
    sede = None

    if equipo:
        empresa = db.query(Empresa).filter(
            Empresa.id == equipo.empresa_id
        ).first()

        sede = db.query(Sede).filter(
            Sede.id == equipo.sede_id
        ).first()

    return {
        "mantenimiento_id": str(mantenimiento.id),
        "tipo": mantenimiento.tipo,
        "estado": mantenimiento.estado,
        "fecha_programada": mantenimiento.fecha_programada,
        "fecha_inicio": mantenimiento.fecha_inicio,
        "fecha_fin": mantenimiento.fecha_fin,
        "equipo": {
            "id": str(equipo.id) if equipo else None,
            "nombre": equipo.nombre if equipo else None,
            "codigo_id": equipo.codigo_id if equipo else None,
            "inventario": getattr(equipo, "inventario", None) if equipo else None,
            "marca": equipo.marca if equipo else None,
            "modelo": equipo.modelo if equipo else None,
            "serie": equipo.serie if equipo else None,
            "ubicacion": equipo.ubicacion if equipo else None,
            "estado": equipo.estado if equipo else None,
            "criticidad": equipo.criticidad if equipo else None
        },
        "empresa": {
            "nombre": empresa.nombre if empresa else None,
            "logo_url": empresa.logo_url if empresa else None
        },
        "sede": {
            "nombre": sede.nombre if sede else None
        }
    }


def construir_mantenimiento_simple(mantenimiento):
    """
    Devuelve un mantenimiento resumido.
    Si no existe, retorna None.
    """

    if not mantenimiento:
        return None

    return {
        "id": str(mantenimiento.id),
        "tipo": mantenimiento.tipo,
        "estado": mantenimiento.estado,
        "fecha_programada": mantenimiento.fecha_programada,
        "fecha_inicio": mantenimiento.fecha_inicio,
        "fecha_fin": mantenimiento.fecha_fin,
        "resultado_final": mantenimiento.resultado_final,
        "observaciones": mantenimiento.observaciones
    }