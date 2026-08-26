import time
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from app.database import SessionLocal
from app.models.equipo import Equipo
from app.models.equipo_hoja_vida import EquipoHojaVida
from app.routers.equipos import _agregar_historial
from app.services.automation_service import registrar_ejecucion


def obtener_fecha_base_vida_util(equipo, hoja_vida=None):
    fecha = None
    if hoja_vida is not None:
        fecha = hoja_vida.fecha_instalacion or hoja_vida.fecha_compra
    fecha = fecha or equipo.created_at
    if isinstance(fecha, datetime):
        return fecha
    if isinstance(fecha, date):
        return datetime.combine(fecha, datetime.min.time())
    return None


def procesar_vida_util(equipos_con_hoja, ahora=None):
    ahora = ahora or datetime.utcnow()
    actualizados = 0
    for equipo, hoja_vida in equipos_con_hoja:
        fecha_base = obtener_fecha_base_vida_util(equipo, hoja_vida)
        if not fecha_base or not equipo.vida_util_meses:
            continue
        if ahora < fecha_base + relativedelta(months=equipo.vida_util_meses):
            continue
        if equipo.estado == "FUERA_DE_SERVICIO":
            continue
        estado_anterior = equipo.estado
        equipo.estado = "FUERA_DE_SERVICIO"
        equipo.activo = True
        _agregar_historial(
            equipo,
            "estado",
            estado_anterior,
            equipo.estado,
            "system_vida_util",
            "VIDA_UTIL_VENCIDA",
            f"Vida útil de {equipo.vida_util_meses} meses vencida (fecha base: {fecha_base.strftime('%Y-%m-%d')})",
            ahora,
        )
        actualizados += 1
    return actualizados


def ejecutar_vida_util_job() -> None:
    inicio = time.perf_counter()
    db = SessionLocal()
    try:
        equipos = (
            db.query(Equipo, EquipoHojaVida)
            .outerjoin(EquipoHojaVida, EquipoHojaVida.equipo_id == Equipo.id)
            .filter(
                Equipo.vida_util_meses.isnot(None),
                Equipo.estado.in_(["OPERATIVO", "EN_MANTENIMIENTO"]),
                Equipo.activo.is_(True),
            )
            .all()
        )
        actualizados = procesar_vida_util(equipos)
        db.commit()
        registrar_ejecucion(
            db=db,
            modulo="vida_util",
            ok=True,
            mensaje=f"Revisión vida útil completada. Equipos actualizados: {actualizados}",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    except Exception as exc:
        db.rollback()
        try:
            registrar_ejecucion(
                db=db,
                modulo="vida_util",
                ok=False,
                mensaje=f"Error job vida_util: {exc}",
                duracion_ms=int((time.perf_counter() - inicio) * 1000),
            )
        except Exception:
            db.rollback()
    finally:
        db.close()
