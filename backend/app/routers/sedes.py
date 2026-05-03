# =========================================================
# ROUTER SEDES
# CRUD completo de sedes vinculadas a empresas
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sede import Sede
from app.models.empresa import Empresa
from app.schemas.sede import SedeCreate, SedeUpdate, SedeOut


router = APIRouter(prefix="/sedes", tags=["Sedes"])


@router.post("/", response_model=SedeOut)
def crear_sede(data: SedeCreate, db: Session = Depends(get_db)):
    """
    Crea una sede vinculada a una empresa.
    Antes valida que la empresa exista.
    """

    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La empresa asociada no existe"
        )

    nueva_sede = Sede(**data.model_dump())

    db.add(nueva_sede)
    db.commit()
    db.refresh(nueva_sede)

    return nueva_sede


@router.get("/", response_model=list[SedeOut])
def listar_sedes(db: Session = Depends(get_db)):
    """
    Lista todas las sedes registradas.
    """

    sedes = db.query(Sede).order_by(Sede.created_at.desc()).all()
    return sedes


@router.get("/empresa/{empresa_id}", response_model=list[SedeOut])
def listar_sedes_por_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    """
    Lista únicamente las sedes de una empresa.
    Esta ruta será clave para el portal EMPRESA.
    """

    sedes = db.query(Sede).filter(Sede.empresa_id == empresa_id).all()
    return sedes


@router.get("/{sede_id}", response_model=SedeOut)
def obtener_sede(sede_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene una sede por ID.
    """

    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sede no encontrada"
        )

    return sede


@router.put("/{sede_id}", response_model=SedeOut)
def actualizar_sede(
    sede_id: UUID,
    data: SedeUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una sede existente.
    Si se cambia empresa_id, valida que la empresa nueva exista.
    """

    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sede no encontrada"
        )

    datos = data.model_dump(exclude_unset=True)

    if "empresa_id" in datos:
        empresa = db.query(Empresa).filter(Empresa.id == datos["empresa_id"]).first()

        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La empresa asociada no existe"
            )

    for campo, valor in datos.items():
        setattr(sede, campo, valor)

    db.commit()
    db.refresh(sede)

    return sede


@router.delete("/{sede_id}")
def eliminar_sede(sede_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina una sede.
    Nota: por ahora eliminación física.
    Más adelante podemos cambiar a activo=False.
    """

    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sede no encontrada"
        )

    db.delete(sede)
    db.commit()

    return {"message": "Sede eliminada correctamente"}