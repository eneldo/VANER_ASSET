import re
import unicodedata
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth_dependencies import require_roles
from app.database import get_db
from app.models.categoria import Categoria
from app.models.equipo import Equipo
from app.models.usuario import Usuario
from app.routers.auth import obtener_usuario_actual
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate


router = APIRouter(prefix='/categorias', tags=['Categorias'])


def _normalizar_codigo(valor: str) -> str:
    texto = unicodedata.normalize('NFKD', valor or '')
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    codigo = re.sub(r'[^A-Z0-9]+', '_', texto.upper()).strip('_')
    if not codigo:
        raise HTTPException(status_code=422, detail='Codigo de categoria no valido')
    return codigo[:50]


def _normalizar_nombre(valor: str) -> str:
    nombre = (valor or '').strip()
    if not nombre:
        raise HTTPException(status_code=422, detail='Nombre de categoria obligatorio')
    return nombre


def _buscar_duplicada(db: Session, codigo: str, nombre: str, excluir_id: UUID | None = None):
    query = db.query(Categoria).filter(
        or_(Categoria.code == codigo, func.lower(Categoria.nombre) == nombre.lower())
    )
    if excluir_id:
        query = query.filter(Categoria.id != excluir_id)
    return query.first()


@router.post('/', response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    data: CategoriaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles('ADMIN')),
):
    nombre = _normalizar_nombre(data.nombre)
    codigo = _normalizar_codigo(data.code or nombre)
    if _buscar_duplicada(db, codigo, nombre):
        raise HTTPException(status_code=409, detail='Nombre o codigo de categoria duplicado')

    categoria = Categoria(
        code=codigo,
        nombre=nombre,
        descripcion=(data.descripcion or '').strip() or None,
        activo=data.activo,
    )
    db.add(categoria)
    try:
        db.commit()
        db.refresh(categoria)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail='Nombre o codigo de categoria duplicado') from error
    return categoria


@router.get('/', response_model=list[CategoriaOut])
def listar_categorias(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    return db.query(Categoria).order_by(Categoria.nombre.asc()).all()


@router.get('/{categoria_id}', response_model=CategoriaOut)
def obtener_categoria(
    categoria_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail='Categoria no encontrada')
    return categoria


@router.put('/{categoria_id}', response_model=CategoriaOut)
def actualizar_categoria(
    categoria_id: UUID,
    data: CategoriaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles('ADMIN')),
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail='Categoria no encontrada')

    datos = data.model_dump(exclude_unset=True)
    nombre = _normalizar_nombre(datos.get('nombre', categoria.nombre))
    codigo = _normalizar_codigo(datos.get('code') or categoria.code or nombre)
    if _buscar_duplicada(db, codigo, nombre, excluir_id=categoria_id):
        raise HTTPException(status_code=409, detail='Nombre o codigo de categoria duplicado')

    categoria.nombre = nombre
    categoria.code = codigo
    if 'descripcion' in datos:
        categoria.descripcion = (datos['descripcion'] or '').strip() or None
    if 'activo' in datos:
        categoria.activo = datos['activo']

    try:
        db.commit()
        db.refresh(categoria)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail='Nombre o codigo de categoria duplicado') from error
    return categoria


@router.delete('/{categoria_id}')
def eliminar_categoria(
    categoria_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles('ADMIN')),
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail='Categoria no encontrada')

    equipo_asociado = db.query(Equipo.id).filter(Equipo.categoria_id == categoria_id).first()
    if equipo_asociado:
        raise HTTPException(
            status_code=409,
            detail='No se puede eliminar la categoria porque tiene equipos asociados. Puede marcarla como inactiva.',
        )

    db.delete(categoria)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail='No se puede eliminar la categoria porque esta en uso') from error
    return {'message': 'Categoria eliminada correctamente'}
