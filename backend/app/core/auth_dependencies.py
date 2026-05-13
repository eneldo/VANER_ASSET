# =========================================================
# DEPENDENCIAS AUTH REUSABLES - FASE 31.1
# Úsalas en routers para proteger endpoints por usuario/rol.
# =========================================================

from fastapi import Depends, HTTPException, status
from app.models.usuario import Usuario
from app.routers.auth import obtener_usuario_actual


def require_roles(*roles_permitidos: str):
    """
    Crea una dependencia para permitir solo roles específicos.

    Ejemplo en un endpoint:
        @router.get('/admin')
        def ruta(usuario: Usuario = Depends(require_roles('ADMIN', 'COORDINADOR'))):
            ...
    """
    def _dependency(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso"
            )
        return usuario

    return _dependency
