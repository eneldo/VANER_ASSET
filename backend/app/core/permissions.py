# ================================================================
# SGA PRO - FASE 31.2 CORREGIDA
# Archivo: backend/app/core/permissions.py
#
# Objetivo:
#   Helpers de seguridad para validar permisos en backend.
#
# Corrección aplicada:
#   - ADMIN siempre puede entrar aunque la tabla roles_sistema todavía
#     no tenga permisos sembrados.
#   - COORDINADOR conserva permisos por rol si existen.
#   - Evita que Usuarios/Permisos quede bloqueado por falta inicial
#     del permiso PERMISOS_GESTIONAR.
# ================================================================

from typing import Callable, Set
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.permiso import PermisoSistema, RolSistema, UsuarioPermiso
#//from app.routers.auth import obtener_usuario_actual as get_current_user
try:
    from app.routers.auth import obtener_usuario_actual as get_current_user
except ImportError:
    try:
        from app.routers.auth import get_current_user
    except ImportError:
        from app.routers.auth import get_usuario_actual as get_current_user


# Permisos mínimos de respaldo mientras se ejecuta el SQL/seeder de roles.
# Esto evita bloquear el sistema después de instalar la Fase 31.2.
FALLBACK_ADMIN_PERMISSIONS = {
    "DASHBOARD_VER",
    "PERMISOS_GESTIONAR",
    "USUARIOS_VER",
    "USUARIOS_CREAR",
    "USUARIOS_EDITAR",
    "USUARIOS_ELIMINAR",
    "EMPRESAS_VER",
    "SEDES_VER",
    "EQUIPOS_VER",
    "MANTENIMIENTOS_VER",
    "NOTIFICACIONES_VER",
    "REPORTES_VER",
    "AUDITORIA_VER",
    "EXPORTACIONES_VER",
    "CRONOGRAMA_VER",
}


def normalizar_rol(valor: str | None) -> str:
    """
    Convierte roles escritos de varias formas al código oficial.
    Ejemplo: usuarios.rol='EMPRESA' se interpreta como 'CLIENTE'.
    """
    if not valor:
        return ""

    rol = str(valor).strip().upper()
    equivalencias = {
        "ADMINISTRADOR": "ADMIN",
        "EMPRESA": "CLIENTE",
        "CLIENTE_EMPRESA": "CLIENTE",
        "TÉCNICO": "TECNICO",
    }
    return equivalencias.get(rol, rol)


def obtener_permisos_usuario(db: Session, usuario) -> Set[str]:
    """
    Retorna el conjunto final de permisos del usuario autenticado.
    Considera:
      1. Permisos del rol en roles_sistema.
      2. Permisos directos del usuario.
      3. Respaldo seguro para ADMIN si aún no se sembró la matriz.
    """
    rol_codigo = normalizar_rol(getattr(usuario, "rol", None))
    permisos: Set[str] = set()

    # ADMIN no debe quedar bloqueado aunque la matriz esté vacía.
    if rol_codigo == "ADMIN":
        permisos.update(FALLBACK_ADMIN_PERMISSIONS)

    # Cargar permisos asociados al rol si existen en BD.
    rol = db.query(RolSistema).filter(
        RolSistema.codigo == rol_codigo,
        RolSistema.activo.is_(True),
    ).first()

    if rol:
        permisos.update(p.codigo for p in rol.permisos if p.activo)

    # Cargar permisos directos del usuario.
    directos = (
        db.query(PermisoSistema.codigo, UsuarioPermiso.permitido)
        .join(UsuarioPermiso, UsuarioPermiso.permiso_id == PermisoSistema.id)
        .filter(
            UsuarioPermiso.usuario_id == usuario.id,
            PermisoSistema.activo.is_(True),
        )
        .all()
    )

    for codigo, permitido in directos:
        if permitido:
            permisos.add(codigo)
        else:
            permisos.discard(codigo)

    return permisos


def require_permission(codigo_permiso: str) -> Callable:
    """
    Dependency FastAPI para proteger endpoints por permiso granular.

    Nota PRO:
      ADMIN pasa de forma segura aunque no se haya sembrado la matriz,
      para poder entrar al módulo Usuarios y Permisos y corregirla.
    """

    def dependency(db: Session = Depends(get_db), usuario=Depends(get_current_user)):
        rol_codigo = normalizar_rol(getattr(usuario, "rol", None))

        # Respaldo administrativo para no bloquear la plataforma.
        if rol_codigo == "ADMIN":
            return usuario

        permisos = obtener_permisos_usuario(db, usuario)

        if codigo_permiso not in permisos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No autorizado. Requiere permiso: {codigo_permiso}",
            )
        return usuario

    return dependency
