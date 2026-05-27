# ============================================================
# SERVICIO: Logs Inteligentes SaaS PRO
# Archivo: backend/app/services/logs_inteligentes_service.py
# FASE 34.2.5
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_

from app.models.log_sistema import LogSistema

NIVELES_VALIDOS = {"INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"}


def normalizar_nivel(nivel: Optional[str]) -> str:
    nivel_ok = (nivel or "INFO").upper().strip()
    return nivel_ok if nivel_ok in NIVELES_VALIDOS else "INFO"


def crear_log(
    db: Session,
    modulo: str = "sistema",
    nivel: str = "INFO",
    evento: str = "evento",
    mensaje: Optional[str] = None,
    usuario: Optional[str] = None,
    ip: Optional[str] = None,
    metodo: Optional[str] = None,
    ruta: Optional[str] = None,
    metadata_json: Optional[dict] = None,
) -> LogSistema:
    """Crea un log sin afectar el flujo principal del sistema."""
    log = LogSistema(
        modulo=(modulo or "sistema")[:80],
        nivel=normalizar_nivel(nivel),
        evento=(evento or "evento")[:160],
        mensaje=mensaje,
        usuario=usuario,
        ip=ip,
        metodo=metodo,
        ruta=ruta,
        metadata_json=metadata_json or {},
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def listar_logs(
    db: Session,
    modulo: Optional[str] = None,
    nivel: Optional[str] = None,
    texto: Optional[str] = None,
    limite: int = 100,
):
    limite = min(max(int(limite or 100), 1), 500)
    query = db.query(LogSistema)

    if modulo:
        query = query.filter(LogSistema.modulo.ilike(f"%{modulo}%"))

    if nivel:
        query = query.filter(LogSistema.nivel == normalizar_nivel(nivel))

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                LogSistema.evento.ilike(patron),
                LogSistema.mensaje.ilike(patron),
                LogSistema.ruta.ilike(patron),
                LogSistema.usuario.ilike(patron),
            )
        )

    return query.order_by(desc(LogSistema.creado_en)).limit(limite).all()


def resumen_logs(db: Session) -> dict:
    total = db.query(func.count(LogSistema.id)).scalar() or 0

    def count_nivel(nivel: str) -> int:
        return db.query(func.count(LogSistema.id)).filter(LogSistema.nivel == nivel).scalar() or 0

    modulos_rows = db.query(LogSistema.modulo).distinct().order_by(LogSistema.modulo.asc()).all()
    modulos = [m[0] for m in modulos_rows if m and m[0]]

    return {
        "total": total,
        "info": count_nivel("INFO"),
        "warning": count_nivel("WARNING"),
        "error": count_nivel("ERROR"),
        "critical": count_nivel("CRITICAL"),
        "modulos": modulos,
    }


def limpiar_logs_antiguos(db: Session, dias: int = 30) -> dict:
    dias = max(int(dias or 30), 1)
    limite = datetime.now(timezone.utc) - timedelta(days=dias)
    eliminados = db.query(LogSistema).filter(LogSistema.creado_en < limite).delete()
    db.commit()
    return {"ok": True, "eliminados": eliminados, "dias_retencion": dias}


def crear_logs_demo(db: Session) -> dict:
    ejemplos = [
        ("sistema", "INFO", "Sistema operativo", "Logs inteligentes inicializados correctamente."),
        ("automatizacion", "INFO", "Scheduler", "Scheduler SaaS PRO activo y listo."),
        ("backups", "INFO", "Backups", "Módulo de backups disponible."),
        ("monitor", "WARNING", "Observabilidad", "Monitoreo VPS y PostgreSQL activo."),
    ]
    for modulo, nivel, evento, mensaje in ejemplos:
        crear_log(db, modulo=modulo, nivel=nivel, evento=evento, mensaje=mensaje)
    return {"ok": True, "creados": len(ejemplos)}
