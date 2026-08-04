# ============================================================
# SGAHolding — CORE PERMISSIONS
# Archivo: backend/app/core/permissions.py
#
# Control centralizado de:
# - Roles
# - Permisos
# - Sidebar dinámico
# - Guards
# - Coordinador NO hereda permisos ADMIN
# ============================================================

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.permiso import (
    PermisoSistema,
    RolSistema,
    UsuarioPermiso,
)

from app.models.usuario import Usuario

from app.routers.auth import obtener_usuario_actual


# ============================================================
# NORMALIZAR ROL
# ============================================================

def normalizar_rol(rol: str | None):
    """
    Convierte el rol a mayúsculas.
    """

    if not rol:
        return "SIN_ROL"

    return str(rol).strip().upper()


# ============================================================
# OBTENER PERMISOS DEL USUARIO
# ============================================================

def obtener_permisos_usuario(
    db: Session,
    usuario: Usuario,
):
    """
    Retorna lista FINAL de permisos del usuario.

    REGLAS:
    - ADMIN = todos los permisos.
    - COORDINADOR = SOLO permisos asignados.
    - TECNICO = permisos limitados.
    - CLIENTE/EMPRESA = permisos limitados.
    """

    rol_codigo = normalizar_rol(usuario.rol)

    # =======================================================
    # ADMIN → TODOS LOS PERMISOS
    # =======================================================

    if rol_codigo == "ADMIN":
        permisos = (
            db.query(PermisoSistema.codigo)
            .filter(PermisoSistema.activo.is_(True))
            .all()
        )

        return sorted([p[0] for p in permisos])

    # =======================================================
    # RESTO DE ROLES → SOLO SUS PERMISOS
    # =======================================================

    permisos_finales = set()

    # =======================================================
    # PERMISOS POR ROL
    # =======================================================

    rol = (
        db.query(RolSistema)
        .options(joinedload(RolSistema.permisos))
        .filter(
            RolSistema.codigo == rol_codigo,
            RolSistema.activo.is_(True),
        )
        .first()
    )

    if rol:
        for permiso in rol.permisos:
            if permiso.activo:
                permisos_finales.add(permiso.codigo)

    # =======================================================
    # PERMISOS DIRECTOS POR USUARIO
    # =======================================================

    permisos_directos = (
        db.query(PermisoSistema)
        .join(
            UsuarioPermiso,
            UsuarioPermiso.permiso_id == PermisoSistema.id,
        )
        .filter(
            UsuarioPermiso.usuario_id == usuario.id,
            UsuarioPermiso.permitido.is_(True),
            PermisoSistema.activo.is_(True),
        )
        .all()
    )

    for permiso in permisos_directos:
        permisos_finales.add(permiso.codigo)

    return sorted(list(permisos_finales))


# ============================================================
# VALIDAR PERMISO
# ============================================================

def require_permission(codigo_permiso: str):
    """
    Dependency FastAPI para proteger endpoints.

    Ejemplo:
        Depends(require_permission("EMPRESAS_VER"))
    """

    def validator(
        usuario=Depends(obtener_usuario_actual),
        db: Session = Depends(get_db),
    ):

        rol_codigo = normalizar_rol(usuario.rol)

        # ===================================================
        # ADMIN → ACCESO TOTAL
        # ===================================================

        if rol_codigo == "ADMIN":
            return usuario

        # ===================================================
        # RESTO → VALIDAR PERMISO
        # ===================================================

        permisos_usuario = obtener_permisos_usuario(db, usuario)

        if codigo_permiso not in permisos_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso: {codigo_permiso}",
            )

        return usuario

    return validator