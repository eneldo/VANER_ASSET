# =========================================================
# ROUTER USUARIOS PRO
# Archivo: backend/app/routers/usuarios.py
#
# CRUD completo de usuarios + reset password.
#
# REGLA MULTIEMPRESA:
# - ADMIN: no requiere empresa.
# - EMPRESA: requiere empresa_id.
# - COORDINADOR: requiere empresa_id.
# - TECNICO: requiere empresa_id.
# =========================================================

from hmac import compare_digest
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.config import settings
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.schemas.usuario import (
    AdminCreate,
    UsuarioCreate,
    UsuarioUpdate,
    ResetPasswordRequest,
    UsuarioOut,
)
from app.security import hash_password


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
bootstrap_router = APIRouter(prefix="/usuarios", tags=["Bootstrap"], include_in_schema=False)


# =========================================================
# ROLES OFICIALES DEL SISTEMA
# =========================================================

ROLES_VALIDOS = ["ADMIN", "TECNICO", "EMPRESA", "COORDINADOR"]

# Roles que obligatoriamente deben estar asociados a una empresa.
ROLES_CON_EMPRESA = ["EMPRESA", "COORDINADOR", "TECNICO"]


# =========================================================
# HELPERS
# =========================================================

def validar_rol(rol: str):
    """
    Valida que el rol enviado exista dentro de los roles permitidos.
    """

    if rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol no permitido. Use uno de: {ROLES_VALIDOS}",
        )


def validar_empresa_si_aplica(rol: str, empresa_id, db: Session):
    """
    Valida empresa obligatoria según rol.

    ADMIN:
        No requiere empresa.

    EMPRESA:
        Debe tener empresa_id.

    COORDINADOR:
        Debe tener empresa_id porque coordina una empresa específica.

    TECNICO:
        Debe tener empresa_id porque cada empresa tiene sus propios técnicos.
    """

    if rol in ROLES_CON_EMPRESA:
        if not empresa_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Los usuarios con rol {rol} deben tener empresa asociada",
            )

        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La empresa asociada no existe",
            )


def limpiar_empresa_si_admin(rol: str, empresa_id):
    """
    Si el usuario es ADMIN, no debe quedar amarrado a una empresa.
    """

    if rol == "ADMIN":
        return None

    return empresa_id


# =========================================================
# CREAR ADMIN INICIAL
# =========================================================

@bootstrap_router.post("/crear-admin-inicial")
def crear_admin_inicial(
    data: AdminCreate,
    bootstrap_token: Annotated[str | None, Header(alias="X-Bootstrap-Token")] = None,
    db: Session = Depends(get_db),
):
    """
    Crea el primer usuario administrador del sistema.
    Solo debe usarse durante la configuración inicial.
    """

    expected_token = settings.BOOTSTRAP_ADMIN_TOKEN
    if (
        not expected_token
        or not bootstrap_token
        or not compare_digest(bootstrap_token, expected_token)
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no disponible")

    admin_existente = db.query(Usuario).filter(Usuario.rol == "ADMIN").first()

    if admin_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario ADMIN en el sistema",
        )

    nuevo_admin = Usuario(
        nombre_completo=data.nombre_completo,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        rol="ADMIN",
        empresa_id=None,
        activo=True,
    )

    db.add(nuevo_admin)
    db.commit()
    db.refresh(nuevo_admin)

    return {
        "message": "Usuario ADMIN creado correctamente",
        "usuario_id": str(nuevo_admin.id),
        "username": nuevo_admin.username,
        "rol": nuevo_admin.rol,
    }


# =========================================================
# CREAR USUARIO
# =========================================================

@router.post("/", response_model=UsuarioOut)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea usuarios del sistema:
    ADMIN, TECNICO, EMPRESA o COORDINADOR.
    """

    validar_rol(data.rol)
    validar_empresa_si_aplica(data.rol, data.empresa_id, db)

    existente = (
        db.query(Usuario)
        .filter(
            or_(
                Usuario.username == data.username,
                Usuario.email == data.email,
            )
        )
        .first()
    )

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username o email ya está registrado",
        )

    empresa_id_final = limpiar_empresa_si_admin(data.rol, data.empresa_id)

    nuevo_usuario = Usuario(
        nombre_completo=data.nombre_completo,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        rol=data.rol,
        empresa_id=empresa_id_final,
        activo=True,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


# =========================================================
# LISTAR USUARIOS
# =========================================================

@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    """
    Lista todos los usuarios del sistema.
    """

    usuarios = db.query(Usuario).order_by(Usuario.created_at.desc()).all()
    return usuarios


# =========================================================
# OBTENER USUARIO
# =========================================================

@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene el detalle de un usuario por ID.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return usuario


# =========================================================
# ACTUALIZAR USUARIO
# =========================================================

@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: UUID,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza datos del usuario.
    No actualiza contraseña; para eso existe reset-password.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    datos = data.model_dump(exclude_unset=True)

    if "rol" in datos:
        validar_rol(datos["rol"])

    rol_final = datos.get("rol", usuario.rol)
    empresa_final = datos.get("empresa_id", usuario.empresa_id)

    empresa_final = limpiar_empresa_si_admin(rol_final, empresa_final)

    validar_empresa_si_aplica(rol_final, empresa_final, db)

    if "username" in datos:
        duplicado = (
            db.query(Usuario)
            .filter(
                Usuario.username == datos["username"],
                Usuario.id != usuario_id,
            )
            .first()
        )

        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro usuario con ese username",
            )

    if "email" in datos:
        duplicado = (
            db.query(Usuario)
            .filter(
                Usuario.email == datos["email"],
                Usuario.id != usuario_id,
            )
            .first()
        )

        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro usuario con ese email",
            )

    for campo, valor in datos.items():
        setattr(usuario, campo, valor)

    usuario.rol = rol_final
    usuario.empresa_id = empresa_final

    db.commit()
    db.refresh(usuario)

    return usuario


# =========================================================
# ACTIVAR / INACTIVAR
# =========================================================

@router.patch("/{usuario_id}/estado", response_model=UsuarioOut)
def cambiar_estado_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """
    Activa o inactiva un usuario.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    usuario.activo = not usuario.activo

    db.commit()
    db.refresh(usuario)

    return usuario


# =========================================================
# RESET PASSWORD
# =========================================================

@router.patch("/{usuario_id}/reset-password")
def reset_password(
    usuario_id: UUID,
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Resetea o cambia la contraseña de un usuario.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    if len(data.nueva_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener mínimo 6 caracteres",
        )

    usuario.password_hash = hash_password(data.nueva_password)

    db.commit()

    return {
        "message": "Contraseña actualizada correctamente",
        "usuario": usuario.username,
    }


# =========================================================
# ELIMINAR / INACTIVAR
# =========================================================

@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """
    Eliminación segura PRO.

    No elimina físicamente el usuario porque puede tener relaciones con:
    - técnicos
    - mantenimientos
    - permisos
    - auditoría
    - historial

    En su lugar lo deja INACTIVO.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    if usuario.rol == "ADMIN" and usuario.username.lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar/inactivar el administrador principal",
        )

    usuario.activo = False

    db.commit()
    db.refresh(usuario)

    return {
        "message": "Usuario eliminado/inactivado correctamente",
        "usuario": usuario.username,
    }
