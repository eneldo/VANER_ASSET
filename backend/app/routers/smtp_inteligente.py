# ============================================================
# ROUTER: SMTP Inteligente SaaS PRO
# Archivo: backend/app/routers/smtp_inteligente.py
# FASE 34.2.3
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.smtp_log import SMTPLog
from app.schemas.smtp_inteligente import (
    SMTPLogOut,
    SMTPManualRequest,
    SMTPStatusOut,
    SMTPTestRequest,
)
from app.services.smtp_inteligente_service import (
    crear_plantillas_disponibles,
    enviar_correo_smtp,
    obtener_estado_smtp,
    render_template_base,
)

router = APIRouter(
    prefix="/smtp-inteligente",
    tags=["SMTP Inteligente SaaS PRO"],
)


@router.post("/inicializar")
def inicializar_smtp_inteligente():
    """Compatibilidad: el esquema se administra exclusivamente con Alembic."""
    return {"ok": True, "mensaje": "Esquema SMTP administrado por Alembic"}


@router.get("/estado", response_model=SMTPStatusOut)
def estado_smtp(db: Session = Depends(get_db)):
    return obtener_estado_smtp(db)


@router.get("/plantillas")
def plantillas_smtp():
    return crear_plantillas_disponibles()


@router.post("/probar", response_model=SMTPLogOut)
def probar_smtp(payload: SMTPTestRequest, db: Session = Depends(get_db)):
    html = render_template_base(
        "Prueba SMTP SGA SaaS PRO",
        f"<p>{payload.mensaje}</p><p>Si recibes este correo, la configuración SMTP está funcionando correctamente.</p>",
        "Validación SMTP corporativa",
    )
    return enviar_correo_smtp(
        db=db,
        destinatario=str(payload.destinatario),
        asunto=payload.asunto,
        mensaje=payload.mensaje,
        plantilla="prueba",
        metadata={"tipo": "prueba_smtp"},
        html=html,
    )


@router.post("/enviar", response_model=SMTPLogOut)
def enviar_manual(payload: SMTPManualRequest, db: Session = Depends(get_db)):
    return enviar_correo_smtp(
        db=db,
        destinatario=str(payload.destinatario),
        asunto=payload.asunto,
        mensaje=payload.mensaje,
        plantilla=payload.plantilla or "manual",
        metadata=payload.metadata,
    )


@router.get("/logs", response_model=list[SMTPLogOut])
def listar_logs_smtp(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
):
    return (
        db.query(SMTPLog)
        .order_by(SMTPLog.creado_en.desc())
        .limit(limit)
        .all()
    )
