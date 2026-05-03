# =========================================================
# ROUTER USUARIOS
# Crea usuarios del sistema y admin inicial
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import AdminCreate, UsuarioCreate
from app.security import hash_password


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


ROLES_VALIDOS = ["ADMIN", "TECNICO", "EMPRESA", "COORDINADOR"]


@router.post("/crear-admin-inicial")
def crear_admin_inicial(data: AdminCreate, db: Session = Depends(get_db)):
    """
    Crea el primer usuario ADMIN del sistema.
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


@router.post("/")
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea usuarios del sistema:
    ADMIN, TECNICO, EMPRESA o COORDINADOR.
    """

    if data.rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol no permitido. Use uno de: {ROLES_VALIDOS}"
        )

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

    return {
        "message": "Usuario creado correctamente",
        "usuario_id": str(nuevo_usuario.id),
        "nombre_completo": nuevo_usuario.nombre_completo,
        "username": nuevo_usuario.username,
        "rol": nuevo_usuario.rol
    }