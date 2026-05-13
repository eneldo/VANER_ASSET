"""
===========================================================
MIDDLEWARE DE SEGURIDAD DE ARCHIVOS
FASE 31.8 — SGA PRO
===========================================================

Aquí inicia:
- Validación de tamaño
- Validación MIME
- Validación extensión
- Sanitización de nombre
- Protección Path Traversal
===========================================================
"""

import os
import re
import uuid
from fastapi import UploadFile, HTTPException

# ===========================================================
# CONFIGURACIÓN GLOBAL
# ===========================================================

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
    ".doc",
    ".docx",
    ".xlsx"
}

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}


# ===========================================================
# SANITIZAR NOMBRE
# ===========================================================

def sanitize_filename(filename: str) -> str:
    """
    Limpia nombres peligrosos
    """

    filename = filename.replace("..", "")
    filename = filename.replace("/", "")
    filename = filename.replace("\\", "")

    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    return filename


# ===========================================================
# VALIDAR EXTENSIÓN
# ===========================================================

def validate_extension(filename: str):

    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida: {ext}"
        )


# ===========================================================
# VALIDAR MIME
# ===========================================================

def validate_mime(file: UploadFile):

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo MIME no permitido: {file.content_type}"
        )


# ===========================================================
# VALIDAR TAMAÑO
# ===========================================================

async def validate_size(file: UploadFile):

    content = await file.read()

    size = len(content)

    await file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Archivo supera el tamaño permitido (15MB)"
        )


# ===========================================================
# GENERAR NOMBRE SEGURO
# ===========================================================

def generate_secure_filename(filename: str):

    ext = os.path.splitext(filename)[1]

    unique_name = f"{uuid.uuid4()}{ext}"

    return unique_name