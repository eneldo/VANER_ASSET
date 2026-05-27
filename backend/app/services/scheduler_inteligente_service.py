# ============================================================
# SERVICIO - SCHEDULER INTELIGENTE PRO
# Archivo: backend/app/services/scheduler_inteligente_service.py
# Fase 34.2.7
# ============================================================

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.scheduler_inteligente import SchedulerLog, SchedulerRegla, SchedulerSugerencia

try:
    from app.models.mantenimiento import Mantenimiento
except Exception:  # pragma: no cover
    Mantenimiento = None


MODOS_VALIDOS = {"MANUAL", "SEMIAUTOMATICO", "AUTOMATICO"}


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def registrar_log(db: Session, nivel: str, evento: str, mensaje: str, metadata: Optional[dict] = None) -> None:
    log = SchedulerLog(
        nivel=nivel,
        evento=evento,
        mensaje=mensaje,
        metadata_json=metadata or {},
    )
    db.add(log)
    db.commit()


def calcular_proxima_fecha(fecha_base: date, frecuencia_dias: int) -> date:
    return fecha_base + timedelta(days=max(int(frecuencia_dias or 1), 1))


def listar_reglas(db: Session) -> list[SchedulerRegla]:
    return db.query(SchedulerRegla).order_by(SchedulerRegla.activo.desc(), SchedulerRegla.nombre.asc()).all()


def crear_regla(db: Session, data) -> SchedulerRegla:
    modo = str(data.modo or "SEMIAUTOMATICO").upper()
    if modo not in MODOS_VALIDOS:
        modo = "SEMIAUTOMATICO"

    proxima = data.proxima_fecha or data.fecha_inicio

    regla = SchedulerRegla(
        nombre=data.nombre,
        descripcion=data.descripcion,
        equipo_id=data.equipo_id,
        tecnico_id=data.tecnico_id,
        tipo_mantenimiento=str(data.tipo_mantenimiento or "PREVENTIVO").upper(),
        frecuencia_dias=data.frecuencia_dias,
        fecha_inicio=data.fecha_inicio,
        proxima_fecha=proxima,
        prioridad=str(data.prioridad or "MEDIA").upper(),
        estado_inicial=str(data.estado_inicial or "PROGRAMADO").upper(),
        modo=modo,
        activo=data.activo,
        configuracion=data.configuracion or {},
    )
    db.add(regla)
    db.commit()
    db.refresh(regla)

    registrar_log(db, "INFO", "REGLA_CREADA", f"Regla creada: {regla.nombre}", {"regla_id": str(regla.id)})
    return regla


def actualizar_regla(db: Session, regla_id: UUID, data) -> Optional[SchedulerRegla]:
    regla = db.query(SchedulerRegla).filter(SchedulerRegla.id == regla_id).first()
    if not regla:
        return None

    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        if key == "modo" and value:
            value = str(value).upper()
            if value not in MODOS_VALIDOS:
                value = "SEMIAUTOMATICO"
        elif key in {"tipo_mantenimiento", "prioridad", "estado_inicial"} and value:
            value = str(value).upper()
        setattr(regla, key, value)

    regla.actualizado_en = _now()
    db.commit()
    db.refresh(regla)
    registrar_log(db, "INFO", "REGLA_ACTUALIZADA", f"Regla actualizada: {regla.nombre}", {"regla_id": str(regla.id)})
    return regla


def eliminar_regla(db: Session, regla_id: UUID) -> bool:
    regla = db.query(SchedulerRegla).filter(SchedulerRegla.id == regla_id).first()
    if not regla:
        return False
    db.delete(regla)
    db.commit()
    registrar_log(db, "WARNING", "REGLA_ELIMINADA", f"Regla eliminada: {regla.nombre}", {"regla_id": str(regla_id)})
    return True


def listar_sugerencias(db: Session, estado: Optional[str] = None) -> list[SchedulerSugerencia]:
    q = db.query(SchedulerSugerencia)
    if estado:
        q = q.filter(SchedulerSugerencia.estado == estado.upper())
    return q.order_by(SchedulerSugerencia.fecha_programada.asc(), SchedulerSugerencia.creado_en.desc()).all()


def _existe_sugerencia(db: Session, regla: SchedulerRegla, fecha_programada: date) -> bool:
    return (
        db.query(SchedulerSugerencia)
        .filter(
            SchedulerSugerencia.regla_id == regla.id,
            SchedulerSugerencia.fecha_programada == fecha_programada,
            SchedulerSugerencia.estado.in_(["PENDIENTE", "GENERADA", "APROBADA"]),
        )
        .first()
        is not None
    )


def crear_sugerencia(db: Session, regla: SchedulerRegla) -> Optional[SchedulerSugerencia]:
    fecha_programada = regla.proxima_fecha or regla.fecha_inicio
    if _existe_sugerencia(db, regla, fecha_programada):
        return None

    sugerencia = SchedulerSugerencia(
        regla_id=regla.id,
        equipo_id=regla.equipo_id,
        tecnico_id=regla.tecnico_id,
        tipo_mantenimiento=regla.tipo_mantenimiento,
        fecha_programada=fecha_programada,
        prioridad=regla.prioridad,
        estado="PENDIENTE",
        mensaje=f"Sugerencia generada automáticamente por regla: {regla.nombre}",
    )
    db.add(sugerencia)
    regla.ultima_ejecucion = _now()
    regla.proxima_fecha = calcular_proxima_fecha(fecha_programada, regla.frecuencia_dias)
    db.commit()
    db.refresh(sugerencia)
    return sugerencia


def crear_mantenimiento_desde_regla(db: Session, regla: SchedulerRegla) -> Optional[int]:
    if Mantenimiento is None:
        registrar_log(db, "ERROR", "MODELO_MANTENIMIENTO_NO_DISPONIBLE", "No fue posible importar el modelo Mantenimiento")
        return None

    fecha_programada = regla.proxima_fecha or regla.fecha_inicio

    # Se usan solo campos comunes para evitar romper modelos existentes.
    mantenimiento = Mantenimiento(
        equipo_id=regla.equipo_id,
        tecnico_id=regla.tecnico_id,
        tipo=regla.tipo_mantenimiento,
        estado=regla.estado_inicial,
        fecha_programada=fecha_programada,
        observaciones=f"Generado automáticamente por Scheduler Inteligente: {regla.nombre}",
    )

    db.add(mantenimiento)
    db.flush()

    regla.ultimo_mantenimiento_id = mantenimiento.id
    regla.ultima_ejecucion = _now()
    regla.proxima_fecha = calcular_proxima_fecha(fecha_programada, regla.frecuencia_dias)

    db.commit()
    return mantenimiento.id


def aprobar_sugerencia(db: Session, sugerencia_id: UUID) -> Optional[SchedulerSugerencia]:
    sugerencia = db.query(SchedulerSugerencia).filter(SchedulerSugerencia.id == sugerencia_id).first()
    if not sugerencia or sugerencia.estado not in {"PENDIENTE", "APROBADA"}:
        return sugerencia

    if Mantenimiento is None:
        sugerencia.estado = "APROBADA"
        sugerencia.mensaje = "Aprobada, pero no se pudo crear mantenimiento: modelo no disponible."
        db.commit()
        return sugerencia

    mantenimiento = Mantenimiento(
        equipo_id=sugerencia.equipo_id,
        tecnico_id=sugerencia.tecnico_id,
        tipo=sugerencia.tipo_mantenimiento,
        estado="PROGRAMADO",
        fecha_programada=sugerencia.fecha_programada,
        observaciones=f"Generado desde sugerencia Scheduler Inteligente: {sugerencia.id}",
    )
    db.add(mantenimiento)
    db.flush()

    sugerencia.estado = "GENERADA"
    sugerencia.mantenimiento_id = mantenimiento.id
    sugerencia.mensaje = "Mantenimiento generado desde sugerencia aprobada."
    db.commit()
    db.refresh(sugerencia)

    registrar_log(db, "INFO", "SUGERENCIA_APROBADA", "Sugerencia aprobada y mantenimiento generado", {"sugerencia_id": str(sugerencia.id), "mantenimiento_id": mantenimiento.id})
    return sugerencia


def rechazar_sugerencia(db: Session, sugerencia_id: UUID) -> Optional[SchedulerSugerencia]:
    sugerencia = db.query(SchedulerSugerencia).filter(SchedulerSugerencia.id == sugerencia_id).first()
    if not sugerencia:
        return None
    sugerencia.estado = "RECHAZADA"
    sugerencia.mensaje = "Sugerencia rechazada manualmente."
    db.commit()
    db.refresh(sugerencia)
    registrar_log(db, "WARNING", "SUGERENCIA_RECHAZADA", "Sugerencia rechazada", {"sugerencia_id": str(sugerencia.id)})
    return sugerencia


def ejecutar_revision(db: Session) -> dict:
    hoy = _today()
    reglas: Iterable[SchedulerRegla] = (
        db.query(SchedulerRegla)
        .filter(SchedulerRegla.activo == True)  # noqa: E712
        .all()
    )

    revisadas = 0
    sugerencias = 0
    mantenimientos = 0

    for regla in reglas:
        revisadas += 1
        fecha = regla.proxima_fecha or regla.fecha_inicio
        if fecha > hoy:
            continue

        modo = str(regla.modo or "SEMIAUTOMATICO").upper()

        if modo == "MANUAL":
            regla.ultima_ejecucion = _now()
            continue

        if modo == "SEMIAUTOMATICO":
            sug = crear_sugerencia(db, regla)
            if sug:
                sugerencias += 1
            continue

        if modo == "AUTOMATICO":
            mid = crear_mantenimiento_desde_regla(db, regla)
            if mid:
                mantenimientos += 1
            continue

    registrar_log(
        db,
        "INFO",
        "REVISION_EJECUTADA",
        "Revisión Scheduler Inteligente ejecutada.",
        {"reglas": revisadas, "sugerencias": sugerencias, "mantenimientos": mantenimientos},
    )

    return {
        "ok": True,
        "mensaje": "Revisión ejecutada correctamente",
        "reglas_revisadas": revisadas,
        "sugerencias_creadas": sugerencias,
        "mantenimientos_creados": mantenimientos,
    }


def dashboard_scheduler(db: Session) -> dict:
    total_reglas = db.query(SchedulerRegla).count()
    activas = db.query(SchedulerRegla).filter(SchedulerRegla.activo == True).count()  # noqa: E712
    pendientes = db.query(SchedulerSugerencia).filter(SchedulerSugerencia.estado == "PENDIENTE").count()
    generadas = db.query(SchedulerSugerencia).filter(SchedulerSugerencia.estado == "GENERADA").count()
    logs = db.query(SchedulerLog).count()

    proximas = (
        db.query(SchedulerRegla)
        .filter(SchedulerRegla.activo == True)  # noqa: E712
        .order_by(SchedulerRegla.proxima_fecha.asc())
        .limit(8)
        .all()
    )

    return {
        "total_reglas": total_reglas,
        "reglas_activas": activas,
        "sugerencias_pendientes": pendientes,
        "sugerencias_generadas": generadas,
        "total_logs": logs,
        "proximas_reglas": [
            {
                "id": str(r.id),
                "nombre": r.nombre,
                "modo": r.modo,
                "proxima_fecha": r.proxima_fecha.isoformat() if r.proxima_fecha else None,
                "frecuencia_dias": r.frecuencia_dias,
            }
            for r in proximas
        ],
    }
