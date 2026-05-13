"""
FASE 31.6 - MULTIEMPRESA SEGURA PRO
Archivo: backend/app/security/multiempresa.py

Objetivo:
- Centralizar reglas SaaS multiempresa.
- Evitar que CLIENTE vea información de otra empresa.
- Permitir que ADMIN/COORDINADOR vean datos globales según permisos.

IMPORTANTE:
Este archivo no reemplaza tu autenticación actual. Se integra con el usuario autenticado
que normalmente obtienes desde get_current_user o dependencia equivalente.
"""

from fastapi import HTTPException, status

ROLES_GLOBALES = {"ADMIN", "COORDINADOR"}
ROLES_EMPRESA = {"CLIENTE", "EMPRESA"}
ROLES_TECNICOS = {"TECNICO"}


def get_user_role(usuario):
    """Devuelve el rol del usuario de forma tolerante según tu modelo actual."""
    rol = getattr(usuario, "rol", None) or getattr(usuario, "role", None)
    if hasattr(rol, "nombre"):
        return str(rol.nombre).upper()
    if isinstance(rol, str):
        return rol.upper()
    return str(rol).upper() if rol else ""


def get_user_empresa_id(usuario):
    """Obtiene empresa_id del usuario autenticado."""
    empresa_id = getattr(usuario, "empresa_id", None)
    return str(empresa_id) if empresa_id else None


def es_usuario_global(usuario) -> bool:
    """ADMIN y COORDINADOR pueden consultar datos globales si el backend lo permite."""
    return get_user_role(usuario) in ROLES_GLOBALES


def require_empresa_scope(usuario, empresa_id: str | None = None) -> str | None:
    """
    Valida alcance empresarial.

    Reglas:
    - ADMIN/COORDINADOR: pueden consultar cualquier empresa o global.
    - CLIENTE/EMPRESA: solo pueden consultar su propia empresa_id.
    - TECNICO: debe filtrarse por técnico asignado o por empresa si existe.
    """
    rol = get_user_role(usuario)
    user_empresa_id = get_user_empresa_id(usuario)

    if rol in ROLES_GLOBALES:
        return empresa_id

    if rol in ROLES_EMPRESA:
        if not user_empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario cliente no tiene empresa asignada.",
            )
        if empresa_id and str(empresa_id) != user_empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado: no puedes acceder a información de otra empresa.",
            )
        return user_empresa_id

    if rol in ROLES_TECNICOS:
        return user_empresa_id

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Rol no autorizado para consultar información empresarial.",
    )


def apply_empresa_filter(query, modelo, usuario, empresa_id: str | None = None):
    """
    Aplica filtro empresa_id a un query SQLAlchemy.

    Uso:
        query = db.query(Equipo)
        query = apply_empresa_filter(query, Equipo, current_user, empresa_id)
        return query.all()
    """
    empresa_scope = require_empresa_scope(usuario, empresa_id)

    if empresa_scope and hasattr(modelo, "empresa_id"):
        query = query.filter(modelo.empresa_id == empresa_scope)

    return query
