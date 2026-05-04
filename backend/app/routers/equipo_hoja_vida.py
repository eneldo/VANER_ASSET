# =========================================================
# ROUTER: EQUIPO HOJA DE VIDA TÉCNICA
# Maneja el PASO 2 de hoja de vida del equipo
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.categoria import Categoria
from app.models.equipo_hoja_vida import EquipoHojaVida
from app.schemas.equipo_hoja_vida import HojaVidaCreate, HojaVidaUpdate, HojaVidaOut


router = APIRouter(prefix="/equipo-hoja-vida", tags=["Equipo Hoja de Vida"])


@router.post("/", response_model=HojaVidaOut)
def crear_hoja_vida(data: HojaVidaCreate, db: Session = Depends(get_db)):
    """
    Crea la hoja de vida técnica para un equipo existente.
    Regla: solo puede existir una hoja de vida por equipo.
    """

    equipo = db.query(Equipo).filter(Equipo.id == data.equipo_id).first()

    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El equipo asociado no existe"
        )

    hoja_existente = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.equipo_id == data.equipo_id
    ).first()

    if hoja_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este equipo ya tiene hoja de vida técnica"
        )

    nueva_hoja = EquipoHojaVida(**data.model_dump())

    db.add(nueva_hoja)
    db.commit()
    db.refresh(nueva_hoja)

    return nueva_hoja


@router.get("/", response_model=list[HojaVidaOut])
def listar_hojas_vida(db: Session = Depends(get_db)):
    """
    Lista todas las hojas de vida técnicas registradas.
    """

    hojas = db.query(EquipoHojaVida).order_by(
        EquipoHojaVida.created_at.desc()
    ).all()

    return hojas


@router.get("/equipo/{equipo_id}", response_model=HojaVidaOut)
def obtener_hoja_por_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene la hoja de vida técnica de un equipo.
    """

    hoja = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.equipo_id == equipo_id
    ).first()

    if not hoja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El equipo aún no tiene hoja de vida técnica"
        )

    return hoja


@router.get("/equipo/{equipo_id}/completa")
def obtener_hoja_completa(equipo_id: UUID, db: Session = Depends(get_db)):
    """
    Devuelve la hoja de vida completa para vista tipo PDF.

    Incluye:
    - Logo de empresa cliente
    - Nombre de empresa
    - Nombre de sede
    - Datos básicos del equipo
    - Categoría
    - Datos técnicos de hoja de vida
    """

    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()

    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )

    empresa = db.query(Empresa).filter(Empresa.id == equipo.empresa_id).first()
    sede = db.query(Sede).filter(Sede.id == equipo.sede_id).first()

    categoria = None
    if equipo.categoria_id:
        categoria = db.query(Categoria).filter(
            Categoria.id == equipo.categoria_id
        ).first()

    hoja = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.equipo_id == equipo_id
    ).first()

    return {
        "encabezado": {
            "empresa_nombre": empresa.nombre if empresa else None,
            "empresa_logo_url": empresa.logo_url if empresa else None,
            "sede_nombre": sede.nombre if sede else None
        },
        "equipo_basico": {
            "id": str(equipo.id),
            "nombre": equipo.nombre,
            "marca": equipo.marca,
            "modelo": equipo.modelo,
            "serie": equipo.serie,
            "ubicacion": equipo.ubicacion,
            "invima": equipo.invima,
            "codigo_id": equipo.codigo_id,
            "inventario": getattr(equipo, "inventario", None),
            "estado": equipo.estado,
            "criticidad": equipo.criticidad,
            "categoria": categoria.nombre if categoria else None
        },
        "hoja_vida_tecnica": hoja
    }


@router.put("/{hoja_id}", response_model=HojaVidaOut)
def actualizar_hoja_vida(
    hoja_id: UUID,
    data: HojaVidaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente una hoja de vida técnica usando el ID de la hoja.
    """

    hoja = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.id == hoja_id
    ).first()

    if not hoja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hoja de vida no encontrada"
        )

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(hoja, campo, valor)

    db.commit()
    db.refresh(hoja)

    return hoja


@router.put("/equipo/{equipo_id}", response_model=HojaVidaOut)
def actualizar_hoja_por_equipo(
    equipo_id: UUID,
    data: HojaVidaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente una hoja de vida usando el ID del equipo.
    Esta ruta es útil para el frontend.
    """

    hoja = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.equipo_id == equipo_id
    ).first()

    if not hoja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El equipo aún no tiene hoja de vida técnica"
        )

    datos = data.model_dump(exclude_unset=True)

    for campo, valor in datos.items():
        setattr(hoja, campo, valor)

    db.commit()
    db.refresh(hoja)

    return hoja


@router.delete("/{hoja_id}")
def eliminar_hoja_vida(hoja_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina una hoja de vida técnica.
    """

    hoja = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.id == hoja_id
    ).first()

    if not hoja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hoja de vida no encontrada"
        )

    db.delete(hoja)
    db.commit()

    return {"message": "Hoja de vida técnica eliminada correctamente"}