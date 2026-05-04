# ============================================================
# ROUTER: Permisos PRO
# Archivo: app/routers/permisos.py
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.permiso import Rol, Permiso, RolPermiso, UsuarioPermiso
from app.models.usuario import Usuario
from app.schemas.permisos import (
    PermisoOut,
    RolOut,
    AsignarPermisosUsuarioRequest,
    UsuarioPermisosOut,
    RolPermisosOut,
)

router = APIRouter(prefix="/permisos", tags=["Permisos PRO"])


# ============================================================
# GET /permisos
# Lista todos los permisos activos
# ============================================================

@router.get("/", response_model=list[PermisoOut])
def listar_permisos(db: Session = Depends(get_db)):
    return (
        db.query(Permiso)
        .filter(Permiso.activo == True)
        .order_by(Permiso.modulo.asc(), Permiso.nombre.asc())
        .all()
    )


# ============================================================
# GET /permisos/roles
# Lista roles del sistema
# ============================================================

@router.get("/roles", response_model=list[RolOut])
def listar_roles(db: Session = Depends(get_db)):
    return (
        db.query(Rol)
        .filter(Rol.activo == True)
        .order_by(Rol.nombre.asc())
        .all()
    )


# ============================================================
# GET /permisos/roles/{rol_id}
# Permisos asignados a un rol
# ============================================================

@router.get("/roles/{rol_id}", response_model=RolPermisosOut)
def permisos_por_rol(rol_id: int, db: Session = Depends(get_db)):
    rol = db.query(Rol).filter(Rol.id == rol_id).first()

    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")

    permisos = (
        db.query(Permiso.codigo)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .filter(RolPermiso.rol_id == rol_id)
        .all()
    )

    return {
        "rol_id": rol.id,
        "rol": rol.nombre,
        "permisos": [p[0] for p in permisos],
    }


# ============================================================
# GET /permisos/usuario/{usuario_id}
# Retorna permisos efectivos del usuario:
#   - permisos del rol
#   - permisos directos del usuario
# ============================================================

@router.get("/usuario/{usuario_id}", response_model=UsuarioPermisosOut)
def permisos_usuario(usuario_id: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    permisos_set = set()

    # Permisos del rol
    if getattr(usuario, "rol_id", None):
        permisos_rol = (
            db.query(Permiso.codigo)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .filter(RolPermiso.rol_id == usuario.rol_id)
            .all()
        )

        for p in permisos_rol:
            permisos_set.add(p[0])

    # Permisos directos del usuario
    permisos_directos = (
        db.query(Permiso.codigo)
        .join(UsuarioPermiso, UsuarioPermiso.permiso_id == Permiso.id)
        .filter(UsuarioPermiso.usuario_id == usuario_id)
        .all()
    )

    for p in permisos_directos:
        permisos_set.add(p[0])

    return {
        "usuario_id": usuario_id,
        "permisos": sorted(list(permisos_set)),
    }


# ============================================================
# POST /permisos/usuario/asignar
# Reemplaza los permisos directos de un usuario
# ============================================================

@router.post("/usuario/asignar", response_model=UsuarioPermisosOut)
def asignar_permisos_usuario(
    payload: AsignarPermisosUsuarioRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.id == payload.usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Eliminar permisos directos actuales
    db.query(UsuarioPermiso).filter(
        UsuarioPermiso.usuario_id == payload.usuario_id
    ).delete()

    permisos = (
        db.query(Permiso)
        .filter(Permiso.codigo.in_(payload.permisos))
        .all()
    )

    for permiso in permisos:
        db.add(
            UsuarioPermiso(
                usuario_id=payload.usuario_id,
                permiso_id=permiso.id
            )
        )

    db.commit()

    return {
        "usuario_id": payload.usuario_id,
        "permisos": payload.permisos,
    }