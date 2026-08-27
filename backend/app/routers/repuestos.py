# ============================================================
# ROUTER: Repuestos y Consumibles
# CRUD catálogo, bodegas, existencias, movimientos,
# solicitudes, reservas, entregas, devoluciones.
# ============================================================

from datetime import datetime, timezone, date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.repuestos import (
    CategoriaRepuesto, UnidadMedida, Repuesto, Bodega,
    Existencia, MovimientoRepuesto, SolicitudRepuesto,
    ProveedorRepuesto, RepuestoProveedor, RepuestoCompatibilidad,
)
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.mantenimiento import Mantenimiento
from app.routers.auth import obtener_usuario_actual
from app.core.auth_dependencies import require_roles

from app.schemas.repuestos import (
    CategoriaRepuestoCreate, CategoriaRepuestoOut,
    UnidadMedidaOut,
    RepuestoCreate, RepuestoUpdate, RepuestoOut,
    BodegaCreate, BodegaUpdate, BodegaOut,
    ExistenciaOut,
    MovimientoCreate, MovimientoOut,
    SolicitudCreate, SolicitudUpdate, SolicitudOut,
    ProveedorCreate, ProveedorUpdate, ProveedorOut,
    CompatibilidadCreate, CompatibilidadOut,
    DashboardRepuestos,
)


router = APIRouter(
    prefix="/repuestos",
    tags=["Repuestos y Consumibles"],
    dependencies=[Depends(require_roles("ADMIN", "COORDINADOR", "TECNICO"))],
)


# ============================================================
# HELPERS
# ============================================================

def _now():
    return datetime.now(timezone.utc)


def _filtrar_por_empresa(query, usuario):
    if usuario.rol != "ADMIN" or not usuario.empresa_id:
        if usuario.empresa_id:
            query = query.filter_by(empresa_id=usuario.empresa_id)
    return query


def _get_empresa_id(usuario):
    return usuario.empresa_id


def _validar_empresa(usuario):
    if not usuario.empresa_id:
        raise HTTPException(status_code=400, detail="Usuario sin empresa asignada")
    return usuario.empresa_id


def _obtener_repuesto(repuesto_id: str, db: Session, usuario: Usuario):
    q = db.query(Repuesto).filter(Repuesto.id == repuesto_id)
    q = _filtrar_por_empresa(q, usuario)
    rep = q.first()
    if not rep:
        raise HTTPException(status_code=404, detail="Repuesto no encontrado")
    return rep


def _obtener_bodega(bodega_id: str, db: Session, usuario: Usuario):
    q = db.query(Bodega).filter(Bodega.id == bodega_id)
    q = _filtrar_por_empresa(q, usuario)
    b = q.first()
    if not b:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return b


def _get_or_create_existencia(db, empresa_id, repuesto_id, bodega_id, lote=None, serial=None):
    ex = db.query(Existencia).filter(
        Existencia.empresa_id == empresa_id,
        Existencia.repuesto_id == repuesto_id,
        Existencia.bodega_id == bodega_id,
        Existencia.lote == lote,
        Existencia.serial == serial,
    ).first()
    if not ex:
        ex = Existencia(
            empresa_id=empresa_id,
            repuesto_id=repuesto_id,
            bodega_id=bodega_id,
            existencia_fisica=Decimal("0"),
            cantidad_reservada=Decimal("0"),
            lote=lote,
            serial=serial,
        )
        db.add(ex)
        db.flush()
    return ex


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/dashboard", response_model=DashboardRepuestos)
def dashboard(usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    eid = _validar_empresa(usuario)

    total = db.query(func.count(Repuesto.id)).filter(
        Repuesto.empresa_id == eid, Repuesto.activo == True
    ).scalar() or 0

    existencias = db.query(Existencia).filter(Empresa.id == eid if not eid else Existencia.empresa_id == eid).all()
    disponibles = sum(float(e.existencia_fisica - e.cantidad_reservada) for e in existencias)
    agotados = sum(1 for e in existencias if e.existencia_fisica <= 0)
    stock_bajo = 0
    for e in existencias:
        if e.existencia_fisica > 0:
            rep = db.query(Repuesto).filter(Repuesto.id == e.repuesto_id).first()
            if rep and rep.stock_minimo and e.existencia_fisica <= float(rep.stock_minimo):
                stock_bajo += 1

    valor = sum(float(e.existencia_fisica) * float(e.costo_promedio or 0) for e in existencias)

    sol_pend = db.query(func.count(SolicitudRepuesto.id)).filter(
        SolicitudRepuesto.empresa_id == eid,
        SolicitudRepuesto.estado.in_(["SOLICITADO", "APROBADO"]),
    ).scalar() or 0

    res_pend = db.query(func.count(SolicitudRepuesto.id)).filter(
        SolicitudRepuesto.empresa_id == eid,
        SolicitudRepuesto.estado == "RESERVADO",
    ).scalar() or 0

    return DashboardRepuestos(
        total_repuestos_activos=total,
        total_unidades_disponibles=Decimal(str(disponibles)),
        repuestos_stock_bajo=stock_bajo,
        repuestos_agotados=agotados,
        valor_inventario=Decimal(str(valor)),
        solicitudes_pendientes=sol_pend,
        reservas_pendientes=res_pend,
        entregas_periodo=0,
        ordenes_detenidas=0,
    )


# ============================================================
# CATEGORÍAS
# ============================================================

@router.get("/categorias", response_model=list[CategoriaRepuestoOut])
def listar_categorias(usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    q = db.query(CategoriaRepuesto).filter(CategoriaRepuesto.activo == True)
    q = _filtrar_por_empresa(q, usuario)
    return q.order_by(CategoriaRepuesto.nombre).all()


@router.post("/categorias", response_model=CategoriaRepuestoOut)
def crear_categoria(data: CategoriaRepuestoCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    empresa_id = _validar_empresa(usuario)
    cat = CategoriaRepuesto(empresa_id=empresa_id, **data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ============================================================
# UNIDADES DE MEDIDA
# ============================================================

@router.get("/unidades", response_model=list[UnidadMedidaOut])
def listar_unidades(db: Session = Depends(get_db)):
    return db.query(UnidadMedida).filter(UnidadMedida.activo == True).order_by(UnidadMedida.nombre).all()


# ============================================================
# CATÁLOGO DE REPUESTOS
# ============================================================

@router.get("/", response_model=list[RepuestoOut])
def listar_repuestos(
    buscar: str = Query(None),
    tipo: str = Query(None),
    categoria_id: str = Query(None),
    activo: bool = Query(True),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    q = db.query(Repuesto)
    q = _filtrar_por_empresa(q, usuario)
    if activo is not None:
        q = q.filter(Repuesto.activo == activo)
    if tipo:
        q = q.filter(Repuesto.tipo == tipo)
    if categoria_id:
        q = q.filter(Repuesto.categoria_id == categoria_id)
    if buscar:
        like = f"%{buscar}%"
        q = q.filter(or_(
            Repuesto.codigo.ilike(like),
            Repuesto.nombre.ilike(like),
            Repuesto.referencia.ilike(like),
            Repuesto.marca.ilike(like),
        ))
    total = q.count()
    items = q.order_by(Repuesto.nombre).offset((page - 1) * per_page).limit(per_page).all()
    return items


@router.post("/", response_model=RepuestoOut)
def crear_repuesto(data: RepuestoCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    empresa_id = _validar_empresa(usuario)
    rep = Repuesto(empresa_id=empresa_id, creado_por=usuario.id, **data.model_dump())
    db.add(rep)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un repuesto con ese código en esta empresa")
    db.refresh(rep)
    return rep


@router.get("/{repuesto_id}", response_model=RepuestoOut)
def obtener_repuesto(repuesto_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    return _obtener_repuesto(repuesto_id, db, usuario)


@router.put("/{repuesto_id}", response_model=RepuestoOut)
def actualizar_repuesto(repuesto_id: str, data: RepuestoUpdate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    rep = _obtener_repuesto(repuesto_id, db, usuario)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(rep, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al actualizar repuesto")
    db.refresh(rep)
    return rep


@router.patch("/{repuesto_id}/estado")
def toggle_estado(repuesto_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    rep = _obtener_repuesto(repuesto_id, db, usuario)
    rep.activo = not rep.activo
    db.commit()
    return {"id": str(rep.id), "activo": rep.activo}


# ============================================================
# BODEGAS
# ============================================================

@router.get("/bodegas", response_model=list[BodegaOut])
def listar_bodegas(usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    q = db.query(Bodega).filter(Bodega.activo == True)
    q = _filtrar_por_empresa(q, usuario)
    return q.order_by(Bodega.nombre).all()


@router.post("/bodegas", response_model=BodegaOut)
def crear_bodega(data: BodegaCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    empresa_id = _validar_empresa(usuario)
    b = Bodega(empresa_id=empresa_id, **data.model_dump())
    db.add(b)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una bodega con ese nombre")
    db.refresh(b)
    return b


@router.put("/bodegas/{bodega_id}", response_model=BodegaOut)
def actualizar_bodega(bodega_id: str, data: BodegaUpdate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    b = _obtener_bodega(bodega_id, db, usuario)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(b, k, v)
    db.commit()
    db.refresh(b)
    return b


# ============================================================
# EXISTENCIAS
# ============================================================

@router.get("/existencias", response_model=list[ExistenciaOut])
def listar_existencias(
    repuesto_id: str = Query(None),
    bodega_id: str = Query(None),
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    q = db.query(Existencia)
    q = _filtrar_por_empresa(q, usuario)
    if repuesto_id:
        q = q.filter(Existencia.repuesto_id == repuesto_id)
    if bodega_id:
        q = q.filter(Existencia.bodega_id == bodega_id)
    return q.order_by(Existencia.id).all()


@router.get("/existencias/{repuesto_id}")
def existencias_por_repuesto(repuesto_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    q = db.query(Existencia).filter(Existencia.repuesto_id == repuesto_id)
    q = _filtrar_por_empresa(q, usuario)
    items = q.all()
    total_fisica = sum(float(e.existencia_fisica) for e in items)
    total_reservada = sum(float(e.cantidad_reservada) for e in items)
    return {
        "repuesto_id": repuesto_id,
        "total_fisica": total_fisica,
        "total_reservada": total_reservada,
        "total_disponible": total_fisica - total_reservada,
        "bodegas": [
            {
                "bodega_id": str(e.bodega_id),
                "existencia_fisica": float(e.existencia_fisica),
                "cantidad_reservada": float(e.cantidad_reservada),
                "disponible": float(e.existencia_fisica - e.cantidad_reservada),
                "lote": e.lote,
                "serial": e.serial,
                "fecha_vencimiento": str(e.fecha_vencimiento) if e.fecha_vencimiento else None,
            }
            for e in items
        ],
    }


# ============================================================
# MOVIMIENTOS
# ============================================================

@router.get("/movimientos", response_model=list[MovimientoOut])
def listar_movimientos(
    repuesto_id: str = Query(None),
    tipo_movimiento: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    q = db.query(MovimientoRepuesto)
    q = _filtrar_por_empresa(q, usuario)
    if repuesto_id:
        q = q.filter(MovimientoRepuesto.repuesto_id == repuesto_id)
    if tipo_movimiento:
        q = q.filter(MovimientoRepuesto.tipo_movimiento == tipo_movimiento)
    total = q.count()
    items = q.order_by(MovimientoRepuesto.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return items


@router.post("/movimientos/entrada", response_model=MovimientoOut)
def registrar_entrada(data: MovimientoCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    empresa_id = _validar_empresa(usuario)
    if data.tipo_movimiento not in ["ENTRADA_COMPRA", "ENTRADA_INICIAL"]:
        raise HTTPException(status_code=400, detail="Tipo de entrada inválido")
    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
    if data.bodega_destino_id is None:
        raise HTTPException(status_code=400, detail="Debe especificar bodega destino")

    rep = _obtener_repuesto(data.repuesto_id, db, usuario)
    _obtener_bodega(data.bodega_destino_id, db, usuario)

    ex = _get_or_create_existencia(db, empresa_id, data.repuesto_id, data.bodega_destino_id)
    anterior = ex.existencia_fisica

    ex.existencia_fisica += data.cantidad
    if data.costo_unitario:
        if ex.costo_promedio:
            total_anterior = float(anterior) * float(ex.costo_promedio)
            total_nuevo = float(data.cantidad) * float(data.costo_unitario)
            total_cantidad = float(anterior + data.cantidad)
            ex.costo_promedio = Decimal(str((total_anterior + total_nuevo) / total_cantidad)) if total_cantidad > 0 else data.costo_unitario
        else:
            ex.costo_promedio = data.costo_unitario
        ex.ultimo_costo = data.costo_unitario

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=data.repuesto_id,
        bodega_destino_id=data.bodega_destino_id,
        tipo_movimiento=data.tipo_movimiento,
        cantidad=data.cantidad,
        unidad=data.unidad,
        costo_unitario=data.costo_unitario,
        costo_total=data.cantidad * data.costo_unitario if data.costo_unitario else None,
        existencia_anterior=anterior,
        existencia_posterior=ex.existencia_fisica,
        mantenimiento_id=data.mantenimiento_id,
        documento=data.documento,
        motivo=data.motivo,
        idempotency_key=data.idempotency_key,
        usuario_id=usuario.id,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


@router.post("/movimientos/ajuste", response_model=MovimientoOut)
def registrar_ajuste(data: MovimientoCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    empresa_id = _validar_empresa(usuario)
    if data.tipo_movimiento not in ["AJUSTE_POSITIVO", "AJUSTE_NEGATIVO"]:
        raise HTTPException(status_code=400, detail="Tipo de ajuste inválido")
    if not data.bodega_destino_id:
        raise HTTPException(status_code=400, detail="Debe especificar bodega")

    _obtener_repuesto(data.repuesto_id, db, usuario)
    _obtener_bodega(data.bodega_destino_id, db, usuario)
    ex = _get_or_create_existencia(db, empresa_id, data.repuesto_id, data.bodega_destino_id)
    anterior = ex.existencia_fisica

    if data.tipo_movimiento == "AJUSTE_POSITIVO":
        ex.existencia_fisica += data.cantidad
    else:
        if ex.existencia_fisica < data.cantidad:
            raise HTTPException(status_code=400, detail="Ajuste excede existencia disponible")
        ex.existencia_fisica -= data.cantidad

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=data.repuesto_id,
        bodega_origen_id=data.bodega_destino_id if data.tipo_movimiento == "AJUSTE_NEGATIVO" else None,
        bodega_destino_id=data.bodega_destino_id if data.tipo_movimiento == "AJUSTE_POSITIVO" else None,
        tipo_movimiento=data.tipo_movimiento,
        cantidad=data.cantidad,
        unidad=data.unidad,
        existencia_anterior=anterior,
        existencia_posterior=ex.existencia_fisica,
        motivo=data.motivo,
        usuario_id=usuario.id,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


@router.post("/movimientos/transferencia", response_model=MovimientoOut)
def registrar_transferencia(data: MovimientoCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    empresa_id = _validar_empresa(usuario)
    if not data.bodega_origen_id or not data.bodega_destino_id:
        raise HTTPException(status_code=400, detail="Debe especificar bodega origen y destino")
    if data.bodega_origen_id == data.bodega_destino_id:
        raise HTTPException(status_code=400, detail="Las bodegas origen y destino deben ser diferentes")
    if data.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    _obtener_repuesto(data.repuesto_id, db, usuario)
    _obtener_bodega(data.bodega_origen_id, db, usuario)
    _obtener_bodega(data.bodega_destino_id, db, usuario)

    ex_origen = _get_or_create_existencia(db, empresa_id, data.repuesto_id, data.bodega_origen_id)
    if ex_origen.existencia_fisica < data.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente en bodega origen")

    anterior_origen = ex_origen.existencia_fisica
    ex_origen.existencia_fisica -= data.cantidad

    ex_destino = _get_or_create_existencia(db, empresa_id, data.repuesto_id, data.bodega_destino_id)
    anterior_destino = ex_destino.existencia_fisica
    ex_destino.existencia_fisica += data.cantidad

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=data.repuesto_id,
        bodega_origen_id=data.bodega_origen_id,
        bodega_destino_id=data.bodega_destino_id,
        tipo_movimiento="TRANSFERENCIA",
        cantidad=data.cantidad,
        unidad=data.unidad,
        existencia_anterior=anterior_origen,
        existencia_posterior=ex_origen.existencia_fisica,
        motivo=data.motivo,
        usuario_id=usuario.id,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


# ============================================================
# SOLICITUDES
# ============================================================

@router.get("/solicitudes", response_model=list[SolicitudOut])
def listar_solicitudes(
    estado: str = Query(None),
    mantenimiento_id: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    q = db.query(SolicitudRepuesto)
    q = _filtrar_por_empresa(q, usuario)
    if estado:
        q = q.filter(SolicitudRepuesto.estado == estado)
    if mantenimiento_id:
        q = q.filter(SolicitudRepuesto.mantenimiento_id == mantenimiento_id)
    total = q.count()
    items = q.order_by(SolicitudRepuesto.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return items


@router.post("/solicitudes", response_model=SolicitudOut)
def crear_solicitud(data: SolicitudCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    empresa_id = _validar_empresa(usuario)
    if data.cantidad_solicitada <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    _obtener_repuesto(data.repuesto_id, db, usuario)

    sol = SolicitudRepuesto(
        empresa_id=empresa_id,
        mantenimiento_id=data.mantenimiento_id,
        repuesto_id=data.repuesto_id,
        bodega_id=data.bodega_id,
        cantidad_solicitada=data.cantidad_solicitada,
        observaciones=data.observaciones,
        solicitado_por=usuario.id,
        estado="SOLICITADO",
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    return sol


@router.patch("/solicitudes/{solicitud_id}", response_model=SolicitudOut)
def actualizar_solicitud(solicitud_id: str, data: SolicitudUpdate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if data.estado:
        transiciones = {
            "SOLICITADO": ["APROBADO", "RECHAZADO", "CANCELADO"],
            "APROBADO": ["RESERVADO", "CANCELADO"],
            "RESERVADO": ["ENTREGADO", "CANCELADO"],
            "ENTREGADO": ["CONSUMIDO", "DEVUELTO_PARCIAL", "DEVUELTO"],
        }
        permitidos = transiciones.get(sol.estado, [])
        if data.estado not in permitidos:
            raise HTTPException(status_code=400, detail=f"No se puede cambiar de {sol.estado} a {data.estado}")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(sol, k, v)
    db.commit()
    db.refresh(sol)
    return sol


@router.post("/solicitudes/{solicitud_id}/aprobar", response_model=SolicitudOut)
def aprobar_solicitud(solicitud_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado != "SOLICITADO":
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}, se esperaba SOLICITADO")

    sol.estado = "APROBADO"
    sol.autorizado_por = usuario.id
    sol.cantidad_aprobada = sol.cantidad_solicitada
    db.commit()
    db.refresh(sol)
    return sol


@router.post("/solicitudes/{solicitud_id}/reservar")
def reservar_solicitud(solicitud_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado != "APROBADO":
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}, se esperaba APROBADO")

    empresa_id = _validar_empresa(usuario)
    bodega_id = sol.bodega_id
    if not bodega_id:
        raise HTTPException(status_code=400, detail="Solicitud sin bodega asignada")

    ex = _get_or_create_existencia(db, empresa_id, sol.repuesto_id, bodega_id)
    disponible = ex.existencia_fisica - ex.cantidad_reservada
    cantidad = sol.cantidad_aprobada or sol.cantidad_solicitada

    if disponible < cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {disponible}, solicitado: {cantidad}")

    ex.cantidad_reservada += cantidad

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=sol.repuesto_id,
        bodega_origen_id=bodega_id,
        tipo_movimiento="RESERVA",
        cantidad=cantidad,
        solicitud_id=sol.id,
        existencia_anterior=ex.existencia_fisica,
        existencia_posterior=ex.existencia_fisica,
        motivo=f"Reserva para solicitud {str(sol.id)[:8]}",
        usuario_id=usuario.id,
    )
    db.add(mov)
    sol.estado = "RESERVADO"
    db.commit()
    return {"ok": True, "estado": "RESERVADO"}


@router.post("/solicitudes/{solicitud_id}/entregar")
def entregar_solicitud(solicitud_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado != "RESERVADO":
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}, se esperaba RESERVADO")

    empresa_id = _validar_empresa(usuario)
    bodega_id = sol.bodega_id
    cantidad = sol.cantidad_aprobada or sol.cantidad_solicitada

    ex = _get_or_create_existencia(db, empresa_id, sol.repuesto_id, bodega_id)
    anterior = ex.existencia_fisica

    if ex.existencia_fisica < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente para entrega")

    ex.existencia_fisica -= cantidad
    ex.cantidad_reservada = max(Decimal("0"), ex.cantidad_reservada - cantidad)

    rep = db.query(Repuesto).filter(Repuesto.id == sol.repuesto_id).first()
    costo = rep.ultimo_costo if rep else None

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=sol.repuesto_id,
        bodega_origen_id=bodega_id,
        tipo_movimiento="ENTREGA_TECNICO",
        cantidad=cantidad,
        costo_unitario=costo,
        costo_total=cantidad * costo if costo else None,
        existencia_anterior=anterior,
        existencia_posterior=ex.existencia_fisica,
        solicitud_id=sol.id,
        usuario_id=usuario.id,
    )
    db.add(mov)
    sol.estado = "ENTREGADO"
    sol.cantidad_entregada = cantidad
    sol.entregado_por = usuario.id
    db.commit()
    return {"ok": True, "estado": "ENTREGADO"}


@router.post("/solicitudes/{solicitud_id}/consumir")
def consumir_solicitud(solicitud_id: str, cantidad: Decimal = Query(..., gt=0), usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado != "ENTREGADO":
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}, se esperaba ENTREGADO")

    empresa_id = _validar_empresa(usuario)
    cantidad_entregada = sol.cantidad_entregada or sol.cantidad_aprobada or sol.cantidad_solicitada
    if cantidad > cantidad_entregada:
        raise HTTPException(status_code=400, detail="La cantidad consumida excede la entregada")

    rep = db.query(Repuesto).filter(Repuesto.id == sol.repuesto_id).first()
    costo = rep.ultimo_costo if rep else None

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=sol.repuesto_id,
        tipo_movimiento="CONSUMO",
        cantidad=cantidad,
        costo_unitario=costo,
        costo_total=cantidad * costo if costo else None,
        solicitud_id=sol.id,
        usuario_id=usuario.id,
    )
    db.add(mov)

    sol.estado = "CONSUMIDO"
    if cantidad < cantidad_entregada:
        sol.estado = "DEVUELTO_PARCIAL"
    db.commit()
    return {"ok": True, "estado": sol.estado}


@router.post("/solicitudes/{solicitud_id}/devolver")
def devolver_solicitud(solicitud_id: str, cantidad: Decimal = Query(..., gt=0), bodega_id: str = Query(...), usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado not in ["ENTREGADO", "DEVUELTO_PARCIAL", "CONSUMIDO"]:
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}")

    empresa_id = _validar_empresa(usuario)
    _obtener_bodega(bodega_id, db, usuario)

    ex = _get_or_create_existencia(db, empresa_id, sol.repuesto_id, bodega_id)
    anterior = ex.existencia_fisica
    ex.existencia_fisica += cantidad

    ex_reserva = db.query(Existencia).filter(
        Existencia.empresa_id == empresa_id,
        Existencia.repuesto_id == sol.repuesto_id,
        Existencia.bodega_id == sol.bodega_id,
    ).first()
    if ex_reserva:
        ex_reserva.cantidad_reservada = max(Decimal("0"), ex_reserva.cantidad_reservada - cantidad)

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=sol.repuesto_id,
        bodega_destino_id=bodega_id,
        tipo_movimiento="DEVOLUCION",
        cantidad=cantidad,
        existencia_anterior=anterior,
        existencia_posterior=ex.existencia_fisica,
        solicitud_id=sol.id,
        usuario_id=usuario.id,
    )
    db.add(mov)

    devuelta_anterior = sol.cantidad_devuelta or Decimal("0")
    sol.cantidad_devuelta = devuelta_anterior + cantidad
    sol.estado = "DEVUELTO"
    db.commit()
    return {"ok": True, "estado": "DEVUELTO"}


# ============================================================
# PROVEEDORES
# ============================================================

@router.get("/proveedores", response_model=list[ProveedorOut])
def listar_proveedores(usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    q = db.query(ProveedorRepuesto).filter(ProveedorRepuesto.activo == True)
    q = _filtrar_por_empresa(q, usuario)
    return q.order_by(ProveedorRepuesto.nombre).all()


@router.post("/proveedores", response_model=ProveedorOut)
def crear_proveedor(data: ProveedorCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    empresa_id = _validar_empresa(usuario)
    p = ProveedorRepuesto(empresa_id=empresa_id, **data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/proveedores/{proveedor_id}", response_model=ProveedorOut)
def actualizar_proveedor(proveedor_id: str, data: ProveedorUpdate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    p = db.query(ProveedorRepuesto).filter(ProveedorRepuesto.id == proveedor_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


# ============================================================
# COMPATIBILIDAD
# ============================================================

@router.get("/compatibilidad", response_model=list[CompatibilidadOut])
def listar_compatibilidad(repuesto_id: str = Query(None), usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    q = db.query(RepuestoCompatibilidad).filter(RepuestoCompatibilidad.activo == True)
    if repuesto_id:
        q = q.filter(RepuestoCompatibilidad.repuesto_id == repuesto_id)
    return q.all()


@router.post("/compatibilidad", response_model=CompatibilidadOut)
def crear_compatibilidad(data: CompatibilidadCreate, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    c = RepuestoCompatibilidad(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ============================================================
# INTEGRACIÓN CON ÓRDENES DE TRABAJO
# ============================================================

@router.get("/ot/{mantenimiento_id}")
def repuestos_por_ot(mantenimiento_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    solicitudes = db.query(SolicitudRepuesto).filter(
        SolicitudRepuesto.mantenimiento_id == mantenimiento_id
    ).all()

    items = []
    costo_total = Decimal("0")
    for s in solicitudes:
        rep = db.query(Repuesto).filter(Repuesto.id == s.repuesto_id).first()
        costo_linea = Decimal("0")
        if s.estado in ["CONSUMIDO", "DEVUELTO_PARCIAL", "DEVUELTO"]:
            cantidad_consumida = s.cantidad_entregada or s.cantidad_aprobada or s.cantidad_solicitada
            if s.cantidad_devuelta:
                cantidad_consumida = cantidad_consumida - s.cantidad_devuelta
            costo_unitario = rep.ultimo_costo or Decimal("0")
            costo_linea = cantidad_consumida * costo_unitario
            costo_total += costo_linea

        items.append({
            "solicitud_id": str(s.id),
            "repuesto_id": str(s.repuesto_id),
            "repuesto_nombre": rep.nombre if rep else "—",
            "repuesto_codigo": rep.codigo if rep else "—",
            "cantidad_solicitada": float(s.cantidad_solicitada),
            "cantidad_aprobada": float(s.cantidad_aprobada) if s.cantidad_aprobada else None,
            "cantidad_entregada": float(s.cantidad_entregada) if s.cantidad_entregada else None,
            "cantidad_devuelta": float(s.cantidad_devuelta) if s.cantidad_devuelta else None,
            "estado": s.estado,
            "costo_unitario": float(rep.ultimo_costo) if rep and rep.ultimo_costo else None,
            "costo_linea": float(costo_linea),
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })

    return {
        "mantenimiento_id": mantenimiento_id,
        "repuestos": items,
        "total_repuestos": len(items),
        "costo_total_repuestos": float(costo_total),
    }


@router.post("/ot/{mantenimiento_id}/solicitar")
def solicitar_repuesto_ot(
    mantenimiento_id: str,
    data: SolicitudCreate,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    empresa_id = _validar_empresa(usuario)
    if data.cantidad_solicitada <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

    rep = _obtener_repuesto(data.repuesto_id, db, usuario)

    sol = SolicitudRepuesto(
        empresa_id=empresa_id,
        mantenimiento_id=mantenimiento_id,
        repuesto_id=data.repuesto_id,
        bodega_id=data.bodega_id,
        cantidad_solicitada=data.cantidad_solicitada,
        observaciones=data.observaciones,
        solicitado_por=usuario.id,
        estado="SOLICITADO",
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    return {"ok": True, "solicitud_id": str(sol.id), "estado": "SOLICITADO"}


@router.post("/ot/solicitudes/{solicitud_id}/aprobar")
def aprobar_solicitud_ot(solicitud_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado != "SOLICITADO":
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}, se esperaba SOLICITADO")

    sol.estado = "APROBADO"
    sol.autorizado_por = usuario.id
    sol.cantidad_aprobada = sol.cantidad_solicitada
    db.commit()
    return {"ok": True, "estado": "APROBADO"}


@router.post("/ot/solicitudes/{solicitud_id}/reservar")
def reservar_solicitud_ot(solicitud_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado != "APROBADO":
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}, se esperaba APROBADO")

    empresa_id = _validar_empresa(usuario)
    bodega_id = sol.bodega_id
    if not bodega_id:
        raise HTTPException(status_code=400, detail="Solicitud sin bodega asignada")

    ex = _get_or_create_existencia(db, empresa_id, sol.repuesto_id, bodega_id)
    cantidad = sol.cantidad_aprobada or sol.cantidad_solicitada
    disponible = ex.existencia_fisica - ex.cantidad_reservada

    if disponible < cantidad:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {disponible}, solicitado: {cantidad}")

    ex.cantidad_reservada += cantidad

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=sol.repuesto_id,
        bodega_origen_id=bodega_id,
        tipo_movimiento="RESERVA",
        cantidad=cantidad,
        solicitud_id=sol.id,
        existencia_anterior=ex.existencia_fisica,
        existencia_posterior=ex.existencia_fisica,
        motivo=f"Reserva para OT",
        usuario_id=usuario.id,
    )
    db.add(mov)
    sol.estado = "RESERVADO"
    db.commit()
    return {"ok": True, "estado": "RESERVADO"}


@router.post("/ot/solicitudes/{solicitud_id}/entregar")
def entregar_solicitud_ot(solicitud_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado != "RESERVADO":
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}, se esperaba RESERVADO")

    empresa_id = _validar_empresa(usuario)
    bodega_id = sol.bodega_id
    cantidad = sol.cantidad_aprobada or sol.cantidad_solicitada

    ex = _get_or_create_existencia(db, empresa_id, sol.repuesto_id, bodega_id)
    anterior = ex.existencia_fisica

    if ex.existencia_fisica < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente para entrega")

    ex.existencia_fisica -= cantidad
    ex.cantidad_reservada = max(Decimal("0"), ex.cantidad_reservada - cantidad)

    rep = db.query(Repuesto).filter(Repuesto.id == sol.repuesto_id).first()
    costo = rep.ultimo_costo if rep else None

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=sol.repuesto_id,
        bodega_origen_id=bodega_id,
        tipo_movimiento="ENTREGA_TECNICO",
        cantidad=cantidad,
        costo_unitario=costo,
        costo_total=cantidad * costo if costo else None,
        existencia_anterior=anterior,
        existencia_posterior=ex.existencia_fisica,
        solicitud_id=sol.id,
        usuario_id=usuario.id,
    )
    db.add(mov)
    sol.estado = "ENTREGADO"
    sol.cantidad_entregada = cantidad
    sol.entregado_por = usuario.id
    db.commit()
    return {"ok": True, "estado": "ENTREGADO"}


@router.post("/ot/solicitudes/{solicitud_id}/consumir")
def consumir_solicitud_ot(
    solicitud_id: str,
    cantidad: Decimal = Query(..., gt=0),
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado not in ["ENTREGADO", "DEVUELTO_PARCIAL"]:
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}")

    empresa_id = _validar_empresa(usuario)
    cantidad_entregada = sol.cantidad_entregada or sol.cantidad_aprobada or sol.cantidad_solicitada
    if cantidad > cantidad_entregada:
        raise HTTPException(status_code=400, detail="La cantidad consumida excede la entregada")

    rep = db.query(Repuesto).filter(Repuesto.id == sol.repuesto_id).first()
    costo = rep.ultimo_costo if rep else None

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=sol.repuesto_id,
        tipo_movimiento="CONSUMO",
        cantidad=cantidad,
        costo_unitario=costo,
        costo_total=cantidad * costo if costo else None,
        solicitud_id=sol.id,
        usuario_id=usuario.id,
    )
    db.add(mov)

    sol.estado = "CONSUMIDO"
    if cantidad < cantidad_entregada:
        sol.estado = "DEVUELTO_PARCIAL"
    db.commit()
    return {"ok": True, "estado": sol.estado}


@router.post("/ot/solicitudes/{solicitud_id}/devolver")
def devolver_solicitud_ot(
    solicitud_id: str,
    cantidad: Decimal = Query(..., gt=0),
    bodega_id: str = Query(...),
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    sol = db.query(SolicitudRepuesto).filter(SolicitudRepuesto.id == solicitud_id).first()
    if not sol:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if sol.estado not in ["ENTREGADO", "DEVUELTO_PARCIAL", "CONSUMIDO"]:
        raise HTTPException(status_code=400, detail=f"Solicitud en estado {sol.estado}")

    empresa_id = _validar_empresa(usuario)
    _obtener_bodega(bodega_id, db, usuario)

    ex = _get_or_create_existencia(db, empresa_id, sol.repuesto_id, bodega_id)
    anterior = ex.existencia_fisica
    ex.existencia_fisica += cantidad

    ex_reserva = db.query(Existencia).filter(
        Existencia.empresa_id == empresa_id,
        Existencia.repuesto_id == sol.repuesto_id,
        Existencia.bodega_id == sol.bodega_id,
    ).first()
    if ex_reserva:
        ex_reserva.cantidad_reservada = max(Decimal("0"), ex_reserva.cantidad_reservada - cantidad)

    mov = MovimientoRepuesto(
        empresa_id=empresa_id,
        repuesto_id=sol.repuesto_id,
        bodega_destino_id=bodega_id,
        tipo_movimiento="DEVOLUCION",
        cantidad=cantidad,
        existencia_anterior=anterior,
        existencia_posterior=ex.existencia_fisica,
        solicitud_id=sol.id,
        usuario_id=usuario.id,
    )
    db.add(mov)

    devuelta_anterior = sol.cantidad_devuelta or Decimal("0")
    sol.cantidad_devuelta = devuelta_anterior + cantidad
    sol.estado = "DEVUELTO"
    if cantidad < (sol.cantidad_entregada or sol.cantidad_solicitada):
        sol.estado = "DEVUELTO_PARCIAL"
    db.commit()
    return {"ok": True, "estado": sol.estado}


@router.get("/ot/{mantenimiento_id}/trazabilidad")
def trazabilidad_ot(mantenimiento_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    solicitudes = db.query(SolicitudRepuesto).filter(
        SolicitudRepuesto.mantenimiento_id == mantenimiento_id
    ).all()

    movimientos = []
    for s in solicitudes:
        movs = db.query(MovimientoRepuesto).filter(MovimientoRepuesto.solicitud_id == s.id).order_by(MovimientoRepuesto.created_at).all()
        rep = db.query(Repuesto).filter(Repuesto.id == s.repuesto_id).first()
        for m in movs:
            movimientos.append({
                "fecha": m.created_at.isoformat() if m.created_at else None,
                "tipo": m.tipo_movimiento,
                "repuesto": rep.nombre if rep else "—",
                "cantidad": float(m.cantidad),
                "costo_unitario": float(m.costo_unitario) if m.costo_unitario else None,
                "costo_total": float(m.costo_total) if m.costo_total else None,
                "usuario_id": str(m.usuario_id) if m.usuario_id else None,
                "documento": m.documento,
                "motivo": m.motivo,
            })

    movimientos.sort(key=lambda x: x["fecha"] or "", reverse=True)
    return {"mantenimiento_id": mantenimiento_id, "movimientos": movimientos}


@router.get("/ot/{mantenimiento_id}/costos")
def costos_ot(mantenimiento_id: str, usuario: Usuario = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    solicitudes = db.query(SolicitudRepuesto).filter(
        SolicitudRepuesto.mantenimiento_id == mantenimiento_id,
        SolicitudRepuesto.estado.in_(["CONSUMIDO", "DEVUELTO_PARCIAL", "DEVUELTO"]),
    ).all()

    detalle = []
    costo_total = Decimal("0")
    for s in solicitudes:
        rep = db.query(Repuesto).filter(Repuesto.id == s.repuesto_id).first()
        cantidad_consumida = s.cantidad_entregada or s.cantidad_aprobada or s.cantidad_solicitada
        if s.cantidad_devuelta:
            cantidad_consumida = cantidad_consumida - s.cantidad_devuelta
        costo_unitario = rep.ultimo_costo or Decimal("0")
        costo_linea = cantidad_consumida * costo_unitario
        costo_total += costo_linea

        detalle.append({
            "repuesto": rep.nombre if rep else "—",
            "codigo": rep.codigo if rep else "—",
            "cantidad_consumida": float(cantidad_consumida),
            "costo_unitario": float(costo_unitario),
            "costo_linea": float(costo_linea),
        })

    return {
        "mantenimiento_id": mantenimiento_id,
        "detalle": detalle,
        "costo_total_repuestos": float(costo_total),
    }
