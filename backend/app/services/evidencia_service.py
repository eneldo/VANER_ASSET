"""
===========================================================
SERVICIO DE EVIDENCIAS PRO
Archivo: backend/app/services/evidencia_service.py

FIX PRODUCCIÓN:
- Unifica la ruta física con main.py.
- Guarda en /app/uploads/evidencias dentro del contenedor.
- docker-compose.yml persiste esa ruta con volumen.
- Retorna URL pública /uploads/evidencias/<archivo>.
===========================================================
"""

import os
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.middleware.file_security import (
    sanitize_filename,
    validate_extension,
    validate_mime,
    validate_size,
    generate_secure_filename,
)

# ===========================================================
# RUTA ÚNICA DE UPLOADS
# ===========================================================
# En Docker/Dokploy usa /app/uploads.
# En local puedes usar UPLOAD_DIR desde .env si lo necesitas.
# ===========================================================

UPLOADS_DIR = Path(os.getenv("UPLOAD_DIR") or "/app/uploads").resolve()
EVIDENCIAS_DIR = UPLOADS_DIR / "evidencias"

EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)


# ===========================================================
# GUARDAR ARCHIVO SEGURO
# ===========================================================

async def save_secure_file(file: UploadFile) -> dict:
    """
    Valida y guarda una evidencia.

    Retorna:
    {
        "filename": "uuid.ext",
        "path": "/app/uploads/evidencias/uuid.ext",
        "public_url": "/uploads/evidencias/uuid.ext"
    }
    """

    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Archivo no recibido")

    validate_extension(file.filename)
    validate_mime(file)
    await validate_size(file)

    clean_name = sanitize_filename(file.filename)
    secure_name = generate_secure_filename(clean_name)

    final_path = EVIDENCIAS_DIR / secure_name

    try:
        file.file.seek(0)

        with final_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo guardar la evidencia en disco: {exc}",
        )

    return {
        "filename": secure_name,
        "path": str(final_path),
        "public_url": f"/uploads/evidencias/{secure_name}",
    }


# ===========================================================
# OBTENER RUTA FÍSICA SEGURA
# ===========================================================

def get_evidencia_path(filename_or_url: str) -> Path:
    """
    Recibe un nombre o URL y devuelve la ruta segura del archivo.
    """

    safe_name = Path(filename_or_url or "").name

    if not safe_name:
        raise ValueError("Nombre de archivo inválido")

    return EVIDENCIAS_DIR / safe_name
