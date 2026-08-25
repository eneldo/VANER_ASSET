from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile, is_zipfile

from fastapi import HTTPException, UploadFile, status

from app.config import settings


ALLOWED_MIME_TYPES = {
    ".csv": {"text/csv", "application/csv", "text/plain", "application/octet-stream"},
    ".xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
        "application/octet-stream",
    },
}
READ_CHUNK_SIZE = 1024 * 1024
MAX_XLSX_ENTRIES = 500
MAX_XLSX_EXPANSION_FACTOR = 8


async def read_inventory_upload(archivo: UploadFile) -> tuple[bytes, str]:
    filename = archivo.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no permitido. Usa CSV o XLSX.",
        )

    content_type = (archivo.content_type or "application/octet-stream").lower()
    if content_type not in ALLOWED_MIME_TYPES[extension]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de archivo no coincide con CSV o XLSX.",
        )

    max_bytes = settings.MAX_INVENTORY_IMPORT_MB * 1024 * 1024
    chunks = []
    total = 0
    while True:
        chunk = await archivo.read(READ_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo supera {settings.MAX_INVENTORY_IMPORT_MB} MB.",
            )
        chunks.append(chunk)

    content = b"".join(chunks)
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    if extension == ".csv":
        _validate_csv(content)
    else:
        _validate_xlsx(content, max_bytes)
    return content, extension


def validate_inventory_shape(row_count: int, column_count: int) -> None:
    if row_count > settings.MAX_INVENTORY_IMPORT_ROWS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo supera {settings.MAX_INVENTORY_IMPORT_ROWS} filas.",
        )
    if column_count > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo supera el máximo de 100 columnas.",
        )


def _validate_csv(content: bytes) -> None:
    if b"\x00" in content:
        raise HTTPException(status_code=400, detail="El CSV contiene datos binarios inválidos.")
    try:
        content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="El CSV debe estar codificado en UTF-8.",
        ) from exc


def _validate_xlsx(content: bytes, max_bytes: int) -> None:
    stream = BytesIO(content)
    if not is_zipfile(stream):
        raise HTTPException(status_code=400, detail="El XLSX no tiene una estructura válida.")

    try:
        with ZipFile(stream) as workbook:
            entries = workbook.infolist()
            if len(entries) > MAX_XLSX_ENTRIES:
                raise HTTPException(status_code=400, detail="El XLSX contiene demasiados archivos internos.")

            names = {entry.filename for entry in entries}
            required = {"[Content_Types].xml", "xl/workbook.xml"}
            if not required.issubset(names):
                raise HTTPException(status_code=400, detail="El XLSX está incompleto o no es válido.")

            expanded_size = 0
            for entry in entries:
                path = PurePosixPath(entry.filename)
                if path.is_absolute() or ".." in path.parts:
                    raise HTTPException(status_code=400, detail="El XLSX contiene rutas internas inválidas.")
                expanded_size += entry.file_size
                if expanded_size > max_bytes * MAX_XLSX_EXPANSION_FACTOR:
                    raise HTTPException(status_code=400, detail="El XLSX excede el tamaño expandido permitido.")
    except BadZipFile as exc:
        raise HTTPException(status_code=400, detail="El XLSX está dañado.") from exc
