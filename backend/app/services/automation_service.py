# ============================================================
# SERVICIO: Automatización SaaS PRO
# Archivo: backend/app/services/automation_service.py
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models.automatizacion import Automatizacion, AutomatizacionLog


DEFAULT_AUTOMATIZACIONES = [
    {
        "modulo": "backups",
        "nombre": "Backups automáticos",
        "descripcion": "Motor base para backups ZIP, PostgreSQL y evidencias. En 34.2.2 se activa ejecución real.",
        "activo": False,
        "frecuencia_minutos": 1440,
        "configuracion": {"hora": "02:00", "retencion_dias": 15},
    },
    {
        "modulo": "smtp",
        "nombre": "Correos automáticos SMTP",
        "descripcion": "Base para envío automático de correos corporativos y alertas.",
        "activo": False,
        "frecuencia_minutos": 30,
        "configuracion": {"modo": "cola", "plantillas_html": True},
    },
    {
        "modulo": "whatsapp",
        "nombre": "WhatsApp automático",
        "descripcion": "Base preparada para Twilio, Meta Cloud API o proveedor externo.",
        "activo": False,
        "frecuencia_minutos": 30,
        "configuracion": {"proveedor": "pendiente"},
    },
    {
        "modulo": "monitor",
        "nombre": "Monitor sistema",
        "descripcion": "Monitoreo de CPU, RAM, disco y estado básico del servidor.",
        "activo": True,
        "frecuencia_minutos": 5,
        "configuracion": {"alerta_disco_pct": 85, "alerta_ram_pct": 90},
    },
    {
        "modulo": "mantenimientos",
        "nombre": "Automatización mantenimientos",
        "descripcion": "Base para detectar mantenimientos vencidos, recordatorios y escalamiento.",
        "activo": False,
        "frecuencia_minutos": 60,
        "configuracion": {"recordar_horas_antes": 24},
    },
    {
        "modulo": "limpieza_logs",
        "nombre": "Limpieza automática de logs",
        "descripcion": "Base para limpiar logs antiguos de automatización.",
        "activo": False,
        "frecuencia_minutos": 1440,
        "configuracion": {"retencion_dias": 30},
    },
    {
        "modulo": "devops",
        "nombre": "Centro DevOps SaaS",
        "descripcion": "Base para dashboard DevOps y estado de servicios.",
        "activo": True,
        "frecuencia_minutos": 10,
        "configuracion": {"healthcheck": True},
    },
]


def crear_tablas_automatizacion_si_faltan() -> None:
    """Crea solo las tablas de esta fase si no existen."""

    Base.metadata.create_all(
        bind=engine,
        tables=[Automatizacion.__table__, AutomatizacionLog.__table__],
        checkfirst=True,
    )


def inicializar_automatizaciones(db: Session) -> List[Automatizacion]:
    """Inserta configuraciones por defecto sin duplicar registros."""

    crear_tablas_automatizacion_si_faltan()

    creadas = []
    for item in DEFAULT_AUTOMATIZACIONES:
        existente = db.query(Automatizacion).filter(Automatizacion.modulo == item["modulo"]).first()
        if existente:
            continue
        registro = Automatizacion(
            modulo=item["modulo"],
            nombre=item["nombre"],
            descripcion=item["descripcion"],
            activo=item["activo"],
            frecuencia_minutos=item["frecuencia_minutos"],
            estado="ACTIVO" if item["activo"] else "INACTIVO",
            mensaje="Configuración inicial Fase 34.2.1",
            configuracion=item.get("configuracion") or {},
            proxima_ejecucion=datetime.now(timezone.utc) + timedelta(minutes=item["frecuencia_minutos"]),
        )
        db.add(registro)
        creadas.append(registro)

    db.commit()
    return listar_automatizaciones(db)


def listar_automatizaciones(db: Session) -> List[Automatizacion]:
    crear_tablas_automatizacion_si_faltan()
    return db.query(Automatizacion).order_by(Automatizacion.nombre.asc()).all()


def obtener_automatizacion(db: Session, modulo: str) -> Optional[Automatizacion]:
    crear_tablas_automatizacion_si_faltan()
    return db.query(Automatizacion).filter(Automatizacion.modulo == modulo).first()


def actualizar_automatizacion(db: Session, modulo: str, data: Dict) -> Optional[Automatizacion]:
    registro = obtener_automatizacion(db, modulo)
    if not registro:
        return None

    for campo in ["nombre", "descripcion", "activo", "frecuencia_minutos", "configuracion"]:
        if campo in data and data[campo] is not None:
            setattr(registro, campo, data[campo])

    registro.estado = "ACTIVO" if registro.activo else "INACTIVO"
    registro.mensaje = "Actualizado desde UI SaaS PRO"

    if registro.activo:
        registro.proxima_ejecucion = datetime.now(timezone.utc) + timedelta(minutes=registro.frecuencia_minutos)
    else:
        registro.proxima_ejecucion = None

    db.commit()
    db.refresh(registro)
    return registro


def registrar_ejecucion(db: Session, modulo: str, ok: bool, mensaje: str, duracion_ms: int = 0) -> None:
    registro = obtener_automatizacion(db, modulo)
    if not registro:
        return

    ahora = datetime.now(timezone.utc)
    registro.ultima_ejecucion = ahora
    registro.proxima_ejecucion = ahora + timedelta(minutes=registro.frecuencia_minutos)
    registro.estado = "OK" if ok else "ERROR"
    registro.mensaje = mensaje

    db.add(AutomatizacionLog(
        automatizacion_id=registro.id,
        modulo=modulo,
        nivel="INFO" if ok else "ERROR",
        evento="EJECUCION_JOB",
        mensaje=mensaje,
        duracion_ms=duracion_ms,
        metadata_json={"fase": "34.2.1"},
    ))
    db.commit()


def listar_logs(db: Session, limite: int = 100) -> List[AutomatizacionLog]:
    crear_tablas_automatizacion_si_faltan()
    return (
        db.query(AutomatizacionLog)
        .order_by(AutomatizacionLog.creado_en.desc())
        .limit(min(max(limite, 1), 500))
        .all()
    )
