# =========================================================
# ROUTER HOJA DE VIDA TÉCNICA
# PASO 2 del registro del equipo
# =========================================================

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hoja_vida import EquipoHojaVida
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.categoria import Categoria
from app.schemas.hoja_vida import HojaVidaCreate, HojaVidaUpdate, HojaVidaOut


router = APIRouter(prefix="/hoja-vida", tags=["Hoja de Vida"])


@router.post("/", response_model=HojaVidaOut)
def crear_hoja_vida(data: HojaVidaCreate, db: Session = Depends(get_db)):
    """
    Crea la hoja de vida técnica de un equipo existente.

    REGLA:
    Solo puede existir una hoja de vida por equipo.
    """

    # Validar que el equipo exista
    equipo = db.query(Equipo).filter(Equipo.id == data.equipo_id).first()

    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El equipo asociado no existe"
        )

    # Validar que no exista hoja de vida para ese equipo
    existente = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.equipo_id == data.equipo_id
    ).first()

    if existente:
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
    Lista todas las hojas de vida técnicas.
    """

    hojas = db.query(EquipoHojaVida).order_by(
        EquipoHojaVida.created_at.desc()
    ).all()

    return hojas


@router.get("/equipo/{equipo_id}", response_model=HojaVidaOut)
def obtener_hoja_por_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """
    Consulta la hoja de vida técnica de un equipo.
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
    Consulta completa para imprimir o mostrar hoja de vida PRO.

    Incluye:
    - Logo de empresa cliente
    - Nombre de empresa
    - Nombre de sede
    - Datos básicos del equipo
    - Categoría
    - Datos técnicos de hoja de vida
    """

    # Buscar equipo
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()

    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )

    # Buscar empresa
    empresa = db.query(Empresa).filter(Empresa.id == equipo.empresa_id).first()

    # Buscar sede
    sede = db.query(Sede).filter(Sede.id == equipo.sede_id).first()

    # Buscar categoría
    categoria = None
    if equipo.categoria_id:
        categoria = db.query(Categoria).filter(
            Categoria.id == equipo.categoria_id
        ).first()

    # Buscar hoja de vida técnica
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
    Actualiza parcialmente la hoja de vida técnica.
    Ideal para completar datos cuando el técnico o administrador
    obtenga nueva información.
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
    Actualiza la hoja de vida usando el ID del equipo.
    Esta ruta es útil para el frontend porque normalmente
    se trabaja desde la ficha del equipo.
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
    Usar con cuidado porque elimina los datos técnicos del equipo.
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

    return {"message": "Hoja de vida eliminada correctamente"}