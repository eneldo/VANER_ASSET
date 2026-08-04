import asyncio
import os
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import settings
from app.middleware.file_security import (
    generate_secure_filename,
    sanitize_filename,
    validate_extension,
    validate_mime,
    validate_size,
)
from app.models.configuracion_saas import ConfiguracionSaaS
from app.services.file_optimizer import IMAGE_EXTENSIONS, PDF_EXTENSION, optimize_file_content


UPLOADS_DIR = Path(os.getenv("UPLOAD_DIR") or settings.UPLOAD_DIR).resolve()
EVIDENCIAS_DIR = UPLOADS_DIR / "evidencias"
EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_EVIDENCE_CONFIG = {
    "max_mb": 15,
    "formatos_permitidos": ["jpg", "jpeg", "png", "pdf", "webp"],
    "permitir_pdf": True,
    "permitir_imagen": True,
    "compresion_imagen": True,
    "compresion_pdf": True,
    "calidad_imagen": 82,
    "max_dimension_imagen": 2048,
}


def get_evidence_upload_config(db) -> dict:
    row = db.query(ConfiguracionSaaS).filter(ConfiguracionSaaS.id == 1).first()
    stored_config = row.evidencias if row and isinstance(row.evidencias, dict) else {}
    return {**DEFAULT_EVIDENCE_CONFIG, **stored_config}


async def save_secure_file(file: UploadFile, evidence_config: dict | None = None) -> dict:
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Archivo no recibido")

    config = {**DEFAULT_EVIDENCE_CONFIG, **(evidence_config or {})}
    extension = Path(file.filename).suffix.lower()
    allowed_formats = {
        str(item).strip().lower().lstrip(".")
        for item in config.get("formatos_permitidos", [])
        if str(item).strip()
    }

    validate_extension(file.filename)
    validate_mime(file)

    if extension.lstrip(".") not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"Formato no permitido: {extension}")
    if extension in IMAGE_EXTENSIONS and not config.get("permitir_imagen", True):
        raise HTTPException(status_code=400, detail="La carga de imagenes esta deshabilitada")
    if extension == PDF_EXTENSION and not config.get("permitir_pdf", True):
        raise HTTPException(status_code=400, detail="La carga de PDF esta deshabilitada")

    max_mb = max(1, min(int(config.get("max_mb", 15)), 100))
    content = await validate_size(file, max_mb * 1024 * 1024)
    optimized = await asyncio.to_thread(optimize_file_content, content, extension, config)

    clean_name = sanitize_filename(file.filename)
    secure_name = generate_secure_filename(f"{Path(clean_name).stem}{optimized.extension}")
    final_path = EVIDENCIAS_DIR / secure_name
    temporary_path = final_path.with_suffix(f"{final_path.suffix}.tmp")

    try:
        temporary_path.write_bytes(optimized.content)
        temporary_path.replace(final_path)
    except Exception as exc:
        temporary_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"No se pudo guardar la evidencia en disco: {exc}") from exc

    return {
        "filename": secure_name,
        "path": str(final_path),
        "public_url": secure_name,
        "optimized": optimized.optimized,
        "original_size": optimized.original_size,
        "stored_size": optimized.stored_size,
        "optimization_engine": optimized.engine,
    }


def get_evidencia_path(filename_or_url: str) -> Path:
    safe_name = Path(filename_or_url or "").name
    if not safe_name:
        raise ValueError("Nombre de archivo invalido")
    return EVIDENCIAS_DIR / safe_name
