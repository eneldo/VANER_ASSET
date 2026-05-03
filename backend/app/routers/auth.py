# =========================================================
# ROUTER AUTH
# Login del sistema según roles
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.security import verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Permite ingresar al sistema con usuario o correo.
    Retorna token JWT y rol para redireccionar el dashboard.
    """

    # Buscar usuario por username o email
    usuario = db.query(Usuario).filter(
        or_(
            Usuario.username == data.username,
            Usuario.email == data.username
        )
    ).first()

    # Validar usuario existente
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    # Validar usuario activo
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    # Validar contraseña
    if not verify_password(data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    # Crear token con información importante del usuario
    token = create_access_token({
        "sub": str(usuario.id),
        "rol": usuario.rol,
        "empresa_id": str(usuario.empresa_id) if usuario.empresa_id else None
    })

    return TokenResponse(
        access_token=token,
        usuario_id=str(usuario.id),
        nombre_completo=usuario.nombre_completo,
        rol=usuario.rol
    )