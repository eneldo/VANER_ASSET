import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
PDF_EXTENSION = ".pdf"


@dataclass(frozen=True)
class OptimizationResult:
    content: bytes
    extension: str
    optimized: bool
    original_size: int
    stored_size: int
    engine: str


def optimize_file_content(content: bytes, extension: str, config: dict) -> OptimizationResult:
    normalized_extension = extension.lower()

    if normalized_extension in IMAGE_EXTENSIONS:
        return _optimize_image(content, normalized_extension, config)
    if normalized_extension == PDF_EXTENSION:
        return _optimize_pdf(content, config)

    return _unchanged(content, normalized_extension, "none")


def _optimize_image(content: bytes, extension: str, config: dict) -> OptimizationResult:
    if not config.get("compresion_imagen", True):
        _validate_image(content)
        return _unchanged(content, extension, "disabled")

    quality = max(50, min(int(config.get("calidad_imagen", 82)), 95))
    max_dimension = max(800, min(int(config.get("max_dimension_imagen", 2048)), 4096))

    try:
        with Image.open(BytesIO(content)) as source:
            source.load()
            image = ImageOps.exif_transpose(source)
            original_dimensions = image.size
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            resized = image.size != original_dimensions
            output = BytesIO()

            if extension in {".jpg", ".jpeg"}:
                image = _flatten_for_jpeg(image)
                image.save(output, format="JPEG", quality=quality, optimize=True, progressive=True)
                stored_extension = ".jpg"
            elif extension == ".png":
                image.save(output, format="PNG", optimize=True, compress_level=9)
                stored_extension = ".png"
            else:
                image.save(output, format="WEBP", quality=quality, method=6)
                stored_extension = ".webp"
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="La imagen esta danada o no es valida") from exc

    optimized_content = output.getvalue()
    if not resized and len(optimized_content) >= len(content):
        return _unchanged(content, extension, "pillow")

    return OptimizationResult(
        content=optimized_content,
        extension=stored_extension,
        optimized=True,
        original_size=len(content),
        stored_size=len(optimized_content),
        engine="pillow",
    )


def _validate_image(content: bytes) -> None:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="La imagen esta danada o no es valida") from exc


def _flatten_for_jpeg(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return image if image.mode == "RGB" else image.convert("RGB")


def _optimize_pdf(content: bytes, config: dict) -> OptimizationResult:
    if not content.lstrip().startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="El archivo PDF esta danado o no es valido")
    if not config.get("compresion_pdf", True):
        return _unchanged(content, PDF_EXTENSION, "disabled")

    qpdf = shutil.which("qpdf")
    if not qpdf:
        return _unchanged(content, PDF_EXTENSION, "qpdf-unavailable")

    try:
        with tempfile.TemporaryDirectory(prefix="sga-pdf-") as temp_dir:
            input_path = Path(temp_dir) / "input.pdf"
            output_path = Path(temp_dir) / "optimized.pdf"
            input_path.write_bytes(content)
            result = subprocess.run(
                [qpdf, "--stream-data=compress", "--object-streams=generate",
                 "--recompress-flate", "--compression-level=9",
                 str(input_path), str(output_path)],
                capture_output=True,
                check=False,
                timeout=60,
            )
            if result.returncode not in {0, 3} or not output_path.exists():
                return _unchanged(content, PDF_EXTENSION, "qpdf-fallback")
            optimized_content = output_path.read_bytes()
    except (OSError, subprocess.SubprocessError):
        return _unchanged(content, PDF_EXTENSION, "qpdf-fallback")

    if not optimized_content.startswith(b"%PDF-") or len(optimized_content) >= len(content):
        return _unchanged(content, PDF_EXTENSION, "qpdf")

    return OptimizationResult(
        content=optimized_content,
        extension=PDF_EXTENSION,
        optimized=True,
        original_size=len(content),
        stored_size=len(optimized_content),
        engine="qpdf",
    )


def _unchanged(content: bytes, extension: str, engine: str) -> OptimizationResult:
    return OptimizationResult(
        content=content,
        extension=extension,
        optimized=False,
        original_size=len(content),
        stored_size=len(content),
        engine=engine,
    )
