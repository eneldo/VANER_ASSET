import uuid
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth_dependencies import require_roles
from app.database import get_db
from app.models.empresa import Empresa
from app.models.factura import Factura
from app.models.usuario import Usuario


router = APIRouter(
    prefix="/facturacion",
    tags=["Facturación"],
    dependencies=[Depends(require_roles("ADMIN"))],
)

CENTAVOS = Decimal("0.01")
TRANSICIONES = {
    "BORRADOR": {"EMITIDA", "ANULADA"},
    "EMITIDA": {"PAGADA", "ANULADA"},
    "PAGADA": set(),
    "ANULADA": set(),
}


class LineaFactura(BaseModel):
    descripcion: str = Field(min_length=2, max_length=300)
    cantidad: Decimal = Field(gt=0)
    valor_unitario: Decimal = Field(ge=0)


class FacturaCreate(BaseModel):
    empresa_id: UUID
    concepto: str = Field(min_length=3, max_length=220)
    detalle: list[LineaFactura] = Field(min_length=1)
    impuesto_porcentaje: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    moneda: str = Field(default="COP", min_length=3, max_length=3)
    periodo_inicio: date
    periodo_fin: date
    fecha_emision: date
    fecha_vencimiento: date
    notas: str | None = Field(default=None, max_length=4000)


class EstadoFactura(BaseModel):
    estado: str
    fecha_pago: date | None = None


def calcular_totales(lineas, impuesto_porcentaje):
    subtotal = sum((Decimal(str(item.cantidad)) * Decimal(str(item.valor_unitario)) for item in lineas), Decimal("0"))
    subtotal = subtotal.quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    impuesto = (subtotal * Decimal(str(impuesto_porcentaje)) / Decimal("100")).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    return subtotal, impuesto, subtotal + impuesto


def estado_presentacion(factura, hoy=None):
    hoy = hoy or date.today()
    if factura.estado == "EMITIDA" and factura.fecha_vencimiento < hoy:
        return "VENCIDA"
    return factura.estado


def _serializar(factura, empresa=None):
    return {
        "id": str(factura.id), "empresa_id": str(factura.empresa_id),
        "empresa_nombre": getattr(empresa, "nombre", None), "numero": factura.numero,
        "concepto": factura.concepto, "detalle": factura.detalle, "moneda": factura.moneda,
        "subtotal": float(factura.subtotal), "impuesto_porcentaje": float(factura.impuesto_porcentaje),
        "impuesto": float(factura.impuesto), "total": float(factura.total),
        "estado": estado_presentacion(factura), "estado_persistido": factura.estado,
        "periodo_inicio": str(factura.periodo_inicio), "periodo_fin": str(factura.periodo_fin),
        "fecha_emision": str(factura.fecha_emision), "fecha_vencimiento": str(factura.fecha_vencimiento),
        "fecha_pago": str(factura.fecha_pago) if factura.fecha_pago else None, "notas": factura.notas,
        "created_at": factura.created_at.isoformat() if factura.created_at else None,
    }


@router.post("/facturas", status_code=201)
def crear_factura(
    data: FacturaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_roles("ADMIN")),
):
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    if data.periodo_fin < data.periodo_inicio or data.fecha_vencimiento < data.fecha_emision:
        raise HTTPException(status_code=422, detail="Periodo o vencimiento inválido")
    subtotal, impuesto, total = calcular_totales(data.detalle, data.impuesto_porcentaje)
    factura = Factura(
        empresa_id=data.empresa_id, creado_por_id=usuario.id,
        numero=f"FAC-{data.fecha_emision.year}-{uuid.uuid4().hex[:8].upper()}",
        concepto=data.concepto.strip(), detalle=[{
            "descripcion": item.descripcion.strip(), "cantidad": str(item.cantidad),
            "valor_unitario": str(item.valor_unitario),
        } for item in data.detalle],
        moneda=data.moneda.upper(), subtotal=subtotal,
        impuesto_porcentaje=data.impuesto_porcentaje, impuesto=impuesto, total=total,
        periodo_inicio=data.periodo_inicio, periodo_fin=data.periodo_fin,
        fecha_emision=data.fecha_emision, fecha_vencimiento=data.fecha_vencimiento, notas=data.notas,
    )
    db.add(factura); db.commit(); db.refresh(factura)
    return _serializar(factura, empresa)


@router.get("/facturas")
def listar_facturas(
    empresa_id: UUID | None = Query(default=None),
    estado: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Factura)
    if empresa_id:
        query = query.filter(Factura.empresa_id == empresa_id)
    facturas = query.order_by(Factura.fecha_emision.desc(), Factura.created_at.desc()).all()
    empresas = {e.id: e for e in db.query(Empresa).all()}
    items = [_serializar(f, empresas.get(f.empresa_id)) for f in facturas]
    if estado:
        items = [item for item in items if item["estado"] == estado.upper()]
    return items


@router.patch("/facturas/{factura_id}/estado")
def cambiar_estado(
    factura_id: UUID,
    data: EstadoFactura,
    db: Session = Depends(get_db),
):
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    nuevo = data.estado.strip().upper()
    if nuevo not in TRANSICIONES.get(factura.estado, set()):
        raise HTTPException(status_code=409, detail=f"Transición {factura.estado} → {nuevo} no permitida")
    if nuevo == "PAGADA":
        factura.fecha_pago = data.fecha_pago or date.today()
    factura.estado = nuevo
    db.commit(); db.refresh(factura)
    empresa = db.query(Empresa).filter(Empresa.id == factura.empresa_id).first()
    return _serializar(factura, empresa)


@router.get("/resumen")
def resumen_facturacion(db: Session = Depends(get_db)):
    facturas = db.query(Factura).all()
    vigentes = [f for f in facturas if f.estado != "ANULADA"]
    return {
        "total_facturado": float(sum((f.total for f in vigentes), Decimal("0"))),
        "total_pagado": float(sum((f.total for f in vigentes if f.estado == "PAGADA"), Decimal("0"))),
        "cartera_pendiente": float(sum((f.total for f in vigentes if f.estado == "EMITIDA"), Decimal("0"))),
        "facturas_vencidas": sum(1 for f in vigentes if estado_presentacion(f) == "VENCIDA"),
        "borradores": sum(1 for f in facturas if f.estado == "BORRADOR"),
    }
