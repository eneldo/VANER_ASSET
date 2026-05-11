# ============================================================
# ROUTER: Notificaciones PRO
# Archivo: backend/app/routers/notificaciones.py
# Fase 29 - Notificaciones y Alertas PRO
# ============================================================
# Endpoints principales:
#   GET    /notificaciones/                 -> listar con filtros
#   GET    /notificaciones/resumen          -> KPIs de notificaciones
#   POST   /notificaciones/                 -> crear notificación manual
#   PUT    /notificaciones/{id}/leer        -> marcar una como leída
#   PUT    /notificaciones/leer-todas       -> marcar todas como leídas
#   POST   /notificaciones/generar-alertas  -> crear alertas automáticas
#   DELETE /notificaciones/{id}             -> eliminar una notificación
# ============================================================

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notificacion import Notificacion
from app.models.mantenimiento import Mantenimiento
from app.models.equipo import Equipo
from app.schemas.notificacion_schema import (
    NotificacionCreate,
    NotificacionOut,
    NotificacionResumen,
)

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones PRO"])


# ============================================================
# HELPERS INTERNOS
# ============================================================

def _normalizar_texto(valor: Optional[str]) -> Optional[str]:
    """Limpia strings vacíos para evitar filtros inválidos."""
    if valor is None:
        return None
    valor = str(valor).strip()
    return valor or None


def _existe_notificacion(db: Session, titulo: str, mantenimiento_id: Optional[int], rol_destino: str) -> bool:
    """
    Evita duplicar alertas automáticas para el mismo mantenimiento.
    Se usa en el generador automático de alertas.
    """
    consulta = db.query(Notificacion).filter(
        Notificacion.titulo == titulo,
        Notificacion.rol_destino == rol_destino,
        Notificacion.mantenimiento_id == mantenimiento_id,
    )
    return db.query(consulta.exists()).scalar()


def _crear_notificacion_si_no_existe(
    db: Session,
    *,
    titulo: str,
    mensaje: str,
    rol_destino: str,
    tipo: str,
    prioridad: str,
    enlace: Optional[str] = None,
    empresa_id: Optional[int] = None,
    sede_id: Optional[int] = None,
    equipo_id: Optional[int] = None,
    mantenimiento_id: Optional[int] = None,
    tecnico_id: Optional[int] = None,
):
    """Crea una notificación automática sin duplicarla."""
    if _existe_notificacion(db, titulo, mantenimiento_id, rol_destino):
        return None

    notificacion = Notificacion(
        rol_destino=rol_destino,
        tipo=tipo,
        prioridad=prioridad,
        titulo=titulo,
        mensaje=mensaje,
        enlace=enlace,
        empresa_id=empresa_id,
        sede_id=sede_id,
        equipo_id=equipo_id,
        mantenimiento_id=mantenimiento_id,
        tecnico_id=tecnico_id,
    )
    db.add(notificacion)
    return notificacion


# ============================================================
# LISTAR NOTIFICACIONES
# ============================================================

@router.get("/", response_model=list[NotificacionOut])
def listar_notificaciones(
    rol_destino: Optional[str] = Query(None, description="ADMIN, COORDINADOR, TECNICO, EMPRESA o CLIENTE"),
    empresa_id: Optional[int] = Query(None),
    tecnico_id: Optional[int] = Query(None),
    leida: Optional[bool] = Query(None),
    prioridad: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    limite: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Lista notificaciones con filtros.

    Uso recomendado:
    - Admin:      /notificaciones?rol_destino=ADMIN
    - Cliente:    /notificaciones?rol_destino=EMPRESA&empresa_id=1
    - Técnico:    /notificaciones?rol_destino=TECNICO&tecnico_id=1
    """
    query = db.query(Notificacion)

    rol_destino = _normalizar_texto(rol_destino)
    prioridad = _normalizar_texto(prioridad)
    tipo = _normalizar_texto(tipo)

    if rol_destino:
        query = query.filter(Notificacion.rol_destino == rol_destino.upper())
    if empresa_id is not None:
        query = query.filter(Notificacion.empresa_id == empresa_id)
    if tecnico_id is not None:
        query = query.filter(Notificacion.tecnico_id == tecnico_id)
    if leida is not None:
        query = query.filter(Notificacion.leida == leida)
    if prioridad:
        query = query.filter(Notificacion.prioridad == prioridad.upper())
    if tipo:
        query = query.filter(Notificacion.tipo == tipo.upper())

    return query.order_by(Notificacion.creado_en.desc()).limit(limite).all()


# ============================================================
# RESUMEN KPI
# ============================================================

@router.get("/resumen", response_model=NotificacionResumen)
def resumen_notificaciones(
    rol_destino: Optional[str] = Query(None),
    empresa_id: Optional[int] = Query(None),
    tecnico_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Devuelve contadores rápidos para dashboard/campana."""
    query = db.query(Notificacion)

    if rol_destino:
        query = query.filter(Notificacion.rol_destino == rol_destino.upper())
    if empresa_id is not None:
        query = query.filter(Notificacion.empresa_id == empresa_id)
    if tecnico_id is not None:
        query = query.filter(Notificacion.tecnico_id == tecnico_id)

    total = query.count()
    no_leidas = query.filter(Notificacion.leida == False).count()  # noqa: E712
    alta = query.filter(Notificacion.prioridad == "ALTA").count()
    media = query.filter(Notificacion.prioridad == "MEDIA").count()
    baja = query.filter(Notificacion.prioridad == "BAJA").count()

    return NotificacionResumen(
        total=total,
        no_leidas=no_leidas,
        alta=alta,
        media=media,
        baja=baja,
    )


# ============================================================
# CREAR NOTIFICACIÓN MANUAL
# ============================================================

@router.post("/", response_model=NotificacionOut)
def crear_notificacion(payload: NotificacionCreate, db: Session = Depends(get_db)):
    """Crea una notificación manual desde administración o desde otro módulo."""
    nueva = Notificacion(**payload.model_dump())
    nueva.rol_destino = nueva.rol_destino.upper()
    nueva.tipo = nueva.tipo.upper()
    nueva.prioridad = nueva.prioridad.upper()

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# ============================================================
# MARCAR COMO LEÍDA
# ============================================================

@router.put("/{notificacion_id}/leer", response_model=NotificacionOut)
def marcar_como_leida(notificacion_id: int, db: Session = Depends(get_db)):
    """Marca una notificación como leída."""
    notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    notificacion.leida = True
    notificacion.leido_en = datetime.utcnow()
    db.commit()
    db.refresh(notificacion)
    return notificacion


@router.put("/leer-todas")
def marcar_todas_como_leidas(
    rol_destino: Optional[str] = Query(None),
    empresa_id: Optional[int] = Query(None),
    tecnico_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Marca como leídas todas las notificaciones filtradas."""
    query = db.query(Notificacion).filter(Notificacion.leida == False)  # noqa: E712

    if rol_destino:
        query = query.filter(Notificacion.rol_destino == rol_destino.upper())
    if empresa_id is not None:
        query = query.filter(Notificacion.empresa_id == empresa_id)
    if tecnico_id is not None:
        query = query.filter(Notificacion.tecnico_id == tecnico_id)

    total = query.update({
        Notificacion.leida: True,
        Notificacion.leido_en: datetime.utcnow(),
    }, synchronize_session=False)

    db.commit()
    return {"ok": True, "actualizadas": total}


# ============================================================
# GENERADOR DE ALERTAS AUTOMÁTICAS
# ============================================================

@router.post("/generar-alertas")
def generar_alertas_automaticas(db: Session = Depends(get_db)):
    """
    Genera alertas según reglas operativas.

    Reglas incluidas:
    1. Mantenimientos vencidos: fecha_programada anterior a hoy y no finalizados/anulados.
    2. Mantenimientos próximos: fecha_programada dentro de los próximos 7 días.
    3. Equipos fuera de servicio o críticos, si existen esos campos en equipos.

    Este endpoint se puede ejecutar manualmente desde el panel de notificaciones.
    Más adelante puede programarse con APScheduler/Celery si se desea.
    """
    hoy = date.today()
    proxima_semana = hoy + timedelta(days=7)
    estados_cerrados = ["FINALIZADO", "ANULADO"]
    creadas = 0

    # --------------------------------------------------------
    # 1) Mantenimientos vencidos
    # --------------------------------------------------------
    vencidos = db.query(Mantenimiento).filter(
        Mantenimiento.fecha_programada < hoy,
        ~Mantenimiento.estado.in_(estados_cerrados),
    ).all()

    for mant in vencidos:
        equipo = getattr(mant, "equipo", None)
        titulo = f"Mantenimiento vencido #{mant.id}"
        mensaje = (
            f"El mantenimiento {mant.tipo} programado para {mant.fecha_programada} "
            f"se encuentra en estado {mant.estado}."
        )

        notif_admin = _crear_notificacion_si_no_existe(
            db,
            titulo=titulo,
            mensaje=mensaje,
            rol_destino="ADMIN",
            tipo="MANTENIMIENTO_VENCIDO",
            prioridad="ALTA",
            enlace="/admin/mantenimientos",
            empresa_id=getattr(equipo, "empresa_id", None),
            sede_id=getattr(equipo, "sede_id", None),
            equipo_id=mant.equipo_id,
            mantenimiento_id=mant.id,
            tecnico_id=mant.tecnico_id,
        )
        if notif_admin:
            creadas += 1

        # Copia para técnico asignado si existe.
        if mant.tecnico_id:
            notif_tec = _crear_notificacion_si_no_existe(
                db,
                titulo=titulo,
                mensaje=mensaje,
                rol_destino="TECNICO",
                tipo="MANTENIMIENTO_VENCIDO",
                prioridad="ALTA",
                enlace="/tecnico",
                empresa_id=getattr(equipo, "empresa_id", None),
                sede_id=getattr(equipo, "sede_id", None),
                equipo_id=mant.equipo_id,
                mantenimiento_id=mant.id,
                tecnico_id=mant.tecnico_id,
            )
            if notif_tec:
                creadas += 1

    # --------------------------------------------------------
    # 2) Mantenimientos próximos
    # --------------------------------------------------------
    proximos = db.query(Mantenimiento).filter(
        and_(
            Mantenimiento.fecha_programada >= hoy,
            Mantenimiento.fecha_programada <= proxima_semana,
            ~Mantenimiento.estado.in_(estados_cerrados),
        )
    ).all()

    for mant in proximos:
        equipo = getattr(mant, "equipo", None)
        titulo = f"Mantenimiento próximo #{mant.id}"
        mensaje = (
            f"El mantenimiento {mant.tipo} está programado para {mant.fecha_programada}. "
            "Revise técnico asignado, equipo y sede."
        )

        notif_admin = _crear_notificacion_si_no_existe(
            db,
            titulo=titulo,
            mensaje=mensaje,
            rol_destino="ADMIN",
            tipo="MANTENIMIENTO_PROXIMO",
            prioridad="MEDIA",
            enlace="/admin/mantenimientos",
            empresa_id=getattr(equipo, "empresa_id", None),
            sede_id=getattr(equipo, "sede_id", None),
            equipo_id=mant.equipo_id,
            mantenimiento_id=mant.id,
            tecnico_id=mant.tecnico_id,
        )
        if notif_admin:
            creadas += 1

    # --------------------------------------------------------
    # 3) Equipos críticos o fuera de servicio
    # --------------------------------------------------------
    # El proyecto ha usado campos como estado y criticidad en equipos.
    # Para mantener compatibilidad, se usan getattr y filtros simples.
    try:
        equipos_alerta = db.query(Equipo).filter(
            or_(
                Equipo.estado == "FUERA_DE_SERVICIO",
                Equipo.estado == "Fuera de servicio",
                Equipo.criticidad == "ALTA",
                Equipo.criticidad == "Alta",
            )
        ).all()

        for equipo in equipos_alerta:
            titulo = f"Equipo crítico o fuera de servicio #{equipo.id}"
            mensaje = (
                f"El equipo {getattr(equipo, 'nombre', 'Sin nombre')} requiere revisión. "
                f"Estado: {getattr(equipo, 'estado', 'N/A')} - "
                f"Criticidad: {getattr(equipo, 'criticidad', 'N/A')}."
            )

            notif_admin = _crear_notificacion_si_no_existe(
                db,
                titulo=titulo,
                mensaje=mensaje,
                rol_destino="ADMIN",
                tipo="EQUIPO_CRITICO",
                prioridad="ALTA",
                enlace="/admin/equipos",
                empresa_id=getattr(equipo, "empresa_id", None),
                sede_id=getattr(equipo, "sede_id", None),
                equipo_id=equipo.id,
                mantenimiento_id=None,
                tecnico_id=None,
            )
            if notif_admin:
                creadas += 1
    except Exception:
        # Si la tabla equipos no tiene alguno de esos campos en una versión local,
        # no se rompe el generador; simplemente omite esta regla.
        pass

    db.commit()

    return {
        "ok": True,
        "mensaje": "Alertas automáticas generadas correctamente",
        "creadas": creadas,
        "fecha_revision": str(hoy),
    }


# ============================================================
# ELIMINAR NOTIFICACIÓN
# ============================================================

@router.delete("/{notificacion_id}")
def eliminar_notificacion(notificacion_id: int, db: Session = Depends(get_db)):
    """Elimina una notificación individual."""
    notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    db.delete(notificacion)
    db.commit()
    return {"ok": True, "mensaje": "Notificación eliminada correctamente"}
