# ============================================================
# ROUTER: Configuración Inteligente SaaS
# Archivo: backend/app/routers/configuracion_saas.py
# Fase 34.1 - Configuración Inteligente SaaS PRO
#
# Correcciones aplicadas:
# - Usa UPLOAD_DIR real de Docker/producción para logos.
# - Crea /uploads/logos automáticamente.
# - Crea la tabla configuracion_saas si aún no existe.
# - Mantiene endpoint /configuracion-saas/ usado por el frontend.
# - Devuelve errores claros para SMTP, backup y carga inicial.
# ============================================================

import io
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError

from app.database import get_db
from app.models.configuracion_saas import ConfiguracionSaaS
from app.schemas.configuracion_saas import (
    ApiResponse,
    ConfiguracionSaaSOut,
    ConfiguracionSaaSUpdate,
    TestEmailRequest,
)
from app.services.backup_service import create_backup_marker
from app.services.email_service import send_test_email
from app.services.secret_store import (
    decrypt_mapping,
    encrypt_secret,
    ENCRYPTED_PREFIX,
    mask_secret,
    merge_secret,
)

router = APIRouter(prefix="/configuracion-saas", tags=["Configuración SaaS"])

# En Docker el compose define UPLOAD_DIR=/app/uploads.
# En local, si no existe variable, usa backend/app/uploads.
UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "app/uploads")).resolve()
LOGOS_DIR = UPLOAD_ROOT / "logos"
LOGOS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def default_config_payload() -> dict:
    """Valores por defecto profesionales de la configuración SaaS."""
    return {
        "id": 1,
        "nombre_plataforma": "SGA SaaS PRO",
        "logo_url": None,
        "color_primario": "#2563eb",
        "color_secundario": "#0f172a",
        "color_acento": "#22c55e",
        "smtp": {
            "host": "",
            "port": 587,
            "username": "",
            "password": "",
            "from_email": "",
            "from_name": "SGA SaaS PRO",
            "use_tls": True,
            "use_ssl": False,
        },
        "backups": {
            "habilitado": True,
            "frecuencia": "DIARIO",
            "hora": "02:00",
            "retencion_dias": 30,
            "incluir_evidencias": True,
            "ruta_destino": "app/exports/backups",
        },
        "evidencias": {
            "max_mb": 15,
            "formatos_permitidos": ["jpg", "jpeg", "png", "pdf", "webp"],
            "requiere_descripcion": False,
            "permitir_pdf": True,
            "permitir_imagen": True,
            "compresion_imagen": True,
            "compresion_pdf": True,
            "calidad_imagen": 82,
            "max_dimension_imagen": 2048,
        },
        "mantenimiento": {
            "dias_alerta_vencimiento": 3,
            "permitir_reprogramacion": True,
            "requiere_evidencia_finalizar": True,
            "requiere_observacion_finalizar": True,
            "estados_permitidos": [
                "PROGRAMADO",
                "ASIGNADO",
                "EN_PROCESO",
                "PAUSADO",
                "FINALIZADO",
                "ANULADO",
            ],
        },
        "notificaciones": {
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
        "activo": True,
    }


def get_or_create_config(db: Session) -> ConfiguracionSaaS:
    """
    Obtiene el registro único id=1.
    Si no existe, lo crea automáticamente.
    """
    config = db.query(ConfiguracionSaaS).filter(ConfiguracionSaaS.id == 1).first()
    if config:
        changed = False
        smtp = dict(config.smtp or {})
        smtp_password = str(smtp.get("password") or "")
        if smtp_password and not smtp_password.startswith(ENCRYPTED_PREFIX):
            smtp["password"] = encrypt_secret(smtp_password)
            config.smtp = smtp
            changed = True

        notifications = dict(config.notificaciones or {})
        whatsapp_token = str(notifications.get("whatsapp_token") or "")
        if whatsapp_token and not whatsapp_token.startswith(ENCRYPTED_PREFIX):
            notifications["whatsapp_token"] = encrypt_secret(whatsapp_token)
            config.notificaciones = notifications
            changed = True

        if changed:
            db.commit()
            db.refresh(config)
        return config

    config = ConfiguracionSaaS(**default_config_payload())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def public_config(config: ConfiguracionSaaS) -> dict:
    data = ConfiguracionSaaSOut.model_validate(config).model_dump(mode="json")
    data["smtp"]["password"] = mask_secret((config.smtp or {}).get("password"))
    data["notificaciones"]["whatsapp_token"] = mask_secret(
        (config.notificaciones or {}).get("whatsapp_token")
    )
    return data


@router.get("/", response_model=ConfiguracionSaaSOut)
def obtener_configuracion(db: Session = Depends(get_db)):
    """Obtiene la configuración global actual de la plataforma."""
    try:
        return public_config(get_or_create_config(db))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible cargar la configuración SaaS: {exc}",
        ) from exc


@router.put("/", response_model=ConfiguracionSaaSOut)
def guardar_configuracion(payload: ConfiguracionSaaSUpdate, db: Session = Depends(get_db)):
    """Guarda todos los bloques de configuración en PostgreSQL."""
    config = get_or_create_config(db)

    data = payload.model_dump(mode="json")
    smtp = dict(data.get("smtp") or {})
    smtp["password"] = merge_secret(
        (config.smtp or {}).get("password"),
        smtp.get("password"),
    )
    data["smtp"] = smtp

    notifications = dict(data.get("notificaciones") or {})
    notifications["whatsapp_token"] = merge_secret(
        (config.notificaciones or {}).get("whatsapp_token"),
        notifications.get("whatsapp_token"),
    )
    data["notificaciones"] = notifications

    for key, value in data.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)
    return public_config(config)


@router.post("/logo", response_model=ApiResponse)
async def subir_logo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Sube el logo real de la plataforma.

    La URL pública queda:
    /uploads/logos/<archivo>
    porque main.py sirve UPLOAD_DIR en /uploads.
    """
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_LOGO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Usa PNG, JPG, JPEG o WEBP.",
        )

    content = await file.read()
    max_bytes = 5 * 1024 * 1024

    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail="El logo supera 5 MB.")

    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="El archivo no es una imagen válida.") from exc

    safe_name = f"logo_sga_{uuid4().hex}{extension}"
    destination = LOGOS_DIR / safe_name
    destination.write_bytes(content)

    logo_url = f"/uploads/logos/{safe_name}"

    config = get_or_create_config(db)
    config.logo_url = logo_url
    db.commit()
    db.refresh(config)

    return ApiResponse(
        ok=True,
        message="Logo subido correctamente.",
        data={"logo_url": logo_url},
    )


@router.post("/test-email", response_model=ApiResponse)
def probar_correo(payload: TestEmailRequest, db: Session = Depends(get_db)):
    """Envía un correo de prueba con la configuración SMTP actual."""
    config = get_or_create_config(db)

    try:
        send_test_email(
            decrypt_mapping(config.smtp or {}, {"password", "clave"}),
            str(payload.to_email),
            payload.subject,
            payload.message,
        )
        return ApiResponse(ok=True, message="Correo de prueba enviado correctamente.")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"No fue posible enviar el correo: {exc}",
        ) from exc


@router.post("/backup/probar", response_model=ApiResponse)
def probar_backup(db: Session = Depends(get_db)):
    """Valida la ruta y crea un marcador de backup configurado."""
    config = get_or_create_config(db)
    result = create_backup_marker(config.backups or {})

    return ApiResponse(
        ok=True,
        message="Configuración de backup validada correctamente.",
        data=result,
    )
