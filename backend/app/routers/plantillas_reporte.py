from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth_dependencies import require_roles
from app.database import get_db
from app.models.empresa import Empresa
from app.models.plantilla_reporte import PlantillaReporte
from app.models.usuario import Usuario


router = APIRouter(
    prefix="/plantillas-reporte", tags=["Plantillas de reporte"],
    dependencies=[Depends(require_roles("ADMIN"))],
)


class PlantillaIn(BaseModel):
    empresa_id: UUID | None = None
    nombre: str = Field(min_length=3, max_length=150)
    tipo: str = "AMBOS"
    titulo: str = Field(min_length=3, max_length=220)
    color_primario: str = Field(default="#1E3A8A", pattern=r"^#[0-9A-Fa-f]{6}$")
    pie_pagina: str | None = Field(default=None, max_length=1000)
    incluir_logo: bool = True
    incluir_evidencias: bool = True
    incluir_firmas: bool = True
    incluir_costos: bool = False
    activo: bool = True


def _validar_tipo(tipo):
    tipo = str(tipo or "").upper()
    if tipo not in {"OT", "MENSUAL", "AMBOS"}:
        raise HTTPException(status_code=422, detail="Tipo de plantilla no permitido")
    return tipo


def _serializar(item, empresa=None):
    return {
        "id": str(item.id), "empresa_id": str(item.empresa_id) if item.empresa_id else None,
        "empresa_nombre": getattr(empresa, "nombre", None) or "Plantilla global",
        "nombre": item.nombre, "tipo": item.tipo, "titulo": item.titulo,
        "color_primario": item.color_primario, "pie_pagina": item.pie_pagina,
        "incluir_logo": item.incluir_logo, "incluir_evidencias": item.incluir_evidencias,
        "incluir_firmas": item.incluir_firmas, "incluir_costos": item.incluir_costos,
        "activo": item.activo, "created_at": item.created_at.isoformat() if item.created_at else None,
    }


@router.get("/")
def listar(db: Session = Depends(get_db)):
    empresas = {e.id: e for e in db.query(Empresa).all()}
    return [_serializar(item, empresas.get(item.empresa_id)) for item in db.query(PlantillaReporte).order_by(PlantillaReporte.updated_at.desc()).all()]


@router.post("/", status_code=201)
def crear(
    data: PlantillaIn, db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    empresa = None
    if data.empresa_id:
        empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
    item = PlantillaReporte(
        **data.model_dump(exclude={"tipo"}), tipo=_validar_tipo(data.tipo), creado_por_id=usuario.id,
    )
    db.add(item); db.commit(); db.refresh(item)
    return _serializar(item, empresa)


@router.put("/{plantilla_id}")
def actualizar(plantilla_id: UUID, data: PlantillaIn, db: Session = Depends(get_db)):
    item = db.query(PlantillaReporte).filter(PlantillaReporte.id == plantilla_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    if data.empresa_id and not db.query(Empresa).filter(Empresa.id == data.empresa_id).first():
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    payload = data.model_dump(); payload["tipo"] = _validar_tipo(payload["tipo"])
    for campo, valor in payload.items():
        setattr(item, campo, valor)
    db.commit(); db.refresh(item)
    empresa = db.query(Empresa).filter(Empresa.id == item.empresa_id).first() if item.empresa_id else None
    return _serializar(item, empresa)


@router.delete("/{plantilla_id}")
def eliminar(plantilla_id: UUID, db: Session = Depends(get_db)):
    item = db.query(PlantillaReporte).filter(PlantillaReporte.id == plantilla_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    db.delete(item); db.commit()
    return {"message": "Plantilla eliminada"}
