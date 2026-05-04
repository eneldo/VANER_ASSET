# =========================================================
# ROUTER USUARIOS PRO
# CRUD completo de usuarios + reset password
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.schemas.usuario import (
    AdminCreate,
    UsuarioCreate,
    UsuarioUpdate,
    ResetPasswordRequest,
    UsuarioOut
)
from app.security import hash_password


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# Roles oficiales del sistema
ROLES_VALIDOS = ["ADMIN", "TECNICO", "EMPRESA", "COORDINADOR"]


def validar_rol(rol: str):
    """
    Valida que el rol enviado exista dentro de los roles permitidos.
    """
    if rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol no permitido. Use uno de: {ROLES_VALIDOS}"
        )


def validar_empresa_si_aplica(rol: str, empresa_id, db: Session):
    """
    Si el usuario tiene rol EMPRESA, debe tener empresa_id válido.
    """
    if rol == "EMPRESA":
        if not empresa_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los usuarios con rol EMPRESA deben tener empresa asociada"
            )

        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La empresa asociada no existe"
            )


@router.post("/crear-admin-inicial")
def crear_admin_inicial(data: AdminCreate, db: Session = Depends(get_db)):
    """
    Crea el primer usuario administrador del sistema.
    Solo debe usarse durante la configuración inicial.
    """

    admin_existente = db.query(Usuario).filter(Usuario.rol == "ADMIN").first()

    if admin_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario ADMIN en el sistema"
        )

    nuevo_admin = Usuario(
        nombre_completo=data.nombre_completo,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        rol="ADMIN",
        activo=True
    )

    db.add(nuevo_admin)
    db.commit()
    db.refresh(nuevo_admin)

    return {
        "message": "Usuario ADMIN creado correctamente",
        "usuario_id": str(nuevo_admin.id),
        "username": nuevo_admin.username,
        "rol": nuevo_admin.rol
    }


@router.post("/", response_model=UsuarioOut)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea usuarios del sistema:
    ADMIN, TECNICO, EMPRESA o COORDINADOR.
    """

    validar_rol(data.rol)
    validar_empresa_si_aplica(data.rol, data.empresa_id, db)

    existente = db.query(Usuario).filter(
        or_(
            Usuario.username == data.username,
            Usuario.email == data.email
        )
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username o email ya está registrado"
        )

    nuevo_usuario = Usuario(
        nombre_completo=data.nombre_completo,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        rol=data.rol,
        empresa_id=data.empresa_id,
        activo=True
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario


@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    """
    Lista todos los usuarios del sistema.
    La paginación se hará en frontend por ahora.
    """

    usuarios = db.query(Usuario).order_by(Usuario.created_at.desc()).all()
    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene el detalle de un usuario por ID.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return usuario


@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: UUID,
    data: UsuarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza datos del usuario.
    No actualiza contraseña; para eso existe reset-password.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    datos = data.model_dump(exclude_unset=True)

    if "rol" in datos:
        validar_rol(datos["rol"])

    rol_final = datos.get("rol", usuario.rol)
    empresa_final = datos.get("empresa_id", usuario.empresa_id)

    validar_empresa_si_aplica(rol_final, empresa_final, db)

    if "username" in datos:
        duplicado = db.query(Usuario).filter(
            Usuario.username == datos["username"],
            Usuario.id != usuario_id
        ).first()

        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro usuario con ese username"
            )

    if "email" in datos:
        duplicado = db.query(Usuario).filter(
            Usuario.email == datos["email"],
            Usuario.id != usuario_id
        ).first()

        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro usuario con ese email"
            )

    for campo, valor in datos.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario


@router.patch("/{usuario_id}/estado", response_model=UsuarioOut)
def cambiar_estado_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """
    Activa o inactiva un usuario.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    usuario.activo = not usuario.activo

    db.commit()
    db.refresh(usuario)

    return usuario


@router.patch("/{usuario_id}/reset-password")
def reset_password(
    usuario_id: UUID,
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Resetea o cambia la contraseña de un usuario.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if len(data.nueva_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener mínimo 6 caracteres"
        )

    usuario.password_hash = hash_password(data.nueva_password)

    db.commit()

    return {
        "message": "Contraseña actualizada correctamente",
        "usuario": usuario.username
    }


@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina un usuario físicamente.
    Recomendación futura: cambiar a eliminación lógica.
    """

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    db.delete(usuario)
    db.commit()

    return {"message": "Usuario eliminado correctamente"}