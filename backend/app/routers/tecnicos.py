# =========================================================
# ROUTER TECNICOS PRO
# CRUD de técnicos con datos del usuario relacionado
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.schemas.tecnico import TecnicoCreate, TecnicoUpdate, TecnicoOut


router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])


def tecnico_con_usuario(tecnico: Tecnico, db: Session):
    """
    Construye una respuesta enriquecida del técnico incluyendo datos del usuario.
    Esto facilita mostrar nombre, correo y username en el frontend.
    """

    usuario = db.query(Usuario).filter(Usuario.id == tecnico.usuario_id).first()

    return {
        "id": str(tecnico.id),
        "usuario_id": str(tecnico.usuario_id),
        "documento": tecnico.documento,
        "telefono": tecnico.telefono,
        "especialidad": tecnico.especialidad,
        "cargo": tecnico.cargo,
        "activo": tecnico.activo,
        "created_at": tecnico.created_at,
        "updated_at": tecnico.updated_at,
        "usuario": {
            "id": str(usuario.id) if usuario else None,
            "nombre_completo": usuario.nombre_completo if usuario else None,
            "username": usuario.username if usuario else None,
            "email": usuario.email if usuario else None,
            "rol": usuario.rol if usuario else None,
            "activo": usuario.activo if usuario else None,
        }
    }


@router.post("/", response_model=TecnicoOut)
def crear_tecnico(data: TecnicoCreate, db: Session = Depends(get_db)):
    """
    Crea perfil técnico para un usuario con rol TECNICO.
    """

    usuario = db.query(Usuario).filter(Usuario.id == data.usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    if usuario.rol != "TECNICO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario debe tener rol TECNICO"
        )

    existente = db.query(Tecnico).filter(
        Tecnico.usuario_id == data.usuario_id
    ).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este usuario ya tiene perfil técnico"
        )

    nuevo = Tecnico(**data.model_dump())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@router.get("/")
def listar_tecnicos(db: Session = Depends(get_db)):
    """
    Lista todos los técnicos con datos del usuario.
    """

    tecnicos = db.query(Tecnico).order_by(Tecnico.created_at.desc()).all()

    return [
        tecnico_con_usuario(tecnico, db)
        for tecnico in tecnicos
    ]


@router.get("/{tecnico_id}")
def obtener_tecnico(tecnico_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene técnico por ID con datos de usuario.
    """

    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )

    return tecnico_con_usuario(tecnico, db)


@router.put("/{tecnico_id}", response_model=TecnicoOut)
def actualizar_tecnico(
    tecnico_id: UUID,
    data: TecnicoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza datos del perfil técnico.
    """

    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(tecnico, campo, valor)

    db.commit()
    db.refresh(tecnico)

    return tecnico


@router.patch("/{tecnico_id}/estado", response_model=TecnicoOut)
def cambiar_estado_tecnico(tecnico_id: UUID, db: Session = Depends(get_db)):
    """
    Activa o inactiva un técnico.
    """

    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )

    tecnico.activo = not tecnico.activo

    db.commit()
    db.refresh(tecnico)

    return tecnico


@router.delete("/{tecnico_id}")
def eliminar_tecnico(tecnico_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina perfil técnico.
    No elimina el usuario, solo el perfil técnico.
    """

    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )

    db.delete(tecnico)
    db.commit()

    return {"message": "Técnico eliminado correctamente"}