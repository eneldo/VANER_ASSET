# =========================================================
# ROUTER USUARIOS
# Permite crear usuario ADMIN inicial desde la API
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import AdminCreate
from app.security import hash_password


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/crear-admin-inicial")
def crear_admin_inicial(data: AdminCreate, db: Session = Depends(get_db)):
    """
    Crea el usuario administrador inicial del sistema.

    IMPORTANTE:
    Esta ruta se usa solo para la primera configuración del sistema.
    Después de crear el admin, se recomienda eliminarla o protegerla.
    """

    # Verificar si ya existe un usuario ADMIN
    admin_existente = db.query(Usuario).filter(
        Usuario.rol == "ADMIN"
    ).first()

    if admin_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario ADMIN en el sistema"
        )

    # Verificar si username o email ya existen
    usuario_existente = db.query(Usuario).filter(
        or_(
            Usuario.username == data.username,
            Usuario.email == data.email
        )
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username o email ya se encuentra registrado"
        )

    # Crear usuario ADMIN con contraseña encriptada
    nuevo_admin = Usuario(
        nombre_completo=data.nombre_completo,
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        rol="ADMIN",
        activo=True
    )

    # Guardar en base de datos
    db.add(nuevo_admin)
    db.commit()
    db.refresh(nuevo_admin)

    return {
        "message": "Usuario ADMIN creado correctamente",
        "usuario_id": str(nuevo_admin.id),
        "username": nuevo_admin.username,
        "rol": nuevo_admin.rol
    }