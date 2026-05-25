# ============================================================
# ROUTER: Configuración Inteligente SaaS
# Archivo: backend/app/routers/configuracion_saas.py
# Fase 34.1 - Configuración Inteligente SaaS PRO
# ============================================================

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.configuracion_saas import ConfiguracionSaaS
from app.schemas.configuracion_saas import (
    ApiResponse,
    ConfiguracionSaaSOut,
    ConfiguracionSaaSUpdate,
    TestEmailRequest,
)
from app.services.email_service import send_test_email
from app.services.backup_service import create_backup_marker

router = APIRouter(prefix="/configuracion-saas", tags=["Configuración SaaS"])

# Ruta interna donde se guardan logos corporativos de plataforma.
UPLOAD_DIR = Path("app/uploads/logos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def _default_config() -> ConfiguracionSaaS:
    """Devuelve una configuración inicial profesional si la tabla está vacía."""
    return ConfiguracionSaaS(
        id=1,
        nombre_plataforma="SGA SaaS PRO",
        logo_url=None,
        color_primario="#2563eb",
        color_secundario="#0f172a",
        color_acento="#22c55e",
        smtp={
            "host": "",
            "port": 587,
            "username": "",
            "password": "",
            "from_email": "",
            "from_name": "SGA SaaS PRO",
            "use_tls": True,
            "use_ssl": False,
        },
        backups={
            "habilitado": True,
            "frecuencia": "DIARIO",
            "hora": "02:00",
            "retencion_dias": 30,
            "incluir_evidencias": True,
            "ruta_destino": "app/exports/backups",
        },
        evidencias={
            "max_mb": 15,
            "formatos_permitidos": ["jpg", "jpeg", "png", "pdf", "webp"],
            "requiere_descripcion": False,
            "permitir_pdf": True,
            "permitir_imagen": True,
            "compresion_imagen": True,
        },
        mantenimiento={
            "dias_alerta_vencimiento": 3,
            "permitir_reprogramacion": True,
            "requiere_evidencia_finalizar": True,
            "requiere_observacion_finalizar": True,
            "estados_permitidos": ["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO", "FINALIZADO", "ANULADO"],
        },
        notificaciones={
            "email_habilitado": True,
            "whatsapp_habilitado": False,
            "whatsapp_provider": "",
            "whatsapp_token": "",
            "notificar_asignacion": True,
            "notificar_vencimiento": True,
            "notificar_finalizacion": True,
            "notificar_cliente": True,
            "correos_copia": [],
        },
    )


def get_or_create_config(db: Session) -> ConfiguracionSaaS:
    config = db.query(ConfiguracionSaaS).filter(ConfiguracionSaaS.id == 1).first()
    if config:
        return config

    config = _default_config()
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("/", response_model=ConfiguracionSaaSOut)
def obtener_configuracion(db: Session = Depends(get_db)):
    """Obtiene la configuración global actual de la plataforma."""
    return get_or_create_config(db)


@router.put("/", response_model=ConfiguracionSaaSOut)
def guardar_configuracion(payload: ConfiguracionSaaSUpdate, db: Session = Depends(get_db)):
    """Guarda todos los bloques de configuración en PostgreSQL."""
    config = get_or_create_config(db)

    data = payload.model_dump()
    for key, value in data.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)
    return config


@router.post("/logo", response_model=ApiResponse)
async def subir_logo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Sube el logo real de la plataforma y guarda la URL para preview inmediato."""
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_LOGO_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usa PNG, JPG, JPEG, WEBP o SVG.")

    safe_name = f"logo_sga_{uuid4().hex}{extension}"
    destination = UPLOAD_DIR / safe_name

    content = await file.read()
    max_bytes = 5 * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail="El logo supera 5 MB.")

    destination.write_bytes(content)

    logo_url = f"/uploads/logos/{safe_name}"
    config = get_or_create_config(db)
    config.logo_url = logo_url
    db.commit()

    return ApiResponse(ok=True, message="Logo subido correctamente.", data={"logo_url": logo_url})


@router.post("/test-email", response_model=ApiResponse)
def probar_correo(payload: TestEmailRequest, db: Session = Depends(get_db)):
    """Envía un correo de prueba con la configuración SMTP actual."""
    config = get_or_create_config(db)

    try:
        send_test_email(config.smtp or {}, str(payload.to_email), payload.subject, payload.message)
        return ApiResponse(ok=True, message="Correo de prueba enviado correctamente.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"No fue posible enviar el correo: {exc}") from exc


@router.post("/backup/probar", response_model=ApiResponse)
def probar_backup(db: Session = Depends(get_db)):
    """Valida la ruta y crea un marcador de backup configurado."""
    config = get_or_create_config(db)
    result = create_backup_marker(config.backups or {})
    return ApiResponse(ok=True, message="Configuración de backup validada correctamente.", data=result)
