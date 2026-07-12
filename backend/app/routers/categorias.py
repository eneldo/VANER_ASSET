# =========================================================
# ROUTER CATEGORIAS
# CRUD completo para categorías de equipos
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaUpdate, CategoriaOut
from app.models.usuario import Usuario
from app.routers.auth import obtener_usuario_actual
from app.core.auth_dependencies import require_roles


router = APIRouter(prefix="/categorias", tags=["Categorías"])

CATEGORIAS_CANONICAS = {
    "EQUIPOS_INDUSTRIALES": "Equipos Industriales",
    "AIRES_ACONDICIONADOS": "Aires Acondicionados",
    "CAMARAS_SEGURIDAD": "Cámaras de Seguridad",
    "PROTECCION_CONTRA_INCENDIOS": "Sistemas de Protección Contra Incendios",
}


@router.post("/", response_model=CategoriaOut)
def crear_categoria(usuario: Usuario = Depends(require_roles("ADMIN"))):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="El catálogo es cerrado y contiene exactamente cuatro categorías.",
    )


@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """
    Lista todas las categorías registradas.
    """

    categorias = db.query(Categoria).filter(
        Categoria.code.in_(CATEGORIAS_CANONICAS.keys())
    ).order_by(Categoria.nombre.asc()).all()
    return categorias


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obtener_categoria(
    categoria_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
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
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles("ADMIN")),
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

    if categoria.code not in CATEGORIAS_CANONICAS:
        raise HTTPException(status_code=409, detail="Categoría histórica no canónica")
    categoria.descripcion = data.descripcion
    categoria.nombre = CATEGORIAS_CANONICAS[categoria.code]
    categoria.activo = True

    db.commit()
    db.refresh(categoria)

    return categoria


@router.delete("/{categoria_id}")
def eliminar_categoria(
    categoria_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
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

    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Las cuatro categorías canónicas no se pueden eliminar.",
    )
