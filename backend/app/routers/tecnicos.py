# =========================================================
# ROUTER TECNICOS
# CRUD básico de técnicos vinculados a usuarios
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.schemas.tecnico import TecnicoCreate, TecnicoUpdate, TecnicoOut


router = APIRouter(prefix="/tecnicos", tags=["Técnicos"])


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


@router.get("/", response_model=list[TecnicoOut])
def listar_tecnicos(db: Session = Depends(get_db)):
    """
    Lista todos los técnicos.
    """

    return db.query(Tecnico).order_by(Tecnico.created_at.desc()).all()


@router.get("/{tecnico_id}", response_model=TecnicoOut)
def obtener_tecnico(tecnico_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene técnico por ID.
    """

    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Técnico no encontrado"
        )

    return tecnico


@router.put("/{tecnico_id}", response_model=TecnicoOut)
def actualizar_tecnico(
    tecnico_id: UUID,
    data: TecnicoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza datos del técnico.
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


@router.delete("/{tecnico_id}")
def eliminar_tecnico(tecnico_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina perfil técnico.
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