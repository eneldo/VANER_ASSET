from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import inspect, select
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_committed_value

from app.database import establecer_contexto_empresa
from app.models.usuario import usuario_empresas


def tabla_usuario_empresas_disponible(db: Session) -> bool:
    try:
        bind = db.get_bind()
        dialecto = getattr(getattr(bind, "dialect", None), "name", None)
        if not isinstance(dialecto, str):
            return True
        return inspect(bind).has_table(usuario_empresas.name)
    except (AttributeError, NoInspectionAvailable):
        return True


def ids_empresas_autorizadas(db: Session, usuario) -> list[UUID]:
    empresa_principal = getattr(usuario, "empresa_id", None)
    rol = str(getattr(usuario, "rol", "") or "").upper()
    if rol != "COORDINADOR":
        return [empresa_principal] if empresa_principal else []
    if not tabla_usuario_empresas_disponible(db):
        return [empresa_principal] if empresa_principal else []

    ids = list(
        db.execute(
            select(usuario_empresas.c.empresa_id).where(
                usuario_empresas.c.usuario_id == usuario.id
            )
        ).scalars()
    )
    if empresa_principal:
        ids = [empresa_id for empresa_id in ids if empresa_id != empresa_principal]
        ids.insert(0, empresa_principal)
    return ids


def aplicar_empresa_activa(db: Session, usuario, empresa_activa) -> None:
    rol = str(getattr(usuario, "rol", "") or "").upper()
    if rol != "COORDINADOR":
        establecer_contexto_empresa(
            db,
            getattr(usuario, "empresa_id", None),
            es_admin=rol == "ADMIN",
        )
        return

    autorizadas = ids_empresas_autorizadas(db, usuario)
    if not autorizadas:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El coordinador no tiene empresas autorizadas",
        )

    try:
        empresa_seleccionada = UUID(str(empresa_activa)) if empresa_activa else autorizadas[0]
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La empresa activa no es válida",
        )

    if empresa_seleccionada not in autorizadas:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La empresa seleccionada no está autorizada para este coordinador",
        )

    setattr(usuario, "empresa_id_principal", getattr(usuario, "empresa_id", None))
    set_committed_value(usuario, "empresa_id", empresa_seleccionada)
    establecer_contexto_empresa(db, empresa_seleccionada)
