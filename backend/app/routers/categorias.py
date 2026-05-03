# =========================================================
# ROUTER CATEGORIAS
# CRUD completo para categorías de equipos
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaOut


router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.post("/", response_model=CategoriaOut)
def crear_categoria(data: CategoriaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva categoría de equipo.
    Ejemplo: Biomédico, Refrigeración, CCTV, Cómputo.
    """

    # Validar que no exista una categoría con el mismo nombre
    existente = db.query(Categoria).filter(Categoria.nombre == data.nombre).first()

    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una categoría con ese nombre"
        )

    nueva_categoria = Categoria(**data.model_dump())

    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)

    return nueva_categoria


@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    """
    Lista todas las categorías registradas.
    """

    categorias = db.query(Categoria).order_by(Categoria.nombre.asc()).all()
    return categorias


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obtener_categoria(categoria_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene una categoría por ID.
    """

    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    return categoria


@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(
    categoria_id: UUID,
    data: CategoriaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una categoría existente.
    """

    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    datos = data.model_dump(exclude_unset=True)

    # Validar duplicado si cambia el nombre
    if "nombre" in datos:
        duplicada = db.query(Categoria).filter(
            Categoria.nombre == datos["nombre"],
            Categoria.id != categoria_id
        ).first()

        if duplicada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otra categoría con ese nombre"
            )

    for campo, valor in datos.items():
        setattr(categoria, campo, valor)

    db.commit()
    db.refresh(categoria)

    return categoria


@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina una categoría.
    Nota: si ya está relacionada a equipos, PostgreSQL puede bloquear
    la eliminación según la restricción de llave foránea.
    """

    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    db.delete(categoria)
    db.commit()

    return {"message": "Categoría eliminada correctamente"}