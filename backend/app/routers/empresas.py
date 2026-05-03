# =========================================================
# ROUTER EMPRESAS
# CRUD completo de empresas cliente
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut


router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.post("/", response_model=EmpresaOut)
def crear_empresa(data: EmpresaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva empresa cliente.
    El logo_url será usado luego en la hoja de vida del equipo.
    """

    nueva_empresa = Empresa(**data.model_dump())

    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)

    return nueva_empresa


@router.get("/", response_model=list[EmpresaOut])
def listar_empresas(db: Session = Depends(get_db)):
    """
    Lista todas las empresas registradas.
    """

    empresas = db.query(Empresa).order_by(Empresa.created_at.desc()).all()
    return empresas


@router.get("/{empresa_id}", response_model=EmpresaOut)
def obtener_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene una empresa por ID.
    """

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )

    return empresa


@router.put("/{empresa_id}", response_model=EmpresaOut)
def actualizar_empresa(
    empresa_id: UUID,
    data: EmpresaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una empresa existente.
    Solo modifica los campos enviados.
    """

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)

    return empresa


@router.delete("/{empresa_id}")
def eliminar_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina una empresa.
    Nota: por ahora eliminación física.
    Más adelante podemos cambiar a eliminación lógica activo=False.
    """

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )

    db.delete(empresa)
    db.commit()

    return {"message": "Empresa eliminada correctamente"}