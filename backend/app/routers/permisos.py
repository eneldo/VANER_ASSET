# ================================================================
# SGA PRO - FASE 31.2
# Archivo: backend/app/routers/permisos.py
# Objetivo:
#   API PRO para roles, permisos y permisos directos por usuario.
#   Pensado para integrarse con Fase 31.1 JWT.
# ================================================================

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.permiso import PermisoSistema, RolSistema, UsuarioPermiso
from app.schemas.permiso_schema import (
    PermisoOut,
    RolOut,
    RolPermisosUpdate,
    UsuarioPermisosOut,
    UsuarioPermisosUpdate,
)
from app.core.permissions import normalizar_rol, obtener_permisos_usuario, require_permission
from app.routers.auth import obtener_usuario_actual

# Ajusta este import si tu modelo Usuario está en otra ruta.
from app.models.usuario import Usuario

router = APIRouter(prefix="/permisos", tags=["Permisos PRO"])




@router.get("/", response_model=List[PermisoOut])
def listar_permisos_compatibilidad(
    db: Session = Depends(get_db),
    _usuario=Depends(require_permission("PERMISOS_GESTIONAR")),
):
    """
    Endpoint de compatibilidad para frontend anterior.
    Antes UsuariosPage llamaba GET /permisos/.
    Se conserva para evitar errores mientras migramos a /permisos/catalogo.
    """
    return (
        db.query(PermisoSistema)
        .filter(PermisoSistema.activo.is_(True))
        .order_by(PermisoSistema.modulo, PermisoSistema.codigo)
        .all()
    )


@router.get("/catalogo", response_model=List[PermisoOut])
def listar_catalogo_permisos(
    db: Session = Depends(get_db),
    _usuario=Depends(require_permission("PERMISOS_GESTIONAR")),
):
    """Lista todos los permisos disponibles agrupables en frontend por módulo."""
    return db.query(PermisoSistema).filter(PermisoSistema.activo.is_(True)).order_by(PermisoSistema.modulo, PermisoSistema.codigo).all()


@router.get("/roles", response_model=List[RolOut])
def listar_roles(
    db: Session = Depends(get_db),
    _usuario=Depends(require_permission("PERMISOS_GESTIONAR")),
):
    """Lista roles oficiales con sus permisos actuales."""
    return (
        db.query(RolSistema)
        .options(joinedload(RolSistema.permisos))
        .filter(RolSistema.activo.is_(True))
        .order_by(RolSistema.codigo)
        .all()
    )


@router.put("/roles/{rol_id}/permisos", response_model=RolOut)
def actualizar_permisos_rol(
    rol_id: UUID,
    payload: RolPermisosUpdate,
    db: Session = Depends(get_db),
    _usuario=Depends(require_permission("PERMISOS_GESTIONAR")),
):
    """Reemplaza la matriz de permisos de un rol."""
    rol = db.query(RolSistema).options(joinedload(RolSistema.permisos)).filter(RolSistema.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    permisos = db.query(PermisoSistema).filter(PermisoSistema.id.in_(payload.permiso_ids)).all() if payload.permiso_ids else []
    rol.permisos = permisos
    db.commit()
    db.refresh(rol)
    return rol


@router.get("/usuario/{usuario_id}", response_model=UsuarioPermisosOut)
def obtener_permisos_de_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    _usuario=Depends(require_permission("PERMISOS_GESTIONAR")),
):
    """Retorna permisos por rol, directos y finales de un usuario."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    rol_codigo = normalizar_rol(getattr(usuario, "rol", None))
    rol = db.query(RolSistema).options(joinedload(RolSistema.permisos)).filter(RolSistema.codigo == rol_codigo).first()
    permisos_rol = [p.codigo for p in rol.permisos] if rol else []

    directos = (
        db.query(PermisoSistema.codigo)
        .join(UsuarioPermiso, UsuarioPermiso.permiso_id == PermisoSistema.id)
        .filter(UsuarioPermiso.usuario_id == usuario.id, UsuarioPermiso.permitido.is_(True))
        .all()
    )
    permisos_directos = [p[0] for p in directos]
    finales = sorted(obtener_permisos_usuario(db, usuario))

    return UsuarioPermisosOut(
        usuario_id=usuario.id,
        rol=rol_codigo,
        permisos_rol=sorted(permisos_rol),
        permisos_directos=sorted(permisos_directos),
        permisos_finales=finales,
    )


@router.put("/usuario/{usuario_id}/directos", response_model=UsuarioPermisosOut)
def actualizar_permisos_directos_usuario(
    usuario_id: UUID,
    payload: UsuarioPermisosUpdate,
    db: Session = Depends(get_db),
    _usuario=Depends(require_permission("PERMISOS_GESTIONAR")),
):
    """Reemplaza permisos directos permitidos de un usuario."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.query(UsuarioPermiso).filter(UsuarioPermiso.usuario_id == usuario.id).delete()
    for permiso_id in payload.permiso_ids:
        existe = db.query(PermisoSistema).filter(PermisoSistema.id == permiso_id).first()
        if existe:
            db.add(UsuarioPermiso(usuario_id=usuario.id, permiso_id=permiso_id, permitido=True))

    db.commit()
    return obtener_permisos_de_usuario(usuario_id, db, _usuario)


@router.get("/me", response_model=UsuarioPermisosOut)
def mis_permisos(
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual),
):
    """
    Endpoint usado por React para construir menús dinámicos.
    No debe exigir DASHBOARD_VER, porque primero necesita consultar
    qué permisos tiene el usuario autenticado.
    """
    rol_codigo = normalizar_rol(getattr(usuario, "rol", None))

    rol = (
        db.query(RolSistema)
        .options(joinedload(RolSistema.permisos))
        .filter(RolSistema.codigo == rol_codigo)
        .first()
    )

    permisos_rol = [p.codigo for p in rol.permisos] if rol else []
    finales = sorted(obtener_permisos_usuario(db, usuario))

    directos = (
        db.query(PermisoSistema.codigo)
        .join(UsuarioPermiso, UsuarioPermiso.permiso_id == PermisoSistema.id)
        .filter(
            UsuarioPermiso.usuario_id == usuario.id,
            UsuarioPermiso.permitido.is_(True),
        )
        .all()
    )

    permisos_directos = [p[0] for p in directos]

    return UsuarioPermisosOut(
        usuario_id=usuario.id,
        rol=rol_codigo,
        permisos_rol=sorted(permisos_rol),
        permisos_directos=sorted(permisos_directos),
        permisos_finales=finales,
    )
