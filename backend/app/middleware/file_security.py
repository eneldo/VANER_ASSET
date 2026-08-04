import os
import re
import uuid

from fastapi import HTTPException, UploadFile


MAX_FILE_SIZE = 15 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".pdf",
    ".doc",
    ".docx",
    ".xlsx",
}

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def sanitize_filename(filename: str) -> str:
    filename = filename.replace("..", "")
    filename = filename.replace("/", "")
    filename = filename.replace("\\", "")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", filename)


def validate_extension(filename: str) -> None:
    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extension no permitida: {extension}")


def validate_mime(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Tipo MIME no permitido: {file.content_type}")


async def validate_size(file: UploadFile, max_file_size: int = MAX_FILE_SIZE) -> bytes:
    content = await file.read()
    await file.seek(0)

    if len(content) > max_file_size:
        max_mb = max_file_size // (1024 * 1024)
        raise HTTPException(status_code=400, detail=f"Archivo supera el tamano permitido ({max_mb}MB)")

    return content


def generate_secure_filename(filename: str) -> str:
    extension = os.path.splitext(filename)[1].lower()
    return f"{uuid.uuid4()}{extension}"
