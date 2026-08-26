# ============================================================
# SERVICIO: Backups Inteligentes SaaS PRO
# Archivo: backend/app/services/smart_backup_service.py
# Fase 34.2.2
# ============================================================

import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.models.backup_historial import BackupHistorial
from app.config import settings
from app.services.backup_crypto import (
    backup_encryption_enabled,
    decrypt_backup_file,
    encrypt_backup_file,
)

# Carpeta persistente recomendada. En Docker/Dokploy puede sobrescribirse con BACKUP_DIR.
BACKUP_DIR = Path(os.getenv("BACKUP_DIR") or "app/backups").resolve()
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Ruta correcta para SGA_SaaS en Docker: /app/app/uploads.
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR") or "app/uploads").resolve()


class SmartBackupService:
    """Motor central para generar, listar, limpiar y descargar backups."""

    def __init__(self, db: Session):
        self.db = db

    def _crear_registro(self, tipo: str, incluir_db: bool, incluir_uploads: bool, incluir_codigo: bool, creado_por: Optional[str]):
        registro = BackupHistorial(
            tipo=tipo.upper(),
            estado="EN_PROCESO",
            mensaje="Backup iniciado",
            incluye_db=incluir_db,
            incluye_uploads=incluir_uploads,
            incluye_codigo=incluir_codigo,
            creado_por=creado_por or "sistema",
            metadata_json={},
        )
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def ejecutar_backup(self, tipo="MANUAL", incluir_db=True, incluir_uploads=True, incluir_codigo=False, creado_por="admin") -> BackupHistorial:
        registro = self._crear_registro(tipo, incluir_db, incluir_uploads, incluir_codigo, creado_por)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = BACKUP_DIR / f"tmp_backup_{timestamp}"
        zip_name = f"vaner_backup_{timestamp}.zip"
        zip_path = BACKUP_DIR / zip_name
        work_dir.mkdir(parents=True, exist_ok=True)

        try:
            metadata = {}

            if incluir_db:
                sql_file = work_dir / f"postgres_sga_{timestamp}.sql"
                self._dump_postgres(sql_file)
                metadata["db_sql"] = sql_file.name

            if incluir_uploads:
                uploads_zip = work_dir / f"uploads_{timestamp}.zip"
                self._zip_folder(UPLOAD_DIR, uploads_zip)
                metadata["uploads_zip"] = uploads_zip.name

            if incluir_codigo:
                code_zip = work_dir / f"codigo_backend_{timestamp}.zip"
                self._zip_folder(Path("/app"), code_zip, exclude_names={".venv", "__pycache__", "node_modules", "backups"})
                metadata["codigo_zip"] = code_zip.name

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in work_dir.iterdir():
                    if item.is_file():
                        zf.write(item, arcname=item.name)

            stored_path = zip_path
            if backup_encryption_enabled():
                stored_path = zip_path.with_suffix(zip_path.suffix + ".sgaenc")
                encrypt_backup_file(zip_path, stored_path)
                zip_path.unlink(missing_ok=True)
                metadata["encrypted"] = True
                metadata["encryption_format"] = "SGABKP1"
            elif settings.BACKUP_ENCRYPTION_REQUIRED:
                raise RuntimeError("El cifrado de backups es obligatorio")
            else:
                metadata["encrypted"] = False

            remote_key = self._upload_remote_backup(stored_path)
            if remote_key:
                metadata["remote_key"] = remote_key

            registro.estado = "EXITOSO"
            registro.nombre_archivo = zip_name
            registro.ruta_archivo = str(stored_path)
            registro.tamano_bytes = stored_path.stat().st_size if stored_path.exists() else 0
            registro.mensaje = "Backup generado correctamente"
            registro.finalizado_en = datetime.now(timezone.utc)
            registro.metadata_json = metadata
            self.db.commit()
            self.db.refresh(registro)
            return registro

        except Exception as exc:
            registro.estado = "ERROR"
            registro.mensaje = f"Error generando backup: {exc}"
            registro.finalizado_en = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(registro)
            raise HTTPException(status_code=500, detail=registro.mensaje)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def _upload_remote_backup(self, backup_path: Path) -> str | None:
        if not settings.S3_BACKUP_ENABLED:
            return None

        client = self._s3_client()
        prefix = settings.S3_BACKUP_PREFIX.strip("/")
        remote_key = f"{prefix}/{backup_path.name}" if prefix else backup_path.name
        client.upload_file(
            str(backup_path),
            settings.S3_BACKUP_BUCKET,
            remote_key,
            ExtraArgs={"ServerSideEncryption": "AES256"},
        )
        return remote_key

    def _s3_client(self):
        import boto3

        return boto3.client(
            "s3",
            endpoint_url=settings.S3_BACKUP_ENDPOINT_URL,
            region_name=settings.S3_BACKUP_REGION,
            aws_access_key_id=settings.S3_BACKUP_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_BACKUP_SECRET_ACCESS_KEY,
        )

    def _delete_remote_backup(self, item: BackupHistorial) -> None:
        metadata = dict(item.metadata_json or {})
        remote_key = metadata.get("remote_key")
        if not remote_key:
            return
        if not settings.S3_BACKUP_ENABLED:
            raise RuntimeError("S3 debe estar configurado para eliminar el backup remoto")
        self._s3_client().delete_object(
            Bucket=settings.S3_BACKUP_BUCKET,
            Key=remote_key,
        )

    def preparar_descarga(self, item: BackupHistorial) -> tuple[Path, bool]:
        source = self._safe_local_backup_path(item.ruta_archivo)
        if not source.exists():
            raise HTTPException(status_code=404, detail="Archivo de backup no encontrado")

        if not bool((item.metadata_json or {}).get("encrypted")):
            return source, False

        file_descriptor, temporary_name = tempfile.mkstemp(prefix="vaner_backup_", suffix=".zip")
        os.close(file_descriptor)
        temporary = Path(temporary_name)
        try:
            decrypt_backup_file(source, temporary)
            return temporary, True
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    def _safe_local_backup_path(self, value: str | None) -> Path:
        if not value:
            raise HTTPException(status_code=404, detail="Backup sin archivo asociado")
        path = Path(value).resolve()
        try:
            path.relative_to(BACKUP_DIR)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Ruta de backup inválida") from exc
        return path

    def _dump_postgres(self, destino: Path):
        database_url = settings.BACKUP_DATABASE_URL
        if not database_url and settings.APP_ENV.lower() != "production":
            database_url = settings.DATABASE_URL
        if not database_url:
            raise RuntimeError("BACKUP_DATABASE_URL es obligatoria para generar backups")

        env = os.environ.copy()

        if database_url.startswith("postgres"):
            url = make_url(database_url)
            pg_user = url.username
            pg_db = url.database
            pg_host = url.host
            pg_port = str(url.port or 5432)
            pg_password = url.password
        else:
            pg_user = os.getenv("POSTGRES_USER")
            pg_db = os.getenv("POSTGRES_DB")
            pg_host = os.getenv("POSTGRES_HOST")
            pg_port = os.getenv("POSTGRES_PORT") or "5432"
            pg_password = os.getenv("POSTGRES_PASSWORD")

        if not all((pg_user, pg_db, pg_host, pg_password)):
            raise RuntimeError("Configuración PostgreSQL incompleta para generar el backup")

        env["PGPASSWORD"] = pg_password
        cmd = [
            "pg_dump",
            "-h", pg_host,
            "-p", pg_port,
            "-U", pg_user,
            "-d", pg_db,
        ]

        with destino.open("wb") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode("utf-8", errors="ignore") or "pg_dump falló")

    def _zip_folder(self, carpeta: Path, destino: Path, exclude_names=None):
        exclude_names = exclude_names or set()
        if not carpeta.exists():
            with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("README.txt", f"Carpeta no encontrada: {carpeta}")
            return

        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in carpeta.rglob("*"):
                if any(part in exclude_names for part in path.parts):
                    continue
                if path.is_file():
                    zf.write(path, arcname=str(path.relative_to(carpeta)))

    def listar(self, limit: int = 50):
        return self.db.query(BackupHistorial).order_by(BackupHistorial.iniciado_en.desc()).limit(limit).all()

    def obtener(self, backup_id: UUID) -> BackupHistorial:
        obj = self.db.query(BackupHistorial).filter(BackupHistorial.id == backup_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Backup no encontrado")
        return obj

    def limpiar_antiguos(self, retencion_dias: int = 15) -> int:
        limite = datetime.now(timezone.utc) - timedelta(days=retencion_dias)
        antiguos = self.db.query(BackupHistorial).filter(BackupHistorial.iniciado_en < limite).all()
        eliminados = 0
        for item in antiguos:
            try:
                self._delete_remote_backup(item)
                if item.ruta_archivo:
                    self._safe_local_backup_path(item.ruta_archivo).unlink(missing_ok=True)
                self.db.delete(item)
                eliminados += 1
            except Exception as exc:
                metadata = dict(item.metadata_json or {})
                metadata["cleanup_error"] = str(exc)
                metadata["cleanup_failed_at"] = datetime.now(timezone.utc).isoformat()
                item.metadata_json = metadata
        self.db.commit()
        return eliminados

    def status(self):
        backups = self.listar(1000)
        total_bytes = sum(b.tamano_bytes or 0 for b in backups)
        ultimo = backups[0] if backups else None
        return {
            "ok": True,
            "backups_dir": str(BACKUP_DIR),
            "total_backups": len(backups),
            "total_bytes": total_bytes,
            "ultimo_backup": ultimo,
            "mensaje": "Servicio de backups inteligente operativo",
        }
